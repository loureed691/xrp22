"""
Dynamic Leverage Adjustment
"""
import logging
from typing import Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)


class DynamicLeverage:
    """Dynamically adjust leverage based on market conditions and risk"""
    
    def __init__(self, base_leverage: int = 11, min_leverage: int = 1, max_leverage: int = 20):
        """Initialize dynamic leverage adjuster
        
        Args:
            base_leverage: Base leverage level
            min_leverage: Minimum leverage allowed
            max_leverage: Maximum leverage allowed
        """
        self.base_leverage = base_leverage
        self.min_leverage = min_leverage
        self.max_leverage = max_leverage
        self.current_leverage = base_leverage
        
        logger.info(f"Dynamic leverage initialized: base={base_leverage}x, range={min_leverage}-{max_leverage}x")
    
    def calculate_volatility_score(self, klines_data: list, lookback: int = 20) -> float:
        """Calculate volatility score from recent price data
        
        Args:
            klines_data: Historical kline data
            lookback: Number of candles to analyze
            
        Returns:
            Volatility score (0-1, higher = more volatile)
        """
        if len(klines_data) < lookback:
            return 0.5  # Default to medium volatility
        
        recent_klines = klines_data[-lookback:]
        closes = np.array([float(k[4]) for k in recent_klines])
        
        # Calculate returns
        returns = np.diff(closes) / closes[:-1]
        
        # Calculate volatility (standard deviation of returns)
        volatility = np.std(returns)
        
        # Normalize to 0-1 range (typical crypto volatility range: 0-0.1)
        normalized = min(volatility / 0.1, 1.0)
        
        return normalized
    
    def calculate_market_condition_score(self, signal: Dict) -> float:
        """Calculate market condition score from trading signal
        
        Args:
            signal: Trading signal with indicators
            
        Returns:
            Market condition score (0-1, higher = better conditions)
        """
        strength = signal.get('strength', 0) / 100
        indicators = signal.get('indicators', {})
        
        # Check for strong trending conditions
        rsi = indicators.get('rsi', 50)
        macd_histogram = indicators.get('macd_histogram', 0)
        
        # Strong trend = good for leverage
        if (rsi < 30 or rsi > 70) and abs(macd_histogram) > 0.1:
            trend_score = 0.8
        elif (rsi < 40 or rsi > 60) and abs(macd_histogram) > 0.05:
            trend_score = 0.6
        else:
            trend_score = 0.4
        
        # Combine with signal strength
        condition_score = 0.6 * strength + 0.4 * trend_score
        
        return condition_score
    
    def calculate_risk_score(self, balance: float, position_value: float, 
                            win_rate: float, recent_losses: int) -> float:
        """Calculate risk score based on account status
        
        Args:
            balance: Current account balance
            position_value: Current position value
            win_rate: Historical win rate (0-100)
            recent_losses: Number of recent consecutive losses
            
        Returns:
            Risk score (0-1, higher = lower risk)
        """
        # Factor 1: Position size relative to balance
        if balance > 0:
            position_ratio = position_value / balance
            position_score = max(0, 1 - position_ratio)
        else:
            position_score = 0
        
        # Factor 2: Win rate performance
        win_score = win_rate / 100
        
        # Factor 3: Recent losses penalty
        loss_penalty = max(0, 1 - (recent_losses * 0.15))
        
        # Combine factors
        risk_score = 0.4 * position_score + 0.3 * win_score + 0.3 * loss_penalty
        
        return risk_score
    
    def adjust_leverage(self, klines_data: list, signal: Dict, balance: float, 
                       position_value: float, win_rate: float, 
                       recent_losses: int = 0) -> int:
        """Dynamically adjust leverage based on multiple factors
        
        Args:
            klines_data: Historical kline data
            signal: Current trading signal
            balance: Current account balance
            position_value: Current position value
            win_rate: Historical win rate (0-100)
            recent_losses: Number of recent consecutive losses
            
        Returns:
            Adjusted leverage value
        """
        # Calculate component scores
        volatility_score = self.calculate_volatility_score(klines_data)
        condition_score = self.calculate_market_condition_score(signal)
        risk_score = self.calculate_risk_score(balance, position_value, win_rate, recent_losses)
        
        # Volatility adjustment (lower leverage in high volatility)
        volatility_multiplier = 1.0 - (volatility_score * 0.5)
        
        # Market condition adjustment (higher leverage in good conditions)
        condition_multiplier = 0.5 + (condition_score * 0.5)
        
        # Risk adjustment (lower leverage in high risk situations)
        risk_multiplier = 0.5 + (risk_score * 0.5)
        
        # Calculate final leverage
        adjusted = self.base_leverage * volatility_multiplier * condition_multiplier * risk_multiplier
        adjusted = int(np.round(adjusted))
        
        # Clamp to allowed range
        adjusted = max(self.min_leverage, min(self.max_leverage, adjusted))
        
        # Log adjustment if changed
        if adjusted != self.current_leverage:
            logger.info(f"Leverage adjusted: {self.current_leverage}x -> {adjusted}x")
            logger.info(f"  Volatility: {volatility_score:.2f} | "
                       f"Condition: {condition_score:.2f} | "
                       f"Risk: {risk_score:.2f}")
        
        self.current_leverage = adjusted
        return adjusted
    
    def get_conservative_leverage(self) -> int:
        """Get conservative leverage for uncertain conditions
        
        Returns:
            Conservative leverage value
        """
        return max(self.min_leverage, self.base_leverage // 2)
    
    def get_aggressive_leverage(self) -> int:
        """Get aggressive leverage for favorable conditions
        
        Returns:
            Aggressive leverage value
        """
        return min(self.max_leverage, int(self.base_leverage * 1.5))
    
    def reset_to_base(self):
        """Reset leverage to base level"""
        self.current_leverage = self.base_leverage
        logger.info(f"Leverage reset to base: {self.base_leverage}x")
    
    def get_current_leverage(self) -> int:
        """Get current leverage level
        
        Returns:
            Current leverage value
        """
        return self.current_leverage
