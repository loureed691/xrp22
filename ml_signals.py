"""
Advanced ML-based Signal Generation
"""
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
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
        
        # Performance tracking for adaptive weighting
        self.model_performance = {
            'momentum': {'correct': 0, 'total': 0, 'weight': 1.0},
            'volatility': {'correct': 0, 'total': 0, 'weight': 1.0},
            'ma_crossover': {'correct': 0, 'total': 0, 'weight': 1.0},
            'mean_reversion': {'correct': 0, 'total': 0, 'weight': 1.0},
            'trend_strength': {'correct': 0, 'total': 0, 'weight': 1.0},
            'support_resistance': {'correct': 0, 'total': 0, 'weight': 1.0}
        }
        
        # Market regime tracking
        self.market_regime = 'unknown'  # trending, ranging, volatile
        self.regime_history = []
        
        logger.info("ML signal generator initialized with adaptive learning")
    
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
        
        # Advanced features: Support/Resistance levels
        support_level = np.percentile(lows, 10)
        resistance_level = np.percentile(highs, 90)
        price_to_support = (current_price - support_level) / support_level
        price_to_resistance = (resistance_level - current_price) / current_price
        
        # Trend strength features
        ma_alignment = 1 if (sma_5 > sma_10 > sma_20) else (-1 if (sma_5 < sma_10 < sma_20) else 0)
        trend_consistency = np.sum(np.diff(closes[-20:]) > 0) / 19.0  # % of up candles
        
        # Volatility clustering (GARCH-like)
        vol_clustering = np.std(returns[-10:]) / (np.std(returns[-20:-10]) + 1e-8)
        
        # Volume profile
        volume_momentum = (volumes[-1] - np.mean(volumes[-10:])) / (np.std(volumes[-10:]) + 1e-8)
        
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
            'price_vs_low': price_vs_low,
            'support_level': support_level,
            'resistance_level': resistance_level,
            'price_to_support': price_to_support,
            'price_to_resistance': price_to_resistance,
            'ma_alignment': ma_alignment,
            'trend_consistency': trend_consistency,
            'vol_clustering': vol_clustering,
            'volume_momentum': volume_momentum
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
        
        # Detect market regime
        self.market_regime = self._detect_market_regime(features)
        
        # Ensemble of models with adaptive weights
        scores = []
        weighted_scores = []
        reasons = []
        
        # Model 1: Momentum-based
        momentum_score = self._momentum_model(features)
        weight_1 = self.model_performance['momentum']['weight']
        scores.append(momentum_score)
        weighted_scores.append(momentum_score * weight_1)
        if abs(momentum_score) > 0.5:
            reasons.append(f"Momentum: {momentum_score:.2f}")
        
        # Model 2: Volatility-based
        volatility_score = self._volatility_model(features)
        weight_2 = self.model_performance['volatility']['weight']
        scores.append(volatility_score)
        weighted_scores.append(volatility_score * weight_2)
        if abs(volatility_score) > 0.5:
            reasons.append(f"Volatility: {volatility_score:.2f}")
        
        # Model 3: MA crossover-based
        ma_score = self._ma_crossover_model(features)
        weight_3 = self.model_performance['ma_crossover']['weight']
        scores.append(ma_score)
        weighted_scores.append(ma_score * weight_3)
        if abs(ma_score) > 0.5:
            reasons.append(f"MA Cross: {ma_score:.2f}")
        
        # Model 4: Mean reversion
        reversion_score = self._mean_reversion_model(features)
        weight_4 = self.model_performance['mean_reversion']['weight']
        scores.append(reversion_score)
        weighted_scores.append(reversion_score * weight_4)
        if abs(reversion_score) > 0.5:
            reasons.append(f"Mean Rev: {reversion_score:.2f}")
        
        # Model 5: Trend strength (NEW)
        trend_score = self._trend_strength_model(features)
        weight_5 = self.model_performance['trend_strength']['weight']
        scores.append(trend_score)
        weighted_scores.append(trend_score * weight_5)
        if abs(trend_score) > 0.5:
            reasons.append(f"Trend: {trend_score:.2f}")
        
        # Model 6: Support/Resistance (NEW)
        sr_score = self._support_resistance_model(features)
        weight_6 = self.model_performance['support_resistance']['weight']
        scores.append(sr_score)
        weighted_scores.append(sr_score * weight_6)
        if abs(sr_score) > 0.5:
            reasons.append(f"S/R: {sr_score:.2f}")
        
        # Aggregate scores using adaptive weighted average
        total_weight = sum([weight_1, weight_2, weight_3, weight_4, weight_5, weight_6])
        final_score = sum(weighted_scores) / total_weight
        
        # Enhanced confidence calculation
        confidence = self._calculate_confidence(scores, features)
        
        # Risk-adjusted signal filtering based on market regime
        final_score, adjusted_threshold = self._risk_adjust_signal(final_score, confidence, features)
        
        # Determine action based on score, confidence, and market regime
        if final_score > adjusted_threshold and confidence > 0.6:
            action = 'buy'
            strength = int(min(100, (final_score + confidence) * 50))
        elif final_score < -adjusted_threshold and confidence > 0.6:
            action = 'sell'
            strength = int(min(100, (-final_score + confidence) * 50))
        else:
            action = 'hold'
            strength = int(abs(final_score) * 50)
        
        # Add regime information to reasons
        reasons.append(f"Regime: {self.market_regime}")
        
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
    
    def _trend_strength_model(self, features: Dict) -> float:
        """Trend strength analysis model (NEW)
        
        Returns:
            Score between -1 (strong downtrend) and 1 (strong uptrend)
        """
        ma_alignment = features['ma_alignment']
        trend_consistency = features['trend_consistency']
        price_momentum = features['price_momentum']
        
        # Strong aligned trend with consistent direction
        if ma_alignment == 1 and trend_consistency > 0.6:
            # Strong uptrend
            return 0.8 * np.tanh(price_momentum * 10)
        elif ma_alignment == -1 and trend_consistency < 0.4:
            # Strong downtrend
            return -0.8 * np.tanh(abs(price_momentum) * 10)
        
        # Weak or no clear trend
        return 0.3 * np.tanh(price_momentum * 5)
    
    def _support_resistance_model(self, features: Dict) -> float:
        """Support and resistance levels model (NEW)
        
        Returns:
            Score between -1 (near resistance) and 1 (near support)
        """
        price_to_support = features['price_to_support']
        price_to_resistance = features['price_to_resistance']
        volume_momentum = features['volume_momentum']
        
        # Near support with volume increase = bounce opportunity
        if price_to_support < 0.05 and volume_momentum > 1.0:
            return 0.7
        
        # Near resistance with volume increase = rejection opportunity
        if price_to_resistance < 0.05 and volume_momentum > 1.0:
            return -0.7
        
        # Mid-range with no clear signal
        if 0.3 < price_to_support < 0.7:
            return 0
        
        # Closer to support = bullish, closer to resistance = bearish
        return 0.5 * np.tanh((price_to_resistance - price_to_support) * 5)
    
    def _detect_market_regime(self, features: Dict) -> str:
        """Detect current market regime (NEW)
        
        Returns:
            'trending', 'ranging', or 'volatile'
        """
        volatility = features['volatility']
        trend_consistency = features['trend_consistency']
        ma_alignment = features['ma_alignment']
        vol_clustering = features['vol_clustering']
        
        # High volatility clustering indicates volatile regime
        if vol_clustering > 1.5 or volatility > 0.05:
            regime = 'volatile'
        # Strong trend consistency and alignment = trending
        elif abs(ma_alignment) == 1 and (trend_consistency > 0.65 or trend_consistency < 0.35):
            regime = 'trending'
        # Otherwise ranging/consolidation
        else:
            regime = 'ranging'
        
        # Store in history
        self.regime_history.append({
            'timestamp': datetime.now(),
            'regime': regime
        })
        
        # Keep only recent history
        if len(self.regime_history) > 100:
            self.regime_history = self.regime_history[-100:]
        
        return regime
    
    def _calculate_confidence(self, scores: List[float], features: Dict) -> float:
        """Enhanced confidence calculation (NEW)
        
        Args:
            scores: List of model scores
            features: Market features
            
        Returns:
            Confidence score between 0 and 1
        """
        # Base confidence from score agreement
        score_std = np.std(scores)
        base_confidence = 1 - min(score_std, 1)
        
        # Adjust for volatility (lower confidence in high volatility)
        vol_adjustment = 1 - min(features['vol_clustering'] / 2.0, 0.3)
        
        # Adjust for trend clarity
        trend_clarity = abs(features['ma_alignment']) * 0.2
        
        # Combine factors
        confidence = base_confidence * vol_adjustment + trend_clarity
        confidence = min(max(confidence, 0), 1)  # Clamp to [0, 1]
        
        return confidence
    
    def _risk_adjust_signal(self, signal_score: float, confidence: float, 
                           features: Dict) -> Tuple[float, float]:
        """Risk-adjusted signal filtering based on market regime (NEW)
        
        Args:
            signal_score: Raw signal score
            confidence: Signal confidence
            features: Market features
            
        Returns:
            (adjusted_score, adjusted_threshold)
        """
        adjusted_score = signal_score
        adjusted_threshold = self.signal_threshold
        
        # Adjust based on market regime
        if self.market_regime == 'volatile':
            # Require stronger signals in volatile markets
            adjusted_threshold = self.signal_threshold * 1.3
            adjusted_score = signal_score * 0.8  # Dampen signal strength
        elif self.market_regime == 'trending':
            # Can be more aggressive in trending markets
            adjusted_threshold = self.signal_threshold * 0.9
            adjusted_score = signal_score * 1.1  # Amplify signal strength
        else:  # ranging
            # Normal thresholds for ranging markets
            adjusted_threshold = self.signal_threshold
        
        # Further adjust for volatility clustering
        if features['vol_clustering'] > 2.0:
            adjusted_threshold *= 1.2
        
        return adjusted_score, adjusted_threshold
    
    def update_model_performance(self, model_name: str, was_correct: bool):
        """Update model performance tracking for adaptive weighting (NEW)
        
        Args:
            model_name: Name of the model
            was_correct: Whether the model's prediction was correct
        """
        if model_name not in self.model_performance:
            return
        
        perf = self.model_performance[model_name]
        perf['total'] += 1
        if was_correct:
            perf['correct'] += 1
        
        # Calculate accuracy
        accuracy = perf['correct'] / perf['total'] if perf['total'] > 0 else 0.5
        
        # Update weight based on accuracy (exponential weighting)
        # Better performing models get higher weight
        perf['weight'] = np.exp(accuracy - 0.5) if perf['total'] >= 10 else 1.0
        
        logger.debug(f"Model {model_name}: accuracy={accuracy:.2%}, weight={perf['weight']:.2f}")
    
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
