"""
Quick demo - Ask Velocity a question, see the answer!
"""

import asyncio
from velocity.core.velocity_core import VelocityCore


async def ask_velocity(question: str):
    """Ask Velocity a question"""
    print(f"\n{'='*70}")
    print(f"QUESTION: {question}")
    print('='*70)
    
    core = VelocityCore(
        max_hypotheses=2,
        confidence_threshold=0.6,
        max_iterations=3
    )
    
    result = await core.execute(question)
    
    print(f"\n[ANSWER]")
    print(result['decision'])
    
    print(f"\n[DETAILS]")
    print(f"  Confidence: {result['confidence']:.1%}")
    print(f"  Uncertainty: {result['uncertainty']}")
    print(f"  Evidence: {len(result['evidence'])} pieces")
    print(f"  Sources: {', '.join(result['source_breakdown'].keys())}")
    
    print('='*70)
    
    return result


async def main():
    print("\nVELOCITY - INTERACTIVE DEMO")
    print("Velocity answering your questions...\n")
    
    # Example questions
    questions = [
        "What is machine learning?",
        "Explain quantum entanglement",
        "Who created Python programming language?"
    ]
    
    for q in questions:
        await ask_velocity(q)
        print("\n")
    
    print("\n[OK] Demo completed!")
    print("\nVelocity is working and answering! ✓")


if __name__ == "__main__":
    asyncio.run(main())
