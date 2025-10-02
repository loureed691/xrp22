# Changelog

All notable changes to the XRP Hedge Bot project will be documented in this file.

## [2.0.0] - 2024-12-XX

### Added - Major Feature Release
- **Web Dashboard**: Real-time monitoring dashboard with Flask
  - Live status updates, balance tracking, and performance metrics
  - Position overview across all trading pairs
  - Recent trade history with auto-refresh
  - Accessible at http://localhost:5000 (configurable)

- **Multiple Trading Pairs**: Support for trading multiple pairs simultaneously
  - Configurable via TRADING_PAIRS environment variable
  - Three allocation strategies: equal, weighted, dynamic
  - Independent signal generation for each pair
  - Per-pair position tracking and statistics

- **ML-Based Signal Generation**: Advanced machine learning ensemble
  - Momentum model for trend detection
  - Volatility model for risk adaptation
  - MA crossover model for trend changes
  - Mean reversion model for extremes
  - Ensemble voting for robust predictions

- **Backtesting Framework**: Test strategies on historical data
  - Run backtests with custom parameters
  - Compare different leverage strategies
  - Detailed performance metrics (ROI, win rate, drawdown)
  - Save results to JSON for analysis

- **Telegram Notifications**: Real-time alerts via Telegram
  - Trade execution notifications
  - P&L updates
  - Strong signal alerts
  - Error notifications
  - Bot startup/shutdown messages

- **Portfolio Diversification**: Intelligent position management
  - Automatic correlation analysis between pairs
  - Optimal position sizing for diversification
  - Rebalancing suggestions
  - Portfolio health metrics

- **Dynamic Leverage Adjustment**: Adaptive leverage based on conditions
  - Volatility-based adjustment
  - Performance-based adjustment (reduce after losses)
  - Signal strength consideration
  - Risk-adjusted leverage calculation

### New Files
- `bot_enhanced.py`: Enhanced bot with all new features
- `web_dashboard.py`: Web dashboard module
- `telegram_notifier.py`: Telegram notification system
- `ml_signals.py`: ML-based signal generation
- `multi_pair.py`: Multiple trading pairs manager
- `dynamic_leverage.py`: Dynamic leverage adjuster
- `portfolio_diversification.py`: Portfolio management
- `backtesting.py`: Backtesting framework
- `run_backtest.py`: Backtesting script
- `templates/dashboard.html`: Web dashboard UI

### Changed
- Updated `config.py` to support new features
- Updated `.env.example` with new configuration options
- Enhanced `requirements.txt` with Flask dependency
- Expanded README.md with advanced features documentation

### Configuration
New environment variables:
- `ENABLE_WEB_DASHBOARD`: Enable web dashboard (default: false)
- `WEB_DASHBOARD_PORT`: Dashboard port (default: 5000)
- `TELEGRAM_BOT_TOKEN`: Telegram bot token
- `TELEGRAM_CHAT_ID`: Telegram chat ID
- `USE_ML_SIGNALS`: Enable ML signals (default: false)
- `ENABLE_DYNAMIC_LEVERAGE`: Enable dynamic leverage (default: false)
- `MIN_LEVERAGE`: Minimum leverage (default: 5)
- `MAX_LEVERAGE`: Maximum leverage (default: 20)
- `TRADING_PAIRS`: Comma-separated trading pairs
- `ALLOCATION_STRATEGY`: Allocation strategy (equal/weighted/dynamic)

## [1.0.1] - 2024-10-02

### Fixed
- **Critical:** Fixed 401 Unauthorized error in KuCoin API authentication
  - Query parameters are now correctly included in signature calculation for GET/DELETE requests
  - This resolves authentication failures when calling endpoints like `get_account_overview()` and `get_position()`
  - Follows KuCoin API v2 specification for HMAC-SHA256 signature generation

### Documentation
- Updated API_REFERENCE.md to clarify signature generation requirements
- Added note about query parameter inclusion in signatures

## [1.0.0] - 2024-10-02

### Added
- Initial release of XRP Futures Hedge Bot
- KuCoin Futures API integration with full authentication
- Comprehensive technical analysis module with RSI, MACD, EMA, Bollinger Bands, and ATR
- Sophisticated hedge trading strategy with risk management
- Automatic position sizing based on available balance and 11x leverage
- Stop loss, take profit, and trailing stop mechanisms
- Auto-reinvestment of all profits
- Real-time market analysis and signal generation
- Multi-indicator confirmation system for trade entries
- Position monitoring and automatic exit management
- Hedge position support for risk mitigation
- Detailed logging system with file and console output
- Trade history tracking in JSON format
- Windows batch files for easy setup and execution
- Comprehensive documentation:
  - README.md with full feature list and setup
  - QUICKSTART.md for 5-minute setup guide
  - API_REFERENCE.md with technical details
  - TROUBLESHOOTING.md for common issues
