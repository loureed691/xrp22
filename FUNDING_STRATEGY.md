# Intelligent Funding Strategy

## Overview

The **Intelligent Funding Strategy** is a risk-based position sizing system that manages your trading bot's account balance more logically and safely. Instead of using a fixed percentage of your balance (like the old 80% approach), it dynamically adjusts position sizes based on multiple factors including market conditions, account performance, and risk levels.

## Key Features

### 1. **Balance Reserve System**
- Always keeps a **minimum reserve** (default 20%) of your balance untouched
- Acts as an emergency fund and prevents total capital depletion
- Configurable via `MIN_BALANCE_RESERVE_PERCENT`

### 2. **Risk-Based Position Sizing**
Position sizes are calculated based on:
- **Market Volatility**: Lower volatility = larger positions allowed
- **Win Rate**: Higher win rate = more confidence, larger positions
- **Recent Losses**: Multiple losses trigger smaller positions or trading pause
- **Signal Strength**: Stronger signals allow larger positions
- **Existing Exposure**: Limits total capital at risk across all positions

### 3. **Circuit Breaker Protection**
- After **3 consecutive losses**: Only minimum position sizes allowed
- After **5 consecutive losses**: Trading is paused automatically
- Prevents emotional revenge trading and capital preservation

### 4. **Risk Tier System**
Positions are sized based on market volatility tiers:
- **Low Risk** (< 2% volatility): 1.5x base position size
- **Medium Risk** (2-5% volatility): 1.0x base position size  
- **High Risk** (> 5% volatility): 0.6x base position size

## Configuration

Add these settings to your `.env` file:

```env
# Enable the intelligent funding strategy (recommended)
USE_FUNDING_STRATEGY=true

# Minimum % of balance to always keep in reserve
MIN_BALANCE_RESERVE_PERCENT=20

# Base % of available balance to use per position
BASE_POSITION_SIZE_PERCENT=15

# Maximum % of available balance for a single position
MAX_POSITION_SIZE_PERCENT_NEW=40

# Minimum % of available balance for a single position
MIN_POSITION_SIZE_PERCENT=5
```

## How It Works

### Position Size Calculation

The system calculates position size through multiple steps:

1. **Calculate Available Funds**
   ```
   Reserve = Total Balance × (MIN_BALANCE_RESERVE_PERCENT / 100)
   Available = Total Balance - Reserve
   ```

2. **Calculate Risk Score** (0-1, where 1 is lowest risk)
   - Volatility component: Lower volatility scores higher
   - Win rate component: Higher win rate scores higher
   - Recent losses component: More losses scores lower
   - Signal strength component: Stronger signals score higher
   
   ```
   Risk Score = (volatility_score × 0.3) + 
                (win_rate_score × 0.25) + 
                (loss_score × 0.25) + 
                (signal_score × 0.2)
   ```

3. **Apply Risk Tier Multiplier**
   - Determine risk tier based on volatility
   - Apply tier multiplier to base position size

4. **Calculate Final Size**
   ```
   Position % = BASE_POSITION_SIZE × Risk Score × Tier Multiplier
   Position % = Clamp(Position %, MIN_POSITION_SIZE, MAX_POSITION_SIZE)
   Position Value = Available Funds × (Position % / 100)
   Contracts = (Position Value × Leverage) / Current Price
   ```

### Example Scenarios

#### Scenario 1: Optimal Conditions
- Balance: $1,000
- Volatility: 2% (low)
- Win Rate: 70%
- Recent Losses: 0
- Signal Strength: 80

**Result**: ~594 contracts (~$148.50 margin at 10x leverage)
- Uses ~18.5% of total balance
- Higher confidence = larger position

#### Scenario 2: Poor Conditions
- Balance: $1,000
- Volatility: 8% (high)
- Win Rate: 30%
- Recent Losses: 2
- Signal Strength: 55

**Result**: ~160 contracts (~$40 margin at 10x leverage)
- Uses only ~5% of total balance
- High risk = much smaller position

#### Scenario 3: After Multiple Losses
- Balance: $1,000
- Recent Losses: 5

**Result**: Trading blocked automatically
- Circuit breaker activated
- Time to review strategy

## Comparison with Legacy System

### Old System (MAX_POSITION_SIZE_PERCENT = 80%)
```
Balance: $1,000
Position: Uses $800 (80%)
Risk: VERY HIGH - one bad trade can wipe out most capital
Reserve: None - can lose everything
```

