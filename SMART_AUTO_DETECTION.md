# Smart Auto-Detection Guide

## Overview

The XRP Hedge Bot now features **smart auto-detection** that automatically enables advanced features based on your configuration. You no longer need to choose between `bot.py` and `bot_enhanced.py` - just configure your `.env` file and run `python bot.py`!

## How It Works

The bot analyzes your `.env` configuration and automatically:
- Enables features when their settings are provided
- Uses smart defaults for optimal performance
- Shows you exactly what's enabled when it starts

## Feature Auto-Detection

### 🔔 Telegram Notifications

**Auto-enabled when both values are provided:**

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

**Detection logic:**
- If both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` have values → Telegram notifications enabled
- If either is missing → Telegram notifications disabled

**What you get:**
- Trade execution alerts
- P&L updates every 10 trades
- Strong signal notifications (if ML enabled)
- Error notifications
- Bot startup/shutdown messages

---

### 📊 Multi-Pair Trading

**Auto-enabled when multiple pairs are specified:**

```env
TRADING_PAIRS=XRPUSDTM,BTCUSDTM,ETHUSDTM
```

**Detection logic:**
- Single pair (e.g., `XRPUSDTM`) → Single-pair mode
- Multiple pairs (e.g., `XRPUSDTM,BTCUSDTM,ETHUSDTM`) → Multi-pair mode
- Allocation strategy automatically set to `best` if not specified

**What you get:**
- Trades multiple pairs simultaneously (or focuses on best with 'best' strategy)
- Independent signal generation per pair
- Automatic balance allocation
- Performance tracking per pair
- Pair rankings and statistics

**Allocation Strategies:**
```env
ALLOCATION_STRATEGY=best  # Auto-selected for multi-pair if not specified
# Options: equal, weighted, dynamic, best
```

- `best`: Automatically trades only the most profitable pair ⭐ (default for multi-pair)
- `equal`: Splits balance equally across all pairs
- `weighted`: Allocates based on win rate
- `dynamic`: Adaptive allocation based on recent performance

---

### ⚡ Dynamic Leverage

**Auto-enabled when leverage range differs from base:**

```env
LEVERAGE=11              # Base leverage
MIN_LEVERAGE=5           # Minimum leverage
MAX_LEVERAGE=20          # Maximum leverage
ENABLE_DYNAMIC_LEVERAGE=auto  # or true/false
```

**Detection logic:**
- If `ENABLE_DYNAMIC_LEVERAGE=true` → Always enabled
- If `ENABLE_DYNAMIC_LEVERAGE=false` → Always disabled
- If `ENABLE_DYNAMIC_LEVERAGE=auto` (or not set):
  - Enabled if `MIN_LEVERAGE` or `MAX_LEVERAGE` differ from `LEVERAGE`
  - Disabled otherwise

**What you get:**
- Leverage adjusts based on market volatility
- Higher leverage in good conditions, lower in risky conditions
- Considers win rate and recent performance
- Automatic risk management

---

### 🤖 ML-Based Signals

**Explicitly enable in .env:**

```env
USE_ML_SIGNALS=true
```

**What you get:**
- 6 advanced ML models
- 19 engineered features
- Market regime detection
- Adaptive model weighting
- Combined with traditional signals

---

### 🌐 Web Dashboard

**Explicitly enable in .env:**

```env
ENABLE_WEB_DASHBOARD=true
WEB_DASHBOARD_PORT=5000
```

**What you get:**
- Real-time bot status
- Balance and P&L tracking
- Performance metrics
- Active positions overview
- Recent trade history
- Access at http://localhost:5000

---

## Quick Configuration Examples

### Beginner: Basic Trading
```env
# Minimal configuration
KUCOIN_API_KEY=your_key
KUCOIN_API_SECRET=your_secret
KUCOIN_API_PASSPHRASE=your_passphrase
TRADING_PAIRS=XRPUSDTM

# Result: Basic single-pair trading with intelligent funding strategy
```

### Intermediate: With Notifications
```env
# Add Telegram for alerts
TRADING_PAIRS=XRPUSDTM
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# Result: Single-pair trading + Telegram notifications
```

### Advanced: Multi-Pair + ML
```env
# Multiple features
TRADING_PAIRS=XRPUSDTM,BTCUSDTM,ETHUSDTM
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
USE_ML_SIGNALS=true
ENABLE_DYNAMIC_LEVERAGE=auto

# Result: Multi-pair with 'best' strategy, Telegram, ML signals, dynamic leverage
```

### Expert: Everything Enabled
```env
# All features
TRADING_PAIRS=XRPUSDTM,BTCUSDTM,ETHUSDTM,SOLUSDTM
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
USE_ML_SIGNALS=true
ENABLE_WEB_DASHBOARD=true
ENABLE_DYNAMIC_LEVERAGE=true
MIN_LEVERAGE=5
MAX_LEVERAGE=20

# Result: Full-featured trading bot with all advanced capabilities
```

---

## Checking Enabled Features

When you start the bot, it displays all enabled features:

```
Initializing XRP Hedge Bot...
Enabled features:
  ✓ Telegram notifications
  ✓ ML-based signals
  ✓ Web dashboard (port 5000)
  ✓ Dynamic leverage (5x-20x)
  ✓ Multi-pair trading (4 pairs, best strategy)
  ✓ Intelligent funding strategy
```

---

## Migration from Previous Versions

### Before (v2.2.0 and earlier)
You had to choose:
```bash
python bot.py           # Basic bot
python bot_enhanced.py  # Advanced bot
```

### Now (v2.2.1+)
Just one command:
```bash
python bot.py  # Automatically adapts to your configuration!
```

**No configuration changes needed!** Your existing `.env` file will work as-is.

---

## Benefits of Smart Auto-Detection

1. **Simpler**: No need to choose between different bot files
2. **Smarter**: Bot knows what you want based on configuration
3. **Safer**: Graceful degradation if advanced modules unavailable
4. **Clearer**: See exactly what's enabled at startup
5. **Flexible**: Easy to enable/disable features by editing `.env`

---

## Troubleshooting

### "Feature not enabled even though I configured it"

1. Check the startup log to see what was detected
2. Verify your `.env` file has the correct syntax
3. Make sure there are no typos in variable names
4. For Telegram: Both token AND chat_id must be provided
5. For multi-pair: Pairs must be comma-separated with no spaces

### "Advanced feature failed to enable"

The bot will continue running in basic mode. Check:
1. Are all dependencies installed? (`pip install -r requirements.txt`)
2. Check the log for specific error messages
3. Some features require additional modules

### "Want to force-disable a feature"

Set explicit values:
```env
ENABLE_DYNAMIC_LEVERAGE=false  # Force disable
USE_ML_SIGNALS=false           # Force disable
```

---

## Best Practices

1. **Start Simple**: Begin with basic config, add features gradually
2. **Test on Testnet**: Always test new configurations on testnet first
3. **Monitor Startup**: Check the feature summary at bot startup
4. **Read Logs**: Logs show why features are enabled/disabled
5. **One Change at a Time**: Enable features one by one to understand impact

---

## Support

For questions or issues:
1. Check the startup feature summary
2. Review bot logs for error messages
3. Consult documentation (README.md, ADVANCED_FEATURES.md)
4. Open an issue on GitHub
