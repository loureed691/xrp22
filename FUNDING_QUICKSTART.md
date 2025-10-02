# Quick Start: Intelligent Funding Strategy

## What Is It?

The Intelligent Funding Strategy replaces the old fixed 80% position sizing with a smart, risk-aware system that:
- **Protects 20% of your balance** as an emergency reserve
- **Adapts position size** based on market volatility, win rate, and signal strength
- **Prevents disaster** with circuit breakers after consecutive losses
- **Uses your money logically**, not recklessly

## Enable It (2 Steps)

### Step 1: Update Your `.env` File

Add these lines to your `.env` file (or modify if they exist):

```env
# Enable intelligent funding strategy (RECOMMENDED)
USE_FUNDING_STRATEGY=true

# Keep 20% in reserve (adjust if needed)
MIN_BALANCE_RESERVE_PERCENT=20

# Base position size: 15% (will be adjusted by risk)
BASE_POSITION_SIZE_PERCENT=15

# Maximum position size: 40% (in optimal conditions)
MAX_POSITION_SIZE_PERCENT_NEW=40

# Minimum position size: 5% (in risky conditions)
MIN_POSITION_SIZE_PERCENT=5
```

### Step 2: Restart Your Bot

That's it! The bot will now use intelligent position sizing.

## Try the Demo

See how it works before trading:

```bash
python demo_funding_strategy.py
```

This shows how position sizes adapt to different market conditions.

## Understanding the Settings

### `USE_FUNDING_STRATEGY`
- **true**: Use intelligent risk-based sizing (RECOMMENDED)
- **false**: Use old fixed percentage method

### `MIN_BALANCE_RESERVE_PERCENT` (Default: 20)
- **What it does**: Percentage of balance always kept safe
- **Recommended**: 15-30% depending on risk tolerance
- **Example**: With $1000 balance and 20% reserve, only $800 is used for trading

### `BASE_POSITION_SIZE_PERCENT` (Default: 15)
- **What it does**: Starting point for position size calculations
- **Recommended**: 10-20% for most traders
- **Note**: Actual position will be adjusted up or down based on risk

### `MAX_POSITION_SIZE_PERCENT_NEW` (Default: 40)
- **What it does**: Maximum position size in optimal conditions
- **Recommended**: 30-50% for moderate risk
- **When used**: Low volatility + high win rate + strong signal

### `MIN_POSITION_SIZE_PERCENT` (Default: 5)
- **What it does**: Minimum position size in risky conditions
- **Recommended**: 3-10% for safety
- **When used**: High volatility + poor win rate + weak signal

## Risk Profiles

Choose settings based on your risk tolerance:

### Conservative (Low Risk)
```env
MIN_BALANCE_RESERVE_PERCENT=30
BASE_POSITION_SIZE_PERCENT=10
MAX_POSITION_SIZE_PERCENT_NEW=25
MIN_POSITION_SIZE_PERCENT=3
```

### Moderate (Recommended)
```env
MIN_BALANCE_RESERVE_PERCENT=20
BASE_POSITION_SIZE_PERCENT=15
MAX_POSITION_SIZE_PERCENT_NEW=40
MIN_POSITION_SIZE_PERCENT=5
```

### Aggressive (Higher Risk)
```env
MIN_BALANCE_RESERVE_PERCENT=10
BASE_POSITION_SIZE_PERCENT=20
MAX_POSITION_SIZE_PERCENT_NEW=50
MIN_POSITION_SIZE_PERCENT=8
```

## What Changes After Enabling?

### Before (Old System)
```
Balance: $1000
Position: ALWAYS 80% = $800
Risk: Very high, no protection
```

### After (New System)
```
Balance: $1000
Reserve: $200 (always protected)
Position: 5-40% based on conditions
  - Good conditions: ~15-20%
  - Bad conditions: ~5-10%
  - After losses: 0% (trading paused)
Risk: Managed, multiple protections
```

## Built-in Protections

The system automatically:

1. **Reserves Balance**: 20% always kept safe
2. **Reduces Size in Volatility**: Smaller positions when market is wild
3. **Reduces Size After Losses**: 
   - After 3 losses: Only minimum positions
   - After 5 losses: Trading stops completely
4. **Limits Total Exposure**: Considers existing positions
5. **Requires Strong Signals**: Weak signals = smaller positions

## Monitoring

The bot logs detailed information:

```
Position sizing calculation:
  Available balance: $1000.00
  Available funds (after reserve): $800.00
  Risk score: 0.65
  Risk tier: medium (multiplier: 1.0)
  Position size %: 15.50%
  Position value: $124.00
  Leverage: 10x
  Contracts: 496
```

Watch for:
- **Risk score**: Higher = more confident (0-1 scale)
- **Risk tier**: low/medium/high based on volatility
- **Position size %**: Actual percentage used

## Troubleshooting

### "Trade blocked: Insufficient funds after reserve"
- Your balance is too low after reserve
- Either add funds or reduce `MIN_BALANCE_RESERVE_PERCENT`

### "Trade blocked: Too many recent losses"
- Circuit breaker activated after 5 losses
- This is intentional - time to review strategy
- Bot will resume after you restart it

### "Position size is very small"
- Market conditions are risky (high volatility, poor signals)
- This is intentional protection
- Wait for better conditions

## Testing

Before going live:

1. **Run the demo**:
   ```bash
   python demo_funding_strategy.py
   ```

2. **Check with testnet**:
   ```env
   USE_TESTNET=true
   ```

3. **Start with small balance**:
   ```env
   INITIAL_BALANCE=50
   ```

## FAQ

**Q: Will this work with my existing bot?**
A: Yes! Just add the settings to `.env` and restart.

**Q: Can I disable it?**
A: Yes, set `USE_FUNDING_STRATEGY=false`

**Q: What if I want to use more/less than 20% reserve?**
A: Adjust `MIN_BALANCE_RESERVE_PERCENT` to your preference.

**Q: Does this work with multi-pair trading?**
A: Yes! It works with both basic and enhanced bots.

**Q: Is this better than the old system?**
A: Absolutely! See [FUNDING_BEFORE_AFTER.md](FUNDING_BEFORE_AFTER.md) for detailed comparison.

## Learn More

- **Detailed Guide**: [FUNDING_STRATEGY.md](FUNDING_STRATEGY.md)
- **Before/After Comparison**: [FUNDING_BEFORE_AFTER.md](FUNDING_BEFORE_AFTER.md)
- **Interactive Demo**: `python demo_funding_strategy.py`

## Summary

✅ Enable with `USE_FUNDING_STRATEGY=true`
✅ Keep 20% reserve for safety
✅ Position sizes adapt from 5-40% based on risk
✅ Circuit breakers prevent disaster
✅ Your bot uses money logically! 🎯
