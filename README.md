# XRP Futures Hedge Trading Bot

A sophisticated, automated trading bot for KuCoin XRP futures with 11x leverage, featuring intelligent hedge strategies, ML-based signals, and advanced risk management.

## Features

### Core Features
- **11x Leverage Trading**: Maximizes potential returns with controlled risk
- **Hedge Strategy**: Automatically opens counter-positions to protect against adverse movements
- **Multiple Technical Indicators**: RSI, MACD, EMA, Bollinger Bands, ATR
- **Smart Position Management**: Dynamic position sizing based on available balance
- **Risk Management**: Stop loss, take profit, and trailing stop mechanisms
- **Auto-Reinvestment**: Automatically reinvests all profits to compound gains
- **Comprehensive Logging**: Detailed logs of all trades and decisions
- **Trade History**: JSON log of all executed trades

### Advanced Features (NEW!)
- **🌐 Web Dashboard**: Real-time monitoring dashboard with trade history and performance metrics
- **📊 Multiple Trading Pairs**: Trade multiple pairs simultaneously with intelligent allocation
  - **⭐ Automatic Best Pair Selection**: NEW! Bot automatically identifies and trades only the most profitable pair
  - Supports equal, weighted, dynamic, and best allocation strategies
- **💰 Intelligent Funding Strategy**: NEW! Risk-based position sizing with balance reserves
  - Automatic position size adjustment based on market conditions
  - 20% balance reserve (emergency fund always protected)
  - Circuit breakers after consecutive losses
  - Adaptive to volatility, win rate, and signal strength
  - See [FUNDING_STRATEGY.md](FUNDING_STRATEGY.md) for details
- **🤖 ML-Based Signals (ENHANCED v2.1)**: 
  - 6 advanced models with adaptive learning
  - Market regime detection (trending/ranging/volatile)
  - Automatic model weight adjustment based on performance
  - 19 engineered features including support/resistance levels
  - Risk-adjusted signal filtering for smarter decisions
- **📈 Backtesting Framework**: Test strategies on historical data before live trading
- **📱 Telegram Notifications**: Real-time trade alerts and P&L updates via Telegram
- **💼 Portfolio Diversification**: Automatic correlation analysis and position sizing
- **⚡ Dynamic Leverage**: Adjust leverage based on market conditions and risk

## Technical Indicators Used

1. **RSI (Relative Strength Index)**: Identifies overbought/oversold conditions
2. **MACD (Moving Average Convergence Divergence)**: Detects trend changes
3. **EMA (Exponential Moving Average)**: Short and long-term trend analysis
4. **Bollinger Bands**: Volatility and mean reversion signals
5. **ATR (Average True Range)**: Measures market volatility

## Requirements

- Python 3.11
- Windows OS
- KuCoin Futures Account (or Testnet account for testing)
- Initial balance: $100 (or test funds in testnet)

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/loureed691/xrp22.git
cd xrp22
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure the bot**:
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Edit `.env` and add your KuCoin API credentials
   - **IMPORTANT**: For testing, set `USE_TESTNET=true`

## KuCoin API Setup

1. **Create a KuCoin account** (or use testnet):
   - Production: https://www.kucoin.com/
   - Testnet: https://sandbox-futures.kucoin.com/

2. **Enable Futures Trading**:
   - Complete KYC verification (for production)
   - Enable futures trading in your account settings

3. **Create API Keys**:
   - Go to API Management
   - Create a new API key with futures trading permissions
   - **Required permissions**: General, Futures Trading
   - Save your API Key, Secret, and Passphrase securely

4. **Add funds**:
   - Transfer USDT to your Futures account
   - Minimum recommended: $100

## Configuration

The bot now features **smart auto-detection** that automatically enables advanced features based on your configuration!

Edit the `.env` file to customize bot behavior:

