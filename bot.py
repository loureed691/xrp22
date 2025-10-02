"""
Unified XRP Futures Hedge Trading Bot
Automatically enables advanced features based on configuration
"""
import logging
import time
import json
from datetime import datetime
from typing import Dict, Optional
import os

from config import Config
from kucoin_client import KuCoinFuturesClient
from technical_analysis import TechnicalAnalyzer
from hedge_strategy import HedgeStrategy
from funding_strategy import FundingStrategy

# Conditionally import advanced modules
try:
    from web_dashboard import WebDashboard
    from telegram_notifier import TelegramNotifier
    from ml_signals import MLSignalGenerator
    from multi_pair import MultiPairManager
    from dynamic_leverage import DynamicLeverage
    from portfolio_diversification import PortfolioDiversifier
    ADVANCED_MODULES_AVAILABLE = True
except ImportError as e:
    ADVANCED_MODULES_AVAILABLE = False
    logging.warning(f"Some advanced modules not available: {e}")

# Setup logging with UTF-8 encoding support
import sys

# Create file handler with UTF-8 encoding
file_handler = logging.FileHandler('bot.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Create console handler with error handling for Windows
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Configure console handler to handle encoding errors gracefully on Windows
if sys.platform == 'win32':
    # On Windows, wrap stdout to handle Unicode encoding errors
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)


