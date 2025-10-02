"""
Demo of Advanced Features (v2.0)
Showcases new features without real trading
"""
import logging
import sys
import time
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_web_dashboard():
    """Demonstrate web dashboard"""
    print("\n" + "=" * 60)
    print("WEB DASHBOARD DEMO")
    print("=" * 60)
    
    print("\n📊 Features:")
    print("  • Real-time bot status and balance")
    print("  • Performance metrics (win rate, ROI, total trades)")
    print("  • Active positions across all trading pairs")
    print("  • Recent trade history with auto-refresh")
    print("  • Accessible at http://localhost:5000")
    
    print("\n💡 Usage:")
    print("  1. Set ENABLE_WEB_DASHBOARD=true in .env")
    print("  2. Run: python bot_enhanced.py")
    print("  3. Open browser: http://localhost:5000")
    
    print("\n✨ Key Metrics:")
    print("  • Current Balance: Real-time balance updates")
    print("  • Total Profit: Cumulative P&L")
    print("  • Win Rate: Percentage of winning trades")
    print("  • Positions: All active positions with P&L")


def demo_multiple_pairs():
    """Demonstrate multiple trading pairs"""
    print("\n" + "=" * 60)
    print("MULTIPLE TRADING PAIRS DEMO")
    print("=" * 60)
    
    from multi_pair import MultiPairManager
    
    pairs = ['XRPUSDTM', 'BTCUSDTM', 'ETHUSDTM']
    manager = MultiPairManager(pairs)
    
    print(f"\n📈 Trading {len(pairs)} pairs simultaneously:")
    for pair in pairs:
        print(f"  • {pair}")
    
    # Demonstrate allocation strategies
    balance = 300.0
    
    print("\n💰 Balance Allocation Strategies:")
    
    # Equal allocation
    allocations = manager.allocate_balance(balance, 'equal')
    print("\n  Equal Allocation:")
    for pair, amount in allocations.items():
        print(f"    {pair}: ${amount:.2f}")
    
    # Simulate some trades for weighted allocation
    manager.pair_states['XRPUSDTM']['winning_trades'] = 8
    manager.pair_states['XRPUSDTM']['losing_trades'] = 2
    manager.pair_states['BTCUSDTM']['winning_trades'] = 6
    manager.pair_states['BTCUSDTM']['losing_trades'] = 4
    manager.pair_states['ETHUSDTM']['winning_trades'] = 5
    manager.pair_states['ETHUSDTM']['losing_trades'] = 5
    
    allocations = manager.allocate_balance(balance, 'weighted')
    print("\n  Weighted Allocation (by performance):")
    for pair, amount in allocations.items():
        stats = manager.get_pair_statistics(pair)
        print(f"    {pair}: ${amount:.2f} (Win rate: {stats['win_rate']:.1f}%)")


def demo_ml_signals():
    """Demonstrate ML-based signals"""
    print("\n" + "=" * 60)
    print("ML-BASED SIGNALS DEMO")
    print("=" * 60)
    
    from ml_signals import MLSignalGenerator
    import numpy as np
    
    ml = MLSignalGenerator()
    
    print("\n🤖 ML Ensemble Models:")
    print("  1. Momentum Model - Detects trends and acceleration")
    print("  2. Volatility Model - Adapts to market conditions")
    print("  3. MA Crossover Model - Identifies trend changes")
    print("  4. Mean Reversion Model - Spots extremes")
    
    # Generate sample klines
    base_price = 0.52
    klines = []
    for i in range(60):
        # Simulate uptrend
        price = base_price + (i * 0.001) + np.random.normal(0, 0.002)
        klines.append([
            int(time.time() * 1000) - (60-i) * 60000,  # timestamp
            price - 0.001,  # open
            price + 0.002,  # high
            price - 0.002,  # low
            price,  # close
            1000 + np.random.randint(-100, 100)  # volume
        ])
    
    current_price = klines[-1][4]
    
    print(f"\n📊 Analyzing market data...")
    print(f"  Current price: ${current_price:.6f}")
    print(f"  Data points: {len(klines)}")
    
    # Generate signal
    signal = ml.generate_ml_signal(klines, current_price)
    
    print(f"\n🎯 ML Signal Generated:")
    print(f"  Action: {signal['action'].upper()}")
    print(f"  Strength: {signal['strength']}/100")
    print(f"  Reason: {signal['reason']}")
    
    indicators = signal['indicators']
    if 'ml_confidence' in indicators:
        print(f"  Confidence: {indicators['ml_confidence']:.1f}%")
    if 'ml_score' in indicators:
        print(f"  ML Score: {indicators['ml_score']:.2f}")


