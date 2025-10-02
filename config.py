"""
Configuration module for the KuCoin XRP Futures Hedge Bot
Smart auto-detection of features based on environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration class with smart auto-detection"""
    
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
    
    # Funding Strategy (Better balance management)
    USE_FUNDING_STRATEGY = os.getenv('USE_FUNDING_STRATEGY', 'true').lower() == 'true'
    MIN_BALANCE_RESERVE_PERCENT = float(os.getenv('MIN_BALANCE_RESERVE_PERCENT', 20))
    BASE_POSITION_SIZE_PERCENT = float(os.getenv('BASE_POSITION_SIZE_PERCENT', 15))
    MAX_POSITION_SIZE_PERCENT_NEW = float(os.getenv('MAX_POSITION_SIZE_PERCENT_NEW', 40))
    MIN_POSITION_SIZE_PERCENT = float(os.getenv('MIN_POSITION_SIZE_PERCENT', 5))
    
    # Technical Indicators
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', 14))
    RSI_OVERSOLD = float(os.getenv('RSI_OVERSOLD', 30))
    RSI_OVERBOUGHT = float(os.getenv('RSI_OVERBOUGHT', 70))
    EMA_SHORT = int(os.getenv('EMA_SHORT', 12))
    EMA_LONG = int(os.getenv('EMA_LONG', 26))
    MACD_SIGNAL = int(os.getenv('MACD_SIGNAL', 9))
    
    # Smart Feature Auto-Detection
    # Telegram: Auto-enable if both token and chat_id are provided
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    _telegram_configured = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
    
    # ML Signals: Auto-enable if explicitly set to true
    USE_ML_SIGNALS = os.getenv('USE_ML_SIGNALS', 'false').lower() == 'true'
    
    # Web Dashboard: Auto-enable if explicitly set to true
    ENABLE_WEB_DASHBOARD = os.getenv('ENABLE_WEB_DASHBOARD', 'false').lower() == 'true'
    WEB_DASHBOARD_PORT = int(os.getenv('WEB_DASHBOARD_PORT', 5000))
    
    # Dynamic Leverage: Auto-enable if MIN/MAX are different from base leverage
    MIN_LEVERAGE = int(os.getenv('MIN_LEVERAGE', 5))
    MAX_LEVERAGE = int(os.getenv('MAX_LEVERAGE', 20))
    _dynamic_leverage_configured = (MIN_LEVERAGE != LEVERAGE or MAX_LEVERAGE != LEVERAGE)
    # Enable if explicitly set OR if leverage range is configured differently
    ENABLE_DYNAMIC_LEVERAGE = (
        os.getenv('ENABLE_DYNAMIC_LEVERAGE', 'auto').lower() == 'true' or
        (os.getenv('ENABLE_DYNAMIC_LEVERAGE', 'auto').lower() == 'auto' and _dynamic_leverage_configured)
    )
    
    # Multiple Trading Pairs: Auto-detect from comma-separated list
    TRADING_PAIRS = [pair.strip() for pair in os.getenv('TRADING_PAIRS', 'XRPUSDTM').split(',')]
    _is_multi_pair = len(TRADING_PAIRS) > 1
    
    # Allocation strategy: Use 'best' automatically if multiple pairs configured
    ALLOCATION_STRATEGY = os.getenv('ALLOCATION_STRATEGY', 'best' if _is_multi_pair else 'equal')
    
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
    
    @classmethod
    def get_feature_summary(cls):
        """Get a summary of enabled features for logging"""
        features = []
        
        if cls._telegram_configured:
            features.append("✓ Telegram notifications")
        
        if cls.USE_ML_SIGNALS:
            features.append("✓ ML-based signals")
        
        if cls.ENABLE_WEB_DASHBOARD:
            features.append(f"✓ Web dashboard (port {cls.WEB_DASHBOARD_PORT})")
        
        if cls.ENABLE_DYNAMIC_LEVERAGE:
            features.append(f"✓ Dynamic leverage ({cls.MIN_LEVERAGE}x-{cls.MAX_LEVERAGE}x)")
        
        if cls._is_multi_pair:
            features.append(f"✓ Multi-pair trading ({len(cls.TRADING_PAIRS)} pairs, {cls.ALLOCATION_STRATEGY} strategy)")
        
        if cls.USE_FUNDING_STRATEGY:
            features.append("✓ Intelligent funding strategy")
        
        if not features:
            features.append("Basic trading mode")
        
        return "\n  ".join(features)
