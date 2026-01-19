"""
Test code generation improvements
"""

import asyncio
from velocity.core.velocity_core import VelocityCore


async def test_code_generation():
    """Test that code generation works correctly for different languages"""
    core = VelocityCore(
        max_hypotheses=2,
        confidence_threshold=0.6,
        max_iterations=2
    )
    
    test_queries = [
        "bir python kodu yaz",
        "bir c kodu yaz",
        "javascript kodu yaz",
        "python nedir",  # Not code generation
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"SORU: {query}")
        print('='*70)
        
        result = await core.execute(query)
        
        # Extract just the answer, not the full hypothesis text
        decision = result['decision']
        
        # Show full response
        print(f"\n[YANIT]")
        print(decision)
        
        print(f"\n[META]")
        print(f"  Confidence: {result['confidence']:.1%}")
        print(f"  Sources: {list(result['source_breakdown'].keys())}")
        print('='*70)


if __name__ == "__main__":
    asyncio.run(test_code_generation())