def demo_backtesting():
    """Demonstrate backtesting"""
    print("\n" + "=" * 60)
    print("BACKTESTING DEMO")
    print("=" * 60)
    
    print("\n📈 Backtest Your Strategy:")
    print("  Test strategies on historical data before live trading")
    
    print("\n💡 Usage:")
    print("  # Basic backtest")
    print("  python run_backtest.py")
    print("\n  # Custom parameters")
    print("  python run_backtest.py --balance 100 --leverage 11 --days 30")
    print("\n  # Compare strategies")
    print("  python run_backtest.py --compare")
    
    print("\n📊 Example Output:")
    print("  Total trades: 45")
    print("  Winning trades: 28")
    print("  Losing trades: 17")
    print("  Win rate: 62.22%")
    print("  Total P&L: $23.45")
    print("  Final balance: $123.45")
    print("  ROI: 23.45%")
    print("  Max drawdown: 8.32%")
    
    print("\n✨ Benefits:")
    print("  • Test without risking real money")
    print("  • Compare different strategies")
    print("  • Understand risk/reward")
    print("  • Optimize parameters")


def demo_telegram():
    """Demonstrate Telegram notifications"""
    print("\n" + "=" * 60)
    print("TELEGRAM NOTIFICATIONS DEMO")
    print("=" * 60)
    
    print("\n📱 Real-time Notifications:")
    print("  • Trade executions (open, close, hedge)")
    print("  • P&L updates")
    print("  • Strong trading signals")
    print("  • Error alerts")
    print("  • Bot status updates")
    
    print("\n🔧 Setup:")
    print("  1. Create bot with @BotFather on Telegram")
    print("  2. Get bot token")
    print("  3. Start chat with your bot")
    print("  4. Get your chat ID")
    print("  5. Add to .env:")
    print("     TELEGRAM_BOT_TOKEN=your_token")
    print("     TELEGRAM_CHAT_ID=your_chat_id")
    
    print("\n💬 Example Notifications:")
    print("  📈 OPEN BUY")
    print("  Size: 500 contracts")
    print("  Price: $0.523400")
    print("  Reason: RSI oversold + MACD bullish")
    print("\n  💰 P&L Update")
    print("  PnL: +$12.45")
    print("  Balance: $112.45")
    print("  ROI: +12.45%")


def demo_portfolio_diversification():
    """Demonstrate portfolio diversification"""
    print("\n" + "=" * 60)
    print("PORTFOLIO DIVERSIFICATION DEMO")
    print("=" * 60)
    
    from portfolio_diversification import PortfolioDiversifier
    import numpy as np
    
    diversifier = PortfolioDiversifier()
    
    print("\n💼 Portfolio Management:")
    print("  • Correlation analysis between pairs")
    print("  • Optimal position sizing")
    print("  • Rebalancing suggestions")
    print("  • Diversification scoring")
    
    # Simulate price history for correlation
    symbols = ['XRPUSDTM', 'BTCUSDTM', 'ETHUSDTM']
    
    # XRP and BTC somewhat correlated, ETH less so
    for i in range(100):
        base = 0.52 + np.random.normal(0, 0.01)
        diversifier.update_price_history('XRPUSDTM', base)
        diversifier.update_price_history('BTCUSDTM', base * 80000 + np.random.normal(0, 1000))
        diversifier.update_price_history('ETHUSDTM', 3000 + np.random.normal(0, 50))
    
    print("\n📊 Correlation Analysis:")
    for i, sym1 in enumerate(symbols):
        for sym2 in symbols[i+1:]:
            corr = diversifier.calculate_correlation(sym1, sym2)
            status = "✓ Good" if abs(corr) < 0.7 else "⚠ High"
            print(f"  {sym1} vs {sym2}: {corr:.2f} {status}")
    
    # Example portfolio
    positions = {
        'XRPUSDTM': 80.0,
        'BTCUSDTM': 100.0,
        'ETHUSDTM': 70.0
    }
    
    metrics = diversifier.get_portfolio_metrics(positions)
    
    print(f"\n💹 Portfolio Metrics:")
    print(f"  Positions: {metrics['num_positions']}")
    print(f"  Total Value: ${metrics['total_value']:.2f}")
    print(f"  Diversification Score: {metrics['diversification_score']:.2f}")
    print(f"  Largest Position: {metrics['largest_position_pct']:.1f}%")
    print(f"  Avg Correlation: {metrics['avg_correlation']:.2f}")


