# Quick Start Guide

## Getting Started in 5 Minutes

### Step 1: Install Python 3.11+
Make sure you have Python 3.11 or higher installed on Windows.

Check your version:
```bash
python --version
```

### Step 2: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/loureed691/xrp22.git
cd xrp22

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure API Keys

1. Get KuCoin API credentials:
   - **Testnet** (recommended for testing): https://sandbox-futures.kucoin.com/
   - **Production**: https://www.kucoin.com/

2. Create API key with these permissions:
   - General
   - Futures Trading

3. Configure the bot:
```bash
# Copy example config
copy .env.example .env

# Edit .env with your favorite text editor
notepad .env
```

Add your credentials:
```env
KUCOIN_API_KEY=your_actual_api_key
KUCOIN_API_SECRET=your_actual_secret
KUCOIN_API_PASSPHRASE=your_actual_passphrase
USE_TESTNET=true
```

### Step 4: Validate Setup
```bash
python validate_setup.py
```

This will check:
- Python version
- Dependencies
- Configuration
- API connection
- Balance availability

### Step 5: Start Trading
```bash
python bot.py
```

**The unified bot automatically detects and enables features based on your .env configuration!**

The bot will:
- Auto-detect enabled features from your configuration
- Analyze markets every 60 seconds
- Generate trading signals using technical indicators (+ ML if enabled)
- Execute trades automatically
- Manage positions with intelligent risk management
- Send notifications (if Telegram is configured)
- Track multiple pairs (if multiple pairs configured)
- Adjust leverage dynamically (if enabled)
- Provide web dashboard (if enabled)

### Step 6: Monitor Performance
- Watch console output for real-time updates and feature detection
- Check `bot.log` for detailed logs
- Review `bot_data/trade_history.jsonl` for trade records

### Stopping the Bot
Press `Ctrl+C` to safely stop the bot.

## Important Settings

### Risk Management (in .env)
```env
LEVERAGE=11                      # 11x leverage
MAX_POSITION_SIZE_PERCENT=80     # Use 80% of balance
STOP_LOSS_PERCENT=5              # Exit at 5% loss
TAKE_PROFIT_PERCENT=8            # Take profit at 8% gain
TRAILING_STOP_PERCENT=3          # Trail 3% from peak
```

### Trading Cycle
Default: 60 seconds between cycles
- Faster trading: Edit `bot.py`, change `bot.run(interval=30)` 
- Slower trading: Use `bot.run(interval=120)` or higher

## Understanding the Output

### Signal Strength
- 0-40: Weak signal (bot waits)
- 40-60: Moderate signal (bot may trade)
- 60-80: Strong signal (bot trades)
- 80-100: Very strong signal (high confidence)

### Position Management
- **Open**: Opens a new long or short position
- **Close**: Closes existing position (profit/loss)
- **Hedge**: Opens counter-position to protect against loss
- **Hold**: Monitors existing position
- **Wait**: No action, waiting for better signal

### Performance Metrics
- **Win Rate**: Percentage of profitable trades
- **Total Profit**: Net profit/loss in dollars
- **ROI**: Return on investment percentage

## Trading Strategy Explained

### Entry Conditions
The bot enters positions when multiple indicators align:

**Long (Buy) Entry:**
- RSI < 30 (oversold)
- MACD bullish crossover
- Price below lower Bollinger Band
- EMA short > EMA long

**Short (Sell) Entry:**
- RSI > 70 (overbought)
- MACD bearish crossover
- Price above upper Bollinger Band
- EMA short < EMA long

### Exit Conditions
Positions are closed when:
- **Stop Loss**: -5% loss
- **Take Profit**: +8% gain
- **Trailing Stop**: 3% decline from peak (long) or 3% rise from low (short)

### Hedging Strategy
When a position is losing >2%, the bot may open a counter-position:
- Long position losing → Open short hedge (50% size)
- Short position losing → Open long hedge (50% size)

This reduces overall exposure and protects capital.

## Tips for Success

1. **Start with Testnet**
   - Test strategy risk-free
   - Understand bot behavior
   - Validate performance

2. **Start Small**
   - Begin with minimum capital ($100)
   - Increase as confidence grows
   - Never risk more than you can lose

3. **Monitor Initially**
   - Watch first few trades closely
   - Verify bot behavior
   - Adjust settings if needed

4. **Be Patient**
   - Not every cycle will trade
   - Wait for strong signals
   - Quality over quantity

5. **Manage Risk**
   - Don't increase leverage beyond comfort
   - Keep stop losses enabled
   - Take profits regularly

6. **Keep Learning**
   - Review trade history
   - Analyze winning/losing patterns
   - Adjust strategy based on results

## Common Issues

### Bot not trading
- Check signal strength (needs >60%)
- Verify sufficient balance
- Check position limits
- Review technical indicators

### API errors
- Verify credentials in .env
- Check API key permissions
- Ensure futures trading enabled
- Try testnet first

### Position not closing
- Check trailing stop settings
- Verify stop loss/take profit levels
- Monitor market conditions
- Can manually close in KuCoin UI

## Advanced Configuration

### Customize Technical Indicators
```env
RSI_PERIOD=14           # RSI calculation period
RSI_OVERSOLD=30         # Buy threshold
RSI_OVERBOUGHT=70       # Sell threshold
EMA_SHORT=12            # Fast EMA
EMA_LONG=26             # Slow EMA
MACD_SIGNAL=9           # MACD signal line
```

### Adjust Risk Parameters
```env
MAX_POSITION_SIZE_PERCENT=80   # Lower for less risk
STOP_LOSS_PERCENT=3            # Tighter stops
TAKE_PROFIT_PERCENT=12         # Higher targets
TRAILING_STOP_PERCENT=2        # Tighter trailing
```

### Multiple Trading Pairs ⭐ NEW!
Trade multiple pairs simultaneously or let the bot automatically select the best one:
```env
# Multiple pairs (comma-separated)
TRADING_PAIRS=XRPUSDTM,BTCUSDTM,ETHUSDTM

# Allocation strategy
ALLOCATION_STRATEGY=best     # Automatically trades only the most profitable pair
# Options: equal, weighted, dynamic, best
```

**Allocation Strategies:**
- `equal`: Splits balance equally across all pairs
- `weighted`: Allocates based on win rate (better performers get more)
- `dynamic`: Adaptive allocation considering recent performance
- `best`: ⭐ Automatically selects and trades ONLY the most profitable pair

**Example:**
```env
# Let the bot choose the best pair automatically
TRADING_PAIRS=XRPUSDTM,BTCUSDTM,ETHUSDTM,SOLUSDTM
ALLOCATION_STRATEGY=best
```

The bot will track performance and automatically focus all trading on the pair with the best win rate and reliability!

## Safety Checklist

Before running with real money:
- [ ] Tested on testnet
- [ ] Understand the strategy
- [ ] Comfortable with risk settings
- [ ] Have stop losses configured
- [ ] Using only risk capital
- [ ] Monitoring is set up
- [ ] Emergency stop plan ready

## Support and Resources

- GitHub Issues: Report bugs or request features
- KuCoin API Docs: https://docs.kucoin.com/futures/
- Python Docs: https://docs.python.org/3.11/

## Disclaimer

This bot is for educational purposes. Futures trading with leverage is highly risky. Only trade with money you can afford to lose. Past performance does not guarantee future results.