### New System (Intelligent Funding Strategy)
```
Balance: $1,000
Reserve: $200 (20%) - always protected
Available: $800

Position (good conditions): ~$150 (18.5% of total)
Position (poor conditions): ~$50 (5% of total)
Position (after losses): Blocked or minimal

Risk: MANAGED - Multiple layers of protection
Reserve: $200 always safe
```

## Benefits

1. **Capital Preservation**: Always maintains a reserve fund
2. **Risk Management**: Automatically reduces exposure in risky conditions
3. **Emotional Protection**: Circuit breakers prevent revenge trading
4. **Adaptive Sizing**: Positions adjust to market conditions and performance
5. **Longevity**: Keeps you in the game longer by preventing total loss

## Trade Approval System

Before executing any trade, the system checks:

1. **Sufficient Funds**: Available funds after reserve > $1
2. **Position Size Limits**: Position doesn't exceed max allowed percentage
3. **Loss Circuit Breaker**: Not too many recent consecutive losses
4. **Progressive Limits**: After 3 losses, only minimum positions allowed

## Risk Score Components

### 1. Volatility Score (30% weight)
- Measures market stability
- Lower volatility = safer trading conditions
- Formula: `max(0, 1 - (volatility / 0.1))`

### 2. Win Rate Score (25% weight)
- Based on historical performance
- Higher win rate = more confident sizing
- Formula: `win_rate / 100`

### 3. Loss Score (25% weight)
- Penalizes consecutive losses
- Each loss adds 20% risk penalty
- Formula: `max(0, 1 - (recent_losses × 0.2))`

### 4. Signal Score (20% weight)
- Considers current signal strength
- Stronger signals allow larger positions
- Formula: `signal_strength / 100`

## Maximum Loss Calculation

The system can calculate maximum potential loss for any position:

```python
Position Value = Contracts × Entry Price
Margin = Position Value / Leverage
Max Loss = Margin × (Stop Loss % / 100)
```

Example:
- 1000 contracts @ $2.50 = $2,500 position
- 10x leverage = $250 margin required
- 5% stop loss = $12.50 max loss

## Usage in Code

The funding strategy is automatically integrated when enabled:

```python
# Initialize (done automatically by bot)
funding_strategy = FundingStrategy(
    min_balance_reserve_percent=20.0,
    base_position_size_percent=15.0,
    max_position_size_percent=40.0,
    min_position_size_percent=5.0
)

# Calculate position size (done automatically by bot)
size = funding_strategy.calculate_position_size(
    available_balance=1000,
    current_price=2.5,
    leverage=10,
    volatility=0.03,
    win_rate=50.0,
    recent_losses=0,
    signal_strength=65,
    existing_positions_value=0
)
```

## Backward Compatibility

The new funding strategy is **opt-in** via configuration:

- Set `USE_FUNDING_STRATEGY=true` to enable (recommended)
- Set `USE_FUNDING_STRATEGY=false` to use legacy sizing
- Default is `true` in `.env.example`

Existing bots will continue to work with their current configuration.

## Testing

A comprehensive test suite validates all functionality:

```bash
python /tmp/test_funding_strategy.py
```

Tests cover:
- Position sizing in various conditions
- Reserve calculations
- Trade approval logic
- Risk scoring
- Circuit breaker functionality
- Maximum loss calculations

## Recommendations

### For Conservative Trading
```env
MIN_BALANCE_RESERVE_PERCENT=30
BASE_POSITION_SIZE_PERCENT=10
MAX_POSITION_SIZE_PERCENT_NEW=25
```

### For Moderate Trading (Recommended)
```env
MIN_BALANCE_RESERVE_PERCENT=20
BASE_POSITION_SIZE_PERCENT=15
MAX_POSITION_SIZE_PERCENT_NEW=40
```

### For Aggressive Trading
```env
MIN_BALANCE_RESERVE_PERCENT=10
BASE_POSITION_SIZE_PERCENT=20
MAX_POSITION_SIZE_PERCENT_NEW=50
```

## Monitoring

The system provides detailed logging:
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

## Summary

The Intelligent Funding Strategy transforms the bot from using a **risky fixed percentage** approach to a **dynamic, risk-aware** system that:

- Protects your capital with reserves
- Adjusts position sizes based on conditions
- Prevents catastrophic losses with circuit breakers
- Maximizes profit potential when conditions are favorable
- Minimizes risk when conditions are unfavorable

**Bottom Line**: Use your money more logically by adapting to market conditions and your trading performance.