def demo_dynamic_leverage():
    """Demonstrate dynamic leverage"""
    print("\n" + "=" * 60)
    print("DYNAMIC LEVERAGE DEMO")
    print("=" * 60)
    
    from dynamic_leverage import DynamicLeverage
    import numpy as np
    
    dl = DynamicLeverage(base_leverage=11, min_leverage=5, max_leverage=20)
    
    print("\n⚡ Dynamic Leverage Adjustment:")
    print("  Adapts to market conditions and risk")
    
    print("\n📊 Factors:")
    print("  1. Volatility - Lower leverage in volatile markets")
    print("  2. Signal Strength - Higher leverage with strong signals")
    print("  3. Account Risk - Lower leverage after losses")
    
    # Simulate different scenarios
    scenarios = [
        {
            'name': 'Low Volatility + Strong Signal',
            'volatility': 0.02,
            'signal_strength': 85,
            'win_rate': 70,
            'recent_losses': 0
        },
        {
            'name': 'High Volatility + Weak Signal',
            'volatility': 0.08,
            'signal_strength': 45,
            'win_rate': 55,
            'recent_losses': 2
        },
        {
            'name': 'Moderate Conditions',
            'volatility': 0.04,
            'signal_strength': 65,
            'win_rate': 60,
            'recent_losses': 1
        }
    ]
    
    # Generate sample klines
    klines = []
    for i in range(30):
        price = 0.52 + np.random.normal(0, 0.01)
        klines.append([0, price, price, price, price, 1000])
    
    print("\n🎯 Leverage Adjustments:")
    for scenario in scenarios:
        signal = {
            'strength': scenario['signal_strength'],
            'indicators': {'rsi': 50, 'macd_histogram': 0}
        }
        
        leverage = dl.adjust_leverage(
            klines, signal, 100.0, 10.0,
            scenario['win_rate'], scenario['recent_losses']
        )
        
        print(f"\n  {scenario['name']}:")
        print(f"    Base: 11x → Adjusted: {leverage}x")
        print(f"    Volatility: {scenario['volatility']:.2f}")
        print(f"    Signal: {scenario['signal_strength']}/100")
        print(f"    Win Rate: {scenario['win_rate']}%")
        print(f"    Recent Losses: {scenario['recent_losses']}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("XRP FUTURES BOT - ADVANCED FEATURES DEMO (v2.0)")
    print("=" * 60)
    print("\nThis demo showcases the new features without real trading")
    
    try:
        demo_web_dashboard()
        time.sleep(1)
        
        demo_multiple_pairs()
        time.sleep(1)
        
        demo_ml_signals()
        time.sleep(1)
        
        demo_backtesting()
        time.sleep(1)
        
        demo_telegram()
        time.sleep(1)
        
        demo_portfolio_diversification()
        time.sleep(1)
        
        demo_dynamic_leverage()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print("\n✨ All features demonstrated successfully!")
        print("\n📚 For detailed usage, see ADVANCED_FEATURES.md")
        print("🚀 To start trading, run: python bot_enhanced.py")
        print("\n⚠️  Remember to test on testnet first!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)


if __name__ == '__main__':
    main()
