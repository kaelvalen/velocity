"""
Quick demo - Velocity'ye soru sor, yanitini gor!
"""

import asyncio
from velocity.core.velocity_core import VelocityCore


async def ask_velocity(question: str):
    """Velocity'ye soru sor"""
    print(f"\n{'='*70}")
    print(f"SORU: {question}")
    print('='*70)
    
    core = VelocityCore(
        max_hypotheses=2,
        confidence_threshold=0.6,
        max_iterations=3
    )
    
    result = await core.execute(question)
    
    print(f"\n[YANIT]")
    print(result['decision'])
    
    print(f"\n[DETAYLAR]")
    print(f"  Guven: {result['confidence']:.1%}")
    print(f"  Belirsizlik: {result['uncertainty']}")
    print(f"  Kanit: {len(result['evidence'])} parca")
    print(f"  Kaynaklar: {', '.join(result['source_breakdown'].keys())}")
    
    print('='*70)
    
    return result


async def main():
    print("\nVELOCITY - INTERAKTIF DEMO")
    print("Velocity sorunuza yanit veriyor...\n")
    
    # Ornek sorular
    questions = [
        "What is pornography?",
        "Explain quantum entanglement",
        "Who created Python programming language?"
    ]
    
    for q in questions:
        await ask_velocity(q)
        print("\n")
    
    print("\n[OK] Demo tamamlandi!")
    print("\nVelocity calisiyor ve yanit veriyor! ✓")


if __name__ == "__main__":
    asyncio.run(main())