### Basic Configuration
```env
# API Credentials
KUCOIN_API_KEY=your_api_key
KUCOIN_API_SECRET=your_api_secret
KUCOIN_API_PASSPHRASE=your_passphrase

# Bot Settings
INITIAL_BALANCE=100
LEVERAGE=11
SYMBOL=XRPUSDTM
USE_TESTNET=true  # Set to 'false' for production

# Risk Management
MAX_POSITION_SIZE_PERCENT=80  # Use 80% of balance per trade
STOP_LOSS_PERCENT=5           # Exit if loss exceeds 5%
TAKE_PROFIT_PERCENT=8         # Take profit at 8% gain
TRAILING_STOP_PERCENT=3       # Trail stop 3% from peak
```

### Advanced Features - Smart Auto-Detection! 🎯

The bot automatically enables features based on your configuration:

#### Telegram Notifications
**Auto-enabled when both values are provided:**
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```
✓ Simply provide your credentials and notifications are automatically enabled!

#### Multiple Trading Pairs
**Auto-enabled when multiple pairs are specified:**
```env
TRADING_PAIRS=XRPUSDTM,BTCUSDTM,ETHUSDTM  # Comma-separated
ALLOCATION_STRATEGY=  # Leave blank for auto-detection (uses 'best' for multi-pair)
```
✓ Bot automatically uses 'best' strategy to trade only the most profitable pair!

#### Dynamic Leverage
**Auto-enabled when leverage range is different from base:**
```env
ENABLE_DYNAMIC_LEVERAGE=auto  # or true/false
MIN_LEVERAGE=5
MAX_LEVERAGE=20
```
✓ Set to 'auto' and the bot will enable it if your min/max differ from base leverage!

#### ML-Based Signals (Optional)
```env
USE_ML_SIGNALS=true  # Explicitly enable ML signals
```

#### Web Dashboard (Optional)
```env
ENABLE_WEB_DASHBOARD=true
WEB_DASHBOARD_PORT=5000
```

# Technical Indicators
RSI_PERIOD=14
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70
EMA_SHORT=12
EMA_LONG=26
MACD_SIGNAL=9
```

## Usage

### Unified Bot (Automatic Feature Detection)
Start the bot - it automatically adapts to your configuration:
```bash
python bot.py
```

The bot will:
1. **Auto-detect enabled features** from your .env configuration
2. Connect to KuCoin Futures API
3. Analyze market conditions every 60 seconds
4. Generate trading signals (traditional + ML if enabled)
5. Execute trades automatically based on strategy
6. Monitor positions and manage risk
7. Track portfolio diversification (if multi-pair enabled)
8. Adjust leverage dynamically (if enabled)
9. Send notifications via Telegram (if configured)
10. Provide web dashboard (if enabled)

### Web Dashboard
If enabled, access the web dashboard at:
```
http://localhost:5000
```

The dashboard shows:
- Real-time bot status
- Current balance and P&L
- Win rate and trade statistics
- Active positions
- Recent trade history

### Backtesting
Run backtests on historical data:
```bash
# Basic backtest
python run_backtest.py

# Custom parameters
python run_backtest.py --balance 100 --leverage 11 --days 30

# Compare strategies
python run_backtest.py --compare
```

### Stop the bot:
- Press `Ctrl+C` to safely stop the bot

## Trading Strategy

### Entry Signals
The bot opens positions when multiple indicators align:
- **Long Entry**: RSI oversold + MACD bullish + price below Bollinger lower band
- **Short Entry**: RSI overbought + MACD bearish + price above Bollinger upper band

### Exit Signals
Positions are closed when:
- Stop loss is triggered (-5% by default)
- Take profit target is reached (+8% by default)
- Trailing stop is triggered (3% from peak/low)

### Hedge Strategy
The bot opens counter-positions to protect against losses:
- If a long position is losing >2%, opens a short hedge
- If a short position is losing >2%, opens a long hedge
- Hedge size is 50% of the original position

## Advanced Features Guide

