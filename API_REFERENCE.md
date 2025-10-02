# API Reference

## KuCoin Futures API Integration

This bot uses the KuCoin Futures API directly via REST calls. Below is documentation of the key endpoints and how they're used.

## Authentication

All requests require authentication via API key, secret, and passphrase.

### Required Headers
```
KC-API-KEY: Your API Key
KC-API-SIGN: Request signature (HMAC-SHA256)
KC-API-TIMESTAMP: Current timestamp in milliseconds
KC-API-PASSPHRASE: Encrypted passphrase
KC-API-KEY-VERSION: 2
```

### Signature Generation
```python
# For GET/DELETE requests with query parameters, include them in the endpoint
# Example: endpoint = "/api/v1/account-overview?currency=USDT"
str_to_sign = timestamp + method + endpoint + body
signature = base64(hmac_sha256(api_secret, str_to_sign))
```

**Important:** For GET and DELETE requests with query parameters, the endpoint must include the query string (e.g., `/api/v1/account-overview?currency=USDT`) when calculating the signature.

## Endpoints Used

### 1. Get Account Overview
**Endpoint:** `GET /api/v1/account-overview`

**Purpose:** Get account balance and margin information

**Parameters:**
- `currency`: USDT (default)

**Response:**
```json
{
  "accountEquity": 100.0,
  "availableBalance": 95.0,
  "unrealisedPNL": 5.0,
  "marginBalance": 100.0,
  "positionMargin": 5.0
}
```

### 2. Get Position
**Endpoint:** `GET /api/v1/position`

**Purpose:** Get current position details

**Parameters:**
- `symbol`: XRPUSDTM

**Response:**
```json
{
  "symbol": "XRPUSDTM",
  "currentQty": 1000,
  "avgEntryPrice": 0.52,
  "unrealisedPnl": 10.0,
  "unrealisedPnlPcnt": 0.02,
  "realisedPnl": 5.0,
  "liquidationPrice": 0.45
}
```

### 3. Get Ticker
**Endpoint:** `GET /api/v1/ticker`

**Purpose:** Get current market price

**Parameters:**
- `symbol`: XRPUSDTM

**Response:**
```json
{
  "symbol": "XRPUSDTM",
  "price": 0.5234,
  "bestBidPrice": 0.5233,
  "bestAskPrice": 0.5235,
  "size": 100000
}
```

### 4. Get K-line Data
**Endpoint:** `GET /api/v1/kline/query`

**Purpose:** Get historical price data for analysis

**Parameters:**
- `symbol`: XRPUSDTM
- `granularity`: 1, 5, 15, 30, 60, 240, 480, 1440 (minutes)
- `from`: Start timestamp (milliseconds)
- `to`: End timestamp (milliseconds)

**Response:**
```json
[
  [1609459200000, 0.52, 0.525, 0.518, 0.523, 10000],
  // [timestamp, open, high, low, close, volume]
]
```

### 5. Place Order
**Endpoint:** `POST /api/v1/orders`

**Purpose:** Execute a trade

**Request Body:**
```json
{
  "symbol": "XRPUSDTM",
  "side": "buy",
  "leverage": "11",
  "size": 1000,
  "type": "market"
}
```

**Response:**
```json
{
  "orderId": "5cdfc138b21023a909e5ad55"
}
```

### 6. Cancel Order
**Endpoint:** `DELETE /api/v1/orders/{orderId}`

**Purpose:** Cancel a pending order

### 7. Get Open Orders
**Endpoint:** `GET /api/v1/orders`

**Purpose:** Get list of open orders

**Parameters:**
- `symbol`: XRPUSDTM (optional)

## Rate Limits

KuCoin enforces rate limits:
- **Public endpoints**: 100 requests per 10 seconds
- **Private endpoints**: 30 requests per 3 seconds

The bot respects these limits by:
- Running cycles every 60 seconds (default)
- Batching requests when possible
- Implementing exponential backoff on errors

## Error Handling

### Common Error Codes

| Code | Message | Meaning | Solution |
|------|---------|---------|----------|
| 200000 | Success | Request successful | - |
| 400100 | Invalid Parameter | Bad request parameter | Check request format |
| 401001 | Unauthorized | Invalid API credentials | Verify API key/secret |
| 411100 | Insufficient Balance | Not enough funds | Add funds to account |
| 200200 | Order Size Below Minimum | Order too small | Increase position size |
| 300000 | Order Failed | Order execution failed | Check market conditions |

### Retry Logic

The bot implements automatic retry for:
- Network timeouts
- Rate limit errors (429)
- Server errors (5xx)

Retry strategy:
1. First retry: 2 seconds
2. Second retry: 5 seconds
3. Third retry: 10 seconds
4. Give up and log error

