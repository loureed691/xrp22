"""
Multiple Trading Pairs Support
"""
import logging
from typing import Dict, List, Optional
from config import Config

logger = logging.getLogger(__name__)


class MultiPairManager:
    """Manage multiple trading pairs simultaneously"""
    
    def __init__(self, trading_pairs: List[str] = None):
        """Initialize multi-pair manager
        
        Args:
            trading_pairs: List of trading pair symbols (e.g., ['XRPUSDTM', 'BTCUSDTM'])
        """
        self.trading_pairs = trading_pairs or [Config.SYMBOL]
        self.pair_states = {}
        self.pair_balances = {}
        
        # Initialize state for each pair
        for pair in self.trading_pairs:
            self.pair_states[pair] = {
                'position': None,
                'last_signal': None,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'allocated_balance': 0
            }
        
        logger.info(f"Multi-pair manager initialized with {len(self.trading_pairs)} pairs: {', '.join(self.trading_pairs)}")
    
    def allocate_balance(self, total_balance: float, allocation_strategy: str = 'equal') -> Dict[str, float]:
        """Allocate balance across trading pairs
        
        Args:
            total_balance: Total available balance
            allocation_strategy: Strategy for allocation ('equal', 'weighted', 'dynamic', 'best')
            
        Returns:
            Dict mapping pair symbols to allocated balance
        """
        allocations = {}
        
        if allocation_strategy == 'best':
            # Allocate all balance to the best performing pair
            return self.allocate_to_best_pair(total_balance)
        
        elif allocation_strategy == 'equal':
            # Equal allocation across all pairs
            balance_per_pair = total_balance / len(self.trading_pairs)
            for pair in self.trading_pairs:
                allocations[pair] = balance_per_pair
        
        elif allocation_strategy == 'weighted':
            # Weight by performance (winning percentage)
            total_wins = sum(
                self.pair_states[pair]['winning_trades'] 
                for pair in self.trading_pairs
            )
            
            if total_wins == 0:
                # No history yet, use equal allocation
                balance_per_pair = total_balance / len(self.trading_pairs)
                for pair in self.trading_pairs:
                    allocations[pair] = balance_per_pair
            else:
                # Allocate based on win rate
                for pair in self.trading_pairs:
                    wins = self.pair_states[pair]['winning_trades']
                    weight = wins / total_wins if total_wins > 0 else 1 / len(self.trading_pairs)
                    allocations[pair] = total_balance * weight
        
        elif allocation_strategy == 'dynamic':
            # Allocate more to pairs with recent winning signals
            weights = {}
            for pair in self.trading_pairs:
                state = self.pair_states[pair]
                total = state['winning_trades'] + state['losing_trades']
                win_rate = state['winning_trades'] / max(1, total)
                
                # Base weight on win rate and recency
                weights[pair] = max(0.1, win_rate)  # Minimum 10% allocation
            
            total_weight = sum(weights.values())
            for pair in self.trading_pairs:
                allocations[pair] = total_balance * (weights[pair] / total_weight)
        
        else:
            # Default to equal
            balance_per_pair = total_balance / len(self.trading_pairs)
            for pair in self.trading_pairs:
                allocations[pair] = balance_per_pair
        
        # Store allocations
        self.pair_balances = allocations
        
        logger.info(f"Balance allocated across {len(self.trading_pairs)} pairs using {allocation_strategy} strategy")
        for pair, balance in allocations.items():
            logger.info(f"  {pair}: ${balance:.2f}")
        
        return allocations
    
    def get_pair_allocation(self, symbol: str) -> float:
        """Get allocated balance for a specific pair
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Allocated balance for the pair
        """
        return self.pair_balances.get(symbol, 0)
    
    def update_pair_state(self, symbol: str, position: Optional[Dict], signal: Dict):
        """Update state for a specific trading pair
        
        Args:
            symbol: Trading pair symbol
            position: Current position info
            signal: Latest signal
        """
        if symbol not in self.pair_states:
            logger.warning(f"Unknown trading pair: {symbol}")
            return
        
        self.pair_states[symbol]['position'] = position
        self.pair_states[symbol]['last_signal'] = signal
    
    def record_trade_result(self, symbol: str, pnl: float):
        """Record trade result for a pair
        
        Args:
            symbol: Trading pair symbol
            pnl: Profit/loss from the trade
        """
        if symbol not in self.pair_states:
            logger.warning(f"Unknown trading pair: {symbol}")
            return
        
        self.pair_states[symbol]['total_trades'] += 1
        
        if pnl > 0:
            self.pair_states[symbol]['winning_trades'] += 1
        else:
            self.pair_states[symbol]['losing_trades'] += 1
    
    def get_pair_statistics(self, symbol: str) -> Dict:
        """Get statistics for a specific pair
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Dict with pair statistics
        """
        if symbol not in self.pair_states:
            return {}
        
        state = self.pair_states[symbol]
        total = state['winning_trades'] + state['losing_trades']
        win_rate = (state['winning_trades'] / max(1, total)) * 100
        
        return {
            'symbol': symbol,
            'total_trades': state['total_trades'],
            'winning_trades': state['winning_trades'],
            'losing_trades': state['losing_trades'],
            'win_rate': win_rate,
            'allocated_balance': self.pair_balances.get(symbol, 0),
            'has_position': state['position'] is not None
        }
    
    def get_all_statistics(self) -> Dict:
        """Get statistics for all pairs
        
        Returns:
            Dict with statistics for each pair
        """
        return {
            pair: self.get_pair_statistics(pair)
            for pair in self.trading_pairs
        }
    
    def should_trade_pair(self, symbol: str, signal: Dict) -> bool:
        """Determine if we should trade a specific pair
        
        Args:
            symbol: Trading pair symbol
            signal: Current trading signal
            
        Returns:
            True if should trade, False otherwise
        """
        if symbol not in self.pair_states:
            return False
        
        state = self.pair_states[symbol]
        
        # Don't trade if no balance allocated
        if self.pair_balances.get(symbol, 0) <= 0:
            return False
        
        # Check signal strength
        if signal.get('strength', 0) < 60:
            return False
        
        # Additional logic can be added here
        # e.g., correlation checks, market conditions, etc.
        
        return True
    
    def get_active_pairs(self) -> List[str]:
        """Get list of pairs with active positions
        
        Returns:
            List of symbols with active positions
        """
        return [
            pair for pair, state in self.pair_states.items()
            if state['position'] is not None
        ]
    
    def rebalance(self, total_balance: float, strategy: str = 'dynamic'):
        """Rebalance allocations across pairs
        
        Args:
            total_balance: Total available balance
            strategy: Rebalancing strategy
        """
        logger.info("Rebalancing portfolio...")
        self.allocate_balance(total_balance, strategy)
    
    def get_best_pair(self) -> Optional[str]:
        """Identify the best/most profitable trading pair
        
        Returns:
            Symbol of the best performing pair, or None if no data
        """
        if not self.trading_pairs:
            return None
        
        best_pair = None
        best_score = -float('inf')
        
        for pair in self.trading_pairs:
            state = self.pair_states[pair]
            total = state['winning_trades'] + state['losing_trades']
            
            # Skip pairs with no trading history
            if total == 0:
                continue
            
            # Calculate composite score based on multiple factors
            win_rate = state['winning_trades'] / total
            total_trades = state['total_trades']
            
            # Weighted score: win_rate (60%) + trade activity (40%)
            # More trades = more reliable statistics
            activity_score = min(1.0, total_trades / 20.0)  # Normalize to max at 20 trades
            composite_score = (win_rate * 0.6) + (activity_score * 0.4)
            
            if composite_score > best_score:
                best_score = composite_score
                best_pair = pair
        
        if best_pair:
            stats = self.get_pair_statistics(best_pair)
            logger.info(f"Best performing pair: {best_pair} (Win rate: {stats['win_rate']:.1f}%, Trades: {stats['total_trades']})")
        
        return best_pair
    
    def get_pair_rankings(self) -> List[Dict]:
        """Get ranking of all pairs by performance
        
        Returns:
            List of dicts with pair stats, sorted by performance (best first)
        """
        rankings = []
        
        for pair in self.trading_pairs:
            state = self.pair_states[pair]
            total = state['winning_trades'] + state['losing_trades']
            
            if total == 0:
                # No history, assign neutral score
                composite_score = 0.0
                win_rate = 0.0
            else:
                win_rate = (state['winning_trades'] / total) * 100
                total_trades = state['total_trades']
                
                # Same scoring as get_best_pair
                activity_score = min(1.0, total_trades / 20.0)
                composite_score = ((state['winning_trades'] / total) * 0.6) + (activity_score * 0.4)
            
            rankings.append({
                'symbol': pair,
                'score': composite_score,
                'win_rate': win_rate,
                'total_trades': state['total_trades'],
                'winning_trades': state['winning_trades'],
                'losing_trades': state['losing_trades']
            })
        
        # Sort by score (highest first)
        rankings.sort(key=lambda x: x['score'], reverse=True)
        
        return rankings
    
    def allocate_to_best_pair(self, total_balance: float) -> Dict[str, float]:
        """Allocate all balance to the best performing pair
        
        Args:
            total_balance: Total available balance
            
        Returns:
            Dict mapping pair symbols to allocated balance
        """
        allocations = {pair: 0.0 for pair in self.trading_pairs}
        
        best_pair = self.get_best_pair()
        
        if best_pair:
            # Allocate all to best pair
            allocations[best_pair] = total_balance
            logger.info(f"Allocated full balance (${total_balance:.2f}) to best pair: {best_pair}")
        else:
            # No trading history, use equal allocation as fallback
            logger.info("No trading history yet, using equal allocation as fallback")
            balance_per_pair = total_balance / len(self.trading_pairs)
            for pair in self.trading_pairs:
                allocations[pair] = balance_per_pair
        
        # Store allocations
        self.pair_balances = allocations
        
        return allocations
