"""
Enhanced XRP Futures Bot with Advanced Features
Integrates all roadmap features: web dashboard, ML signals, multi-pair, etc.
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

# Import new modules
from web_dashboard import WebDashboard
from telegram_notifier import TelegramNotifier
from ml_signals import MLSignalGenerator
from multi_pair import MultiPairManager
from dynamic_leverage import DynamicLeverage
from portfolio_diversification import PortfolioDiversifier
from funding_strategy import FundingStrategy

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedXRPBot:
    """Enhanced XRP Futures Hedge Trading Bot with advanced features"""
    
    def __init__(self):
        """Initialize the enhanced bot"""
        logger.info("Initializing Enhanced XRP Hedge Bot...")
        
        # Validate configuration
        Config.validate()
        
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
        
        # Initialize strategy with dynamic leverage if enabled
        if Config.ENABLE_DYNAMIC_LEVERAGE:
            self.dynamic_leverage = DynamicLeverage(
                base_leverage=Config.LEVERAGE,
                min_leverage=Config.MIN_LEVERAGE,
                max_leverage=Config.MAX_LEVERAGE
            )
            current_leverage = Config.LEVERAGE
        else:
            self.dynamic_leverage = None
            current_leverage = Config.LEVERAGE
        
        # Initialize funding strategy if enabled
        funding_strategy = None
        if Config.USE_FUNDING_STRATEGY:
            funding_strategy = FundingStrategy(
                min_balance_reserve_percent=Config.MIN_BALANCE_RESERVE_PERCENT,
                base_position_size_percent=Config.BASE_POSITION_SIZE_PERCENT,
                max_position_size_percent=Config.MAX_POSITION_SIZE_PERCENT_NEW,
                min_position_size_percent=Config.MIN_POSITION_SIZE_PERCENT
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
        
        # Initialize new features
        self.telegram = TelegramNotifier(
            Config.TELEGRAM_BOT_TOKEN,
            Config.TELEGRAM_CHAT_ID
        )
        
        if Config.USE_ML_SIGNALS:
            self.ml_generator = MLSignalGenerator()
            logger.info("ML-based signal generation enabled")
        else:
            self.ml_generator = None
        
        # Initialize multi-pair manager
        self.multi_pair = MultiPairManager(Config.TRADING_PAIRS)
        
        # Initialize portfolio diversifier
        self.diversifier = PortfolioDiversifier()
        
        # Initialize web dashboard if enabled
        self.dashboard = None
        if Config.ENABLE_WEB_DASHBOARD:
            self.dashboard = WebDashboard(self)
            self.dashboard.run_async(port=Config.WEB_DASHBOARD_PORT)
            logger.info(f"Web dashboard available at http://localhost:{Config.WEB_DASHBOARD_PORT}")
        
        # Bot state
        self.running = False
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0
        self.initial_balance = Config.INITIAL_BALANCE
        self.current_balance = Config.INITIAL_BALANCE
        self.positions = {}  # Track positions for each pair
        self.recent_losses = 0  # Track consecutive losses for risk management
        
        # Create data directory
        os.makedirs('bot_data', exist_ok=True)
        
        logger.info(f"Bot initialized with {Config.LEVERAGE}x base leverage")
        logger.info(f"Initial balance: ${self.initial_balance}")
        logger.info(f"Trading pairs: {', '.join(Config.TRADING_PAIRS)}")
        logger.info(f"Using {'TESTNET' if Config.USE_TESTNET else 'PRODUCTION'} environment")
        
        # Send startup notification
        startup_msg = f"Initial balance: ${self.initial_balance}\n"
        startup_msg += f"Trading pairs: {', '.join(Config.TRADING_PAIRS)}\n"
        startup_msg += f"ML signals: {'Enabled' if Config.USE_ML_SIGNALS else 'Disabled'}\n"
        startup_msg += f"Dynamic leverage: {'Enabled' if Config.ENABLE_DYNAMIC_LEVERAGE else 'Disabled'}"
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
    
    def get_current_position(self, symbol: str) -> Optional[Dict]:
        """Get current position information for a symbol"""
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
    
    def get_market_data(self, symbol: str) -> Dict:
        """Get current market data and indicators for a symbol"""
        try:
            ticker = self.client.get_ticker(symbol)
            current_price = float(ticker.get('price', 0))
            
            klines = self.client.get_klines(
                symbol=symbol,
                granularity=5,
                from_time=int(time.time() - 8 * 60 * 60) * 1000,
                to_time=int(time.time()) * 1000
            )
            
            logger.info(f"{symbol} price: ${current_price:.6f}")
            
            # Update price history for diversification
            self.diversifier.update_price_history(symbol, current_price)
            
            return {
                'price': current_price,
                'klines': klines,
                'timestamp': datetime.now(),
                'symbol': symbol
            }
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
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
            if ml_signal['strength'] >= 70:
                self.telegram.notify_signal(ml_signal['action'], ml_signal['strength'], ml_signal['reason'])
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
    
    def execute_trade(self, symbol: str, action: str, side: str, size: int, 
                     price: float, reason: str) -> bool:
        """Execute a trade"""
        try:
            logger.info(f"Executing {action} on {symbol}: {side} {size} contracts - {reason}")
            
            # Adjust leverage if dynamic leverage is enabled
            if self.dynamic_leverage:
                balance = self.get_account_balance()
                position_value = size * price / Config.LEVERAGE
                win_rate = (self.winning_trades / max(1, self.winning_trades + self.losing_trades)) * 100
                
                # Get market data for leverage adjustment
                market_data = self.get_market_data(symbol)
                if market_data:
                    signal = self.analyze_market(market_data)
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
            self.save_trade_history(symbol, action, side, size, price, reason, order)
            
            # Send Telegram notification
            self.telegram.notify_trade(action, side, size, price, reason)
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            self.telegram.notify_error(f"Trade execution failed: {str(e)}")
            return False
    
    def save_trade_history(self, symbol: str, action: str, side: str, size: int,
                          price: float, reason: str, order: Dict):
        """Save trade to history file"""
        try:
            trade_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'action': action,
                'side': side,
                'size': size,
                'price': price,
                'reason': reason,
                'order_id': order.get('orderId', 'N/A'),
                'balance': self.current_balance,
                'leverage': self.strategy.leverage
            }
            
            with open('bot_data/trade_history.jsonl', 'a') as f:
                f.write(json.dumps(trade_data) + '\n')
                
        except Exception as e:
            logger.error(f"Error saving trade history: {e}")
    
    def update_statistics(self):
        """Update bot statistics"""
        # Update balance
        self.current_balance = self.get_account_balance()
        
        # Calculate overall performance
        profit_percent = ((self.current_balance - self.initial_balance) / self.initial_balance) * 100
        win_rate = (self.winning_trades / max(1, self.winning_trades + self.losing_trades)) * 100
        
        # Get portfolio metrics
        position_values = {}
        for symbol in Config.TRADING_PAIRS:
            position = self.positions.get(symbol)
            if position:
                position_values[symbol] = abs(position.get('currentQty', 0)) * position.get('avgEntryPrice', 0)
        
        portfolio_metrics = self.diversifier.get_portfolio_metrics(position_values)
        
        logger.info(f"=== Bot Statistics ===")
        logger.info(f"Total trades: {self.total_trades}")
        logger.info(f"Winning trades: {self.winning_trades}")
        logger.info(f"Losing trades: {self.losing_trades}")
        logger.info(f"Win rate: {win_rate:.2f}%")
        logger.info(f"Total profit: ${self.total_profit:.2f}")
        logger.info(f"Current balance: ${self.current_balance:.2f}")
        logger.info(f"Profit: {profit_percent:.2f}%")
        logger.info(f"Portfolio diversification: {portfolio_metrics.get('diversification_score', 0):.2f}")
        logger.info(f"Active positions: {portfolio_metrics.get('num_positions', 0)}")
        logger.info(f"======================")
        
        # Send periodic P&L updates
        if self.total_trades > 0 and self.total_trades % 10 == 0:
            self.telegram.notify_profit_loss(self.total_profit, self.current_balance, profit_percent)
    
    def run_cycle(self):
        """Run one trading cycle"""
        try:
            logger.info("=== Starting trading cycle ===")
            
            # Get account balance
            balance = self.get_account_balance()
            
            # Allocate balance across trading pairs
            allocations = self.multi_pair.allocate_balance(
                balance,
                Config.ALLOCATION_STRATEGY
            )
            
            # Process each trading pair
            for symbol in Config.TRADING_PAIRS:
                logger.info(f"\n--- Processing {symbol} ---")
                
                # Get current position
                position = self.get_current_position(symbol)
                self.positions[symbol] = position
                
                # Get market data
                market_data = self.get_market_data(symbol)
                if not market_data:
                    logger.warning(f"Failed to get market data for {symbol}, skipping")
                    continue
                
                # Analyze market
                signal = self.analyze_market(market_data)
                
                # Update multi-pair state
                self.multi_pair.update_pair_state(symbol, position, signal)
                
                # Check if we should trade this pair
                if not self.multi_pair.should_trade_pair(symbol, signal):
                    logger.info(f"Skipping {symbol} - conditions not met")
                    continue
                
                # Check diversification before opening new position
                if not position:
                    active_positions = self.multi_pair.get_active_pairs()
                    is_diversified, reason = self.diversifier.check_diversification(
                        symbol, active_positions
                    )
                    if not is_diversified:
                        logger.info(f"Skipping {symbol} - {reason}")
                        continue
                
                # Get allocated balance for this pair
                pair_balance = allocations.get(symbol, 0)
                
                # Get strategy suggestion
                suggestion = self.strategy.suggest_action(signal, position, pair_balance)
                
                logger.info(f"Strategy suggestion: {suggestion['action']} - {suggestion['reason']}")
                
                # Execute action based on suggestion
                if suggestion['action'] == 'open' and pair_balance > 0:
                    # Calculate volatility and win rate for intelligent sizing
                    volatility = self.calculate_volatility(market_data['klines'])
                    win_rate = self.calculate_win_rate()
                    
                    # Calculate total value of existing positions
                    existing_positions_value = sum(
                        abs(self.positions.get(s, {}).get('currentQty', 0)) * 
                        self.positions.get(s, {}).get('avgEntryPrice', 1)
                        for s in Config.TRADING_PAIRS if self.positions.get(s)
                    )
                    
                    # Use funding strategy if available, otherwise use diversifier
                    if self.funding_strategy:
                        size = self.strategy.calculate_position_size(
                            available_balance=pair_balance,
                            current_price=market_data['price'],
                            volatility=volatility,
                            win_rate=win_rate,
                            recent_losses=self.recent_losses,
                            signal_strength=signal['strength'],
                            existing_positions_value=existing_positions_value
                        )
                        
                        # Check if trade should be allowed
                        position_value = size * market_data['price'] / self.strategy.leverage
                        should_allow, reason = self.funding_strategy.should_allow_trade(
                            balance, position_value, self.recent_losses
                        )
                        if not should_allow:
                            logger.warning(f"Trade blocked for {symbol}: {reason}")
                            continue
                    else:
                        # Original diversifier logic
                        existing_positions = {
                            s: abs(self.positions.get(s, {}).get('currentQty', 0)) * 
                               self.positions.get(s, {}).get('avgEntryPrice', 1)
                            for s in Config.TRADING_PAIRS if self.positions.get(s)
                        }
                        
                        optimal_value = self.diversifier.calculate_optimal_position_size(
                            symbol, pair_balance, existing_positions
                        )
                        
                        size = int(optimal_value / market_data['price'] * self.strategy.leverage)
                    
                    if size > 0:
                        success = self.execute_trade(
                            symbol, 'open', suggestion['side'], size,
                            market_data['price'], suggestion['reason']
                        )
                        if success:
                            self.strategy.reset_tracking()
                            self.recent_losses = 0
                        
                elif suggestion['action'] == 'close':
                    if position:
                        size = abs(position.get('currentQty', 0))
                        if size > 0:
                            pnl = float(position.get('unrealisedPnl', 0))
                            success = self.execute_trade(
                                symbol, 'close', suggestion['side'], size,
                                market_data['price'], suggestion['reason']
                            )
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
                                self.multi_pair.record_trade_result(symbol, pnl)
                            
                elif suggestion['action'] == 'hedge':
                    if position:
                        hedge_size = self.strategy.calculate_hedge_size(position.get('currentQty', 0))
                        if hedge_size > 0:
                            self.execute_trade(
                                symbol, 'hedge', suggestion['side'], hedge_size,
                                market_data['price'], suggestion['reason']
                            )
            
            # Update statistics
            self.update_statistics()
            
            # Check for rebalancing suggestions
            position_values = {}
            for symbol in Config.TRADING_PAIRS:
                position = self.positions.get(symbol)
                if position:
                    position_values[symbol] = abs(position.get('currentQty', 0)) * position.get('avgEntryPrice', 0)
            
            rebalance_suggestions = self.diversifier.suggest_rebalancing(position_values)
            if rebalance_suggestions:
                logger.info("Rebalancing suggestions:")
                for symbol, suggestion in rebalance_suggestions.items():
                    logger.info(f"  {symbol}: {suggestion}")
            
            # Log pair rankings when using best strategy or periodically
            if Config.ALLOCATION_STRATEGY == 'best' or self.total_trades % 5 == 0:
                rankings = self.multi_pair.get_pair_rankings()
                if rankings:
                    logger.info("\n=== Trading Pair Performance Rankings ===")
                    for i, rank in enumerate(rankings, 1):
                        logger.info(f"{i}. {rank['symbol']}: "
                                  f"Win Rate {rank['win_rate']:.1f}%, "
                                  f"Trades {rank['total_trades']}, "
                                  f"Score {rank['score']:.3f}")
                    logger.info("=" * 45)
            
            logger.info("=== Trading cycle complete ===\n")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)
            self.telegram.notify_error(f"Trading cycle error: {str(e)}")
    
    def run(self, interval: int = 60):
        """Run the bot continuously"""
        logger.info(f"Starting enhanced bot with {interval}s interval...")
        self.running = True
        
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
            final_stats = f"Total trades: {self.total_trades}\n"
            final_stats += f"Win rate: {(self.winning_trades / max(1, self.winning_trades + self.losing_trades)) * 100:.1f}%\n"
            final_stats += f"Final balance: ${self.current_balance:.2f}\n"
            final_stats += f"Total profit: ${self.total_profit:.2f}"
            self.telegram.notify_shutdown(final_stats)
            
            logger.info("Bot shutdown complete")
    
    def stop(self):
        """Stop the bot"""
        logger.info("Stopping bot...")
        self.running = False


def main():
    """Main entry point"""
    try:
        bot = EnhancedXRPBot()
        bot.run(interval=60)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)


if __name__ == '__main__':
    main()