## Technical Indicators Implementation

### RSI (Relative Strength Index)
```python
deltas = diff(prices)
gains = where(deltas > 0, deltas, 0)
losses = where(deltas < 0, -deltas, 0)
avg_gain = mean(gains[-period:])
avg_loss = mean(losses[-period:])
rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))
```

### MACD (Moving Average Convergence Divergence)
```python
ema_short = EMA(prices, short_period)
ema_long = EMA(prices, long_period)
macd_line = ema_short - ema_long
signal_line = EMA(macd_line, signal_period)
histogram = macd_line - signal_line
```

### Bollinger Bands
```python
middle_band = SMA(prices, period)
std_dev = std(prices[-period:])
upper_band = middle_band + (2 * std_dev)
lower_band = middle_band - (2 * std_dev)
```

### ATR (Average True Range)
```python
tr = max(
    high - low,
    abs(high - previous_close),
    abs(low - previous_close)
)
atr = SMA(tr, period)
```

## Position Sizing Formula

```python
# Base calculation
position_value = available_balance * (max_position_percent / 100)

# Apply leverage
leveraged_value = position_value * leverage

# Calculate contracts
contracts = int(leveraged_value / current_price)

# Minimum 1 contract
contracts = max(1, contracts)
```

### Example
- Available Balance: $100
- Max Position: 80%
- Leverage: 11x
- XRP Price: $0.52

```
position_value = 100 * 0.80 = $80
leveraged_value = 80 * 11 = $880
contracts = 880 / 0.52 = 1,692 contracts
```

## Risk Management Calculations

### Stop Loss
```python
if current_price <= entry_price * (1 - stop_loss_percent/100):
    close_position()
```

### Take Profit
```python
if current_price >= entry_price * (1 + take_profit_percent/100):
    close_position()
```

### Trailing Stop (Long)
```python
highest_price = max(highest_price, current_price)
if current_price <= highest_price * (1 - trailing_percent/100):
    close_position()
```

### Trailing Stop (Short)
```python
lowest_price = min(lowest_price, current_price)
if current_price >= lowest_price * (1 + trailing_percent/100):
    close_position()
```

## Performance Metrics

### Win Rate
```python
win_rate = (winning_trades / total_trades) * 100
```

### Profit/Loss
```python
total_pnl = sum(realized_pnl_per_trade)
roi = (current_balance - initial_balance) / initial_balance * 100
```

### Sharpe Ratio (Future Implementation)
```python
returns = daily_returns
sharpe = mean(returns) / std(returns) * sqrt(252)
```

## WebSocket (Future Implementation)

For real-time updates, consider upgrading to WebSocket:

```python
# Subscribe to ticker updates
ws.connect('wss://api-futures.kucoin.com')
ws.subscribe('/contractMarket/ticker:XRPUSDTM')

# Subscribe to position updates  
ws.subscribe('/contract/position:XRPUSDTM')
```

Benefits:
- Lower latency
- Real-time price updates
- Reduced API calls
- Instant position updates

## Testing with Testnet

### Testnet Environment
- Base URL: `https://api-sandbox-futures.kucoin.com`
- No real money at risk
- Same API structure as production
- Free test funds available

### Getting Test Funds
1. Register at https://sandbox-futures.kucoin.com/
2. Use test faucet for free USDT
3. Test all strategies risk-free

### Differences from Production
- May have slightly different liquidity
- Price may vary from production
- Some features may be limited
- Orders execute instantly (simulated)

## Security Best Practices

### API Key Security
1. Never commit API keys to git
2. Use environment variables (.env)
3. Restrict API key permissions
4. Use IP whitelist if available
5. Rotate keys regularly

### Key Permissions
Required:
- ✓ General
- ✓ Futures Trading

Not required:
- ✗ Transfer
- ✗ Withdrawal

### Rate Limiting
- Respect API limits
- Implement backoff strategies
- Cache data when possible
- Use WebSocket for real-time data

## Logging and Monitoring

### Log Levels
- **INFO**: Normal operation, trades, signals
- **WARNING**: Unusual conditions, retries
- **ERROR**: Failed operations, API errors
- **CRITICAL**: Fatal errors, system issues

### What to Monitor
- Trade execution success rate
- API response times
- Error frequencies
- Position sizes and P&L
- Balance changes
- Signal accuracy

## Additional Resources

- [KuCoin API Documentation](https://docs.kucoin.com/futures/)
- [Python Requests Library](https://requests.readthedocs.io/)
- [Trading Strategy Basics](https://www.investopedia.com/trading-4427765)
- [Risk Management](https://www.investopedia.com/articles/trading/09/risk-management.asp)
