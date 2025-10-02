"""
Technical Analysis Module
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Technical analysis for trading signals"""
    
    def __init__(self, rsi_period: int = 14, ema_short: int = 12, 
                 ema_long: int = 26, macd_signal: int = 9):
        self.rsi_period = rsi_period
        self.ema_short = ema_short
        self.ema_long = ema_long
        self.macd_signal = macd_signal
    
    def calculate_rsi(self, prices: List[float]) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < self.rsi_period + 1:
            return 50.0  # Neutral RSI
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-self.rsi_period:])
        avg_loss = np.mean(losses[-self.rsi_period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return np.mean(prices)
        
        prices_array = np.array(prices)
        multiplier = 2 / (period + 1)
        ema = prices_array[0]
        
        for price in prices_array[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def calculate_macd(self, prices: List[float]) -> Tuple[float, float, float]:
        """Calculate MACD (Moving Average Convergence Divergence)
        Returns: (macd_line, signal_line, histogram)
        """
        if len(prices) < self.ema_long:
            return 0.0, 0.0, 0.0
        
        ema_short = self.calculate_ema(prices, self.ema_short)
        ema_long = self.calculate_ema(prices, self.ema_long)
        
        macd_line = ema_short - ema_long
        
        # Calculate signal line (EMA of MACD)
        # For simplicity, we'll use a basic average here
        signal_line = macd_line * 0.8  # Simplified signal
        
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, 
                                  std_dev: float = 2.0) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands
        Returns: (upper_band, middle_band, lower_band)
        """
        if len(prices) < period:
            avg = np.mean(prices)
            return avg, avg, avg
        
        recent_prices = prices[-period:]
        middle_band = np.mean(recent_prices)
        std = np.std(recent_prices)
        
        upper_band = middle_band + (std_dev * std)
        lower_band = middle_band - (std_dev * std)
        
        return upper_band, middle_band, lower_band
    
    def calculate_atr(self, high: List[float], low: List[float], 
                     close: List[float], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(high) < 2 or len(low) < 2 or len(close) < 2:
            return 0.0
        
        tr_list = []
        for i in range(1, len(close)):
            h_l = high[i] - low[i]
            h_pc = abs(high[i] - close[i-1])
            l_pc = abs(low[i] - close[i-1])
            tr = max(h_l, h_pc, l_pc)
            tr_list.append(tr)
        
        if len(tr_list) < period:
            return np.mean(tr_list) if tr_list else 0.0
        
        return np.mean(tr_list[-period:])
    
    def generate_signal(self, klines_data: List[List], current_price: float,
                       rsi_oversold: float = 30, rsi_overbought: float = 70) -> Dict:
        """Generate trading signal based on multiple indicators
        
        Returns:
            dict with 'action' ('buy', 'sell', 'hold'), 'strength' (0-100), 
            and 'indicators' dict with individual indicator values
        """
        if not klines_data or len(klines_data) < 30:
            return {
                'action': 'hold',
                'strength': 0,
                'indicators': {},
                'reason': 'Insufficient data'
            }
        
        # Extract price data from klines
        # KuCoin kline format: [timestamp, open, high, low, close, volume]
        closes = [float(k[4]) for k in klines_data]
        highs = [float(k[2]) for k in klines_data]
        lows = [float(k[3]) for k in klines_data]
        
        # Calculate indicators
        rsi = self.calculate_rsi(closes)
        macd_line, signal_line, histogram = self.calculate_macd(closes)
        upper_bb, middle_bb, lower_bb = self.calculate_bollinger_bands(closes)
        atr = self.calculate_atr(highs, lows, closes)
        ema_short = self.calculate_ema(closes, self.ema_short)
        ema_long = self.calculate_ema(closes, self.ema_long)
        
        indicators = {
            'rsi': rsi,
            'macd_line': macd_line,
            'signal_line': signal_line,
            'histogram': histogram,
            'upper_bb': upper_bb,
            'middle_bb': middle_bb,
            'lower_bb': lower_bb,
            'atr': atr,
            'ema_short': ema_short,
            'ema_long': ema_long,
            'current_price': current_price
        }
        
        # Signal generation logic
        buy_signals = 0
        sell_signals = 0
        signal_strength = 0
        reasons = []
        
        # RSI signals
        if rsi < rsi_oversold:
            buy_signals += 2
            signal_strength += 25
            reasons.append(f"RSI oversold ({rsi:.2f})")
        elif rsi > rsi_overbought:
            sell_signals += 2
            signal_strength += 25
            reasons.append(f"RSI overbought ({rsi:.2f})")
        
        # MACD signals
        if histogram > 0 and macd_line > signal_line:
            buy_signals += 1
            signal_strength += 15
            reasons.append("MACD bullish")
        elif histogram < 0 and macd_line < signal_line:
            sell_signals += 1
            signal_strength += 15
            reasons.append("MACD bearish")
        
        # EMA crossover signals
        if ema_short > ema_long:
            buy_signals += 1
            signal_strength += 15
            reasons.append("EMA bullish crossover")
        elif ema_short < ema_long:
            sell_signals += 1
            signal_strength += 15
            reasons.append("EMA bearish crossover")
        
        # Bollinger Bands signals
        if current_price < lower_bb:
            buy_signals += 1
            signal_strength += 20
            reasons.append("Price below lower Bollinger Band")
        elif current_price > upper_bb:
            sell_signals += 1
            signal_strength += 20
            reasons.append("Price above upper Bollinger Band")
        
        # Mean reversion from middle band
        distance_from_middle = abs(current_price - middle_bb) / middle_bb * 100
        if distance_from_middle > 2:  # More than 2% away from middle
            if current_price < middle_bb:
                buy_signals += 1
                signal_strength += 10
                reasons.append("Price far below middle band")
            else:
                sell_signals += 1
                signal_strength += 10
                reasons.append("Price far above middle band")
        
        # Determine action
        if buy_signals > sell_signals and buy_signals >= 2:
            action = 'buy'
        elif sell_signals > buy_signals and sell_signals >= 2:
            action = 'sell'
        else:
            action = 'hold'
            signal_strength = max(20, signal_strength)  # Minimum strength for hold
        
        return {
            'action': action,
            'strength': min(100, signal_strength),
            'indicators': indicators,
            'reason': '; '.join(reasons) if reasons else 'No strong signals',
            'buy_signals': buy_signals,
            'sell_signals': sell_signals
        }
