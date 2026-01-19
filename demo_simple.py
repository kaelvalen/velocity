"""
Simple demo - runs immediately
"""

import asyncio
import sys


async def quick_demo():
    """Quick demo"""
    print("\n" + "="*70)
    print("VELOCITY - QUICK DEMO")
    print("="*70)
    print("\nPreparing system...")
    
    try:
        from velocity.core.velocity_core import VelocityCore
        
        core = VelocityCore(
            max_hypotheses=2,
            max_iterations=2
        )
        
        print("[OK] Velocity ready!\n")
        
        # Simple test query
        query = "What is Python?"
        
        print(f"Question: {query}")
        print("Finding answer...\n")
        
        result = await core.execute(query)
        
        print("="*70)
        print("RESULT")
        print("="*70)
        
        # Decision (first 500 characters)
        decision = result['decision']
        print(f"\nAnswer:")
        print(decision[:500])
        if len(decision) > 500:
            print("...")
        
        print(f"\nConfidence: {result['confidence']:.1%}")
        print(f"Uncertainty: {result.get('uncertainty', 'N/A')}")
        
        # Sources
        sources = result.get('source_breakdown', {})
        print(f"\nSources:")
        for source, count in sources.items():
            print(f"  - {source}: {count} queries")
        
        print("\n" + "="*70)
        print("[OK] Test completed!")
        print("="*70)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\nStarting Velocity...")
    asyncio.run(quick_demo())
