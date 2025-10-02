# XRP Futures Hedge Trading Bot

A sophisticated, automated trading bot for KuCoin XRP futures with 11x leverage, featuring intelligent hedge strategies and risk management.

## Features

- **11x Leverage Trading**: Maximizes potential returns with controlled risk
- **Hedge Strategy**: Automatically opens counter-positions to protect against adverse movements
- **Multiple Technical Indicators**: RSI, MACD, EMA, Bollinger Bands, ATR
- **Smart Position Management**: Dynamic position sizing based on available balance
- **Risk Management**: Stop loss, take profit, and trailing stop mechanisms
- **Auto-Reinvestment**: Automatically reinvests all profits to compound gains
- **Comprehensive Logging**: Detailed logs of all trades and decisions
- **Trade History**: JSON log of all executed trades

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

Edit the `.env` file to customize bot behavior:

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

# Technical Indicators
RSI_PERIOD=14
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70
EMA_SHORT=12
EMA_LONG=26
MACD_SIGNAL=9
```

## Usage

### Start the bot:
```bash
python bot.py
```

The bot will:
1. Connect to KuCoin Futures API
2. Analyze market conditions every 60 seconds
3. Generate trading signals based on technical analysis
4. Execute trades automatically based on strategy
5. Monitor positions and manage risk
6. Reinvest all profits automatically

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

## Risk Management

- **Maximum Position Size**: 80% of available balance
- **11x Leverage**: Amplifies both gains and losses
- **Stop Loss**: Automatically exits at 5% loss
- **Take Profit**: Locks in gains at 8% profit
- **Trailing Stop**: Protects profits by trailing 3% from peak

## File Structure

```
xrp22/
├── bot.py                 # Main bot execution
├── config.py              # Configuration management
├── kucoin_client.py       # KuCoin API client
├── technical_analysis.py  # Technical indicators
├── hedge_strategy.py      # Trading strategy logic
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .env                  # Your configuration (create this)
├── .gitignore            # Git ignore rules
├── bot.log               # Bot execution log
└── bot_data/
    └── trade_history.jsonl  # Trade history log
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

Future enhancements:
- [ ] Web dashboard for monitoring
- [ ] Multiple trading pairs
- [ ] Advanced ML-based signals
- [ ] Backtesting framework
- [ ] Telegram notifications
- [ ] Portfolio diversification
- [ ] Dynamic leverage adjustment
