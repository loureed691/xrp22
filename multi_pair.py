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
        
        # Check signal strength first
        if signal.get('strength', 0) < 60:
            return False
        
        # If pair has insufficient balance but has a strong signal, try to boost allocation
        current_balance = self.pair_balances.get(symbol, 0)
        if current_balance <= 1:
            logger.info(f"Pair {symbol} has strong signal (strength: {signal.get('strength', 0)}) but insufficient balance (${current_balance:.2f})")
            # Try to boost allocation for this pair
            if self.boost_allocation_for_signal(symbol, signal):
                logger.info(f"Successfully boosted allocation for {symbol}")
                # Re-check the updated balance after boosting
                updated_balance = self.pair_balances.get(symbol, 0)
                if updated_balance > 1:
                    return True
                else:
                    logger.warning(f"Boosted allocation for {symbol}, but balance still insufficient (${updated_balance:.2f}), skipping trade")
                    return False
            else:
                logger.warning(f"Could not boost allocation for {symbol}, skipping trade")
                return False
        
        # Additional logic can be added here
        # e.g., correlation checks, market conditions, etc.
        
        return True
    
    def boost_allocation_for_signal(self, symbol: str, signal: Dict) -> bool:
        """
        Boost allocation for a pair that matches a signal.

        Redistribution rules:
        - Target allocation for the specified pair is at least 10% of the total allocated balance.
        - No more than 20% of the balance can be taken from any donor pair.
        - Donor pairs cannot be reduced below 10% of the total allocated balance.

        Side effects:
        - Mutates self.pair_balances to reflect the redistribution.

        Args:
            symbol: Trading pair symbol
            signal: Current trading signal
        Returns:
            True if allocation was boosted, False otherwise
        """
        # Find pairs with excess allocation to redistribute
        # Target: Get at least 10% of total allocated balance
        total_allocated = sum(self.pair_balances.values())
        if total_allocated <= 0:
            return False
        
        target_amount = total_allocated * 0.10  # 10% of total
        current_amount = self.pair_balances.get(symbol, 0)
        
        if current_amount >= target_amount:
            return True  # Already has enough
        
        needed_amount = target_amount - current_amount
        
        # Try to get funds from pairs with higher allocation
        # Sort pairs by allocation (highest first), excluding the target pair
        sorted_pairs = sorted(
            [(p, bal) for p, bal in self.pair_balances.items() if p != symbol],
            key=lambda x: x[1],
            reverse=True
        )
        
        redistributed = 0
        for pair, balance in sorted_pairs:
            if redistributed >= needed_amount:
                break
            
            # Take up to 20% from each pair, but don't reduce below 10% of total
            min_balance_for_pair = total_allocated * 0.10
            available_to_take = max(0, balance - min_balance_for_pair)
            max_to_take = balance * 0.20  # Don't take more than 20%
            
            to_take = min(available_to_take, max_to_take, needed_amount - redistributed)
            
            if to_take > 0:
                self.pair_balances[pair] -= to_take
                redistributed += to_take
                logger.info(f"Redistributed ${to_take:.2f} from {pair} to {symbol}")
        
        # Add redistributed amount to target pair
        self.pair_balances[symbol] = current_amount + redistributed
        
        if redistributed > 0:
            logger.info(f"Boosted {symbol} allocation from ${current_amount:.2f} to ${self.pair_balances[symbol]:.2f}")
            return True
        else:
            logger.warning(f"Could not redistribute enough balance to {symbol}")
            return False
    
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
            # Allocate most to best pair, but reserve some for signal-matching pairs
            # Reserve 20% for other pairs that might match signals
            reserve_percent = 0.20
            reserve_amount = total_balance * reserve_percent
            best_pair_amount = total_balance - reserve_amount
            
            allocations[best_pair] = best_pair_amount
            logger.info(f"Allocated ${best_pair_amount:.2f} to best pair: {best_pair}")
            logger.info(f"Reserved ${reserve_amount:.2f} for signal-matching pairs")
            
            # Distribute reserve equally among other pairs
            other_pairs = [p for p in self.trading_pairs if p != best_pair]
            if other_pairs:
                reserve_per_pair = reserve_amount / len(other_pairs)
                for pair in other_pairs:
                    allocations[pair] = reserve_per_pair
            else:
                # Only one trading pair, allocate full balance to best pair
                allocations[best_pair] = total_balance
            # No trading history, use equal allocation as fallback
            logger.info("No trading history yet, using equal allocation as fallback")
            balance_per_pair = total_balance / len(self.trading_pairs)
            for pair in self.trading_pairs:
                allocations[pair] = balance_per_pair
        
        # Store allocations
        self.pair_balances = allocations
        
        return allocations
