"""
Debug Helper Script
Provides utilities for debugging and monitoring the bot
"""
import sys
import os
import json
from datetime import datetime

def check_trade_history():
    """Analyze trade history for issues"""
    print("=" * 60)
    print("TRADE HISTORY ANALYSIS")
    print("=" * 60)
    
    history_file = 'bot_data/trade_history.jsonl'
    
    if not os.path.exists(history_file):
        print("❌ No trade history found")
        return
    
    trades = []
    with open(history_file, 'r') as f:
        for line in f:
            if line.strip():
                trades.append(json.loads(line))
    
    if not trades:
        print("❌ Trade history is empty")
        return
    
    print(f"✓ Total trades: {len(trades)}")
    
    # Analyze by symbol
    by_symbol = {}
    for trade in trades:
        symbol = trade.get('symbol', 'UNKNOWN')
        if symbol not in by_symbol:
            by_symbol[symbol] = []
        by_symbol[symbol].append(trade)
    
    print(f"\nTrades by symbol:")
    for symbol, symbol_trades in by_symbol.items():
        print(f"  {symbol}: {len(symbol_trades)} trades")
    
    # Analyze recent trades
    print(f"\nLast 5 trades:")
    for trade in trades[-5:]:
        timestamp = trade.get('timestamp', 'N/A')
        symbol = trade.get('symbol', 'N/A')
        action = trade.get('action', 'N/A')
        side = trade.get('side', 'N/A')
        size = trade.get('size', 'N/A')
        print(f"  {timestamp}: {symbol} {action} {side} x{size}")
    
    # Check for issues
    print(f"\n🔍 Checking for issues:")
    
    # Check for failed trades (missing order_id)
    failed = [t for t in trades if t.get('order_id') == 'N/A']
    if failed:
        print(f"  ⚠️  {len(failed)} trades with missing order IDs")
    else:
        print(f"  ✓ All trades have order IDs")
    
    # Check leverage values
    leverages = [t.get('leverage', 0) for t in trades]
    if leverages:
        avg_leverage = sum(leverages) / len(leverages)
        print(f"  ✓ Average leverage: {avg_leverage:.1f}x")
        print(f"  ✓ Min leverage: {min(leverages)}x, Max: {max(leverages)}x")


def check_bot_data():
    """Check bot data directory"""
    print("\n" + "=" * 60)
    print("BOT DATA DIRECTORY")
    print("=" * 60)
    
    if not os.path.exists('bot_data'):
        print("❌ bot_data directory not found")
        return
    
    files = os.listdir('bot_data')
    print(f"✓ Found {len(files)} files in bot_data/")
    
    for filename in files:
        filepath = os.path.join('bot_data', filename)
        size = os.path.getsize(filepath)
        print(f"  {filename}: {size:,} bytes")


def check_config():
    """Check configuration"""
    print("\n" + "=" * 60)
    print("CONFIGURATION CHECK")
    print("=" * 60)
    
    try:
        from config import Config
        
        print(f"✓ Configuration loaded")
        print(f"\nTrading Configuration:")
        print(f"  Symbol(s): {', '.join(Config.TRADING_PAIRS)}")
        print(f"  Multi-pair: {Config._is_multi_pair}")
        print(f"  Leverage: {Config.LEVERAGE}x")
        print(f"  Initial balance: ${Config.INITIAL_BALANCE}")
        print(f"  Environment: {'TESTNET' if Config.USE_TESTNET else 'PRODUCTION'}")
        
        print(f"\nRisk Management:")
        print(f"  Stop loss: {Config.STOP_LOSS_PERCENT}%")
        print(f"  Take profit: {Config.TAKE_PROFIT_PERCENT}%")
        print(f"  Trailing stop: {Config.TRAILING_STOP_PERCENT}%")
        print(f"  Max position: {Config.MAX_POSITION_SIZE_PERCENT}%")
        
        print(f"\nEnabled Features:")
        print(f"  {Config.get_feature_summary()}")
        
        # Check API credentials
        if Config.API_KEY and Config.API_SECRET and Config.API_PASSPHRASE:
            print(f"\n✓ API credentials configured")
        else:
            print(f"\n❌ API credentials missing!")
        
    except Exception as e:
        print(f"❌ Error loading config: {e}")


def check_api_connection():
    """Test API connection"""
    print("\n" + "=" * 60)
    print("API CONNECTION TEST")
    print("=" * 60)
    
    try:
        from config import Config
        from kucoin_client import KuCoinFuturesClient
        
        client = KuCoinFuturesClient(
            Config.API_KEY,
            Config.API_SECRET,
            Config.API_PASSPHRASE,
            Config.API_URL
        )
        
        print("Testing API connection...")
        
        # Test getting account info
        account = client.get_account_overview('USDT')
        print(f"✓ Successfully connected to KuCoin API")
        print(f"  Available balance: ${account.get('availableBalance', 0)}")
        print(f"  Account equity: ${account.get('accountEquity', 0)}")
        
        # Test getting ticker
        symbol = Config.TRADING_PAIRS[0]
        ticker = client.get_ticker(symbol)
        print(f"✓ Successfully fetched {symbol} ticker")
        print(f"  Current price: ${ticker.get('price', 0)}")
        
        # Cleanup
        client.close()
        print("✓ Connection test passed")
        
    except Exception as e:
        print(f"❌ API connection test failed: {e}")
        import traceback
        traceback.print_exc()


def check_logs():
    """Check recent log entries"""
    print("\n" + "=" * 60)
    print("RECENT LOG ENTRIES")
    print("=" * 60)
    
    log_file = 'bot.log'
    
    if not os.path.exists(log_file):
        print("❌ No log file found")
        return
    
    print(f"✓ Found log file")
    
    # Read last 20 lines
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    print(f"\nLast 10 log entries:")
    for line in lines[-10:]:
        print(f"  {line.rstrip()}")
    
    # Count errors
    error_count = sum(1 for line in lines if 'ERROR' in line)
    warning_count = sum(1 for line in lines if 'WARNING' in line)
    
    print(f"\nLog statistics:")
    print(f"  Total lines: {len(lines)}")
    print(f"  Errors: {error_count}")
    print(f"  Warnings: {warning_count}")
    
    if error_count > 0:
        print(f"\n⚠️  Found {error_count} errors in logs. Recent errors:")
        error_lines = [line for line in lines if 'ERROR' in line]
        for line in error_lines[-5:]:
            print(f"  {line.rstrip()}")


def main():
    """Run all debug checks"""
    print("\n" + "=" * 60)
    print("BOT DEBUG HELPER")
    print("=" * 60)
    print(f"Run at: {datetime.now().isoformat()}")
    
    # Run all checks
    check_config()
    check_bot_data()
    check_trade_history()
    check_logs()
    
    # Only run API check if requested
    if '--test-api' in sys.argv:
        check_api_connection()
    else:
        print("\n💡 Tip: Use --test-api flag to test API connection")
    
    print("\n" + "=" * 60)
    print("DEBUG CHECK COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
