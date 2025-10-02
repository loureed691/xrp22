"""
KuCoin Futures API Client Wrapper
"""
import time
import hmac
import hashlib
import base64
import json
import requests
from typing import Dict, List, Optional
from urllib.parse import urlencode
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def retry_on_failure(max_retries=3, backoff_factor=2):
    """Decorator to retry API calls on failure with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = backoff_factor ** attempt
                        logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s: {e}")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"API call failed after {max_retries} attempts: {e}")
            raise last_exception
        return wrapper
    return decorator


class RateLimiter:
    """Simple rate limiter to prevent API throttling"""
    def __init__(self, calls_per_second=10):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second
        self.last_call = 0
    
    def wait(self):
        """Wait if necessary to respect rate limit"""
        now = time.time()
        time_since_last_call = now - self.last_call
        if time_since_last_call < self.min_interval:
            sleep_time = self.min_interval - time_since_last_call
            time.sleep(sleep_time)
        self.last_call = time.time()


class KuCoinFuturesClient:
    """KuCoin Futures API Client"""
    
    def __init__(self, api_key: str, api_secret: str, api_passphrase: str, base_url: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.base_url = base_url
        
        # Create session with connection pooling for better performance
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=3,
            pool_block=False
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Rate limiter: KuCoin allows ~100 requests per 10 seconds for futures
        # We'll use a conservative 10 requests per second
        self.rate_limiter = RateLimiter(calls_per_second=10)
        
    def _generate_signature(self, timestamp: str, method: str, endpoint: str, body: str = '') -> str:
        """Generate signature for API request"""
        str_to_sign = f"{timestamp}{method}{endpoint}{body}"
        signature = base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                str_to_sign.encode('utf-8'),
                hashlib.sha256
            ).digest()
        )
        return signature.decode('utf-8')
    
    def _generate_passphrase(self) -> str:
        """Generate encrypted passphrase"""
        passphrase = base64.b64encode(
            hmac.new(
                self.api_secret.encode('utf-8'),
                self.api_passphrase.encode('utf-8'),
                hashlib.sha256
            ).digest()
        )
        return passphrase.decode('utf-8')
    
    def _get_headers(self, method: str, endpoint: str, body: str = '') -> Dict:
        """Generate headers for API request"""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp, method, endpoint, body)
        passphrase = self._generate_passphrase()
        
        return {
            'KC-API-KEY': self.api_key,
            'KC-API-SIGN': signature,
            'KC-API-TIMESTAMP': timestamp,
            'KC-API-PASSPHRASE': passphrase,
            'KC-API-KEY-VERSION': '2',
            'Content-Type': 'application/json'
        }
    
    @retry_on_failure(max_retries=3, backoff_factor=2)
    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """Make API request"""
        # Apply rate limiting
        self.rate_limiter.wait()
        
        url = f"{self.base_url}{endpoint}"
        body = ''
        
        if data:
            body = json.dumps(data)
        
        # For GET/DELETE requests with params, include query string in signature
        endpoint_for_signature = endpoint
        if method in ['GET', 'DELETE'] and params:
            query_string = urlencode(sorted(params.items()))
            endpoint_for_signature = f"{endpoint}?{query_string}"
        
        headers = self._get_headers(method, endpoint_for_signature, body)
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, params=params, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, headers=headers, data=body, timeout=10)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('code') != '200000':
                logger.error(f"API error: {result}")
                raise Exception(f"API error: {result.get('msg', 'Unknown error')}")
            
            return result.get('data', {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise
    
    def get_account_overview(self, currency: str = 'USDT') -> Dict:
        """Get account overview"""
        endpoint = f"/api/v1/account-overview"
        params = {'currency': currency}
        return self._request('GET', endpoint, params=params)
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get position details"""
        endpoint = f"/api/v1/position"
        params = {'symbol': symbol}
        return self._request('GET', endpoint, params=params)
    
    def get_ticker(self, symbol: str) -> Dict:
        """Get ticker information"""
        endpoint = f"/api/v1/ticker"
        params = {'symbol': symbol}
        return self._request('GET', endpoint, params=params)
    
    def get_klines(self, symbol: str, granularity: int = 1, from_time: Optional[int] = None, to_time: Optional[int] = None) -> List:
        """Get K-line data
        granularity: 1min, 5min, 15min, 30min, 1hour, 4hour, 8hour, 1day, 1week (in minutes)
        """
        endpoint = f"/api/v1/kline/query"
        params = {
            'symbol': symbol,
            'granularity': granularity
        }
        if from_time:
            params['from'] = from_time
        if to_time:
            params['to'] = to_time
        
        return self._request('GET', endpoint, params=params)
    
    def place_order(self, symbol: str, side: str, leverage: int, size: int, 
                   order_type: str = 'market', price: Optional[float] = None,
                   stop: Optional[str] = None, stop_price: Optional[float] = None,
                   stop_price_type: Optional[str] = None) -> Dict:
        """Place an order
        side: 'buy' or 'sell'
        order_type: 'limit' or 'market'
        stop: 'up' or 'down'
        stop_price_type: 'TP' (take profit) or 'IP' (index price) or 'MP' (mark price)
        """
        # Input validation
        if not symbol or not isinstance(symbol, str):
            raise ValueError(f"Invalid symbol: {symbol}")
        
        if side not in ['buy', 'sell']:
            raise ValueError(f"Invalid side: {side}. Must be 'buy' or 'sell'")
        
        if not isinstance(leverage, int) or leverage < 1 or leverage > 100:
            raise ValueError(f"Invalid leverage: {leverage}. Must be between 1 and 100")
        
        if not isinstance(size, int) or size <= 0:
            raise ValueError(f"Invalid size: {size}. Must be a positive integer")
        
        if order_type not in ['limit', 'market']:
            raise ValueError(f"Invalid order_type: {order_type}. Must be 'limit' or 'market'")
        
        endpoint = "/api/v1/orders"
        data = {
            'symbol': symbol,
            'side': side,
            'leverage': str(leverage),
            'size': size,
            'type': order_type
        }
        
        if order_type == 'limit' and price:
            data['price'] = str(price)
        
        if stop and stop_price:
            data['stop'] = stop
            data['stopPrice'] = str(stop_price)
            if stop_price_type:
                data['stopPriceType'] = stop_price_type
        
        return self._request('POST', endpoint, data=data)
    
    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an order"""
        endpoint = f"/api/v1/orders/{order_id}"
        return self._request('DELETE', endpoint)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List:
        """Get open orders"""
        endpoint = "/api/v1/orders"
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        result = self._request('GET', endpoint, params=params)
        return result.get('items', [])
    
    def get_fills(self, symbol: Optional[str] = None) -> List:
        """Get recent fills"""
        endpoint = "/api/v1/fills"
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        result = self._request('GET', endpoint, params=params)
        return result.get('items', [])
    
    def set_auto_deposit_margin(self, symbol: str, status: bool) -> Dict:
        """Enable/disable auto deposit margin"""
        endpoint = "/api/v1/position/margin/auto-deposit-status"
        data = {
            'symbol': symbol,
            'status': status
        }
        return self._request('POST', endpoint, data=data)
    
    def close(self):
        """Close the session and cleanup resources"""
        if hasattr(self, 'session'):
            self.session.close()
            logger.info("KuCoin client session closed")
    
    def get_funding_history(self, symbol: str, from_time: Optional[int] = None, to_time: Optional[int] = None) -> List:
        """Get funding history"""
        endpoint = "/api/v1/funding-history"
        params = {'symbol': symbol}
        if from_time:
            params['from'] = from_time
        if to_time:
            params['to'] = to_time
        
        result = self._request('GET', endpoint, params=params)
        return result.get('dataList', [])
