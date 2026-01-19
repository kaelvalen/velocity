"""
Basit demo - hemen çalışır
"""

import asyncio
import sys


async def quick_demo():
    """Hızlı demo"""
    print("\n" + "="*70)
    print("VELOCITY - QUICK DEMO")
    print("="*70)
    print("\nSistem hazırlanıyor...")
    
    try:
        from velocity.core.velocity_core import VelocityCore
        
        core = VelocityCore(
            max_hypotheses=2,
            max_iterations=2
        )
        
        print("[OK] Velocity hazır!\n")
        
        # Basit test query
        query = "What is Python?"
        
        print(f"Soru: {query}")
        print("Cevap bulunuyor...\n")
        
        result = await core.execute(query)
        
        print("="*70)
        print("SONUC")
        print("="*70)
        
        # Decision (ilk 500 karakter)
        decision = result['decision']
        print(f"\nYanıt:")
        print(decision[:500])
        if len(decision) > 500:
            print("...")
        
        print(f"\nGüven: {result['confidence']:.1%}")
        print(f"Belirsizlik: {result.get('uncertainty', 'N/A')}")
        
        # Sources
        sources = result.get('source_breakdown', {})
        print(f"\nKaynaklar:")
        for source, count in sources.items():
            print(f"  - {source}: {count} sorgu")
        
        print("\n" + "="*70)
        print("[OK] Test tamamlandı!")
        print("="*70)
        
    except Exception as e:
        print(f"\n[HATA] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\nVelocity başlatılıyor...")
    asyncio.run(quick_demo())
