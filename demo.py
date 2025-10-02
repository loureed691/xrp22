"""
Demo Mode - Analyze market without trading
This script shows what the bot sees and decides, but doesn't execute trades.
Perfect for understanding the bot's behavior before going live.
"""
import logging
import time
from datetime import datetime

# Disable actual API calls for demo
import sys
import os

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_technical_analysis():
    """Demonstrate technical analysis with sample data"""
    from technical_analysis import TechnicalAnalyzer
    
    print("\n" + "=" * 60)
    print("TECHNICAL ANALYSIS DEMO")
    print("=" * 60)
    
    analyzer = TechnicalAnalyzer(
        rsi_period=14,
        ema_short=12,
        ema_long=26,
        macd_signal=9
    )
    
    # Sample price data (simulating market movement)
    sample_prices = [
        0.52, 0.521, 0.519, 0.520, 0.522,  # Slight uptrend
        0.525, 0.528, 0.530, 0.532, 0.535,  # Stronger uptrend
        0.533, 0.531, 0.529, 0.527, 0.525,  # Pullback
        0.526, 0.528, 0.530, 0.532, 0.535,  # Recovery
        0.538, 0.540, 0.542, 0.545, 0.548,  # Breakout
        0.547, 0.546, 0.545, 0.543, 0.542   # Consolidation
    ]
    
    print("\n📊 Sample Price Series:")
    print(f"   Start: ${sample_prices[0]:.4f}")
    print(f"   End: ${sample_prices[-1]:.4f}")
    print(f"   Change: {((sample_prices[-1] - sample_prices[0]) / sample_prices[0] * 100):.2f}%")
    
    # Calculate indicators
    rsi = analyzer.calculate_rsi(sample_prices)
    ema_short = analyzer.calculate_ema(sample_prices, 12)
    ema_long = analyzer.calculate_ema(sample_prices, 26)
    macd_line, signal_line, histogram = analyzer.calculate_macd(sample_prices)
    upper_bb, middle_bb, lower_bb = analyzer.calculate_bollinger_bands(sample_prices)
    
    print(f"\n📈 Technical Indicators:")
    print(f"   RSI: {rsi:.2f}")
    print(f"   EMA (12): ${ema_short:.4f}")
    print(f"   EMA (26): ${ema_long:.4f}")
    print(f"   MACD: {macd_line:.6f}")
    print(f"   Signal: {signal_line:.6f}")
    print(f"   Histogram: {histogram:.6f}")
    print(f"   BB Upper: ${upper_bb:.4f}")
    print(f"   BB Middle: ${middle_bb:.4f}")
    print(f"   BB Lower: ${lower_bb:.4f}")
    
    # Interpret indicators
    print(f"\n💡 Market Interpretation:")
    if rsi < 30:
        print(f"   RSI: OVERSOLD ({rsi:.2f}) - Potential buy signal")
    elif rsi > 70:
        print(f"   RSI: OVERBOUGHT ({rsi:.2f}) - Potential sell signal")
    else:
        print(f"   RSI: NEUTRAL ({rsi:.2f}) - No strong signal")
    
    if ema_short > ema_long:
        print(f"   EMA: BULLISH crossover - Uptrend detected")
    else:
        print(f"   EMA: BEARISH crossover - Downtrend detected")
    
    if histogram > 0:
        print(f"   MACD: BULLISH - Momentum increasing")
    else:
        print(f"   MACD: BEARISH - Momentum decreasing")


def demo_position_sizing():
    """Demonstrate position sizing calculation"""
    from hedge_strategy import HedgeStrategy
    
    print("\n" + "=" * 60)
    print("POSITION SIZING DEMO")
    print("=" * 60)
    
    strategy = HedgeStrategy(
        leverage=11,
        stop_loss_percent=5,
        take_profit_percent=8,
        trailing_stop_percent=3,
        max_position_size_percent=80
    )
    
    balances = [100, 200, 500, 1000]
    xrp_price = 0.52
    
    print(f"\n💰 Position Sizes (XRP @ ${xrp_price}):")
    print(f"   Leverage: {strategy.leverage}x")
    print(f"   Max Position: {strategy.max_position_size_percent}%")
    print()
    
    for balance in balances:
        size = strategy.calculate_position_size(balance, xrp_price)
        position_value = size * xrp_price
        effective_value = position_value * strategy.leverage
        
        print(f"   Balance: ${balance:.2f}")
        print(f"   → Size: {size} contracts")
        print(f"   → Position Value: ${position_value:.2f}")
        print(f"   → With Leverage: ${effective_value:.2f}")
        print()


