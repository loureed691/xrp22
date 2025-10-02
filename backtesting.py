"""
Backtesting Framework
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json

from technical_analysis import TechnicalAnalyzer
from hedge_strategy import HedgeStrategy

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Backtest trading strategies on historical data"""
    
    def __init__(self, initial_balance: float = 100.0, leverage: int = 11,
                 stop_loss_percent: float = 5.0, take_profit_percent: float = 8.0,
                 trailing_stop_percent: float = 3.0, max_position_size_percent: float = 80.0):
        """Initialize backtest engine
        
        Args:
            initial_balance: Starting balance for backtest
            leverage: Leverage multiplier
            stop_loss_percent: Stop loss percentage
            take_profit_percent: Take profit percentage
            trailing_stop_percent: Trailing stop percentage
            max_position_size_percent: Maximum position size as percentage of balance
        """
        self.initial_balance = initial_balance
        self.leverage = leverage
        
        # Initialize strategy and analyzer
        self.analyzer = TechnicalAnalyzer(
            rsi_period=14,
            ema_short=12,
            ema_long=26,
            macd_signal=9
        )
        
        self.strategy = HedgeStrategy(
            leverage=leverage,
            stop_loss_percent=stop_loss_percent,
            take_profit_percent=take_profit_percent,
            trailing_stop_percent=trailing_stop_percent,
            max_position_size_percent=max_position_size_percent
        )
        
        # Results tracking
        self.trades = []
        self.balance_history = []
        self.positions = []
        
    def load_historical_data(self, data: List[Dict]) -> pd.DataFrame:
        """Load and prepare historical data
        
        Args:
            data: List of OHLCV dictionaries
            
        Returns:
            DataFrame with processed data
        """
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        return df
    
    def simulate_trade(self, action: str, side: str, size: int, price: float, 
                      timestamp: datetime, balance: float) -> Tuple[float, Dict]:
        """Simulate a trade execution
        
        Args:
            action: Trade action (open, close, hedge)
            side: Trade side (buy, sell)
            size: Position size
            price: Execution price
            timestamp: Trade timestamp
            balance: Current balance
            
        Returns:
            Tuple of (new_balance, trade_record)
        """
        # Calculate costs and P&L
        position_value = size * price / self.leverage
        
        trade_record = {
            'timestamp': timestamp,
            'action': action,
            'side': side,
            'size': size,
            'price': price,
            'position_value': position_value,
            'balance_before': balance
        }
        
        # Simulate opening position
        if action == 'open':
            new_balance = balance - position_value
            trade_record['cost'] = position_value
            trade_record['pnl'] = 0
        
        # Simulate closing position
        elif action == 'close':
            # Calculate P&L based on previous position
            if self.positions:
                last_pos = self.positions[-1]
                if side == 'sell' and last_pos['side'] == 'buy':
                    # Closing long position
                    pnl = (price - last_pos['price']) * size * self.leverage
                elif side == 'buy' and last_pos['side'] == 'sell':
                    # Closing short position
                    pnl = (last_pos['price'] - price) * size * self.leverage
                else:
                    pnl = 0
                
                new_balance = balance + pnl
                trade_record['pnl'] = pnl
                trade_record['cost'] = 0
            else:
                new_balance = balance
                trade_record['pnl'] = 0
                trade_record['cost'] = 0
        
        else:  # hedge
            new_balance = balance - position_value
            trade_record['cost'] = position_value
            trade_record['pnl'] = 0
        
        trade_record['balance_after'] = new_balance
        
        return new_balance, trade_record
    
    def run_backtest(self, historical_klines: List[List], 
                    rsi_oversold: float = 30, rsi_overbought: float = 70) -> Dict:
        """Run backtest on historical data
        
        Args:
            historical_klines: List of kline data (timestamp, open, high, low, close, volume)
            rsi_oversold: RSI oversold threshold
            rsi_overbought: RSI overbought threshold
            
        Returns:
            Dict with backtest results
        """
        logger.info("Starting backtest...")
        
        balance = self.initial_balance
        current_position = None
        self.trades = []
        self.balance_history = []
        self.positions = []
        
        # Need at least 30 candles for indicators
        if len(historical_klines) < 30:
            logger.error("Insufficient data for backtest (need at least 30 candles)")
            return self._generate_results()
        
        # Iterate through each candle
        for i in range(30, len(historical_klines)):
            # Get data up to current point
            current_klines = historical_klines[:i+1]
            current_price = float(current_klines[-1][4])  # Close price
            timestamp = datetime.fromtimestamp(int(current_klines[-1][0]) / 1000)
            
            # Generate signal
            signal = self.analyzer.generate_signal(
                current_klines,
                current_price,
                rsi_oversold,
                rsi_overbought
            )
            
            # Get strategy suggestion
            suggestion = self.strategy.suggest_action(signal, current_position, balance)
            
            # Execute suggested action
            if suggestion['action'] == 'open' and balance > 0:
                size = self.strategy.calculate_position_size(balance, current_price)
                if size > 0:
                    balance, trade = self.simulate_trade(
                        'open', suggestion['side'], size, current_price, 
                        timestamp, balance
                    )
                    self.trades.append(trade)
                    current_position = {
                        'currentQty': size if suggestion['side'] == 'buy' else -size,
                        'avgEntryPrice': current_price,
                        'unrealisedPnl': 0
                    }
                    self.positions.append({
                        'side': suggestion['side'],
                        'price': current_price,
                        'size': size
                    })
            
            elif suggestion['action'] == 'close' and current_position:
                size = abs(current_position['currentQty'])
                balance, trade = self.simulate_trade(
                    'close', suggestion['side'], size, current_price,
                    timestamp, balance
                )
                self.trades.append(trade)
                current_position = None
            
            # Track balance
            self.balance_history.append({
                'timestamp': timestamp,
                'balance': balance
            })
        
        logger.info("Backtest complete")
        return self._generate_results()
    
    def _generate_results(self) -> Dict:
        """Generate backtest results summary
        
        Returns:
            Dict with backtest statistics
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'final_balance': self.initial_balance,
                'roi': 0,
                'max_drawdown': 0,
                'trades': []
            }
        
        # Calculate statistics
        total_trades = len([t for t in self.trades if t['action'] in ['open', 'close']])
        winning_trades = len([t for t in self.trades if t.get('pnl', 0) > 0])
        losing_trades = len([t for t in self.trades if t.get('pnl', 0) < 0])
        total_pnl = sum(t.get('pnl', 0) for t in self.trades)
        
        final_balance = self.balance_history[-1]['balance'] if self.balance_history else self.initial_balance
        roi = ((final_balance - self.initial_balance) / self.initial_balance) * 100
        
        # Calculate max drawdown
        max_balance = self.initial_balance
        max_drawdown = 0
        for record in self.balance_history:
            max_balance = max(max_balance, record['balance'])
            drawdown = ((max_balance - record['balance']) / max_balance) * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        win_rate = (winning_trades / max(1, winning_trades + losing_trades)) * 100
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'final_balance': final_balance,
            'roi': roi,
            'max_drawdown': max_drawdown,
            'trades': self.trades,
            'balance_history': self.balance_history
        }
    
    def save_results(self, filename: str):
        """Save backtest results to file
        
        Args:
            filename: Output filename
        """
        results = self._generate_results()
        
        with open(filename, 'w') as f:
            json.dump({
                'initial_balance': self.initial_balance,
                'leverage': self.leverage,
                'results': {
                    'total_trades': results['total_trades'],
                    'winning_trades': results['winning_trades'],
                    'losing_trades': results['losing_trades'],
                    'win_rate': results['win_rate'],
                    'total_pnl': results['total_pnl'],
                    'final_balance': results['final_balance'],
                    'roi': results['roi'],
                    'max_drawdown': results['max_drawdown']
                },
                'trades': results['trades'],
                'balance_history': results['balance_history']
            }, f, indent=2, default=str)
        
        logger.info(f"Backtest results saved to {filename}")