class XRPHedgeBot:
    """Unified XRP Futures Hedge Trading Bot with smart feature detection"""
    
    def __init__(self):
        """Initialize the bot with automatic feature detection"""
        logger.info("Initializing XRP Hedge Bot...")
        
        # Validate configuration
        Config.validate()
        
        # Log enabled features
        logger.info("Enabled features:")
        logger.info(f"  {Config.get_feature_summary()}")
        
        # Initialize core components
        self.client = KuCoinFuturesClient(
            Config.API_KEY,
            Config.API_SECRET,
            Config.API_PASSPHRASE,
            Config.API_URL
        )
        
        self.analyzer = TechnicalAnalyzer(
            rsi_period=Config.RSI_PERIOD,
            ema_short=Config.EMA_SHORT,
            ema_long=Config.EMA_LONG,
            macd_signal=Config.MACD_SIGNAL
        )
        
        # Initialize dynamic leverage if enabled
        self.dynamic_leverage = None
        current_leverage = Config.LEVERAGE
        if Config.ENABLE_DYNAMIC_LEVERAGE and ADVANCED_MODULES_AVAILABLE:
            try:
                self.dynamic_leverage = DynamicLeverage(
                    base_leverage=Config.LEVERAGE,
                    min_leverage=Config.MIN_LEVERAGE,
                    max_leverage=Config.MAX_LEVERAGE
                )
                logger.info("Dynamic leverage enabled")
            except Exception as e:
                logger.warning(f"Could not enable dynamic leverage: {e}")
        
        # Initialize funding strategy if enabled
        funding_strategy = None
        if Config.USE_FUNDING_STRATEGY:
            funding_strategy = FundingStrategy(
                min_balance_reserve_percent=Config.MIN_BALANCE_RESERVE_PERCENT,
                base_position_size_percent=Config.BASE_POSITION_SIZE_PERCENT,
                max_position_size_percent=Config.MAX_POSITION_SIZE_PERCENT_NEW,
                min_position_size_percent=Config.MIN_POSITION_SIZE_PERCENT,
                min_position_value_usd=Config.MIN_POSITION_VALUE_USD
            )
            logger.info("Using intelligent funding strategy")
        else:
            logger.info("Using legacy position sizing")
        
        self.strategy = HedgeStrategy(
            leverage=current_leverage,
            stop_loss_percent=Config.STOP_LOSS_PERCENT,
            take_profit_percent=Config.TAKE_PROFIT_PERCENT,
            trailing_stop_percent=Config.TRAILING_STOP_PERCENT,
            max_position_size_percent=Config.MAX_POSITION_SIZE_PERCENT,
            funding_strategy=funding_strategy
        )
        
        # Store reference for direct access
        self.funding_strategy = funding_strategy
        
        # Initialize advanced features if available
        self.telegram = None
        self.ml_generator = None
        self.multi_pair = None
        self.diversifier = None
        self.dashboard = None
        
        if ADVANCED_MODULES_AVAILABLE:
            # Telegram notifications
            if Config._telegram_configured:
                try:
                    self.telegram = TelegramNotifier(
                        Config.TELEGRAM_BOT_TOKEN,
                        Config.TELEGRAM_CHAT_ID
                    )
                    logger.info("Telegram notifications enabled")
                except Exception as e:
                    logger.warning(f"Could not enable Telegram: {e}")
            
            # ML signals
            if Config.USE_ML_SIGNALS:
                try:
                    self.ml_generator = MLSignalGenerator()
                    logger.info("ML-based signal generation enabled")
                except Exception as e:
                    logger.warning(f"Could not enable ML signals: {e}")
            
            # Multi-pair manager
            if Config._is_multi_pair:
                try:
                    self.multi_pair = MultiPairManager(Config.TRADING_PAIRS)
                    self.diversifier = PortfolioDiversifier()
                    logger.info(f"Multi-pair trading enabled for {len(Config.TRADING_PAIRS)} pairs")
                except Exception as e:
                    logger.warning(f"Could not enable multi-pair: {e}")
            
            # Web dashboard
            if Config.ENABLE_WEB_DASHBOARD:
                try:
                    self.dashboard = WebDashboard(self)
                    self.dashboard.run_async(port=Config.WEB_DASHBOARD_PORT)
                    logger.info(f"Web dashboard available at http://localhost:{Config.WEB_DASHBOARD_PORT}")
                except Exception as e:
                    logger.warning(f"Could not enable web dashboard: {e}")
        
        # Bot state
        self.running = False
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0
        self.initial_balance = Config.INITIAL_BALANCE
        self.current_balance = Config.INITIAL_BALANCE
        self.positions = {}  # Track positions for each pair (multi-pair mode)
        self.recent_losses = 0  # Track consecutive losses
        self.start_time = None  # Will be set when bot starts running
        
        # Create data directory
        os.makedirs('bot_data', exist_ok=True)
        
        logger.info(f"Bot initialized with {Config.LEVERAGE}x base leverage")
        logger.info(f"Initial balance: ${self.initial_balance}")
        logger.info(f"Trading {'pairs' if Config._is_multi_pair else 'symbol'}: {', '.join(Config.TRADING_PAIRS)}")
        logger.info(f"Using {'TESTNET' if Config.USE_TESTNET else 'PRODUCTION'} environment")
        
        # Send startup notification
        if self.telegram:
            startup_msg = f"🚀 Bot Started\n"
            startup_msg += f"Initial balance: ${self.initial_balance}\n"
            startup_msg += f"Trading: {', '.join(Config.TRADING_PAIRS)}\n"
            startup_msg += f"Features:\n{Config.get_feature_summary()}"
            self.telegram.notify_startup(startup_msg)
    
    def get_account_balance(self) -> float:
        """Get current account balance"""
        try:
            account = self.client.get_account_overview('USDT')
            available_balance = float(account.get('availableBalance', 0))
            logger.info(f"Available balance: ${available_balance:.2f}")
            return available_balance
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return self.current_balance
    
    def get_current_position(self, symbol: str = None) -> Optional[Dict]:
        """Get current position information
        
        Args:
            symbol: Trading symbol (uses Config.SYMBOL if not provided for single-pair mode)
        """
        if symbol is None:
            symbol = Config.SYMBOL if not Config._is_multi_pair else Config.TRADING_PAIRS[0]
        
        try:
            position = self.client.get_position(symbol)
            if position and position.get('currentQty') != 0:
                logger.info(f"{symbol} position: {position.get('currentQty')} contracts")
                logger.info(f"{symbol} unrealized PnL: ${position.get('unrealisedPnl', 0)}")
                return position
            return None
        except Exception as e:
            logger.error(f"Error getting position for {symbol}: {e}")
            return None
    
    def get_market_data(self, symbol: str = None) -> Dict:
        """Get current market data and indicators
        
        Args:
            symbol: Trading symbol (uses Config.SYMBOL if not provided for single-pair mode)
        """
        if symbol is None:
            symbol = Config.SYMBOL if not Config._is_multi_pair else Config.TRADING_PAIRS[0]
        
        try:
            # Get ticker for current price
            ticker = self.client.get_ticker(symbol)
            current_price = float(ticker.get('price', 0))
            
            if current_price <= 0:
                logger.error(f"Invalid price received for {symbol}: {current_price}")
                return None
            
            # Get kline data for analysis (5 minute candles, last 8 hours)
            klines = self.client.get_klines(
                symbol=symbol,
                granularity=5,  # 5-minute candles
                from_time=int(time.time() - 8 * 60 * 60) * 1000,  # Last 8 hours
                to_time=int(time.time()) * 1000
            )
            
            if not klines or len(klines) < 10:
                logger.warning(f"Insufficient kline data for {symbol}: {len(klines) if klines else 0} candles")
                return None
            
            logger.info(f"{symbol} price: ${current_price:.6f}")
            logger.info(f"Retrieved {len(klines)} candles for analysis")
            
            # Update price history for diversification (if available)
            if self.diversifier:
                self.diversifier.update_price_history(symbol, current_price)
            
            return {
                'price': current_price,
                'klines': klines,
                'timestamp': datetime.now(),
                'symbol': symbol
            }
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}", exc_info=True)
            return None
    
    def analyze_market(self, market_data: Dict) -> Dict:
        """Analyze market and generate trading signals"""
        if not market_data or not market_data.get('klines'):
            return {
                'action': 'hold',
                'strength': 0,
                'indicators': {},
                'reason': 'No market data available'
            }
        
        # Get traditional signal
        traditional_signal = self.analyzer.generate_signal(
            market_data['klines'],
            market_data['price'],
            Config.RSI_OVERSOLD,
            Config.RSI_OVERBOUGHT
        )
        
        # Get ML signal if enabled
        if self.ml_generator:
            try:
                ml_signal = self.ml_generator.generate_ml_signal(
                    market_data['klines'],
                    market_data['price']
                )
                
                # Combine signals (weighted average)
                combined_strength = int(0.5 * traditional_signal['strength'] + 
                                       0.5 * ml_signal['strength'])
                
                # Action is determined by consensus
                if traditional_signal['action'] == ml_signal['action']:
                    action = traditional_signal['action']
                    confidence_boost = 10
                else:
                    # If they disagree, use the stronger signal
                    if traditional_signal['strength'] > ml_signal['strength']:
                        action = traditional_signal['action']
                    else:
                        action = ml_signal['action']
                    confidence_boost = -10
                
                combined_strength = max(0, min(100, combined_strength + confidence_boost))
                
                signal = {
                    'action': action,
                    'strength': combined_strength,
                    'indicators': {**traditional_signal['indicators'], **ml_signal['indicators']},
                    'reason': f"Traditional: {traditional_signal['reason']} | ML: {ml_signal['reason']}"
                }
                
                # Notify strong ML signals
                if self.telegram and ml_signal['strength'] >= 70:
                    self.telegram.notify_signal(ml_signal['action'], ml_signal['strength'], ml_signal['reason'])
            except Exception as e:
                logger.warning(f"ML signal generation failed: {e}, using traditional signal")
                signal = traditional_signal
        else:
            signal = traditional_signal
        
        logger.info(f"Signal: {signal['action'].upper()} | Strength: {signal['strength']} | Reason: {signal['reason']}")
        
        return signal
    
    def calculate_volatility(self, klines: list) -> float:
        """Calculate market volatility from klines
        
        Args:
            klines: List of kline data
            
        Returns:
            Volatility as a decimal (e.g., 0.03 for 3%)
        """
        if not klines or len(klines) < 2:
            return 0.03  # Default 3%
        
        # Calculate returns from close prices
        closes = [float(k[4]) for k in klines]  # Index 4 is close price
        returns = []
        for i in range(1, len(closes)):
            ret = (closes[i] - closes[i-1]) / closes[i-1]
            returns.append(ret)
        
        # Calculate standard deviation of returns
        if not returns:
            return 0.03
        
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        volatility = variance ** 0.5
        
        return volatility
    
    def calculate_win_rate(self) -> float:
        """Calculate current win rate percentage
        
        Returns:
            Win rate as a percentage (0-100)
        """
        total_completed_trades = self.winning_trades + self.losing_trades
        if total_completed_trades == 0:
            return 50.0  # Default 50% if no trades yet
        return (self.winning_trades / total_completed_trades) * 100
    
    def execute_trade(self, symbol: str, action: str, side: str, size: int, reason: str, market_data: Optional[Dict] = None) -> bool:
        """Execute a trade
        
        Args:
            symbol: Trading symbol
            action: Trade action (open, close, hedge)
            side: Trade side (buy/sell)
            size: Position size in contracts
            reason: Reason for the trade
            market_data: Optional pre-fetched market data to avoid redundant API calls
        """
        try:
            # Validate inputs
            if size <= 0:
                logger.error(f"Invalid trade size: {size}")
                return False
            
            if side not in ['buy', 'sell']:
                logger.error(f"Invalid trade side: {side}")
                return False
            
            logger.info(f"Executing {action} on {symbol}: {side} {size} contracts - {reason}")
            
            # Adjust leverage if dynamic leverage is enabled
            if self.dynamic_leverage:
                try:
                    balance = self.get_account_balance()
                    # Reuse market_data if provided, otherwise fetch
                    if not market_data:
                        market_data = self.get_market_data(symbol)
                    if market_data:
                        signal = self.analyze_market(market_data)
                        position_value = size * market_data['price'] / self.strategy.leverage
                        win_rate = self.calculate_win_rate()
                        
                        adjusted_leverage = self.dynamic_leverage.adjust_leverage(
                            market_data['klines'],
                            signal,
                            balance,
                            position_value,
                            win_rate,
                            self.recent_losses
                        )
                        
                        # Update strategy with new leverage
                        self.strategy.leverage = adjusted_leverage
                        logger.info(f"Dynamic leverage adjusted to {adjusted_leverage}x")
                except Exception as e:
                    logger.warning(f"Dynamic leverage adjustment failed: {e}")
            
            order = self.client.place_order(
                symbol=symbol,
                side=side,
                leverage=self.strategy.leverage,
                size=size,
                order_type='market'
            )
            
            logger.info(f"Order executed successfully: {order.get('orderId')}")
            self.total_trades += 1
            
            # Save trade to history
            self.save_trade_history(symbol, action, side, size, reason, order)
            
            # Send Telegram notification
            if self.telegram:
                try:
                    # Reuse market_data if available to avoid another API call
                    if not market_data:
                        market_data = self.get_market_data(symbol)
                    price = market_data['price'] if market_data else 0
                    self.telegram.notify_trade(action, side, size, price, reason)
                except Exception as e:
                    logger.warning(f"Telegram notification failed: {e}")
            
            return True
            
        except ValueError as e:
            logger.error(f"Validation error executing trade: {e}")
            return False
        except Exception as e:
            logger.error(f"Error executing trade on {symbol}: {e}", exc_info=True)
            if self.telegram:
                try:
                    self.telegram.notify_error(f"Trade execution failed for {symbol}: {str(e)}")
                except Exception as telegram_error:
                    logger.warning(f"Failed to send Telegram error notification: {telegram_error}")
            return False
    
    def save_trade_history(self, symbol: str, action: str, side: str, size: int, reason: str, order: Dict):
        """Save trade to history file"""
        try:
            trade_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'action': action,
                'side': side,
                'size': size,
                'reason': reason,
                'order_id': order.get('orderId', 'N/A'),
                'balance': self.current_balance,
                'leverage': self.strategy.leverage
            }
            
            with open('bot_data/trade_history.jsonl', 'a') as f:
                f.write(json.dumps(trade_data) + '\n')
                
        except Exception as e:
            logger.error(f"Error saving trade history: {e}")
    
    def update_statistics(self, position: Optional[Dict] = None):
        """Update bot statistics"""
        # Track realized PnL from closed positions
        if position:
            realized_pnl = float(position.get('realisedPnl', 0))
            if realized_pnl != 0:
                self.total_profit += realized_pnl
                
                if realized_pnl > 0:
                    self.winning_trades += 1
                else:
                    self.losing_trades += 1
        
        # Update current balance
        self.current_balance = self.get_account_balance()
        
        # Calculate performance
        profit_percent = ((self.current_balance - self.initial_balance) / self.initial_balance) * 100
        win_rate = self.calculate_win_rate()
        
        # Get portfolio metrics if multi-pair is enabled
        if self.diversifier and self.positions:
            position_values = {}
            for symbol, pos in self.positions.items():
                if pos:
                    position_values[symbol] = abs(pos.get('currentQty', 0)) * pos.get('avgEntryPrice', 0)
            
            portfolio_metrics = self.diversifier.get_portfolio_metrics(position_values)
        else:
            portfolio_metrics = {'diversification_score': 0, 'num_positions': 0}
        
        logger.info(f"=== Bot Statistics ===")
        logger.info(f"Total trades: {self.total_trades}")
        logger.info(f"Winning trades: {self.winning_trades}")
        logger.info(f"Losing trades: {self.losing_trades}")
        logger.info(f"Win rate: {win_rate:.2f}%")
        logger.info(f"Total profit: ${self.total_profit:.2f}")
        logger.info(f"Current balance: ${self.current_balance:.2f}")
        logger.info(f"Profit: {profit_percent:.2f}%")
        if self.diversifier:
            logger.info(f"Portfolio diversification: {portfolio_metrics.get('diversification_score', 0):.2f}")
            logger.info(f"Active positions: {portfolio_metrics.get('num_positions', 0)}")
        logger.info(f"======================")
        
        # Send periodic P&L updates via Telegram
        if self.telegram and self.total_trades > 0 and self.total_trades % 10 == 0:
            try:
                self.telegram.notify_profit_loss(self.total_profit, self.current_balance, profit_percent)
            except Exception as e:
                logger.warning(f"Telegram P&L notification failed: {e}")
    
    def run_cycle(self):
        """Run one trading cycle - supports both single and multi-pair trading"""
        try:
            logger.info("=== Starting trading cycle ===")
            
            # Get account balance (cached for this cycle)
            balance = self.get_account_balance()
            cycle_start_time = time.time()
            
            # Determine trading pairs to process
            trading_symbols = Config.TRADING_PAIRS if Config._is_multi_pair else [Config.SYMBOL]
            
            # Get allocations if multi-pair manager is available
            allocations = {}
            if self.multi_pair and Config._is_multi_pair:
                try:
                    allocations = self.multi_pair.allocate_balance(balance, Config.ALLOCATION_STRATEGY)
                except Exception as e:
                    logger.warning(f"Multi-pair allocation failed: {e}, using equal split")
                    split_balance = balance / len(trading_symbols)
                    allocations = {symbol: split_balance for symbol in trading_symbols}
            else:
                # Single pair or no multi-pair support - use full balance
                allocations = {trading_symbols[0]: balance}
            
            # Process each trading pair
            for symbol in trading_symbols:
                if Config._is_multi_pair:
                    logger.info(f"\n--- Processing {symbol} ---")
                
                # Get current position
                position = self.get_current_position(symbol)
                if Config._is_multi_pair:
                    self.positions[symbol] = position
                
                # Get market data
                market_data = self.get_market_data(symbol)
                if not market_data:
                    logger.warning(f"Failed to get market data for {symbol}, skipping")
                    continue
                
                # Analyze market
                signal = self.analyze_market(market_data)
                
                # Update multi-pair state if available
                if self.multi_pair:
                    try:
                        self.multi_pair.update_pair_state(symbol, position, signal)
                        
                        # Check if we should trade this pair
                        if not self.multi_pair.should_trade_pair(symbol, signal):
                            logger.info(f"Skipping {symbol} - conditions not met")
                            continue
                    except Exception as e:
                        logger.warning(f"Multi-pair state update failed: {e}")
                
                # Check diversification before opening new position (multi-pair only)
                if Config._is_multi_pair and not position and self.diversifier:
                    try:
                        active_positions = [s for s in trading_symbols if self.positions.get(s)]
                        is_diversified, reason = self.diversifier.check_diversification(symbol, active_positions)
                        if not is_diversified:
                            logger.info(f"Skipping {symbol} - {reason}")
                            continue
                    except Exception as e:
                        logger.warning(f"Diversification check failed: {e}")
                
                # Get allocated balance for this pair
                # Re-fetch from multi_pair manager to get any updated allocations
                if self.multi_pair:
                    pair_balance = self.multi_pair.get_pair_allocation(symbol)
                else:
                    pair_balance = allocations.get(symbol, balance)
                
                # Get strategy suggestion
                suggestion = self.strategy.suggest_action(signal, position, pair_balance)
                
                logger.info(f"Strategy suggestion: {suggestion['action']} - {suggestion['reason']}")
                
                # Execute action based on suggestion
                if suggestion['action'] == 'open' and pair_balance > 0:
                    # Calculate volatility and win rate for intelligent sizing
                    volatility = self.calculate_volatility(market_data['klines'])
                    win_rate = self.calculate_win_rate()
                    
                    # Calculate total value of existing positions
                    if Config._is_multi_pair:
                        existing_positions_value = sum(
                            abs(self.positions.get(s, {}).get('currentQty', 0)) * 
                            self.positions.get(s, {}).get('avgEntryPrice', 1)
                            for s in trading_symbols if self.positions.get(s)
                        )
                    else:
                        existing_positions_value = 0.0
                    
                    # Calculate position size
                    size = self.strategy.calculate_position_size(
                        available_balance=pair_balance,
                        current_price=market_data['price'],
                        volatility=volatility,
                        win_rate=win_rate,
                        recent_losses=self.recent_losses,
                        signal_strength=signal['strength'],
                        existing_positions_value=existing_positions_value
                    )
                    
                    if size > 0:
                        # Check if trade should be allowed
                        if self.funding_strategy:
                            position_value = size * market_data['price'] / self.strategy.leverage
                            should_allow, reason = self.funding_strategy.should_allow_trade(
                                balance, position_value, self.recent_losses
                            )
                            if not should_allow:
                                logger.warning(f"Trade blocked for {symbol}: {reason}")
                                continue
                        
                        success = self.execute_trade(symbol, 'open', suggestion['side'], size, suggestion['reason'], market_data)
                        if success:
                            self.strategy.reset_tracking()
                            self.recent_losses = 0
                    else:
                        logger.info(f"Position size is 0 for {symbol} - insufficient balance or position value below minimum")
                        
                elif suggestion['action'] == 'close':
                    if position:
                        size = abs(position.get('currentQty', 0))
                        if size > 0:
                            pnl = float(position.get('unrealisedPnl', 0))
                            success = self.execute_trade(symbol, 'close', suggestion['side'], size, suggestion['reason'], market_data)
                            if success:
                                self.strategy.reset_tracking()
                                
                                # Update trade statistics
                                if pnl > 0:
                                    self.winning_trades += 1
                                    self.recent_losses = 0
                                else:
                                    self.losing_trades += 1
                                    self.recent_losses += 1
                                
                                self.total_profit += pnl
                                
                                # Record in multi-pair manager if available
                                if self.multi_pair:
                                    try:
                                        self.multi_pair.record_trade_result(symbol, pnl)
                                    except Exception as e:
                                        logger.warning(f"Failed to record trade result: {e}")
                            
                elif suggestion['action'] == 'hedge':
                    if position:
                        hedge_size = self.strategy.calculate_hedge_size(position.get('currentQty', 0))
                        if hedge_size > 0:
                            self.execute_trade(symbol, 'hedge', suggestion['side'], hedge_size, suggestion['reason'], market_data)
            
            # Update statistics
            if Config._is_multi_pair:
                self.update_statistics()
            else:
                position = self.get_current_position(Config.SYMBOL)
                self.update_statistics(position)
            
            # Log pair rankings for multi-pair trading
            if self.multi_pair and (Config.ALLOCATION_STRATEGY == 'best' or self.total_trades % 5 == 0):
                try:
                    rankings = self.multi_pair.get_pair_rankings()
                    if rankings:
                        logger.info("\n=== Trading Pair Performance Rankings ===")
                        for i, rank in enumerate(rankings, 1):
                            logger.info(f"{i}. {rank['symbol']}: "
                                      f"Win Rate {rank['win_rate']:.1f}%, "
                                      f"Trades {rank['total_trades']}, "
                                      f"Score {rank['score']:.3f}")
                        logger.info("=" * 45)
                except Exception as e:
                    logger.warning(f"Failed to get pair rankings: {e}")
            
            # Log cycle performance metrics
            cycle_duration = time.time() - cycle_start_time
            logger.info(f"Cycle completed in {cycle_duration:.2f} seconds")
            
            logger.info("=== Trading cycle complete ===\n")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)
            if self.telegram:
                try:
                    self.telegram.notify_error(f"Trading cycle error: {str(e)}")
                except Exception as telegram_error:
                    logger.warning(f"Failed to send Telegram error notification: {telegram_error}")
    
    def run(self, interval: int = 60):
        """Run the bot continuously
        
        Args:
            interval: Time in seconds between trading cycles (default: 60)
        """
        logger.info(f"Starting bot with {interval}s interval...")
        self.running = True
        self.start_time = datetime.now()
        
        try:
            while self.running:
                self.run_cycle()
                
                logger.info(f"Waiting {interval} seconds until next cycle...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            self.running = False
        finally:
            # Send shutdown notification
            if self.telegram:
                try:
                    win_rate = self.calculate_win_rate()
                    final_stats = f"📊 Bot Shutdown\n"
                    final_stats += f"Total trades: {self.total_trades}\n"
                    final_stats += f"Win rate: {win_rate:.1f}%\n"
                    final_stats += f"Final balance: ${self.current_balance:.2f}\n"
                    final_stats += f"Total profit: ${self.total_profit:.2f}"
                    self.telegram.notify_shutdown(final_stats)
                except Exception as e:
                    logger.warning(f"Final Telegram notification failed: {e}")
            
            # Cleanup resources
            try:
                if hasattr(self, 'client') and self.client:
                    self.client.close()
            except Exception as e:
                logger.warning(f"Error closing client connection: {e}")
            
            logger.info("Bot shutdown complete")
    
    def stop(self):
        """Stop the bot"""
        logger.info("Stopping bot...")
        self.running = False
        
        # Cleanup resources
        try:
            if hasattr(self, 'client') and self.client:
                self.client.close()
        except Exception as e:
            logger.warning(f"Error closing client connection: {e}")


def main():
    """Main entry point"""
    try:
        bot = XRPHedgeBot()
        
        # Run with 60 second interval between cycles
        # For more aggressive trading, use shorter intervals (30s, 45s)
        bot.run(interval=60)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)


if __name__ == '__main__':
    main()
