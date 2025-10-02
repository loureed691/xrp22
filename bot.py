"""
KuCoin XRP Futures Hedge Bot
Main bot orchestration and execution
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


class XRPHedgeBot:
    """Main XRP Futures Hedge Trading Bot"""
    
    def __init__(self):
        """Initialize the bot"""
        logger.info("Initializing XRP Hedge Bot...")
        
        # Validate configuration
        Config.validate()
        
        # Initialize components
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
        
        self.strategy = HedgeStrategy(
            leverage=Config.LEVERAGE,
            stop_loss_percent=Config.STOP_LOSS_PERCENT,
            take_profit_percent=Config.TAKE_PROFIT_PERCENT,
            trailing_stop_percent=Config.TRAILING_STOP_PERCENT,
            max_position_size_percent=Config.MAX_POSITION_SIZE_PERCENT
        )
        
        # Bot state
        self.running = False
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0.0
        self.initial_balance = Config.INITIAL_BALANCE
        self.current_balance = Config.INITIAL_BALANCE
        
        # Create data directory
        os.makedirs('bot_data', exist_ok=True)
        
        logger.info(f"Bot initialized with {Config.LEVERAGE}x leverage")
        logger.info(f"Initial balance: ${self.initial_balance}")
        logger.info(f"Trading symbol: {Config.SYMBOL}")
        logger.info(f"Using {'TESTNET' if Config.USE_TESTNET else 'PRODUCTION'} environment")
    
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
    
    def get_current_position(self) -> Optional[Dict]:
        """Get current position information"""
        try:
            position = self.client.get_position(Config.SYMBOL)
            if position and position.get('currentQty') != 0:
                logger.info(f"Current position: {position.get('currentQty')} contracts")
                logger.info(f"Unrealized PnL: ${position.get('unrealisedPnl', 0)}")
                return position
            return None
        except Exception as e:
            logger.error(f"Error getting position: {e}")
            return None
    
    def get_market_data(self) -> Dict:
        """Get current market data and indicators"""
        try:
            # Get ticker for current price
            ticker = self.client.get_ticker(Config.SYMBOL)
            current_price = float(ticker.get('price', 0))
            
            # Get kline data for analysis (1 minute candles, last 100)
            # granularity in minutes: 1, 5, 15, 30, 60, 240, 480, 1440
            klines = self.client.get_klines(
                symbol=Config.SYMBOL,
                granularity=5,  # 5-minute candles
                from_time=int(time.time() - 8 * 60 * 60) * 1000,  # Last 8 hours
                to_time=int(time.time()) * 1000
            )
            
            logger.info(f"Current price: ${current_price:.6f}")
            logger.info(f"Retrieved {len(klines)} candles for analysis")
            
            return {
                'price': current_price,
                'klines': klines,
                'timestamp': datetime.now()
            }
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
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
        
        signal = self.analyzer.generate_signal(
            market_data['klines'],
            market_data['price'],
            Config.RSI_OVERSOLD,
            Config.RSI_OVERBOUGHT
        )
        
        logger.info(f"Signal: {signal['action'].upper()} | Strength: {signal['strength']} | Reason: {signal['reason']}")
        
        return signal
    
    def execute_trade(self, action: str, side: str, size: int, reason: str) -> bool:
        """Execute a trade"""
        try:
            logger.info(f"Executing {action}: {side} {size} contracts - {reason}")
            
            order = self.client.place_order(
                symbol=Config.SYMBOL,
                side=side,
                leverage=Config.LEVERAGE,
                size=size,
                order_type='market'
            )
            
            logger.info(f"Order executed successfully: {order.get('orderId')}")
            self.total_trades += 1
            
            # Save trade to history
            self.save_trade_history(action, side, size, reason, order)
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False
    
    def save_trade_history(self, action: str, side: str, size: int, reason: str, order: Dict):
        """Save trade to history file"""
        try:
            trade_data = {
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'side': side,
                'size': size,
                'reason': reason,
                'order_id': order.get('orderId', 'N/A'),
                'balance': self.current_balance
            }
            
            with open('bot_data/trade_history.jsonl', 'a') as f:
                f.write(json.dumps(trade_data) + '\n')
                
        except Exception as e:
            logger.error(f"Error saving trade history: {e}")
    
    def update_statistics(self, position: Optional[Dict]):
        """Update bot statistics"""
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
        win_rate = (self.winning_trades / max(1, self.winning_trades + self.losing_trades)) * 100
        
        logger.info(f"=== Bot Statistics ===")
        logger.info(f"Total trades: {self.total_trades}")
        logger.info(f"Winning trades: {self.winning_trades}")
        logger.info(f"Losing trades: {self.losing_trades}")
        logger.info(f"Win rate: {win_rate:.2f}%")
        logger.info(f"Total profit: ${self.total_profit:.2f}")
        logger.info(f"Current balance: ${self.current_balance:.2f}")
        logger.info(f"Profit: {profit_percent:.2f}%")
        logger.info(f"======================")
    
    def run_cycle(self):
        """Run one trading cycle"""
        try:
            logger.info("=== Starting trading cycle ===")
            
            # Get account balance
            balance = self.get_account_balance()
            
            # Get current position
            position = self.get_current_position()
            
            # Get market data
            market_data = self.get_market_data()
            if not market_data:
                logger.warning("Failed to get market data, skipping cycle")
                return
            
            # Analyze market
            signal = self.analyze_market(market_data)
            
            # Get strategy suggestion
            suggestion = self.strategy.suggest_action(signal, position, balance)
            
            logger.info(f"Strategy suggestion: {suggestion['action']} - {suggestion['reason']} (Confidence: {suggestion['confidence']})")
            
            # Execute action based on suggestion
            if suggestion['action'] == 'open':
                size = self.strategy.calculate_position_size(balance, market_data['price'])
                if size > 0:
                    self.execute_trade('open', suggestion['side'], size, suggestion['reason'])
                    self.strategy.reset_tracking()
                    
            elif suggestion['action'] == 'close':
                if position:
                    size = abs(position.get('currentQty', 0))
                    if size > 0:
                        self.execute_trade('close', suggestion['side'], size, suggestion['reason'])
                        self.strategy.reset_tracking()
                        
            elif suggestion['action'] == 'hedge':
                hedge_size = self.strategy.calculate_hedge_size(position.get('currentQty', 0))
                if hedge_size > 0:
                    self.execute_trade('hedge', suggestion['side'], hedge_size, suggestion['reason'])
            
            # Update statistics
            self.update_statistics(position)
            
            logger.info("=== Trading cycle complete ===\n")
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)
    
    def run(self, interval: int = 60):
        """Run the bot continuously
        
        Args:
            interval: Time in seconds between trading cycles (default: 60)
        """
        logger.info(f"Starting bot with {interval}s interval...")
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
            logger.info("Bot shutdown complete")
    
    def stop(self):
        """Stop the bot"""
        logger.info("Stopping bot...")
        self.running = False


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
