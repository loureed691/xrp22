"""
Setup validation and testing script
"""
import sys
import os

print("=" * 60)
print("XRP Hedge Bot - Setup Validation")
print("=" * 60)
print()

# Check Python version
print("1. Checking Python version...")
if sys.version_info >= (3, 11):
    print(f"   ✓ Python {sys.version.split()[0]} detected")
else:
    print(f"   ✗ Python 3.11+ required. Current: {sys.version.split()[0]}")
    sys.exit(1)

# Check dependencies
print("\n2. Checking dependencies...")
dependencies = [
    'dotenv',
    'pandas',
    'numpy',
    'ta',
    'requests'
]

missing = []
for dep in dependencies:
    try:
        __import__(dep.replace('-', '_'))
        print(f"   ✓ {dep}")
    except ImportError:
        print(f"   ✗ {dep} not found")
        missing.append(dep)

if missing:
    print(f"\n   Install missing packages: pip install {' '.join(missing)}")
    sys.exit(1)

# Check .env file
print("\n3. Checking configuration...")
if os.path.exists('.env'):
    print("   ✓ .env file found")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['KUCOIN_API_KEY', 'KUCOIN_API_SECRET', 'KUCOIN_API_PASSPHRASE']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var, '')
        if value and value != f'your_{var.lower()}_here':
            print(f"   ✓ {var} configured")
        else:
            print(f"   ✗ {var} not configured")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n   Please configure: {', '.join(missing_vars)} in .env file")
        sys.exit(1)
    
    # Check testnet setting
    use_testnet = os.getenv('USE_TESTNET', 'true').lower() == 'true'
    if use_testnet:
        print("\n   ⚠ TESTNET mode enabled (recommended for testing)")
    else:
        print("\n   ⚠ PRODUCTION mode enabled (real money at risk!)")
        
else:
    print("   ✗ .env file not found")
    print("   Copy .env.example to .env and configure your API credentials")
    sys.exit(1)

# Test API connection
print("\n4. Testing API connection...")
try:
    from config import Config
    from kucoin_client import KuCoinFuturesClient
    
    Config.validate()
    client = KuCoinFuturesClient(
        Config.API_KEY,
        Config.API_SECRET,
        Config.API_PASSPHRASE,
        Config.API_URL
    )
    
    # Try to get account overview
    account = client.get_account_overview('USDT')
    balance = float(account.get('availableBalance', 0))
    
    print(f"   ✓ API connection successful")
    print(f"   ✓ Available balance: ${balance:.2f}")
    
    if balance < 1:
        print(f"   ⚠ Warning: Low balance. Add funds to start trading.")
    
except Exception as e:
    print(f"   ✗ API connection failed: {e}")
    print(f"   Check your API credentials and network connection")
    sys.exit(1)

# Test technical analysis
print("\n5. Testing technical analysis...")
try:
    from technical_analysis import TechnicalAnalyzer
    
    analyzer = TechnicalAnalyzer()
    
    # Test with sample data
    sample_prices = [100.0 + i * 0.1 for i in range(50)]
    rsi = analyzer.calculate_rsi(sample_prices)
    
    print(f"   ✓ Technical analysis module working")
    print(f"   ✓ Sample RSI calculation: {rsi:.2f}")
    
except Exception as e:
    print(f"   ✗ Technical analysis failed: {e}")
    sys.exit(1)

# Test strategy
print("\n6. Testing strategy module...")
try:
    from hedge_strategy import HedgeStrategy
    
    strategy = HedgeStrategy(
        leverage=11,
        stop_loss_percent=5,
        take_profit_percent=8,
        trailing_stop_percent=3,
        max_position_size_percent=80
    )
    
    size = strategy.calculate_position_size(100, 0.5)
    print(f"   ✓ Strategy module working")
    print(f"   ✓ Sample position size: {size} contracts")
    
except Exception as e:
    print(f"   ✗ Strategy module failed: {e}")
    sys.exit(1)

# Final summary
print("\n" + "=" * 60)
print("✓ All checks passed! Bot is ready to run.")
print("=" * 60)
print("\nTo start the bot, run: python bot.py")
print("\nRemember:")
print("  - Start with testnet to validate strategy")
print("  - Monitor the bot closely during initial runs")
print("  - Only trade with money you can afford to lose")
print("  - Press Ctrl+C to stop the bot safely")
print()
