"""
Test Real Web Search + NLP

LLM yok! Sadece gerçek web search + NLP processing.
"""

import asyncio
import sys


async def test_real_web_search():
    """Test gerçek web araması"""
    print("\n" + "="*70)
    print("VELOCITY - REAL WEB SEARCH TEST")
    print("="*70)
    print("\nLLM YOK! Sadece:")
    print("  [OK] Google/Bing/DuckDuckGo web search")
    print("  [OK] NLP-based text processing (TF-IDF, extractive summarization)")
    print("  [OK] Epistemically sound synthesis")
    print("="*70)
    
    try:
        from velocity.core.velocity_core import VelocityCore
        
        # Initialize (API keys from environment if available)
        core = VelocityCore(
            max_hypotheses=2,
            confidence_threshold=0.6,
            max_iterations=2
        )
        
        # Test queries
        queries = [
            "What is quantum computing?",
            "python vs javascript",
        ]
        
        for query in queries:
            print(f"\n{'='*70}")
            print(f"QUERY: {query}")
            print('='*70)
            
            try:
                result = await core.execute(query)
                
                print(f"\n[RESULT]")
                print(f"  Intent Type: {result.get('intent', {}).get('type', 'N/A')}")
                print(f"  Confidence: {result['confidence']:.1%}")
                print(f"  Uncertainty: {result.get('uncertainty', 'N/A')}")
                
                # Show decision (truncated)
                decision = result['decision']
                lines = decision.split('\n')
                for line in lines[:8]:
                    print(f"  {line}")
                if len(lines) > 8:
                    print("  ...")
                
                # Show sources
                print(f"\n[SOURCES]")
                sources = result.get('source_breakdown', {})
                for source, count in sources.items():
                    print(f"  - {source}: {count} queries")
                    
            except Exception as e:
                print(f"\n[ERROR] {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*70}")
        print("TEST COMPLETE")
        print("="*70)
        
        print("\n💡 NOT:")
        print("  - API keys yoksa DuckDuckGo HTML scraping kullanılır")
        print("  - API keys için: export GOOGLE_API_KEY=... vb.")
        print("  - Detaylar: REAL_WEB_SEARCH.md")
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nYükleme gerekli:")
        print("  pip install beautifulsoup4 requests spacy nltk scikit-learn")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_real_web_search())
