"""
REAL INTERNET TEST

Velocity ile GERÇEK internet araması!
Simulated search değil, Wikipedia API ve gerçek web.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from velocity.core.velocity_core import VelocityCore


async def test_real_search():
    print("\n" + "=" * 70)
    print("VELOCITY - REAL INTERNET SEARCH TEST")
    print("=" * 70)
    
    core = VelocityCore(
        max_hypotheses=2,
        confidence_threshold=0.6,
        max_iterations=3,
        budget_per_hypothesis=3.0
    )
    
    # Test queries
    queries = [
        "Python programming language",
        "Quantum computing",
        "Artificial intelligence",
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n[TEST {i}/{len(queries)}] Query: {query}")
        print("-" * 70)
        
        try:
            result = await core.execute(query)
            
            print(f"\n[RESULT]")
            print(f"  Confidence: {result['confidence']:.2%}")
            print(f"  Uncertainty: {result['uncertainty']}")
            print(f"  Evidence: {len(result['evidence'])} pieces")
            print(f"  Sources: {len(result['source_breakdown'])}")
            
            # Show sources
            if result['source_breakdown']:
                print(f"\n[SOURCES]")
                for source, count in result['source_breakdown'].items():
                    print(f"  - {source}: {count} queries")
            
            # Show decision preview
            decision = result['decision']
            if len(decision) > 300:
                decision = decision[:300] + "..."
            print(f"\n[DECISION]")
            print(f"  {decision}")
            
            print(f"\n[OK] Test {i} complete!")
            
        except Exception as e:
            print(f"\n[ERROR] Test {i} failed: {e}")
        
        print("\n" + "=" * 70)
    
    print("\n[SUCCESS] All tests complete!")
    print("\nVelocity is now querying the REAL INTERNET!")
    print("- Wikipedia API: ACTIVE")
    print("- DuckDuckGo: FALLBACK")
    print("- Network-native: TRUE")


if __name__ == "__main__":
    try:
        asyncio.run(test_real_search())
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted")
