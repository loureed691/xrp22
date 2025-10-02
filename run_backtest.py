"""
Backtesting Script
Run backtests on historical data
"""
import logging
import json
from datetime import datetime, timedelta
import os

from config import Config
from backtesting import BacktestEngine
from kucoin_client import KuCoinFuturesClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def fetch_historical_data(symbol: str = 'XRPUSDTM', days: int = 30):
    """Fetch historical data from KuCoin
    
    Args:
        symbol: Trading pair symbol
        days: Number of days of historical data
        
    Returns:
        List of kline data
    """
    logger.info(f"Fetching {days} days of historical data for {symbol}...")
    
    try:
        client = KuCoinFuturesClient(
            Config.API_KEY,
            Config.API_SECRET,
            Config.API_PASSPHRASE,
            Config.API_URL
        )
        
        # Calculate time range
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        # Fetch klines (5-minute candles)
        klines = client.get_klines(
            symbol=symbol,
            granularity=5,
            from_time=start_time,
            to_time=end_time
        )
        
        logger.info(f"Fetched {len(klines)} candles")
        return klines
        
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        return []


def run_backtest(initial_balance: float = 100.0, leverage: int = 11, 
                days: int = 30, symbol: str = 'XRPUSDTM'):
    """Run backtest with specified parameters
    
    Args:
        initial_balance: Starting balance
        leverage: Leverage multiplier
        days: Days of historical data
        symbol: Trading pair symbol
    """
    logger.info("=" * 60)
    logger.info("BACKTESTING SESSION")
    logger.info("=" * 60)
    logger.info(f"Symbol: {symbol}")
    logger.info(f"Initial balance: ${initial_balance}")
    logger.info(f"Leverage: {leverage}x")
    logger.info(f"Period: {days} days")
    logger.info("=" * 60)
    
    # Fetch historical data
    klines = fetch_historical_data(symbol, days)
    
    if len(klines) < 30:
        logger.error("Insufficient historical data for backtesting")
        return
    
    # Initialize backtest engine
    engine = BacktestEngine(
        initial_balance=initial_balance,
        leverage=leverage,
        stop_loss_percent=Config.STOP_LOSS_PERCENT,
        take_profit_percent=Config.TAKE_PROFIT_PERCENT,
        trailing_stop_percent=Config.TRAILING_STOP_PERCENT,
        max_position_size_percent=Config.MAX_POSITION_SIZE_PERCENT
    )
    
    # Run backtest
    results = engine.run_backtest(
        klines,
        rsi_oversold=Config.RSI_OVERSOLD,
        rsi_overbought=Config.RSI_OVERBOUGHT
    )
    
    # Print results
    logger.info("\n" + "=" * 60)
    logger.info("BACKTEST RESULTS")
    logger.info("=" * 60)
    logger.info(f"Total trades: {results['total_trades']}")
    logger.info(f"Winning trades: {results['winning_trades']}")
    logger.info(f"Losing trades: {results['losing_trades']}")
    logger.info(f"Win rate: {results['win_rate']:.2f}%")
    logger.info(f"Total P&L: ${results['total_pnl']:.2f}")
    logger.info(f"Final balance: ${results['final_balance']:.2f}")
    logger.info(f"ROI: {results['roi']:.2f}%")
    logger.info(f"Max drawdown: {results['max_drawdown']:.2f}%")
    logger.info("=" * 60)
    
    # Save results
    os.makedirs('bot_data', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"bot_data/backtest_{symbol}_{timestamp}.json"
    engine.save_results(filename)
    logger.info(f"\nResults saved to: {filename}")
    
    return results


def compare_strategies():
    """Compare different strategy configurations"""
    logger.info("Running strategy comparison...")
    
    configs = [
        {'leverage': 5, 'name': 'Conservative (5x)'},
        {'leverage': 11, 'name': 'Standard (11x)'},
        {'leverage': 20, 'name': 'Aggressive (20x)'}
    ]
    
    results_comparison = []
    
    for config in configs:
        logger.info(f"\nTesting: {config['name']}")
        results = run_backtest(
            initial_balance=100.0,
            leverage=config['leverage'],
            days=30
        )
        
        results_comparison.append({
            'name': config['name'],
            'leverage': config['leverage'],
            'roi': results['roi'],
            'win_rate': results['win_rate'],
            'max_drawdown': results['max_drawdown']
        })
    
    # Print comparison
    logger.info("\n" + "=" * 60)
    logger.info("STRATEGY COMPARISON")
    logger.info("=" * 60)
    for result in results_comparison:
        logger.info(f"\n{result['name']}:")
        logger.info(f"  ROI: {result['roi']:.2f}%")
        logger.info(f"  Win rate: {result['win_rate']:.2f}%")
        logger.info(f"  Max drawdown: {result['max_drawdown']:.2f}%")
    logger.info("=" * 60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run backtesting on historical data')
    parser.add_argument('--balance', type=float, default=100.0, 
                       help='Initial balance (default: 100)')
    parser.add_argument('--leverage', type=int, default=11,
                       help='Leverage multiplier (default: 11)')
    parser.add_argument('--days', type=int, default=30,
                       help='Days of historical data (default: 30)')
    parser.add_argument('--symbol', type=str, default='XRPUSDTM',
                       help='Trading pair symbol (default: XRPUSDTM)')
    parser.add_argument('--compare', action='store_true',
                       help='Compare different strategies')
    
    args = parser.parse_args()
    
    try:
        if args.compare:
            compare_strategies()
        else:
            run_backtest(
                initial_balance=args.balance,
                leverage=args.leverage,
                days=args.days,
                symbol=args.symbol
            )
    except Exception as e:
        logger.error(f"Backtesting failed: {e}", exc_info=True)


if __name__ == '__main__':
    main()