def demo_risk_management():
    """Demonstrate risk management scenarios"""
    from hedge_strategy import HedgeStrategy
    
    print("\n" + "=" * 60)
    print("RISK MANAGEMENT DEMO")
    print("=" * 60)
    
    strategy = HedgeStrategy(
        leverage=11,
        stop_loss_percent=5,
        take_profit_percent=8,
        trailing_stop_percent=3,
        max_position_size_percent=80
    )
    
    entry_price = 0.52
    position_qty = 1000
    
    scenarios = [
        ("Stop Loss", 0.494),      # -5% from entry
        ("Small Profit", 0.531),   # +2% from entry
        ("Take Profit", 0.562),    # +8% from entry
        ("Large Gain", 0.572),     # +10% from entry
    ]
    
    print(f"\n📊 Long Position Scenarios:")
    print(f"   Entry Price: ${entry_price:.4f}")
    print(f"   Position: {position_qty} contracts")
    print(f"   Stop Loss: {strategy.stop_loss_percent}%")
    print(f"   Take Profit: {strategy.take_profit_percent}%")
    print()
    
    for scenario_name, current_price in scenarios:
        price_change = ((current_price - entry_price) / entry_price) * 100
        pnl = (current_price - entry_price) * position_qty
        should_close, reason = strategy.should_close_long(
            current_price, entry_price, position_qty, pnl
        )
        
        print(f"   {scenario_name}:")
        print(f"   → Price: ${current_price:.4f} ({price_change:+.2f}%)")
        print(f"   → P&L: ${pnl:.2f}")
        print(f"   → Action: {'CLOSE' if should_close else 'HOLD'}")
        if should_close:
            print(f"   → Reason: {reason}")
        print()


def demo_signal_generation():
    """Demonstrate signal generation"""
    print("\n" + "=" * 60)
    print("TRADING SIGNAL DEMO")
    print("=" * 60)
    
    print("\n🔍 Signal Requirements:")
    print("   - Minimum strength: 60/100")
    print("   - Multiple indicator confirmation")
    print("   - Risk/reward validation")
    
    print("\n✅ Strong Buy Signal Example:")
    print("   - RSI: 25 (oversold)")
    print("   - MACD: Bullish crossover")
    print("   - Price: Below lower Bollinger Band")
    print("   - EMA: Bullish alignment")
    print("   → Signal Strength: 85/100")
    print("   → Action: OPEN LONG")
    
    print("\n✅ Strong Sell Signal Example:")
    print("   - RSI: 75 (overbought)")
    print("   - MACD: Bearish crossover")
    print("   - Price: Above upper Bollinger Band")
    print("   - EMA: Bearish alignment")
    print("   → Signal Strength: 85/100")
    print("   → Action: OPEN SHORT")
    
    print("\n❌ Weak Signal Example:")
    print("   - RSI: 50 (neutral)")
    print("   - MACD: Mixed signals")
    print("   - Price: Near middle Bollinger Band")
    print("   - EMA: No clear trend")
    print("   → Signal Strength: 35/100")
    print("   → Action: WAIT")


def demo_hedge_strategy():
    """Demonstrate hedging logic"""
    print("\n" + "=" * 60)
    print("HEDGE STRATEGY DEMO")
    print("=" * 60)
    
    print("\n📖 Hedging Explained:")
    print("   When a position is losing money, the bot can open a")
    print("   counter-position to limit further losses.")
    
    print("\n📊 Example Scenario:")
    print("   1. Bot opens LONG position at $0.52")
    print("   2. Price drops to $0.51 (-2% loss)")
    print("   3. Strong sell signal appears")
    print("   4. Bot opens SHORT hedge (50% of original)")
    print("   5. If price continues down:")
    print("      - Long loses more")
    print("      - Short gains offset the loss")
    print("   6. If price recovers:")
    print("      - Long recovers")
    print("      - Short loses (smaller position)")
    
    print("\n💡 Hedge Benefits:")
    print("   ✓ Reduces downside risk")
    print("   ✓ Allows time for recovery")
    print("   ✓ Protects capital during volatility")
    print("   ✓ Can profit from both directions")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("XRP HEDGE BOT - DEMO MODE")
    print("=" * 60)
    print("\nThis demo shows how the bot works without executing real trades.")
    print("Perfect for understanding the strategy before going live!")
    
    try:
        demo_technical_analysis()
        time.sleep(2)
        
        demo_position_sizing()
        time.sleep(2)
        
        demo_risk_management()
        time.sleep(2)
        
        demo_signal_generation()
        time.sleep(2)
        
        demo_hedge_strategy()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print("\n✓ You now understand how the bot analyzes and trades!")
        print("\nNext steps:")
        print("  1. Configure your .env file")
        print("  2. Run: python validate_setup.py")
        print("  3. Start with testnet: python bot.py")
        print("  4. Monitor performance and adjust settings")
        print()
        
    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)


if __name__ == '__main__':
    main()
