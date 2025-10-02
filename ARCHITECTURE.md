# XRP Trading Bot v2.0 - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
├─────────────────────────────────────────────────────────────────┤
│  Web Dashboard (Flask)         Telegram Bot        CLI/Console   │
│  • Real-time status            • Trade alerts     • Logs         │
│  • Metrics display             • P&L updates      • Statistics   │
│  • Trade history               • Signals          • Commands     │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Enhanced Bot Core                           │
│                      (bot_enhanced.py)                           │
├─────────────────────────────────────────────────────────────────┤
│  • Orchestrates all modules                                      │
│  • Main trading loop                                             │
│  • Error handling & recovery                                     │
│  • Configuration management                                      │
└─────────────────────────────────────────────────────────────────┘
           │              │              │              │
           ▼              ▼              ▼              ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Trading    │  │   Signal     │  │    Risk      │  │  Portfolio   │
│   Manager    │  │  Generation  │  │  Management  │  │  Management  │
├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤
│ Multi-pair   │  │ Technical    │  │ Dynamic      │  │ Diversifier  │
│ Manager      │  │ Analysis     │  │ Leverage     │  │              │
│              │  │              │  │              │  │ • Correlation│
│ • Allocation │  │ • RSI        │  │ • Volatility │  │ • Position   │
│ • Balance    │  │ • MACD       │  │   based      │  │   sizing     │
│ • Tracking   │  │ • EMA        │  │ • Risk       │  │ • Rebalancing│
│              │  │ • Bollinger  │  │   based      │  │              │
│              │  │              │  │              │  │              │
│              │  │ ML Signals   │  │ Hedge        │  │              │
│              │  │              │  │ Strategy     │  │              │
│              │  │ • Momentum   │  │              │  │              │
│              │  │ • Volatility │  │ • SL/TP      │  │              │
│              │  │ • MA Cross   │  │ • Trailing   │  │              │
│              │  │ • Reversion  │  │ • Auto hedge │  │              │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    KuCoin API Client                             │
│                   (kucoin_client.py)                             │
├─────────────────────────────────────────────────────────────────┤
│  • Authentication (HMAC-SHA256)                                  │
│  • Market data retrieval                                         │
│  • Order placement & management                                  │
│  • Position tracking                                             │
│  • Account balance                                               │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    KuCoin Futures API                            │
│                  (Production/Testnet)                            │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Market Data → Technical Analysis → ML Signals → Risk Assessment
                    ↓                   ↓              ↓
                 Indicators          Predictions   Leverage Adj.
                    ↓                   ↓              ↓
              Combined Signal ←─────────┴──────────────┘
                    ↓
            Portfolio Check (Correlation, Allocation)
                    ↓
            Trade Decision (Open/Close/Hedge/Hold)
                    ↓
         Execute Trade → Log → Notify (Telegram/Dashboard)
```

## Module Dependencies

```
bot_enhanced.py
    ├── config.py (Configuration)
    ├── kucoin_client.py (API)
    ├── technical_analysis.py (Indicators)
    ├── hedge_strategy.py (Strategy)
    ├── multi_pair.py (Multiple pairs)
    ├── ml_signals.py (ML models)
    ├── dynamic_leverage.py (Leverage)
    ├── portfolio_diversification.py (Portfolio)
    ├── web_dashboard.py (Dashboard)
    │   └── templates/dashboard.html
    └── telegram_notifier.py (Notifications)

run_backtest.py
    ├── backtesting.py (Backtest engine)
    ├── technical_analysis.py
    ├── hedge_strategy.py
    └── kucoin_client.py

demo_advanced.py
    ├── multi_pair.py
    ├── ml_signals.py
    ├── dynamic_leverage.py
    └── portfolio_diversification.py