### Web Dashboard
The web dashboard provides real-time monitoring:
- **Status Overview**: Bot running status, current balance, total profit
- **Performance Metrics**: Win rate, total trades, profit percentage
- **Position Tracking**: View all active positions across trading pairs
- **Trade History**: Recent trade log with timestamps and reasons
- **Auto-refresh**: Updates every 5 seconds automatically

### ML-Based Signals (v2.1 - Enhanced)
The ML signal generator uses advanced ensemble methods with adaptive learning:

**Six Models:**
- **Momentum Model**: Analyzes price momentum and acceleration
- **Volatility Model**: Adapts to market volatility conditions
- **MA Crossover Model**: Detects trend changes
- **Mean Reversion Model**: Identifies oversold/overbought extremes
- **Trend Strength Model**: Evaluates trend alignment and consistency (NEW)
- **Support/Resistance Model**: Detects key price levels and bounces (NEW)

**Smart Features:**
- **Market Regime Detection**: Automatically detects trending, ranging, or volatile markets
- **Adaptive Learning**: Models learn from performance and adjust their weights
- **Risk-Adjusted Filtering**: More conservative in volatile markets, aggressive in trends
- **19 Engineered Features**: Including support/resistance, trend consistency, volatility clustering

See [ML_ENHANCEMENTS.md](ML_ENHANCEMENTS.md) for detailed technical documentation.

### Multiple Trading Pairs
Trade multiple pairs simultaneously:
- **Equal Allocation**: Split balance equally across all pairs
- **Weighted Allocation**: Allocate based on historical performance
- **Dynamic Allocation**: Adjust allocations based on recent results
- **Correlation Analysis**: Avoid highly correlated positions
- **Independent Signals**: Each pair analyzed separately

### Portfolio Diversification
Automatic portfolio management:
- **Correlation Tracking**: Monitor price correlation between pairs
- **Position Sizing**: Optimize position sizes for diversification
- **Rebalancing**: Suggestions to improve portfolio balance
- **Risk Spreading**: Prevent over-concentration in single asset

### Dynamic Leverage
Leverage adjusts based on conditions:
- **Volatility-based**: Lower leverage in high volatility
- **Performance-based**: Reduce leverage after consecutive losses
- **Signal-based**: Higher leverage with strong signals
- **Risk-adjusted**: Consider account balance and exposure

### Intelligent Funding Strategy (NEW!)
Smart position sizing that protects your capital:
- **Balance Reserve**: Always keeps 20% safe as emergency fund
- **Risk-Based Sizing**: Adapts position size (5-40%) based on:
  - Market volatility (smaller in volatile markets)
  - Win rate (larger when performing well)
  - Signal strength (larger with strong signals)
  - Recent losses (smaller after losses)
- **Circuit Breakers**: 
  - After 3 losses: Only minimum positions
  - After 5 losses: Trading paused automatically
- **Quick Start**: See [FUNDING_QUICKSTART.md](FUNDING_QUICKSTART.md)
- **Full Details**: See [FUNDING_STRATEGY.md](FUNDING_STRATEGY.md)
- **Try It**: Run `python demo_funding_strategy.py`

### Telegram Notifications
Stay informed with real-time alerts:
- Trade executions (open, close, hedge)
- Significant P&L updates
- Strong trading signals
- Error notifications
- Bot startup/shutdown messages

## Risk Management

The bot includes multiple layers of risk protection:

### Intelligent Funding Strategy (Recommended)
- **Balance Reserve**: 20% of balance always protected
- **Adaptive Position Sizing**: 5-40% of available balance based on:
  - Market volatility
  - Historical win rate
  - Signal strength
  - Recent performance
- **Circuit Breakers**: Automatic pause after 5 consecutive losses
- **Total Exposure Limits**: Considers existing positions

