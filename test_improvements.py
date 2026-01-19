"""
Test Velocity improvements
"""

import asyncio
from velocity.core.velocity_core import VelocityCore


async def test_improvements():
    """Test improved responses"""
    core = VelocityCore(
        max_hypotheses=2,
        confidence_threshold=0.6,
        max_iterations=3
    )
    
    test_queries = [
        "bir python kodu yaz",
        "python nedir",
        "what is quantum computing",
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"QUERY: {query}")
        print('='*70)
        
        result = await core.execute(query)
        
        print(f"\nDecision Type: {result.get('decision_type', 'N/A')}")
        print(f"Confidence: {result['confidence']:.1%}")
        print(f"\nRESPONSE:")
        print(result['decision'][:300] + "..." if len(result['decision']) > 300 else result['decision'])
        print('='*70)


if __name__ == "__main__":
    asyncio.run(test_improvements())
