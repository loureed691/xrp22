"""
Configuration module for the KuCoin XRP Futures Hedge Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration class"""
    
    # KuCoin API Configuration
    API_KEY = os.getenv('KUCOIN_API_KEY', '')
    API_SECRET = os.getenv('KUCOIN_API_SECRET', '')
    API_PASSPHRASE = os.getenv('KUCOIN_API_PASSPHRASE', '')
    USE_TESTNET = os.getenv('USE_TESTNET', 'true').lower() == 'true'
    
    # Trading Configuration
    SYMBOL = os.getenv('SYMBOL', 'XRPUSDTM')
    INITIAL_BALANCE = float(os.getenv('INITIAL_BALANCE', 100))
    LEVERAGE = int(os.getenv('LEVERAGE', 11))
    
    # Risk Management
    MAX_POSITION_SIZE_PERCENT = float(os.getenv('MAX_POSITION_SIZE_PERCENT', 80))
    STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', 5))
    TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', 8))
    TRAILING_STOP_PERCENT = float(os.getenv('TRAILING_STOP_PERCENT', 3))
    
    # Technical Indicators
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', 14))
    RSI_OVERSOLD = float(os.getenv('RSI_OVERSOLD', 30))
    RSI_OVERBOUGHT = float(os.getenv('RSI_OVERBOUGHT', 70))
    EMA_SHORT = int(os.getenv('EMA_SHORT', 12))
    EMA_LONG = int(os.getenv('EMA_LONG', 26))
    MACD_SIGNAL = int(os.getenv('MACD_SIGNAL', 9))
    
    # API Endpoints
    API_URL = 'https://api-futures.kucoin.com' if not USE_TESTNET else 'https://api-sandbox-futures.kucoin.com'
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.API_KEY or not cls.API_SECRET or not cls.API_PASSPHRASE:
            raise ValueError("API credentials are required. Please set them in .env file")
        
        if cls.LEVERAGE < 1 or cls.LEVERAGE > 100:
            raise ValueError("Leverage must be between 1 and 100")
        
        if cls.INITIAL_BALANCE <= 0:
            raise ValueError("Initial balance must be positive")
        
        return True
