# Multi-Pair Trading Fix

## Issue
When using multi-pair trading with many pairs (e.g., 600+ pairs with 120 USDT balance), the bot would consistently show the error:
```
Trade blocked: Insufficient funds after reserve: $0.16
```

This prevented the bot from trading despite having sufficient total balance.

## Root Cause
The funding strategy had two problems:

1. **Wrong balance passed**: In `bot.py`, when checking if a trade should be allowed, the code passed the **total balance** instead of the **allocated pair balance** to `should_allow_trade()`.

2. **Hardcoded minimum**: The `funding_strategy.py` had a hardcoded check requiring at least $1 USD available after reserve. This didn't work for multi-pair scenarios where each pair might only get $0.20 allocated.

## Solution

### 1. Pass Allocated Balance (bot.py)
**Before:**
```python
should_allow, reason = self.funding_strategy.should_allow_trade(
    balance, position_value, self.recent_losses  # ❌ Used total balance
)
```

**After:**
```python
should_allow, reason = self.funding_strategy.should_allow_trade(
    pair_balance, position_value, self.recent_losses  # ✅ Use allocated pair balance
)
```

### 2. Dynamic Minimum Check (funding_strategy.py)

**Before:**
```python
if available_funds <= 1:  # ❌ Hardcoded $1 minimum
    return False, f"Insufficient funds after reserve: ${available_funds:.2f}"
```

**After:**
```python
# Calculate minimum funds needed for 1 contract
min_funds_needed = (current_price / leverage) if current_price > 0 else 1.0

if available_funds < min_funds_needed:  # ✅ Dynamic check based on actual needs
    logger.warning(f"Insufficient funds: ${available_funds:.2f} (need at least ${min_funds_needed:.2f} for 1 contract)")
    return 0
```

And in `should_allow_trade()`:
```python
if available_funds <= 0:  # ✅ Only check for positive funds
    return False, f"Insufficient funds after reserve: ${available_funds:.2f}"

if position_value > available_funds:  # ✅ Check against actual available funds
    return False, f"Position too large: ${position_value:.2f} exceeds available funds ${available_funds:.2f}"
```

## How It Works Now

### Example: 120 USDT with 600 pairs
- **Balance per pair**: $120 / 600 = $0.20
- **After 20% reserve**: $0.20 * 0.80 = $0.16 available
- **With 10x leverage**: $0.16 * 10 = $1.60 buying power
- **Can trade**: Assets priced up to ~$1.60 per contract

### Trading Capability
With $0.16 available and 10x leverage:
- ✅ Can trade: DOGE @ $0.10 → 1 contract (needs $0.01 margin)
- ✅ Can trade: XRP @ $0.50 → 1 contract (needs $0.05 margin)  
- ❌ Cannot trade: BNB @ $300 → Would need $30 margin per contract

## Benefits

1. **Multi-pair friendly**: Works with any number of pairs and any balance distribution
2. **Leverage aware**: Correctly calculates minimum based on leverage
3. **Backward compatible**: Single-pair mode still works perfectly
4. **Smart allocation**: Each pair trades based on its allocated balance

## Testing

All scenarios tested and passing:
- ✅ Single-pair mode with large balance ($120)
- ✅ Multi-pair mode with 600 pairs ($0.20 each)
- ✅ Edge cases (very small balances, circuit breakers, high leverage)

## Configuration Tips

If you're trading many pairs with small allocations, consider:

1. **Use 'best' allocation strategy**: Allocates all balance to the best-performing pair
   ```env
   ALLOCATION_STRATEGY=best
   ```

2. **Reduce reserve percentage** for multi-pair:
   ```env
   MIN_BALANCE_RESERVE_PERCENT=10  # Instead of default 20
   ```

3. **Use higher leverage** to maximize small allocations:
   ```env
   LEVERAGE=15  # Or higher, based on risk tolerance
   ```

4. **Start with fewer pairs** to build history:
   - Bot performs better when it has trading history to optimize allocations
   - Start with 10-20 most liquid pairs, then expand

## Related Files
- `bot.py` - Main bot logic, line 607
- `funding_strategy.py` - Position sizing and trade validation, lines 148 and 225