- Demo mode for understanding strategy without trading
- Setup validation script to verify configuration
- Support for both testnet and production environments
- Configuration via .env file
- Virtual environment support

### Features
- **11x Leverage Trading**: Configured for maximum approved leverage
- **Hedge Strategy**: Automatic counter-positions when primary position loses >2%
- **Risk Management**: 
  - 5% stop loss (configurable)
  - 8% take profit (configurable)
  - 3% trailing stop (configurable)
  - 80% max position size (configurable)
- **Technical Indicators**:
  - RSI with oversold/overbought detection
  - MACD with histogram analysis
  - EMA crossover detection
  - Bollinger Bands for volatility
  - ATR for risk assessment
- **Smart Signal Generation**:
  - Multi-indicator confirmation
  - Signal strength scoring (0-100)
  - Minimum 60% strength for trading
  - Buy/sell/hold recommendations
- **Performance Tracking**:
  - Win/loss statistics
  - Win rate calculation
  - Total profit/loss tracking
  - ROI monitoring
  - Trade history logging
- **Safety Features**:
  - Testnet support for risk-free testing
  - Balance validation before trading
  - Error handling and retry logic
  - Graceful shutdown on Ctrl+C
  - API rate limit compliance

### Technical Details
- Python 3.11+ support (tested on 3.12)
- Pure REST API implementation (no SDK dependency issues)
- HMAC-SHA256 signature authentication
- 60-second default trading cycle
- Configurable via environment variables
- Modular architecture for easy customization

### Documentation
- Complete setup instructions for Windows
- API integration guide
- Trading strategy explanation
- Risk management documentation
- Troubleshooting guide for common issues
- Code examples and usage patterns

### Scripts
- `bot.py`: Main bot execution
- `demo.py`: Strategy demonstration without trading
- `validate_setup.py`: Configuration and API validation
- `setup.bat`: Windows automated setup
- `run_bot.bat`: Windows bot launcher
- `run_demo.bat`: Windows demo launcher

### Known Limitations (v1.x)
- ~~Currently XRP/USDT only (XRPUSDTM)~~ - Now supports multiple pairs in v2.0
- 60-second minimum cycle time
- ~~No web dashboard (planned for future)~~ - Added in v2.0
- ~~No backtesting framework yet (planned)~~ - Added in v2.0
- ~~Single trading pair at a time~~ - Multiple pairs supported in v2.0

### Requirements
- Python 3.11 or higher
- Windows OS (tested), Linux/Mac compatible
- KuCoin Futures account (or testnet)
- Minimum $100 initial balance (recommended)
- Internet connection
- API credentials with Futures trading permission

### Dependencies (v2.0)
- python-dotenv >= 1.0.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- ta >= 0.11.0
- requests >= 2.31.0
- python-dateutil >= 2.8.2
- flask >= 3.0.0

## [Unreleased]

### Planned Features
- [x] Web dashboard for monitoring - **Released in v2.0**
- [x] Multiple trading pairs simultaneously - **Released in v2.0**
- [x] Advanced ML-based signal generation - **Released in v2.0**
- [x] Backtesting framework - **Released in v2.0**
- [x] Telegram/Discord notifications - **Released in v2.0**
- [x] Portfolio diversification - **Released in v2.0**
- [x] Dynamic leverage adjustment - **Released in v2.0**
- [ ] Dynamic leverage adjustment
- [ ] WebSocket for real-time updates
- [ ] Database for persistent storage
- [ ] Performance analytics dashboard
- [ ] Paper trading mode
- [ ] Custom strategy plugins
- [ ] Mobile app integration
- [ ] Advanced order types (limit, stop-limit)
- [ ] Multi-exchange support

### Under Consideration
- [ ] Grid trading strategy option
- [ ] DCA (Dollar Cost Averaging) mode
- [ ] Arbitrage between exchanges
- [ ] Copy trading features
- [ ] Social trading integration
- [ ] Risk calculator
- [ ] Position heat map
- [ ] Correlation analysis
- [ ] Sentiment analysis integration

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for new functionality in a backward compatible manner
- PATCH version for backward compatible bug fixes

## Contributing

See [GitHub Issues](https://github.com/loureed691/xrp22/issues) for planned features and known bugs.

## Support

For questions or issues:
1. Check TROUBLESHOOTING.md
2. Search existing GitHub issues
3. Create new issue with details
4. Include logs (remove credentials!)