```

## Feature Toggle Matrix

| Feature | Config Variable | Default | Module |
|---------|----------------|---------|--------|
| Web Dashboard | `ENABLE_WEB_DASHBOARD` | false | web_dashboard.py |
| ML Signals | `USE_ML_SIGNALS` | false | ml_signals.py |
| Dynamic Leverage | `ENABLE_DYNAMIC_LEVERAGE` | false | dynamic_leverage.py |
| Multiple Pairs | `TRADING_PAIRS` | XRPUSDTM | multi_pair.py |
| Telegram | `TELEGRAM_BOT_TOKEN` | - | telegram_notifier.py |
| Portfolio | Always Active | - | portfolio_diversification.py |

## Execution Flow

### Standard Bot (bot.py)
```
1. Initialize
2. Load config
3. Connect to API
4. Main loop:
   a. Get market data
   b. Analyze (technical)
   c. Get strategy suggestion
   d. Execute trade
   e. Update stats
   f. Sleep
```

### Enhanced Bot (bot_enhanced.py)
```
1. Initialize
2. Load config
3. Initialize all modules (dashboard, ML, multi-pair, etc.)
4. Start web dashboard (if enabled)
5. Main loop:
   a. For each trading pair:
      i. Get market data
      ii. Analyze (technical + ML)
      iii. Check portfolio diversification
      iv. Adjust leverage (if enabled)
      v. Get strategy suggestion
      vi. Execute trade
      vii. Notify (Telegram, dashboard)
   b. Update portfolio metrics
   c. Rebalance if needed
   d. Update statistics
   e. Sleep
```

## Backtesting Flow

```
1. Fetch historical data (KuCoin API)
2. Initialize backtest engine
3. For each candle:
   a. Calculate indicators
   b. Generate signals
   c. Simulate trades
   d. Track P&L
4. Calculate metrics (ROI, drawdown, win rate)
5. Export results
```

## Storage

```
bot_data/
    └── trade_history.jsonl      # All executed trades
    └── backtest_*.json          # Backtest results

Logs:
    bot.log                      # Runtime logs

Config:
    .env                         # Configuration
    .env.example                 # Template
```

## API Rate Limiting

- **Standard Bot**: ~10 calls/minute (1 pair)
- **Enhanced Bot**: ~10-30 calls/minute (depends on pairs)
- **Web Dashboard**: 1 call/5 seconds per endpoint
- **KuCoin Limit**: 100 calls/10 seconds

## Resource Requirements

| Configuration | RAM | CPU | Network |
|--------------|-----|-----|---------|
| Standard Bot | 20 MB | 1% | Low |
| Enhanced Bot (1 pair) | 50 MB | 2% | Low |
| Enhanced Bot (3 pairs) | 80 MB | 5% | Medium |
| Enhanced Bot (5 pairs) | 120 MB | 8% | Medium |
| + Web Dashboard | +30 MB | +1% | +Low |
| + ML Signals | +20 MB | +2% | - |

## Security

```
API Credentials → Environment Variables (.env)
                  ↓
              config.py (Validated)
                  ↓
          kucoin_client.py (HMAC signing)
                  ↓
              KuCoin API (HTTPS)

• Credentials never logged
• .env in .gitignore
• HMAC-SHA256 signatures
• HTTPS only
```

## Error Handling

```
Try-Catch Blocks
    ↓
Log Error (bot.log)
    ↓
Notify User (Telegram if configured)
    ↓
Continue Operation (skip cycle)
    ↓
Graceful Shutdown (on critical errors)
```

## Monitoring Points

1. **Bot Status**: Running/Stopped
2. **Balance**: Real-time tracking
3. **Positions**: All active positions
4. **Trades**: History and P&L
5. **Performance**: Win rate, ROI
6. **Errors**: Log and alerts
7. **API**: Rate limit status
8. **Diversification**: Portfolio health

## Scalability

- **Horizontal**: Run multiple bots on different accounts
- **Vertical**: Add more trading pairs (up to 5 recommended)
- **Modular**: Easy to add new features
- **Configurable**: Toggle features as needed

---

*Architecture version: 2.0*
