"""
Portfolio Diversification Module
"""
import logging
from typing import Dict, List, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class PortfolioDiversifier:
    """Manage portfolio diversification across multiple assets and strategies"""
    
    def __init__(self, max_correlation: float = 0.7, max_position_per_pair: float = 0.4):
        """Initialize portfolio diversifier
        
        Args:
            max_correlation: Maximum allowed correlation between positions
            max_position_per_pair: Maximum position size per pair as fraction of portfolio
        """
        self.max_correlation = max_correlation
        self.max_position_per_pair = max_position_per_pair
        self.price_history = {}  # Track price history for correlation
        self.position_sizes = {}  # Track position sizes
        
        logger.info(f"Portfolio diversifier initialized: max_correlation={max_correlation}, "
                   f"max_position_per_pair={max_position_per_pair}")
    
    def update_price_history(self, symbol: str, price: float):
        """Update price history for correlation calculation
        
        Args:
            symbol: Trading pair symbol
            price: Current price
        """
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(price)
        
        # Keep only recent history (last 100 prices)
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
    
    def calculate_correlation(self, symbol1: str, symbol2: str) -> float:
        """Calculate price correlation between two symbols
        
        Args:
            symbol1: First trading pair symbol
            symbol2: Second trading pair symbol
            
        Returns:
            Correlation coefficient (-1 to 1)
        """
        if symbol1 not in self.price_history or symbol2 not in self.price_history:
            return 0.0
        
        prices1 = self.price_history[symbol1]
        prices2 = self.price_history[symbol2]
        
        # Need at least 30 data points for meaningful correlation
        if len(prices1) < 30 or len(prices2) < 30:
            return 0.0
        
        # Use same length for both series
        min_len = min(len(prices1), len(prices2))
        prices1 = prices1[-min_len:]
        prices2 = prices2[-min_len:]
        
        # Calculate correlation
        correlation = np.corrcoef(prices1, prices2)[0, 1]
        
        return correlation
    
    def check_diversification(self, symbol: str, existing_positions: List[str]) -> Tuple[bool, str]:
        """Check if adding a position would maintain good diversification
        
        Args:
            symbol: Symbol to check
            existing_positions: List of symbols with existing positions
            
        Returns:
            Tuple of (is_diversified, reason)
        """
        if not existing_positions:
            return True, "No existing positions"
        
        # Check correlation with existing positions
        high_correlation_pairs = []
        for existing_symbol in existing_positions:
            correlation = self.calculate_correlation(symbol, existing_symbol)
            
            if abs(correlation) > self.max_correlation:
                high_correlation_pairs.append((existing_symbol, correlation))
        
        if high_correlation_pairs:
            pairs_str = ', '.join([f"{sym} ({corr:.2f})" for sym, corr in high_correlation_pairs])
            return False, f"High correlation with: {pairs_str}"
        
        return True, "Good diversification"
    
    def calculate_optimal_position_size(self, symbol: str, available_balance: float,
                                       existing_positions: Dict[str, float]) -> float:
        """Calculate optimal position size considering diversification
        
        Args:
            symbol: Trading pair symbol
            available_balance: Available balance for trading
            existing_positions: Dict of symbol -> position_value
            
        Returns:
            Optimal position size in dollars
        """
        # Calculate total portfolio value
        total_portfolio = available_balance + sum(existing_positions.values())
        
        if total_portfolio == 0:
            return 0
        
        # Base position size (equal weight)
        num_positions = len(existing_positions) + 1  # Include new position
        base_size = total_portfolio * self.max_position_per_pair
        
        # Adjust based on correlation
        if existing_positions:
            avg_correlation = np.mean([
                abs(self.calculate_correlation(symbol, existing_symbol))
                for existing_symbol in existing_positions.keys()
            ])
            
            # Reduce size if high correlation
            correlation_factor = 1.0 - (avg_correlation * 0.5)
            adjusted_size = base_size * correlation_factor
        else:
            adjusted_size = base_size
        
        # Ensure we don't exceed available balance
        adjusted_size = min(adjusted_size, available_balance * 0.8)
        
        return adjusted_size
    
    def get_diversification_score(self, positions: Dict[str, float]) -> float:
        """Calculate overall portfolio diversification score
        
        Args:
            positions: Dict of symbol -> position_value
            
        Returns:
            Diversification score (0-1, higher = better diversified)
        """
        if len(positions) == 0:
            return 1.0  # Empty portfolio is considered diversified
        
        if len(positions) == 1:
            return 0.5  # Single position has moderate score
        
        symbols = list(positions.keys())
        total_value = sum(positions.values())
        
        # Factor 1: Number of positions (more = better)
        num_positions_score = min(1.0, len(positions) / 5)  # Optimal at 5+ positions
        
        # Factor 2: Position size balance (equal = better)
        weights = np.array([positions[s] / total_value for s in symbols])
        balance_score = 1.0 - np.std(weights)
        
        # Factor 3: Low correlation (lower = better)
        correlations = []
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                corr = abs(self.calculate_correlation(symbols[i], symbols[j]))
                correlations.append(corr)
        
        if correlations:
            avg_correlation = np.mean(correlations)
            correlation_score = 1.0 - avg_correlation
        else:
            correlation_score = 1.0
        
        # Combine factors
        overall_score = (0.3 * num_positions_score + 
                        0.3 * balance_score + 
                        0.4 * correlation_score)
        
        return overall_score
    
    def suggest_rebalancing(self, positions: Dict[str, float], 
                           target_balance: float = 0.9) -> Dict[str, str]:
        """Suggest rebalancing actions to improve diversification
        
        Args:
            positions: Dict of symbol -> position_value
            target_balance: Target balance score (0-1)
            
        Returns:
            Dict of symbol -> action (reduce/increase/close)
        """
        suggestions = {}
        
        if len(positions) == 0:
            return suggestions
        
        total_value = sum(positions.values())
        symbols = list(positions.keys())
        
        # Check position sizes
        for symbol, value in positions.items():
            weight = value / total_value
            
            if weight > self.max_position_per_pair:
                suggestions[symbol] = f"reduce (current: {weight:.1%}, max: {self.max_position_per_pair:.1%})"
        
        # Check correlations
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                corr = self.calculate_correlation(symbols[i], symbols[j])
                
                if abs(corr) > self.max_correlation:
                    # Suggest closing smaller position
                    if positions[symbols[i]] < positions[symbols[j]]:
                        if symbols[i] not in suggestions:
                            suggestions[symbols[i]] = f"close (high correlation with {symbols[j]}: {corr:.2f})"
                    else:
                        if symbols[j] not in suggestions:
                            suggestions[symbols[j]] = f"close (high correlation with {symbols[i]}: {corr:.2f})"
        
        return suggestions
    
    def get_portfolio_metrics(self, positions: Dict[str, float]) -> Dict:
        """Get comprehensive portfolio metrics
        
        Args:
            positions: Dict of symbol -> position_value
            
        Returns:
            Dict with portfolio metrics
        """
        if not positions:
            return {
                'num_positions': 0,
                'total_value': 0,
                'diversification_score': 1.0,
                'largest_position_pct': 0,
                'avg_correlation': 0
            }
        
        total_value = sum(positions.values())
        symbols = list(positions.keys())
        
        # Calculate metrics
        largest_position = max(positions.values())
        largest_position_pct = (largest_position / total_value) * 100
        
        # Calculate average correlation
        correlations = []
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                corr = abs(self.calculate_correlation(symbols[i], symbols[j]))
                correlations.append(corr)
        
        avg_correlation = np.mean(correlations) if correlations else 0
        
        return {
            'num_positions': len(positions),
            'total_value': total_value,
            'diversification_score': self.get_diversification_score(positions),
            'largest_position_pct': largest_position_pct,
            'avg_correlation': avg_correlation
        }
