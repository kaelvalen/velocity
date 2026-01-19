"""
Test all supported programming languages
"""

import asyncio
from velocity.core.velocity_core import VelocityCore


async def test_all_languages():
    """Test code generation for all supported languages"""
    core = VelocityCore(
        max_hypotheses=2,
        confidence_threshold=0.6,
        max_iterations=2
    )
    
    test_queries = [
        "html yaz",
        "css kodu yaz",
        "python kodu yaz",
        "javascript kodu yaz",
        "c kodu yaz",
        "java kodu yaz",
        "go kodu yaz",
        "php kodu yaz",
        "sql yaz",
    ]
    
    print("\n" + "="*70)
    print("VELOCITY - ALL LANGUAGE SUPPORT TEST")
    print("="*70)
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"QUERY: {query}")
        print('='*70)
        
        result = await core.execute(query)
        
        # Extract language from response
        decision = result['decision']
        
        # Check if correct language is detected
        print(f"\n[RESULT]")
        
        # Show first 100 chars of response
        lines = decision.split('\n')
        for line in lines[:5]:
            print(line)
        print("...")
        
        print(f"\n[META]")
        print(f"  Type: {result.get('intent', {}).get('type', 'N/A')}")
        print(f"  Confidence: {result['confidence']:.1%}")
        
        # Verify correct language
        query_lang = query.split()[0].lower()
        if query_lang in decision.lower()[:200]:
            print(f"  ✅ Correct language detected!")
        else:
            print(f"  ⚠️  Language mismatch?")
        
        print('='*70)


if __name__ == "__main__":
    asyncio.run(test_all_languages())
