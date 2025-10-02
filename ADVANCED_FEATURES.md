# Advanced Features Guide

This guide explains how to use the advanced features introduced in v2.0.

## Table of Contents
1. [Web Dashboard](#web-dashboard)
2. [Multiple Trading Pairs](#multiple-trading-pairs)
3. [ML-Based Signals](#ml-based-signals)
4. [Backtesting](#backtesting)
5. [Telegram Notifications](#telegram-notifications)
6. [Portfolio Diversification](#portfolio-diversification)
7. [Dynamic Leverage](#dynamic-leverage)

---

## Web Dashboard

### Setup
1. Enable the web dashboard in your `.env` file:
```env
ENABLE_WEB_DASHBOARD=true
WEB_DASHBOARD_PORT=5000
```

2. Run the enhanced bot:
```bash
python bot_enhanced.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

### Features
- **Real-time Status**: See if bot is running, current balance, and profit/loss
- **Performance Metrics**: Total trades, win rate, and ROI
- **Position Overview**: All active positions across trading pairs
- **Trade History**: Last 50 trades with timestamps and reasons
- **Auto-refresh**: Updates every 5 seconds

### Dashboard Metrics
- **Current Balance**: Your available trading balance
- **Total Profit**: Cumulative P&L since bot started
- **Win Rate**: Percentage of winning trades
- **Total Trades**: Number of trades executed

---

## Multiple Trading Pairs

### Setup
Configure multiple trading pairs in `.env`:
```env
# Multiple pairs (comma-separated)
TRADING_PAIRS=XRPUSDTM,BTCUSDTM,ETHUSDTM

# Allocation strategy
ALLOCATION_STRATEGY=dynamic
```

### Allocation Strategies

#### 1. Equal Allocation
Splits balance equally across all pairs:
```env
ALLOCATION_STRATEGY=equal
```
- Simple and balanced
- Good for pairs with similar volatility
- Example: $300 balance → $100 per pair

#### 2. Weighted Allocation
Allocates based on historical performance:
```env
ALLOCATION_STRATEGY=weighted
```
- Winners get more allocation
- Adapts to pair performance
- Requires trading history

#### 3. Dynamic Allocation
Adjusts based on recent results and win rates:
```env
ALLOCATION_STRATEGY=dynamic
```
- Most adaptive strategy
- Considers recent performance
- Minimum 10% per pair
- Recommended for experienced traders

#### 4. Best Pair Allocation ⭐ NEW!
Automatically selects and allocates ALL balance to the most profitable pair:
```env
ALLOCATION_STRATEGY=best
```
- Focuses on the single best performing pair
- Maximizes returns by avoiding underperforming pairs
- Adapts as trading history evolves
- Requires at least some trading history to work effectively
- Falls back to equal allocation when no history exists

**How it works:**
- Calculates a composite score for each pair based on:
  - Win rate (60% weight)
  - Trade activity/reliability (40% weight)
- Automatically allocates 100% of balance to highest scoring pair
- Continuously re-evaluates and can switch pairs as performance changes

**Best for:**
- Focusing capital on proven winners
- Maximizing profitability
- Traders who want automated pair selection
- Situations where some pairs consistently outperform others

### Best Practices
- Start with 2-3 pairs maximum
- Use pairs with low correlation (XRP, BTC, ETH)
- Monitor diversification score in logs
- Ensure sufficient balance ($100+ per pair)

---

## ML-Based Signals

### Setup
Enable ML signals in `.env`:
```env
USE_ML_SIGNALS=true
```

### How It Works
The ML signal generator uses an ensemble of models:

1. **Momentum Model**: Detects price trends and acceleration
2. **Volatility Model**: Adapts to market volatility
3. **MA Crossover Model**: Identifies trend changes
4. **Mean Reversion Model**: Spots extremes

Signals are combined using weighted voting for robust predictions.

### Signal Interpretation
- **Confidence > 80%**: Strong signal, high agreement between models
- **Confidence 60-80%**: Moderate signal, some disagreement
- **Confidence < 60%**: Weak signal, mixed indicators

### Example Output
```
ML Signal: BUY | Confidence: 85.3% | Score: 0.72
Reason: Momentum: 0.65, Volatility: 0.55, MA Cross: 0.80
```

### Tips
- ML signals work best in trending markets
- Combine with traditional indicators for validation
- Higher confidence = more reliable signals
- Monitor ML performance in logs

---

## Backtesting

### Basic Usage
Run a backtest with default parameters:
```bash
python run_backtest.py
```

### Custom Parameters
```bash
# Backtest with custom settings
python run_backtest.py --balance 100 --leverage 11 --days 30

# Different trading pair
python run_backtest.py --symbol BTCUSDTM --days 60

# Compare strategies
python run_backtest.py --compare
```

### Understanding Results
```
BACKTEST RESULTS
==========================================
Total trades: 45
Winning trades: 28
Losing trades: 17
Win rate: 62.22%
Total P&L: $23.45
Final balance: $123.45
ROI: 23.45%
Max drawdown: 8.32%
```

**Key Metrics:**
- **ROI (Return on Investment)**: Overall profitability
- **Win Rate**: Percentage of profitable trades
- **Max Drawdown**: Largest peak-to-trough decline
- **Total P&L**: Net profit/loss

### Strategy Comparison
Compare different leverage levels:
```bash
python run_backtest.py --compare
```

Output:
```
Conservative (5x):  ROI: 12.3%, Win rate: 65%, Max drawdown: 5.2%
Standard (11x):     ROI: 23.4%, Win rate: 62%, Max drawdown: 8.3%
Aggressive (20x):   ROI: 34.5%, Win rate: 58%, Max drawdown: 15.6%
```

### Best Practices
- Test on at least 30 days of data
- Compare multiple strategies
- Consider max drawdown (lower is better)
- Balance ROI with win rate
- Backtest ≠ future performance

---

## Telegram Notifications

### Setup

#### Step 1: Create Telegram Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

#### Step 2: Get Chat ID
1. Start a chat with your bot
2. Send any message
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find your chat ID in the response (looks like: `123456789`)

#### Step 3: Configure Bot
Add to your `.env` file:
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=123456789
```

### Notification Types

#### Trade Notifications
Sent when trades are executed:
```
📈 OPEN BUY
Size: 500 contracts
Price: $0.523400
Reason: RSI oversold + MACD bullish
```

#### P&L Updates
Sent every 10 trades:
```
💰 P&L Update
PnL: +$12.45
Balance: $112.45
ROI: +12.45%
```

#### Signal Alerts
Sent for strong ML signals (strength ≥ 70):
```
🟢 Signal: BUY
Strength: 85/100
Reason: ML Ensemble: Momentum: 0.65, MA Cross: 0.80
```

#### Error Notifications
Sent when errors occur:
```
⚠️ Error
Trade execution failed: Insufficient balance
```

### Customization
Notifications are automatically sent - no configuration needed. The bot will:
- Send startup message when bot starts
- Notify on every trade execution
- Send P&L updates periodically
- Alert on strong signals (if ML enabled)
- Notify on shutdown

---

## Portfolio Diversification

### Automatic Features
Portfolio diversification is enabled automatically in `bot_enhanced.py`.

### Correlation Analysis
The bot tracks price correlation between trading pairs:
- **Correlation > 0.7**: High correlation (similar movements)
- **Correlation 0.3-0.7**: Moderate correlation
- **Correlation < 0.3**: Low correlation (good diversification)

### Position Sizing
Optimal position sizes calculated based on:
- Available balance
- Existing positions
- Correlation with other pairs
- Maximum position limit

### Rebalancing Suggestions
Check logs for rebalancing advice:
```
Rebalancing suggestions:
  XRPUSDTM: reduce (current: 45%, max: 40%)
  BTCUSDTM: close (high correlation with ETHUSDTM: 0.82)
```

### Diversification Score
Monitor portfolio health:
- **Score 0.8-1.0**: Excellent diversification
- **Score 0.6-0.8**: Good diversification
- **Score 0.4-0.6**: Moderate diversification
- **Score < 0.4**: Poor diversification (rebalance needed)

### Best Practices
- Trade uncorrelated assets (e.g., XRP + BTC + ETH)
- Limit positions to 40% of portfolio each
- Monitor correlation in logs
- Rebalance when diversification score drops
- Avoid too many highly correlated positions

---

## Dynamic Leverage

### Setup
Enable dynamic leverage in `.env`:
```env
ENABLE_DYNAMIC_LEVERAGE=true
MIN_LEVERAGE=5
MAX_LEVERAGE=20
```

### How It Works
Leverage adjusts based on three factors:

#### 1. Volatility
- **High volatility**: Reduce leverage (safer)
- **Low volatility**: Can use higher leverage
- Calculation: Based on price standard deviation

#### 2. Market Conditions
- **Strong signals**: Higher leverage allowed
- **Weak signals**: Lower leverage
- **Trending markets**: Can use more leverage

#### 3. Risk Level
- **Recent losses**: Reduce leverage
- **Good performance**: Can increase leverage
- **High exposure**: Lower leverage

### Example Adjustments
```
Leverage adjusted: 11x -> 8x
  Volatility: 0.72 | Condition: 0.55 | Risk: 0.48
Reason: High volatility + recent loss
```

```
Leverage adjusted: 11x -> 15x
  Volatility: 0.35 | Condition: 0.85 | Risk: 0.78
Reason: Low volatility + strong signal + good performance
```

### Best Practices
- Set conservative MIN_LEVERAGE (5x)
- Don't set MAX_LEVERAGE too high (20x max)
- Monitor leverage changes in logs
- Dynamic leverage helps manage risk automatically
- More conservative than fixed leverage

### Risk Considerations
- Lower leverage = Lower risk, lower returns
- Higher leverage = Higher risk, higher returns
- Dynamic adjustment helps balance risk/reward
- Always monitor your positions
- Use stop losses regardless of leverage

---

## Combining Features

### Recommended Configuration
For maximum effectiveness, enable multiple features:

```env
# Core settings
INITIAL_BALANCE=300
LEVERAGE=11
USE_TESTNET=true

# Multiple pairs with diversification
TRADING_PAIRS=XRPUSDTM,BTCUSDTM,ETHUSDTM
ALLOCATION_STRATEGY=dynamic

# ML signals for better entries
USE_ML_SIGNALS=true

# Dynamic leverage for risk management
ENABLE_DYNAMIC_LEVERAGE=true
MIN_LEVERAGE=5
MAX_LEVERAGE=15

# Monitoring
ENABLE_WEB_DASHBOARD=true
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Example Workflow
1. **Start bot**: `python bot_enhanced.py`
2. **Monitor dashboard**: Open http://localhost:5000
3. **Check Telegram**: Receive trade notifications
4. **Review logs**: Check diversification and leverage
5. **Run backtests**: Test strategy changes

---

## Troubleshooting

### Web Dashboard Not Loading
- Check `ENABLE_WEB_DASHBOARD=true` in .env
- Verify port 5000 is not in use
- Check firewall settings
- Look for errors in bot.log

### Telegram Not Working
- Verify bot token and chat ID are correct
- Check you sent a message to your bot first
- Test with: `curl https://api.telegram.org/bot<TOKEN>/getMe`
- Review telegram_notifier.py logs

### ML Signals Not Appearing
- Ensure `USE_ML_SIGNALS=true` in .env
- Check you have enough historical data (30+ candles)
- Look for "ML Signal" in logs
- Verify numpy and pandas are installed

### Multiple Pairs Not Trading
- Check `TRADING_PAIRS` has correct symbols
- Verify sufficient balance for all pairs
- Check correlation warnings in logs
- Ensure each pair has minimum balance

### Dynamic Leverage Not Adjusting
- Confirm `ENABLE_DYNAMIC_LEVERAGE=true`
- Check MIN/MAX leverage settings
- Look for "Leverage adjusted" in logs
- Verify conditions are met for adjustment

---

## Support

For issues or questions:
1. Check this guide first
2. Review bot.log for errors
3. Search existing GitHub issues
4. Open a new issue with:
   - Bot configuration (remove credentials)
   - Relevant log excerpts
   - Steps to reproduce

## Safety Reminders

- **Always test on testnet first**
- **Start with small amounts**
- **Monitor bot regularly**
- **Set appropriate stop losses**
- **Understand the risks**
- **Never invest more than you can lose**

---

*Last updated: v2.0*
