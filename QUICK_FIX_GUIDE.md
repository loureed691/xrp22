# Quick Fix Guide: Smart Fund Allocation with $25 Minimum Trade

## Your Situation
- **Total Balance**: $100-$120 USDT
- **Problem**: Getting "Insufficient balance" errors
- **Goal**: Each trade should be at least $25

## Solution: Configure Minimum Position Value

### Step 1: Update Your .env File

Add or update these settings in your `.env` file:

```env
# Ensure minimum $25 per trade
MIN_POSITION_VALUE_USD=25

# Keep 20% in reserve (recommended)
MIN_BALANCE_RESERVE_PERCENT=20

# Use 'best' strategy to focus on most profitable pair
ALLOCATION_STRATEGY=best

# Can use 500+ pairs - bot will focus on best opportunities
# Or reduce to 5-20 most liquid pairs to reduce API calls
TRADING_PAIRS=XRPUSDTM,BTCUSDTM,ETHUSDTM,SOLUSDTM,ADAUSDTM,DOTUSDTM,LINKUSDTM,BNBUSDTM,AVAXUSDTM,MATICUSDTM
```

### Step 2: Why This Works

#### With $100 balance:
- **Reserve**: $20 (20% protected)
- **Available**: $80 for trading
- **Min per trade**: $25 (margin required)
- **Max positions**: 3 concurrent trades at $25 each

#### With $120 balance:
#### With $120 balance:
- **Reserve**: $24 (20% protected)
- **Available**: $96 for trading
- **Min per trade**: $25 (margin required)
- **Max positions**: 3-4 concurrent trades at $25 each

Using `ALLOCATION_STRATEGY=best`:
- Bot scans all pairs
- Picks the most profitable one
- Allocates majority to that pair (80%)
- Reserves 20% for signal-matching pairs
- Automatically redistributes when needed to meet $25+ position size

### Step 3: Understanding the Results

**Before (without minimum)**:
```
Position Value: $14.40 (15% of $96)
Result: Too small, not worth trading fees
```

**After (with $25 minimum)**:
```
Position Value: $25.00 (adjusted to minimum)
Result: Meaningful position, worth the trade
Contracts: ~7,971 (for HUMAUSDTM at $0.034496)
Leveraged Value: ~$275 (11x leverage)
```

## Addressing the 401 Error

The 401 Unauthorized error for position queries is **separate** from the balance issue:

### Possible Causes:
1. **API Credentials Issue**
   - Check that your API key, secret, and passphrase are correct
   - Verify they're not expired

2. **API Permissions**
   - Ensure your API key has "General" and "Futures Trading" permissions
   - Check on KuCoin website under API Management

3. **Testnet vs Production**
   - If `USE_TESTNET=false`, make sure you're using production API credentials
   - If `USE_TESTNET=true`, make sure you're using testnet credentials

### To Fix:
```env
# In your .env file:
KUCOIN_API_KEY=your_actual_api_key
KUCOIN_API_SECRET=your_actual_secret
KUCOIN_API_PASSPHRASE=your_actual_passphrase
USE_TESTNET=false  # or true if using testnet
```

## Best Practices for Your Balance

### Option 1: Focus on Best Pair (Recommended)
```env
ALLOCATION_STRATEGY=best
MIN_POSITION_VALUE_USD=25
```
- Trades only the most profitable pair
- Uses full available balance ($96)
- 1 position at a time

### Option 2: Diversify (2-3 Pairs)
```env
ALLOCATION_STRATEGY=equal
MIN_POSITION_VALUE_USD=25
TRADING_PAIRS=XRPUSDTM,BTCUSDTM,ETHUSDTM
```
- Splits $96 three ways: $32 per pair
- Each meets $25 minimum ✓
- 3 positions at a time

### Option 3: More Pairs (Not Recommended)
```env
ALLOCATION_STRATEGY=equal
TRADING_PAIRS=pair1,pair2,pair3,pair4,pair5
```
- Splits $96 five ways: $19.20 per pair
- Below $25 minimum ✗
- Trades will be skipped

## Monitoring Your Bot

After making these changes, you should see:

```
✓ Funding Strategy initialized:
✓   Reserve: 20.0%
✓   Base position size: 15.0%
✓   Position size range: 5.0%-40.0%
✓   Minimum position value: $25.00

✓ Available balance: $120.00
✓ XRPUSDTM price: $0.52
✓ Position Size: 528 contracts
✓ Margin Required: $25.00
✓ Trade Status: ALLOWED
```

Instead of:
```
✗ Strategy suggestion: none - Insufficient balance
```

## Need More Balance?

To comfortably trade with $25 minimum:
- **Minimum viable**: $31.25 (allows 1 position)
- **Working**: $100 (allows 3 positions)
- **Current**: $120 (allows 3-4 positions)
- **Comfortable**: $150+ (allows 4-5 positions)
- **Ideal**: $200+ (allows 6-8 positions)

Formula: `Recommended Balance = (MIN_POSITION_VALUE × Desired Positions) / (1 - Reserve%)`

Example for 4 positions:
- $25 × 4 = $100 trading capital needed
- $100 / 0.8 = $125 total balance

## Summary

✅ **Add to .env**:
- `MIN_POSITION_VALUE_USD=25`
- `ALLOCATION_STRATEGY=best`
- Reduce `TRADING_PAIRS` to 5-20 liquid pairs

✅ **Fix 401 errors**:
- Verify API credentials
- Check API permissions

✅ **Result**:
- Each trade is at least $25
- Capital is used efficiently
- Bot focuses on best opportunities