### Traditional Risk Controls
- **Stop Loss**: Automatically exits at 5% loss
- **Take Profit**: Locks in gains at 8% profit
- **Trailing Stop**: Protects profits by trailing 3% from peak
- **11x Leverage**: Balanced leverage for controlled risk amplification

**Note**: The old "Maximum Position Size: 80%" setting is replaced by the Intelligent Funding Strategy when enabled (recommended). See [FUNDING_STRATEGY.md](FUNDING_STRATEGY.md) for details.

## File Structure

```
xrp22/
├── bot.py                      # Unified bot with smart auto-detection (run this!)
├── config.py                   # Configuration with auto-detection logic
├── run_backtest.py             # Backtesting script
├── kucoin_client.py            # KuCoin API client
├── technical_analysis.py       # Technical indicators
├── hedge_strategy.py           # Trading strategy logic
├── funding_strategy.py         # Intelligent position sizing (NEW)
├── web_dashboard.py            # Web dashboard module
├── telegram_notifier.py        # Telegram notifications
├── ml_signals.py               # ML-based signal generation
├── multi_pair.py               # Multiple trading pairs manager
├── dynamic_leverage.py         # Dynamic leverage adjuster
├── portfolio_diversification.py # Portfolio management
├── backtesting.py              # Backtesting framework
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .env                       # Your configuration (create this)
├── .gitignore                 # Git ignore rules
├── bot.log                    # Bot execution log
├── templates/
│   └── dashboard.html         # Web dashboard HTML
└── bot_data/
    └── trade_history.jsonl    # Trade history log
```

## Monitoring

### Log Files
- **bot.log**: Real-time bot activity, decisions, and trades
- **bot_data/trade_history.jsonl**: JSON log of all executed trades

### Console Output
The bot displays:
- Current market price
- Technical indicator values
- Trading signals and decisions
- Position information
- Profit/loss statistics
- Win rate and performance metrics

## Safety Features

1. **Testnet Support**: Test strategies without risking real money
2. **Error Handling**: Comprehensive error handling and recovery
3. **Balance Checks**: Validates sufficient balance before trading
4. **Position Limits**: Prevents over-leveraging
5. **API Rate Limiting**: Respects KuCoin API limits
6. **Graceful Shutdown**: Safely stops on Ctrl+C

## Performance Tracking

The bot tracks:
- Total trades executed
- Winning vs. losing trades
- Win rate percentage
- Total profit/loss
- Current balance
- Return on investment (ROI)

## Troubleshooting

### "API credentials are required"
- Ensure `.env` file exists and contains valid credentials
- Check that API key has futures trading permissions

### "Insufficient balance"
- Verify you have funds in your Futures account
- Check `INITIAL_BALANCE` setting in `.env`

### Connection errors
- Verify internet connection
- Check if KuCoin API is operational
- For testnet, ensure `USE_TESTNET=true`

### No trades being executed
- Check signal strength requirements (minimum 60%)
- Verify market has sufficient volatility
- Review technical indicator values in logs

## Disclaimer

**IMPORTANT**: 
- This bot is for educational purposes
- Trading futures with leverage is highly risky
- Past performance does not guarantee future results
- Only trade with money you can afford to lose
- Test thoroughly on testnet before using real funds
- The authors are not responsible for any financial losses

## Support

For issues, please open a GitHub issue with:
- Bot configuration (remove API credentials)
- Relevant log excerpts
- Description of the problem

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Roadmap

Completed features (v2.0):
- [x] Web dashboard for monitoring
- [x] Multiple trading pairs
- [x] Advanced ML-based signals
- [x] Backtesting framework
- [x] Telegram notifications
- [x] Portfolio diversification
- [x] Dynamic leverage adjustment

Future enhancements:
- [ ] WebSocket for real-time updates
- [ ] Database for persistent storage
- [ ] Paper trading mode
- [ ] Custom strategy plugins
- [ ] Mobile app integration
- [ ] Advanced order types (limit, stop-limit)
- [ ] Multi-exchange support
