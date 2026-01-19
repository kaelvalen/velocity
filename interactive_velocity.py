"""
VELOCITY - INTERACTIVE MODE

Terminal'den soru sor, Velocity yanit versin!
"""

import asyncio
import sys
from velocity.core.velocity_core import VelocityCore


async def ask_velocity(question: str, core: VelocityCore):
    """Velocity'ye soru sor ve yanitini goster"""
    print(f"\n{'='*70}")
    print(f"SORU: {question}")
    print('='*70)
    print("\n[PROCESSING...] Velocity dusunuyor...")
    
    try:
        result = await core.execute(question)
        
        print(f"\n[YANIT]")
        print(result['decision'])
        
        print(f"\n[DETAYLAR]")
        print(f"  Guven: {result['confidence']:.1%}")
        print(f"  Belirsizlik: {result['uncertainty']}")
        print(f"  Kanit sayisi: {len(result['evidence'])} parca")
        
        if result['source_breakdown']:
            print(f"  Kaynaklar:")
            for source, count in result['source_breakdown'].items():
                print(f"    - {source}: {count} sorgu")
        
        print('='*70)
        
        return result
        
    except Exception as e:
        print(f"\n[HATA] {e}")
        print('='*70)
        return None


async def interactive_mode():
    """Interactive mode - soru-cevap dongusu"""
    print("\n" + "="*70)
    print("VELOCITY - INTERACTIVE MODE")
    print("="*70)
    print("\nVelocity network-native cognitive engine")
    print("Her soruda 7 adimlik cognitive loop calisiyor!\n")
    print("Komutlar:")
    print("  - Soru yaz ve Enter'a bas")
    print("  - 'exit' veya 'quit' yaz cikmak icin")
    print("  - 'help' yaz yardim icin")
    print("\n" + "="*70)
    
    # Core engine'i bir kez initialize et (performance icin)
    core = VelocityCore(
        max_hypotheses=2,
        confidence_threshold=0.6,
        max_iterations=3,
        budget_per_hypothesis=3.0
    )
    
    print("\n[OK] Velocity hazir! Soru sorabilirsin.\n")
    
    question_count = 0
    
    while True:
        try:
            # Kullanicidan input al
            user_input = input(f"\n[{question_count + 1}] Sorunuz: ").strip()
            
            # Bos input kontrolu
            if not user_input:
                continue
            
            # Exit komutlari
            if user_input.lower() in ['exit', 'quit', 'q', 'cikis']:
                print("\n[BYE] Velocity kapatiliyor...")
                print(f"Toplam {question_count} soru soruldu.\n")
                break
            
            # Help komutu
            if user_input.lower() in ['help', 'yardim', 'h']:
                print("\n[HELP]")
                print("Velocity'ye herhangi bir soru sorabilirsin:")
                print("  - 'What is ...?' (factual)")
                print("  - 'Compare A vs B' (comparative)")
                print("  - 'Should I ...?' (strategic)")
                print("  - 'How to ...?' (procedural)")
                print("\nVelocity otomatik olarak:")
                print("  1. Soruyu analiz eder (intent parsing)")
                print("  2. En iyi kaynaklari secer (epistemic routing)")
                print("  3. Paralel hipotezler uretir")
                print("  4. Network'u sorgular")
                print("  5. Celiski kontrol eder")
                print("  6. Zayif hipotezleri eler")
                print("  7. Final yaniti sentezler")
                continue
            
            # Soruyu sor
            question_count += 1
            await ask_velocity(user_input, core)
            
        except KeyboardInterrupt:
            print("\n\n[INTERRUPTED] Ctrl+C algilandi.")
            print(f"Toplam {question_count} soru soruldu.\n")
            break
        except EOFError:
            print("\n\n[EOF] Input stream kapandi.")
            break
        except Exception as e:
            print(f"\n[HATA] Beklenmeyen hata: {e}")
            continue


async def main():
    """Ana fonksiyon"""
    # Eger arguman verilmisse direkt o soruyu sor
    if len(sys.argv) > 1:
        question = ' '.join(sys.argv[1:])
        core = VelocityCore()
        await ask_velocity(question, core)
    else:
        # Yoksa interactive mode'a gec
        await interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[EXIT] Velocity kapatildi.\n")
