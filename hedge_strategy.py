"""
Hedge Trading Strategy Manager
"""
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class HedgeStrategy:
    """Manages hedge trading strategy with long and short positions"""
    
    def __init__(self, leverage: int, stop_loss_percent: float, 
                 take_profit_percent: float, trailing_stop_percent: float,
                 max_position_size_percent: float):
        self.leverage = leverage
        self.stop_loss_percent = stop_loss_percent
        self.take_profit_percent = take_profit_percent
        self.trailing_stop_percent = trailing_stop_percent
        self.max_position_size_percent = max_position_size_percent
        
        # Position tracking
        self.long_position = None
        self.short_position = None
        self.entry_price_long = None
        self.entry_price_short = None
        self.highest_price_long = None
        self.lowest_price_short = None
        
    def calculate_position_size(self, available_balance: float, current_price: float) -> int:
        """Calculate position size in contracts"""
        # Use a percentage of available balance
        position_value = available_balance * (self.max_position_size_percent / 100)
        
        # Apply leverage
        position_value_with_leverage = position_value * self.leverage
        
        # Calculate number of contracts (1 contract = $1 in XRP)
        # KuCoin uses multiplier, typically 1 contract = 1 XRP worth of value
        size = int(position_value_with_leverage / current_price)
        
        # Minimum size is 1
        return max(1, size)
    
    def should_open_long(self, signal: Dict, current_positions: Dict) -> Tuple[bool, str]:
        """Determine if we should open a long position"""
        if signal['action'] != 'buy':
            return False, "Signal is not buy"
        
        if signal['strength'] < 60:
            return False, f"Signal strength too low: {signal['strength']}"
        
        # Check if we already have a long position
        if current_positions and current_positions.get('currentQty', 0) > 0:
            return False, "Already have a long position"
        
        return True, "Conditions met for long entry"
    
    def should_open_short(self, signal: Dict, current_positions: Dict) -> Tuple[bool, str]:
        """Determine if we should open a short position"""
        if signal['action'] != 'sell':
            return False, "Signal is not sell"
        
        if signal['strength'] < 60:
            return False, f"Signal strength too low: {signal['strength']}"
        
        # Check if we already have a short position
        if current_positions and current_positions.get('currentQty', 0) < 0:
            return False, "Already have a short position"
        
        return True, "Conditions met for short entry"
    
    def should_close_long(self, current_price: float, entry_price: float, 
                         position_qty: int, unrealized_pnl: float) -> Tuple[bool, str]:
        """Determine if we should close a long position"""
        if position_qty <= 0:
            return False, "No long position to close"
        
        price_change_percent = ((current_price - entry_price) / entry_price) * 100
        
        # Stop loss check
        if price_change_percent <= -self.stop_loss_percent:
            return True, f"Stop loss triggered: {price_change_percent:.2f}%"
        
        # Take profit check
        if price_change_percent >= self.take_profit_percent:
            return True, f"Take profit triggered: {price_change_percent:.2f}%"
        
        # Trailing stop check
        if self.highest_price_long is None:
            self.highest_price_long = current_price
        else:
            self.highest_price_long = max(self.highest_price_long, current_price)
            
        trailing_percent = ((self.highest_price_long - current_price) / self.highest_price_long) * 100
        if trailing_percent >= self.trailing_stop_percent:
            return True, f"Trailing stop triggered: {trailing_percent:.2f}% from high"
        
        return False, "Holding long position"
    
    def should_close_short(self, current_price: float, entry_price: float, 
                          position_qty: int, unrealized_pnl: float) -> Tuple[bool, str]:
        """Determine if we should close a short position"""
        if position_qty >= 0:
            return False, "No short position to close"
        
        price_change_percent = ((entry_price - current_price) / entry_price) * 100
        
        # Stop loss check (price went up)
        if price_change_percent <= -self.stop_loss_percent:
            return True, f"Stop loss triggered: {-price_change_percent:.2f}%"
        
        # Take profit check (price went down)
        if price_change_percent >= self.take_profit_percent:
            return True, f"Take profit triggered: {price_change_percent:.2f}%"
        
        # Trailing stop check
        if self.lowest_price_short is None:
            self.lowest_price_short = current_price
        else:
            self.lowest_price_short = min(self.lowest_price_short, current_price)
            
        trailing_percent = ((current_price - self.lowest_price_short) / self.lowest_price_short) * 100
        if trailing_percent >= self.trailing_stop_percent:
            return True, f"Trailing stop triggered: {trailing_percent:.2f}% from low"
        
        return False, "Holding short position"
    
    def should_hedge(self, signal: Dict, current_position: Dict) -> Tuple[bool, str, str]:
        """Determine if we should open a hedge position
        
        Returns:
            (should_hedge, reason, hedge_side)
        """
        if not current_position:
            return False, "No position to hedge", None
        
        current_qty = current_position.get('currentQty', 0)
        unrealized_pnl_pcnt = current_position.get('unrealisedPnlPcnt', 0)
        
        # If we have a long position and it's losing
        if current_qty > 0 and unrealized_pnl_pcnt < -2:  # Losing more than 2%
            if signal['action'] == 'sell' and signal['strength'] >= 50:
                return True, "Hedging long position with short", "sell"
        
        # If we have a short position and it's losing
        if current_qty < 0 and unrealized_pnl_pcnt < -2:  # Losing more than 2%
            if signal['action'] == 'buy' and signal['strength'] >= 50:
                return True, "Hedging short position with long", "buy"
        
        return False, "No hedge needed", None
    
    def calculate_hedge_size(self, current_position_size: int) -> int:
        """Calculate hedge position size"""
        # Hedge with 50% of current position to partially offset risk
        hedge_size = abs(current_position_size) // 2
        return max(1, hedge_size)
    
    def reset_tracking(self):
        """Reset position tracking variables"""
        self.highest_price_long = None
        self.lowest_price_short = None
    
    def analyze_market_condition(self, signal: Dict) -> str:
        """Analyze overall market condition"""
        indicators = signal.get('indicators', {})
        rsi = indicators.get('rsi', 50)
        
        if rsi < 30:
            return "oversold"
        elif rsi > 70:
            return "overbought"
        elif 45 <= rsi <= 55:
            return "neutral"
        elif rsi < 45:
            return "bearish"
        else:
            return "bullish"
    
    def suggest_action(self, signal: Dict, current_position: Optional[Dict], 
                      available_balance: float) -> Dict:
        """Suggest the best action to take
        
        Returns:
            dict with 'action', 'side', 'size', 'reason', 'confidence'
        """
        if available_balance <= 1:
            return {
                'action': 'none',
                'reason': 'Insufficient balance',
                'confidence': 0
            }
        
        current_qty = 0
        if current_position:
            current_qty = current_position.get('currentQty', 0)
        
        # If no position, look for entry signals
        if current_qty == 0:
            if signal['action'] == 'buy' and signal['strength'] >= 60:
                return {
                    'action': 'open',
                    'side': 'buy',
                    'reason': signal['reason'],
                    'confidence': signal['strength']
                }
            elif signal['action'] == 'sell' and signal['strength'] >= 60:
                return {
                    'action': 'open',
                    'side': 'sell',
                    'reason': signal['reason'],
                    'confidence': signal['strength']
                }
            else:
                return {
                    'action': 'wait',
                    'reason': 'No strong entry signal',
                    'confidence': signal['strength']
                }
        
        # If we have a position, check if we should close or hedge
        else:
            # Check for exit conditions first
            if current_qty > 0:  # Long position
                should_close, reason = self.should_close_long(
                    signal['indicators']['current_price'],
                    current_position.get('avgEntryPrice', 0),
                    current_qty,
                    current_position.get('unrealisedPnl', 0)
                )
                if should_close:
                    return {
                        'action': 'close',
                        'side': 'sell',
                        'reason': reason,
                        'confidence': 100
                    }
            
            elif current_qty < 0:  # Short position
                should_close, reason = self.should_close_short(
                    signal['indicators']['current_price'],
                    current_position.get('avgEntryPrice', 0),
                    current_qty,
                    current_position.get('unrealisedPnl', 0)
                )
                if should_close:
                    return {
                        'action': 'close',
                        'side': 'buy',
                        'reason': reason,
                        'confidence': 100
                    }
            
            # Check for hedge opportunity
            should_hedge, reason, hedge_side = self.should_hedge(signal, current_position)
            if should_hedge:
                return {
                    'action': 'hedge',
                    'side': hedge_side,
                    'reason': reason,
                    'confidence': signal['strength']
                }
            
            return {
                'action': 'hold',
                'reason': 'Monitoring position',
                'confidence': 50
            }
