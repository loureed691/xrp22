"""
Demo script for best pair selection feature
Shows how the bot automatically selects the most profitable trading pair
"""
import logging
from multi_pair import MultiPairManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_best_pair_selection():
    """Demonstrate automatic best pair selection"""
    print("\n" + "=" * 70)
    print("AUTOMATIC BEST PAIR SELECTION DEMO")
    print("=" * 70)
    
    # Initialize manager with multiple pairs
    pairs = ['XRPUSDTM', 'BTCUSDTM', 'ETHUSDTM', 'SOLUSDTM']
    manager = MultiPairManager(pairs)
    
    print(f"\n📊 Initialized with {len(pairs)} trading pairs:")
    for pair in pairs:
        print(f"  • {pair}")
    
    # Simulate trading history for different pairs
    print("\n🔄 Simulating trading history...")
    
    # XRP: Good performance
    for _ in range(8):
        manager.record_trade_result('XRPUSDTM', 1.5)  # winning trades
    for _ in range(2):
        manager.record_trade_result('XRPUSDTM', -0.8)  # losing trades
    
    # BTC: Excellent performance
    for _ in range(9):
        manager.record_trade_result('BTCUSDTM', 2.0)  # winning trades
    for _ in range(1):
        manager.record_trade_result('BTCUSDTM', -0.5)  # losing trade
    
    # ETH: Average performance
    for _ in range(5):
        manager.record_trade_result('ETHUSDTM', 1.2)  # winning trades
    for _ in range(5):
        manager.record_trade_result('ETHUSDTM', -1.0)  # losing trades
    
    # SOL: Poor performance
    for _ in range(3):
        manager.record_trade_result('SOLUSDTM', 0.8)  # winning trades
    for _ in range(7):
        manager.record_trade_result('SOLUSDTM', -1.2)  # losing trades
    
    # Display pair statistics
    print("\n📈 Pair Performance Statistics:")
    print("-" * 70)
    all_stats = manager.get_all_statistics()
    for pair, stats in all_stats.items():
        print(f"\n{pair}:")
        print(f"  Total Trades: {stats['total_trades']}")
        print(f"  Winning: {stats['winning_trades']}")
        print(f"  Losing: {stats['losing_trades']}")
        print(f"  Win Rate: {stats['win_rate']:.1f}%")
    
    # Show pair rankings
    print("\n🏆 Pair Performance Rankings:")
    print("-" * 70)
    rankings = manager.get_pair_rankings()
    for i, rank in enumerate(rankings, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        print(f"{medal} {rank['symbol']}: "
              f"Win Rate {rank['win_rate']:.1f}%, "
              f"Trades {rank['total_trades']}, "
              f"Score {rank['score']:.3f}")
    
    # Demonstrate different allocation strategies
    balance = 1000.0
    
    print("\n\n💰 ALLOCATION STRATEGIES COMPARISON:")
    print("=" * 70)
    
    # Equal allocation
    print("\n1️⃣  Equal Allocation Strategy:")
    print("   (Splits balance equally across all pairs)")
    print("-" * 70)
    equal_alloc = manager.allocate_balance(balance, 'equal')
    for pair, amount in equal_alloc.items():
        print(f"   {pair}: ${amount:.2f}")
    
    # Weighted allocation
    print("\n2️⃣  Weighted Allocation Strategy:")
    print("   (Allocates based on win rate)")
    print("-" * 70)
    weighted_alloc = manager.allocate_balance(balance, 'weighted')
    for pair, amount in weighted_alloc.items():
        stats = manager.get_pair_statistics(pair)
        print(f"   {pair}: ${amount:.2f} (Win rate: {stats['win_rate']:.1f}%)")
    
    # Dynamic allocation
    print("\n3️⃣  Dynamic Allocation Strategy:")
    print("   (Considers win rate and trade activity)")
    print("-" * 70)
    dynamic_alloc = manager.allocate_balance(balance, 'dynamic')
    for pair, amount in dynamic_alloc.items():
        stats = manager.get_pair_statistics(pair)
        print(f"   {pair}: ${amount:.2f} (Win rate: {stats['win_rate']:.1f}%)")
    
    # Best pair allocation (NEW)
    print("\n4️⃣  Best Pair Allocation Strategy: ⭐ NEW!")
    print("   (Automatically selects and allocates ALL to the best pair)")
    print("-" * 70)
    best_alloc = manager.allocate_balance(balance, 'best')
    best_pair = manager.get_best_pair()
    
    for pair, amount in best_alloc.items():
        if amount > 0:
            stats = manager.get_pair_statistics(pair)
            print(f"   ✅ {pair}: ${amount:.2f} (Win rate: {stats['win_rate']:.1f}%)")
            print(f"      👉 SELECTED AS BEST PAIR!")
        else:
            print(f"   ⚪ {pair}: ${amount:.2f} (Not selected)")
    
    # Summary
    print("\n\n📊 SUMMARY:")
    print("=" * 70)
    print(f"✨ Best Performing Pair: {best_pair}")
    best_stats = manager.get_pair_statistics(best_pair)
    print(f"   • Win Rate: {best_stats['win_rate']:.1f}%")
    print(f"   • Total Trades: {best_stats['total_trades']}")
    print(f"   • Wins: {best_stats['winning_trades']}, Losses: {best_stats['losing_trades']}")
    
    print("\n✅ Benefits of 'best' allocation strategy:")
    print("   • Automatically focuses on most profitable pair")
    print("   • Maximizes returns by avoiding underperforming pairs")
    print("   • Adapts as trading history evolves")
    print("   • No manual intervention needed")
    
    print("\n💡 How to use in your bot:")
    print("   Set in .env file: ALLOCATION_STRATEGY=best")
    print("   Or for multiple pairs: TRADING_PAIRS=XRPUSDTM,BTCUSDTM,ETHUSDTM")
    
    print("\n" + "=" * 70)


def demo_best_pair_with_no_history():
    """Show behavior when there's no trading history"""
    print("\n\n" + "=" * 70)
    print("BEST PAIR SELECTION WITH NO HISTORY")
    print("=" * 70)
    
    pairs = ['XRPUSDTM', 'BTCUSDTM']
    manager = MultiPairManager(pairs)
    
    print(f"\n📊 New trading session with {len(pairs)} pairs (no history yet)")
    
    balance = 500.0
    print(f"\n💰 Using 'best' allocation with ${balance:.2f} balance...")
    
    allocations = manager.allocate_balance(balance, 'best')
    
    print("\n📋 Result:")
    for pair, amount in allocations.items():
        print(f"   {pair}: ${amount:.2f}")
    
    print("\n✅ When no history exists, falls back to equal allocation")
    print("   This ensures all pairs get a chance to prove themselves")
    
    print("\n" + "=" * 70)


def main():
    """Run all demonstrations"""
    try:
        demo_best_pair_selection()
        demo_best_pair_with_no_history()
        
        print("\n\n🎉 Demo completed successfully!")
        print("You can now use ALLOCATION_STRATEGY=best in your .env file")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)


if __name__ == '__main__':
    main()
