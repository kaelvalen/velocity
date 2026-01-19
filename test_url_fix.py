"""
Quick test for URL fix
"""
import asyncio
from velocity.core.velocity_core import VelocityCore

async def test():
    print("\n" + "="*70)
    print("TESTING URL FIX")
    print("="*70)
    print("\nInitializing Velocity with real web search...")
    
    core = VelocityCore(max_hypotheses=2, max_iterations=2)
    
    print("\nAsking: What is Python?\n")
    
    result = await core.execute("What is Python?")
    
    print("\n" + "="*70)
    print("RESULT")
    print("="*70)
    
    decision = result['decision']
    print(f"\nAnswer (first 300 chars):")
    print(decision[:300])
    if len(decision) > 300:
        print("...\n")
    
    print(f"\nConfidence: {result['confidence']:.1%}")
    print(f"Uncertainty: {result['uncertainty']}")
    print(f"\nSources used:")
    for source, count in result['source_breakdown'].items():
        print(f"  - {source}: {count} queries")
    
    # Check if we got full content (not just snippets)
    if len(decision) > 100:
        print(f"\n[SUCCESS] Got full content ({len(decision)} chars)!")
    else:
        print(f"\n[WARNING] Only got snippet ({len(decision)} chars)")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(test())
