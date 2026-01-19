"""
VELOCITY - INTERACTIVE MODE

Real-time Q&A with the Velocity cognitive engine.
7-step algorithmic loop running on every question!
"""

import asyncio
from velocity.core.velocity_core import VelocityCore
from velocity.synthesis.llm_synthesizer import SynthesisConfig, LLMProvider
from loguru import logger
import sys
import os


async def ask_velocity(question: str, core: VelocityCore) -> dict:
    """
    Ask Velocity a question
    
    Args:
        question: User question
        core: Velocity core engine
        
    Returns:
        Result dictionary
    """
    print(f"\n{'='*70}")
    print(f"QUESTION: {question}")
    print('='*70)
    
    print("\n[PROCESSING...] Velocity is thinking...")
    
    try:
        result = await core.execute(question)
        
        # Display answer naturally (ChatGPT-like)
        print("\n" + "="*70)
        
        decision = result['decision']
        
        # Word wrap for better readability
        import textwrap
        wrapped_lines = textwrap.fill(decision, width=68, break_long_words=False, break_on_hyphens=False)
        print(wrapped_lines)
        
        # Simplified confidence indicator (subtle)
        confidence = result['confidence']
        if confidence >= 0.7:
            print("\n(High confidence)")
        elif confidence >= 0.5:
            print("\n(Moderate confidence)")
        else:
            print("\n(Low confidence)")
        
        print("="*70)
        
        return result
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        logger.error(f"Query failed: {e}")
        raise


async def interactive_mode():
    """
    Interactive Q&A mode
    
    User can ask unlimited questions.
    Velocity answers using the 7-step cognitive loop.
    """
    print("\n" + "="*70)
    print("VELOCITY - INTERACTIVE MODE (HYBRID)")
    print("="*70)
    print("\nVelocity: Network-Native Epistemic Intelligence")
    print("Mode: NNEI + Qwen3 8B (Natural Language)")
    print("\nCommands:")
    print("  - Type a question and press Enter")
    print("  - Type 'exit' or 'quit' to exit")
    print("  - Type 'help' for help")
    print("\n" + "="*70)
    
    # Configure LLM (Qwen3 8B)
    print("\n[INIT] Checking Ollama...")
    
    llm_config = SynthesisConfig(
        provider=LLMProvider.OLLAMA,
        model="qwen3:8b",
        temperature=0.3,
        max_tokens=500,
        ollama_host="http://localhost:11434",
        fallback_to_raw=True
    )
    
    # Initialize Velocity with Hybrid mode
    try:
        core = VelocityCore(
            max_hypotheses=2,
            confidence_threshold=0.6,
            max_iterations=3,
            llm_config=llm_config,
            enable_llm=True  # Hybrid mode
        )
        
        # Check if Ollama is available
        if core.llm_synthesizer:
            is_available = await core.llm_synthesizer.health_check()
            if is_available:
                print("[OK] Qwen3 8B connected! (Hybrid mode active)")
            else:
                print("[WARNING] Ollama not running, using pure NNEI mode")
                print("         (To enable hybrid: Start Ollama and restart)")
        
    except Exception as e:
        print(f"[WARNING] LLM init failed: {e}")
        print("[OK] Falling back to pure NNEI mode")
        core = VelocityCore(
            max_hypotheses=2,
            confidence_threshold=0.6,
            max_iterations=3,
            enable_llm=False
        )
    
    print("\n[OK] Velocity ready! You can ask questions now.")
    
    question_count = 0
    
    while True:
        try:
            # Get user input
            question_count += 1
            user_input = input(f"\n\n[{question_count}] Your question: ").strip()
            
            # Handle commands
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n[OK] Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\nVELOCITY HELP")
                print("="*70)
                print("\nMode: Hybrid (NNEI + Qwen3 8B)")
                print("  - Facts from web (NNEI)")
                print("  - Natural language (Qwen3 8B)")
                print("  - Always sourced, never hallucinates")
                print("\nHow to use:")
                print("  1. Type any question")
                print("  2. Velocity will:")
                print("     [1/7] Parse intent")
                print("     [2/7] Route to epistemic sources")
                print("     [3/7] Generate parallel hypotheses")
                print("     [4/7] Interrogate network (web search)")
                print("     [5/7] Handle contradictions")
                print("     [6/7] Eliminate weak hypotheses")
                print("     [7/7] Synthesize final state")
                print("     [8/8] Format with Qwen3 (natural language)")
                print("  3. Get natural, calibrated answer with confidence")
                print("\nExamples:")
                print("  - What is quantum computing?")
                print("  - Python nedir?")
                print("  - Compare React vs Vue")
                print("  - Atatürk kimdir?")
                print("\nCommands:")
                print("  - 'exit' or 'quit': Exit program")
                print("  - 'help': Show this help")
                print("="*70)
                continue
            
            # Process question
            await ask_velocity(user_input, core)
            
        except KeyboardInterrupt:
            print("\n\n[OK] Interrupted. Goodbye!")
            break
        except EOFError:
            print("\n\n[OK] End of input. Goodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] {e}")
            logger.error(f"Interactive mode error: {e}")
            continue


async def main():
    """Main entry point"""
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Single question mode
        question = ' '.join(sys.argv[1:])
        
        # Configure Qwen3 for single question too
        llm_config = SynthesisConfig(
            provider=LLMProvider.OLLAMA,
            model="qwen3:8b",
            temperature=0.3,
            fallback_to_raw=True
        )
        
        try:
            core = VelocityCore(
                max_hypotheses=2,
                confidence_threshold=0.6,
                max_iterations=3,
                llm_config=llm_config,
                enable_llm=True
            )
        except:
            # Fallback to pure NNEI
            core = VelocityCore(
                max_hypotheses=2,
                confidence_threshold=0.6,
                max_iterations=3,
                enable_llm=False
            )
        
        await ask_velocity(question, core)
    else:
        # Interactive mode
        await interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[OK] Goodbye!")
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
