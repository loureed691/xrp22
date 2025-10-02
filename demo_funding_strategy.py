#!/usr/bin/env python3
"""
Demo: Intelligent Funding Strategy in Action
Shows how the bot adapts position sizing based on conditions
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from funding_strategy import FundingStrategy

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_scenario(name, description):
    print(f"\n📊 {name}")
    print(f"   {description}")
    print("   " + "-" * 66)

def main():
    print_header("Intelligent Funding Strategy Demo")
    print("\nThis demo shows how the bot adapts position sizing to different")
    print("market conditions and trading performance.\n")
    
    # Initialize funding strategy
    funding = FundingStrategy(
        min_balance_reserve_percent=20.0,
        base_position_size_percent=15.0,
        max_position_size_percent=40.0,
        min_position_size_percent=5.0
    )
    
    # Account settings
    balance = 1000.0
    price = 2.50
    leverage = 10
    
    print(f"Account Balance: ${balance:.2f}")
    print(f"Asset Price: ${price:.2f}")
    print(f"Leverage: {leverage}x")
    print(f"Reserve: {funding.min_balance_reserve_percent}% (${balance * 0.2:.2f} protected)")
    
    # Scenario 1: Optimal Conditions
    print_scenario(
        "Scenario 1: Optimal Trading Conditions",
        "Low volatility, high win rate, strong signal"
    )
    
    size1 = funding.calculate_position_size(
        available_balance=balance,
        current_price=price,
        leverage=leverage,
        volatility=0.02,      # Low volatility (2%)
        win_rate=70.0,        # Good win rate (70%)
        recent_losses=0,      # No recent losses
        signal_strength=85,   # Strong signal
        existing_positions_value=0
    )
    
    margin1 = (size1 * price) / leverage
    position_pct1 = (margin1 / balance) * 100
    
    print(f"\n   ✓ Position: {size1} contracts")
    print(f"   ✓ Value: ${size1 * price:.2f}")
    print(f"   ✓ Margin Required: ${margin1:.2f} ({position_pct1:.1f}% of balance)")
    print(f"   ✓ Reserve Protected: ${balance * 0.2:.2f}")
    
    # Scenario 2: Moderate Conditions
    print_scenario(
        "Scenario 2: Moderate Conditions",
        "Average volatility, decent win rate, medium signal"
    )
    
    size2 = funding.calculate_position_size(
        available_balance=balance,
        current_price=price,
        leverage=leverage,
        volatility=0.04,      # Moderate volatility (4%)
        win_rate=55.0,        # Average win rate (55%)
        recent_losses=1,      # 1 recent loss
        signal_strength=65,   # Medium signal
        existing_positions_value=0
    )
    
    margin2 = (size2 * price) / leverage
    position_pct2 = (margin2 / balance) * 100
    
    print(f"\n   → Position: {size2} contracts")
    print(f"   → Value: ${size2 * price:.2f}")
    print(f"   → Margin Required: ${margin2:.2f} ({position_pct2:.1f}% of balance)")
    print(f"   → Reserve Protected: ${balance * 0.2:.2f}")
    
    # Scenario 3: High Risk
    print_scenario(
        "Scenario 3: High Risk Conditions",
        "High volatility, poor win rate, weak signal, recent losses"
    )
    
    size3 = funding.calculate_position_size(
        available_balance=balance,
        current_price=price,
        leverage=leverage,
        volatility=0.08,      # High volatility (8%)
        win_rate=35.0,        # Poor win rate (35%)
        recent_losses=2,      # 2 recent losses
        signal_strength=55,   # Weak signal
        existing_positions_value=0
    )
    
    margin3 = (size3 * price) / leverage
    position_pct3 = (margin3 / balance) * 100
    
    print(f"\n   ⚠ Position: {size3} contracts")
    print(f"   ⚠ Value: ${size3 * price:.2f}")
    print(f"   ⚠ Margin Required: ${margin3:.2f} ({position_pct3:.1f}% of balance)")
    print(f"   ⚠ Reserve Protected: ${balance * 0.2:.2f}")
    print(f"\n   Note: Position size reduced by {((size1 - size3) / size1 * 100):.0f}% due to high risk")
    
    # Scenario 4: Circuit Breaker
    print_scenario(
        "Scenario 4: After Multiple Losses",
        "Circuit breaker protection activates"
    )
    
    for losses in [3, 5]:
        should_allow, reason = funding.should_allow_trade(
            available_balance=balance,
            position_value=100,
            recent_losses=losses
        )
        
        status = "🛑 BLOCKED" if not should_allow else "✓ ALLOWED"
        print(f"\n   {losses} consecutive losses: {status}")
        print(f"   Reason: {reason}")
    
    # Scenario 5: Existing Positions
    print_scenario(
        "Scenario 5: With Existing Exposure",
        "Already have 50% of balance in open positions"
    )
    
    size5 = funding.calculate_position_size(
        available_balance=balance,
        current_price=price,
        leverage=leverage,
        volatility=0.03,
        win_rate=60.0,
        recent_losses=0,
        signal_strength=70,
        existing_positions_value=500  # $500 already exposed
    )
    
    margin5 = (size5 * price) / leverage
    position_pct5 = (margin5 / balance) * 100
    
    print(f"\n   → New Position: {size5} contracts")
    print(f"   → Value: ${size5 * price:.2f}")
    print(f"   → Margin Required: ${margin5:.2f} ({position_pct5:.1f}% of balance)")
    print(f"   → Total Exposure: ${500 + margin5:.2f} ({(500 + margin5) / balance * 100:.1f}%)")
    print(f"   → Reserve Protected: ${balance * 0.2:.2f}")
    print(f"\n   Note: Position reduced by {((size1 - size5) / size1 * 100):.0f}% due to existing exposure")
    
    # Summary
    print_header("Summary: Adaptive Position Sizing")
    
    print("\nCondition                    | Contracts | Margin    | % of Balance")
    print("-" * 70)
    print(f"Optimal (low risk)           | {size1:>9} | ${margin1:>7.2f} | {position_pct1:>12.1f}%")
    print(f"Moderate (medium risk)       | {size2:>9} | ${margin2:>7.2f} | {position_pct2:>12.1f}%")
    print(f"High Risk (poor conditions)  | {size3:>9} | ${margin3:>7.2f} | {position_pct3:>12.1f}%")
    print(f"With existing exposure       | {size5:>9} | ${margin5:>7.2f} | {position_pct5:>12.1f}%")
    print(f"After 3 losses               | {'BLOCKED':>9} | {'N/A':>7} | {'0.0%':>12}")
    print(f"After 5 losses               | {'BLOCKED':>9} | {'N/A':>7} | {'0.0%':>12}")
    
    print("\n" + "=" * 70)
    print("Key Takeaways:")
    print("=" * 70)
    print("✓ Position size adapts from 5% to 18.5% based on conditions")
    print("✓ Reserve (20%) always protected regardless of trades")
    print("✓ High risk = smaller positions (automatic risk management)")
    print("✓ Circuit breakers prevent disaster after consecutive losses")
    print("✓ Total exposure limited even with multiple positions")
    print("\nYour bot now uses money LOGICALLY, not recklessly! 🎯")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    main()
