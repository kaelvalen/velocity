"""
VELOCITY - INTERACTIVE MODE

Real-time Q&A with the Velocity cognitive engine.
7-step algorithmic loop running on every question!
"""

import asyncio
import time
from velocity.core.velocity_core import VelocityCore
from velocity.synthesis.llm_synthesizer import SynthesisConfig, LLMProvider
from loguru import logger
import sys
import os


# ── ANSI colours (work on all modern terminals) ──────────────────────
_CYAN    = "\033[96m"
_GREEN   = "\033[92m"
_YELLOW  = "\033[93m"
_MAGENTA = "\033[95m"
_DIM     = "\033[2m"
_BOLD    = "\033[1m"
_RESET   = "\033[0m"
_BLUE    = "\033[94m"

_LINE = f"{_DIM}{'─' * 70}{_RESET}"


async def ask_velocity(question: str, core: VelocityCore) -> dict:
    """
    Ask Velocity a question and display a beautifully formatted answer.
    """
    print(f"\n{_LINE}")
    print(f"  {_BOLD}{_CYAN}Q:{_RESET}  {question}")
    print(_LINE)

    t0 = time.time()
    print(f"\n  {_DIM}⏳ Velocity is thinking…{_RESET}", end="", flush=True)

    try:
        result = await core.execute(question)
        elapsed = time.time() - t0
        # Clear the "thinking…" line
        print(f"\r  {_DIM}✓ Ready ({elapsed:.1f}s){_RESET}          ")

        # ── Print the answer ────────────────────────────────────────
        print()
        print(f"  {_LINE}")
        decision = result['decision']

        # Indent every line for clean presentation
        for line in decision.splitlines():
            line = line.rstrip()
            if line.startswith("Key Facts:"):
                print(f"  {_YELLOW}{_BOLD}{line}{_RESET}")
            elif line.strip().startswith("•"):
                print(f"  {_GREEN}{line}{_RESET}")
            elif line.startswith("Sources:"):
                print(f"  {_DIM}{line}{_RESET}")
            elif line.startswith("Confidence:"):
                # Colour-code by confidence level
                colour = _GREEN if "High" in line else _YELLOW if "Moderate" in line else _MAGENTA
                print(f"  {colour}{line}{_RESET}")
            elif line == "":
                print()
            else:
                print(f"  {line}")
        print(f"  {_LINE}")
        print()

        return result

    except Exception as e:
        elapsed = time.time() - t0
        print(f"\r  {_MAGENTA}✗ Error ({elapsed:.1f}s){_RESET}          ")
        print(f"\n  {_MAGENTA}[ERROR] {e}{_RESET}")
        logger.error(f"Query failed: {e}")
        raise


async def interactive_mode():
    """Interactive Q&A mode with a polished terminal interface."""
    # ── Banner ───────────────────────────────────────────────────
    print()
    print(f"  {_BOLD}{_CYAN}╔══════════════════════════════════════════════════════════════╗{_RESET}")
    print(f"  {_BOLD}{_CYAN}║{_RESET}   {_BOLD}VELOCITY{_RESET}  —  Network-Native Epistemic Intelligence       {_BOLD}{_CYAN}║{_RESET}")
    print(f"  {_BOLD}{_CYAN}╚══════════════════════════════════════════════════════════════╝{_RESET}")
    print(f"  {_DIM}Ask anything. Velocity searches the web, verifies facts,{_RESET}")
    print(f"  {_DIM}and synthesises a calibrated answer in real-time.{_RESET}")
    print(f"  {_DIM}Type 'exit' to quit  •  'help' for commands{_RESET}")
    print()

    # ── Init engine ──────────────────────────────────────────────
    print(f"  {_DIM}[init] Checking LLM backend…{_RESET}")

    llm_config = SynthesisConfig(
        provider=LLMProvider.OLLAMA,
        model="qwen3:8b",
        temperature=0.3,
        max_tokens=500,
        ollama_host="http://localhost:11434",
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

        if core.llm_synthesizer:
            is_available = await core.llm_synthesizer.health_check()
            if is_available:
                print(f"  {_GREEN}✓ Qwen3 8B connected (Hybrid mode){_RESET}")
            else:
                print(f"  {_YELLOW}⚠ Ollama offline → Pure NNEI mode{_RESET}")
                print(f"  {_DIM}  (start Ollama for LLM-enhanced answers){_RESET}")

    except Exception as e:
        print(f"  {_YELLOW}⚠ LLM init failed → Pure NNEI mode{_RESET}")
        core = VelocityCore(
            max_hypotheses=2,
            confidence_threshold=0.6,
            max_iterations=3,
            enable_llm=False
        )

    print(f"  {_GREEN}✓ Velocity ready{_RESET}\n")

    question_count = 0

    while True:
        try:
            question_count += 1
            user_input = input(f"  {_BOLD}{_BLUE}[{question_count}] ❯{_RESET} ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'q']:
                print(f"\n  {_DIM}Goodbye! 👋{_RESET}\n")
                break

            if user_input.lower() == 'help':
                print(f"\n{_LINE}")
                print(f"  {_BOLD}VELOCITY — Help{_RESET}")
                print(f"{_LINE}")
                print(f"  {_CYAN}Pipeline:{_RESET}")
                print(f"    1. Parse intent          5. Detect contradictions")
                print(f"    2. Route to sources       6. Eliminate weak hypotheses")
                print(f"    3. Generate hypotheses    7. Synthesise answer")
                print(f"    4. Interrogate the web    8. LLM polish (optional)")
                print()
                print(f"  {_CYAN}Examples:{_RESET}")
                print(f"    • What is quantum computing?")
                print(f"    • Python nedir?")
                print(f"    • Compare React vs Vue")
                print(f"    • Atatürk kimdir?")
                print()
                print(f"  {_CYAN}Commands:{_RESET}")
                print(f"    exit / quit / q — Exit program")
                print(f"    help            — Show this help")
                print(f"{_LINE}\n")
                continue

            await ask_velocity(user_input, core)

        except KeyboardInterrupt:
            print(f"\n\n  {_DIM}Interrupted. Goodbye! 👋{_RESET}\n")
            break
        except EOFError:
            print(f"\n\n  {_DIM}End of input. Goodbye! 👋{_RESET}\n")
            break
        except Exception as e:
            print(f"\n  {_MAGENTA}[ERROR] {e}{_RESET}")
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
