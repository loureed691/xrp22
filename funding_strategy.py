"""
Intelligent Funding Strategy Manager
Manages account balance and position sizing with risk-based approach
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class FundingStrategy:
    """Intelligent funding strategy that considers risk, balance, and market conditions"""
    
    def __init__(
        self,
        min_balance_reserve_percent: float = 20.0,
        base_position_size_percent: float = 15.0,
        max_position_size_percent: float = 40.0,
        min_position_size_percent: float = 5.0,
        risk_tiers: Optional[Dict] = None
    ):
        """Initialize funding strategy
        
        Args:
            min_balance_reserve_percent: Minimum % of balance to always keep in reserve
            base_position_size_percent: Base % of available balance to use per position
            max_position_size_percent: Maximum % of available balance for a single position
            min_position_size_percent: Minimum % of available balance for a single position
            risk_tiers: Custom risk tier configuration
        """
        self.min_balance_reserve_percent = min_balance_reserve_percent
        self.base_position_size_percent = base_position_size_percent
        self.max_position_size_percent = max_position_size_percent
        self.min_position_size_percent = min_position_size_percent
        
        # Default risk tiers
        self.risk_tiers = risk_tiers or {
            'low': {'volatility_max': 0.02, 'size_multiplier': 1.5},
            'medium': {'volatility_max': 0.05, 'size_multiplier': 1.0},
            'high': {'volatility_max': float('inf'), 'size_multiplier': 0.6}
        }
        
        logger.info("Funding Strategy initialized:")
        logger.info(f"  Reserve: {self.min_balance_reserve_percent}%")
        logger.info(f"  Base position size: {self.base_position_size_percent}%")
        logger.info(f"  Position size range: {self.min_position_size_percent}%-{self.max_position_size_percent}%")
    
    def calculate_available_funds(self, total_balance: float) -> float:
        """Calculate available funds after reserving minimum balance
        
        Args:
            total_balance: Total account balance
            
        Returns:
            Available funds for trading (after reserve)
        """
        reserve = total_balance * (self.min_balance_reserve_percent / 100)
        available = total_balance - reserve
        
        logger.debug(f"Total: ${total_balance:.2f}, Reserve: ${reserve:.2f}, Available: ${available:.2f}")
        
        return max(0, available)
    
    def calculate_risk_score(
        self,
        volatility: float,
        win_rate: float,
        recent_losses: int,
        signal_strength: int
    ) -> float:
        """Calculate overall risk score (0-1, where 1 is lowest risk)
        
        Args:
            volatility: Market volatility (0-1)
            win_rate: Historical win rate (0-100)
            recent_losses: Number of recent consecutive losses
            signal_strength: Current signal strength (0-100)
            
        Returns:
            Risk score between 0 and 1
        """
        # Volatility component (lower volatility = lower risk)
        volatility_score = max(0, 1 - (volatility / 0.1))  # Normalize assuming max 10% volatility
        
        # Win rate component (higher win rate = lower risk)
        win_rate_score = win_rate / 100.0
        
        # Recent losses component (more losses = higher risk)
        loss_penalty = min(1.0, recent_losses * 0.2)  # Each loss adds 20% risk
        loss_score = max(0, 1 - loss_penalty)
        
        # Signal strength component (stronger signal = lower risk)
        signal_score = signal_strength / 100.0
        
        # Weighted combination
        risk_score = (
            volatility_score * 0.3 +
            win_rate_score * 0.25 +
            loss_score * 0.25 +
            signal_score * 0.2
        )
        
        return max(0, min(1, risk_score))
    
    def get_risk_tier(self, volatility: float) -> str:
        """Determine risk tier based on volatility
        
        Args:
            volatility: Market volatility
            
        Returns:
            Risk tier name ('low', 'medium', 'high')
        """
        for tier, params in self.risk_tiers.items():
            if volatility <= params['volatility_max']:
                return tier
        return 'high'
    
    def calculate_position_size(
        self,
        available_balance: float,
        current_price: float,
        leverage: int,
        volatility: float = 0.03,
        win_rate: float = 50.0,
        recent_losses: int = 0,
        signal_strength: int = 60,
        existing_positions_value: float = 0.0
    ) -> int:
        """Calculate intelligent position size based on multiple factors
        
        Args:
            available_balance: Total available balance
            current_price: Current asset price
            leverage: Trading leverage
            volatility: Market volatility (default 3%)
            win_rate: Historical win rate (default 50%)
            recent_losses: Number of recent consecutive losses
            signal_strength: Signal strength (0-100)
            existing_positions_value: Value of existing open positions
            
        Returns:
            Position size in contracts
        """
        # Calculate available funds after reserve
        available_funds = self.calculate_available_funds(available_balance)
        
        # Calculate minimum funds needed for 1 contract
        min_funds_needed = (current_price / leverage) if current_price > 0 else 1.0
        
        if available_funds < min_funds_needed:
            logger.warning(f"Insufficient funds: ${available_funds:.2f} (need at least ${min_funds_needed:.2f} for 1 contract)")
            return 0
        
        # Calculate risk score
        risk_score = self.calculate_risk_score(volatility, win_rate, recent_losses, signal_strength)
        
        # Get risk tier
        risk_tier = self.get_risk_tier(volatility)
        tier_multiplier = self.risk_tiers[risk_tier]['size_multiplier']
        
        # Calculate base position size
        position_size_percent = self.base_position_size_percent * risk_score * tier_multiplier
        
        # Clamp to min/max
        position_size_percent = max(
            self.min_position_size_percent,
            min(self.max_position_size_percent, position_size_percent)
        )
        
        # Reduce size if we have existing positions (diversification)
        if existing_positions_value > 0:
            exposure_ratio = existing_positions_value / available_balance
            if exposure_ratio > 0.5:  # Already have 50%+ exposure
                position_size_percent *= 0.7  # Reduce new position by 30%
        
        # Calculate position value
        position_value = available_funds * (position_size_percent / 100)
        
        # Apply leverage
        position_value_with_leverage = position_value * leverage
        
        # Calculate number of contracts
        size = int(position_value_with_leverage / current_price)
        
        # Minimum size is 1
        size = max(1, size)
        
        # Log the calculation
        logger.info(f"Position sizing calculation:")
        logger.info(f"  Available balance: ${available_balance:.2f}")
        logger.info(f"  Available funds (after reserve): ${available_funds:.2f}")
        logger.info(f"  Risk score: {risk_score:.2f}")
        logger.info(f"  Risk tier: {risk_tier} (multiplier: {tier_multiplier})")
        logger.info(f"  Position size %: {position_size_percent:.2f}%")
        logger.info(f"  Position value: ${position_value:.2f}")
        logger.info(f"  Leverage: {leverage}x")
        logger.info(f"  Contracts: {size}")
        
        return size
    
    def should_allow_trade(
        self,
        available_balance: float,
        position_value: float,
        recent_losses: int = 0,
        max_drawdown_percent: float = 30.0
    ) -> tuple[bool, str]:
        """Check if a trade should be allowed based on current conditions
        
        Args:
            available_balance: Current available balance
            position_value: Value of the proposed position
            recent_losses: Number of recent consecutive losses
            max_drawdown_percent: Maximum allowed drawdown
            
        Returns:
            Tuple of (should_allow, reason)
        """
        # Check minimum balance - must have enough for the proposed position
        available_funds = self.calculate_available_funds(available_balance)
        
        # Instead of a fixed $1 check, verify we have enough for the position
        # Allow trades as long as we have some funds available (even if less than $1)
        if available_funds <= 0:
            return False, f"Insufficient funds after reserve: ${available_funds:.2f}"
        
        # Check if position value is reasonable relative to available funds
        if position_value > available_funds:
            return False, f"Position too large: ${position_value:.2f} exceeds available funds ${available_funds:.2f}"
        
        # Check recent losses (circuit breaker)
        if recent_losses >= 5:
            return False, f"Too many recent losses ({recent_losses}), taking a break"
        
        # If losses are mounting, require smaller positions
        if recent_losses >= 3:
            max_value = available_funds * (self.min_position_size_percent / 100)
            if position_value > max_value:
                return False, f"After {recent_losses} losses, only allowing minimum position size"
        
        return True, "Trade allowed"
    
    def get_position_adjustment_factor(
        self,
        current_pnl_percent: float,
        unrealized_pnl: float
    ) -> float:
        """Calculate factor to adjust position size based on current P&L
        
        Args:
            current_pnl_percent: Current P&L as percentage
            unrealized_pnl: Unrealized P&L value
            
        Returns:
            Adjustment factor (0.5 to 1.5)
        """
        # If doing well, can increase size slightly
        if unrealized_pnl > 0 and current_pnl_percent > 5:
            return 1.2
        
        # If losing, reduce size
        if unrealized_pnl < 0 and current_pnl_percent < -5:
            return 0.7
        
        # Neutral
        return 1.0
    
    def calculate_max_loss(
        self,
        position_size: int,
        entry_price: float,
        leverage: int,
        stop_loss_percent: float
    ) -> float:
        """Calculate maximum potential loss for a position
        
        Args:
            position_size: Size in contracts
            entry_price: Entry price
            leverage: Trading leverage
            stop_loss_percent: Stop loss percentage
            
        Returns:
            Maximum loss in USD
        """
        position_value = position_size * entry_price
        margin = position_value / leverage
        max_loss = margin * (stop_loss_percent / 100)
        
        return max_loss
