"""
Advanced ML-based Signal Generation
"""
import logging
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MLSignalGenerator:
    """Advanced ML-based signal generation using ensemble methods"""
    
    def __init__(self, lookback_period: int = 50, signal_threshold: float = 0.6):
        """Initialize ML signal generator
        
        Args:
            lookback_period: Number of candles to analyze
            signal_threshold: Threshold for signal generation (0-1)
        """
        self.lookback_period = lookback_period
        self.signal_threshold = signal_threshold
        self.feature_history = []
        
        logger.info("ML signal generator initialized")
    
    def extract_features(self, klines_data: List[List], current_price: float) -> Dict:
        """Extract features from market data for ML prediction
        
        Args:
            klines_data: Historical kline data
            current_price: Current market price
            
        Returns:
            Dict of extracted features
        """
        if len(klines_data) < self.lookback_period:
            return {}
        
        # Extract recent candles
        recent_klines = klines_data[-self.lookback_period:]
        closes = np.array([float(k[4]) for k in recent_klines])
        highs = np.array([float(k[2]) for k in recent_klines])
        lows = np.array([float(k[3]) for k in recent_klines])
        volumes = np.array([float(k[5]) for k in recent_klines])
        
        # Price-based features
        price_mean = np.mean(closes)
        price_std = np.std(closes)
        price_momentum = (closes[-1] - closes[0]) / closes[0]
        price_acceleration = (closes[-1] - closes[-5]) / closes[-5] - (closes[-5] - closes[-10]) / closes[-10]
        
        # Volatility features
        returns = np.diff(closes) / closes[:-1]
        volatility = np.std(returns)
        volatility_trend = np.std(returns[-10:]) / (np.std(returns[-20:-10]) + 1e-8)
        
        # Volume features
        volume_mean = np.mean(volumes)
        volume_std = np.std(volumes)
        volume_trend = volumes[-1] / (volume_mean + 1e-8)
        
        # Range features
        true_range = np.maximum(highs - lows, 
                                np.maximum(np.abs(highs - np.roll(closes, 1)),
                                          np.abs(lows - np.roll(closes, 1))))
        atr = np.mean(true_range[-14:])
        
        # Moving average features
        sma_5 = np.mean(closes[-5:])
        sma_10 = np.mean(closes[-10:])
        sma_20 = np.mean(closes[-20:])
        ma_cross_5_10 = (sma_5 - sma_10) / sma_10
        ma_cross_10_20 = (sma_10 - sma_20) / sma_20
        
        # Price position features
        price_vs_mean = (current_price - price_mean) / price_std
        price_vs_high = (current_price - np.max(highs)) / np.max(highs)
        price_vs_low = (current_price - np.min(lows)) / np.min(lows)
        
        return {
            'price_momentum': price_momentum,
            'price_acceleration': price_acceleration,
            'volatility': volatility,
            'volatility_trend': volatility_trend,
            'volume_trend': volume_trend,
            'atr': atr,
            'ma_cross_5_10': ma_cross_5_10,
            'ma_cross_10_20': ma_cross_10_20,
            'price_vs_mean': price_vs_mean,
            'price_vs_high': price_vs_high,
            'price_vs_low': price_vs_low
        }
    
    def predict_signal(self, features: Dict) -> Dict:
        """Generate ML-based prediction from features
        
        Args:
            features: Extracted features
            
        Returns:
            Dict with prediction and confidence
        """
        if not features:
            return {
                'action': 'hold',
                'confidence': 0,
                'prediction_score': 0,
                'reason': 'Insufficient data for ML prediction'
            }
        
        # Ensemble of simple models (rule-based for now, can be replaced with trained models)
        scores = []
        reasons = []
        
        # Model 1: Momentum-based
        momentum_score = self._momentum_model(features)
        scores.append(momentum_score)
        if abs(momentum_score) > 0.5:
            reasons.append(f"Momentum: {momentum_score:.2f}")
        
        # Model 2: Volatility-based
        volatility_score = self._volatility_model(features)
        scores.append(volatility_score)
        if abs(volatility_score) > 0.5:
            reasons.append(f"Volatility: {volatility_score:.2f}")
        
        # Model 3: MA crossover-based
        ma_score = self._ma_crossover_model(features)
        scores.append(ma_score)
        if abs(ma_score) > 0.5:
            reasons.append(f"MA Cross: {ma_score:.2f}")
        
        # Model 4: Mean reversion
        reversion_score = self._mean_reversion_model(features)
        scores.append(reversion_score)
        if abs(reversion_score) > 0.5:
            reasons.append(f"Mean Rev: {reversion_score:.2f}")
        
        # Aggregate scores using weighted average
        final_score = np.mean(scores)
        confidence = np.std(scores)  # Lower std = higher agreement = higher confidence
        confidence = 1 - min(confidence, 1)  # Invert so high agreement = high confidence
        
        # Determine action based on score and confidence
        if final_score > self.signal_threshold and confidence > 0.6:
            action = 'buy'
            strength = int(min(100, (final_score + confidence) * 50))
        elif final_score < -self.signal_threshold and confidence > 0.6:
            action = 'sell'
            strength = int(min(100, (-final_score + confidence) * 50))
        else:
            action = 'hold'
            strength = int(abs(final_score) * 50)
        
        return {
            'action': action,
            'confidence': confidence * 100,
            'prediction_score': final_score,
            'strength': strength,
            'reason': f"ML Ensemble: {', '.join(reasons) if reasons else 'Mixed signals'}"
        }
    
    def _momentum_model(self, features: Dict) -> float:
        """Simple momentum-based model
        
        Returns:
            Score between -1 (bearish) and 1 (bullish)
        """
        momentum = features['price_momentum']
        acceleration = features['price_acceleration']
        
        # Combine momentum and acceleration
        score = 0.6 * np.tanh(momentum * 10) + 0.4 * np.tanh(acceleration * 5)
        
        return score
    
    def _volatility_model(self, features: Dict) -> float:
        """Volatility-based model (high volatility = caution)
        
        Returns:
            Score between -1 (bearish) and 1 (bullish)
        """
        vol_trend = features['volatility_trend']
        volume_trend = features['volume_trend']
        
        # Rising volatility with high volume = potential trend
        if vol_trend > 1.2 and volume_trend > 1.5:
            # Use momentum to determine direction
            return np.sign(features['price_momentum']) * 0.7
        elif vol_trend < 0.8:
            # Low volatility = consolidation
            return 0
        
        return 0
    
    def _ma_crossover_model(self, features: Dict) -> float:
        """Moving average crossover model
        
        Returns:
            Score between -1 (bearish) and 1 (bullish)
        """
        ma_5_10 = features['ma_cross_5_10']
        ma_10_20 = features['ma_cross_10_20']
        
        # Bullish if short MA above long MA
        score = 0.5 * np.tanh(ma_5_10 * 20) + 0.5 * np.tanh(ma_10_20 * 10)
        
        return score
    
    def _mean_reversion_model(self, features: Dict) -> float:
        """Mean reversion model
        
        Returns:
            Score between -1 (bearish) and 1 (bullish)
        """
        price_vs_mean = features['price_vs_mean']
        
        # Extreme deviations suggest reversion
        if price_vs_mean > 2:  # Price too high, expect drop
            return -0.8
        elif price_vs_mean < -2:  # Price too low, expect rise
            return 0.8
        
        return 0
    
    def generate_ml_signal(self, klines_data: List[List], current_price: float) -> Dict:
        """Generate complete ML-based trading signal
        
        Args:
            klines_data: Historical kline data
            current_price: Current market price
            
        Returns:
            Trading signal with ML predictions
        """
        # Extract features
        features = self.extract_features(klines_data, current_price)
        
        if not features:
            return {
                'action': 'hold',
                'strength': 0,
                'indicators': {},
                'reason': 'Insufficient data for ML analysis'
            }
        
        # Generate prediction
        prediction = self.predict_signal(features)
        
        # Store features for future learning
        self.feature_history.append({
            'timestamp': datetime.now(),
            'features': features,
            'prediction': prediction
        })
        
        # Keep only recent history
        if len(self.feature_history) > 1000:
            self.feature_history = self.feature_history[-1000:]
        
        logger.info(f"ML Signal: {prediction['action'].upper()} | "
                   f"Confidence: {prediction['confidence']:.1f}% | "
                   f"Score: {prediction['prediction_score']:.2f}")
        
        return {
            'action': prediction['action'],
            'strength': prediction['strength'],
            'indicators': {
                'ml_score': prediction['prediction_score'],
                'ml_confidence': prediction['confidence'],
                'features': features
            },
            'reason': prediction['reason']
        }
