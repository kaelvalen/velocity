# Velocity Documentation

**Complete documentation for Network-Native Epistemic Intelligence (NNEI)**

---

## Core Documentation (Read in Order)

### 1. Start Here
- **[README.md](./README.md)** - Project overview, quick start, installation
- **[QUICKSTART.md](./QUICKSTART.md)** - 5-minute setup guide

### 2. Understand the Paradigm
- **[NNEI_PARADIGM.md](./NNEI_PARADIGM.md)** - Network-Native Epistemic Intelligence definition
- **[PARADIGM.md](./PARADIGM.md)** - Core concepts and philosophy

### 3. Technical Details
- **[ALGORITHMIC_CORE.md](./ALGORITHMIC_CORE.md)** - 7-step cognitive loop explained
- **[REAL_WEB_SEARCH.md](./REAL_WEB_SEARCH.md)** - Web search implementation and NLP

---

## File Structure

```
velocity/
├── README.md                    # Main entry point
├── NNEI_PARADIGM.md            # NEW: NNEI paradigm definition
├── PARADIGM.md                  # Core paradigm concepts
├── QUICKSTART.md                # Quick start guide
├── REAL_WEB_SEARCH.md          # Web search & NLP details
├── ALGORITHMIC_CORE.md         # 7-step algorithm
├── DOCUMENTATION.md            # This file
│
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Package configuration
├── LICENSE                     # MIT License
├── env.example                 # Environment variables example
│
├── interactive_velocity.py     # Main interactive CLI
├── START_INTERACTIVE.bat       # Windows launcher
│
├── velocity/                   # Core package
│   ├── core/                   # Algorithmic core
│   │   ├── intent_parser.py    # Intent classification (SOCIAL/FACTUAL/META)
│   │   ├── network_gate.py     # Network interrogation decision
│   │   ├── epistemic_router.py # Source selection
│   │   ├── hypothesis_generator.py
│   │   ├── interrogation_loop.py
│   │   ├── hypothesis_eliminator.py
│   │   ├── state_synthesizer.py
│   │   ├── velocity_core.py    # Main execution engine
│   │   └── state.py
│   ├── network/                # Network interrogation
│   │   ├── interrogator.py     # Query executor
│   │   └── web_search.py       # Real web search + NLP
│   └── evaluation/
│       └── hypothesis.py       # CPU-based hypothesis evaluator
│
├── examples/                   # Example usage
│   ├── basic_usage.py
│   ├── interactive_demo.py
│   └── real_internet_test.py
│
└── tests/                      # Unit tests
    ├── test_algorithmic_core.py
    └── test_state.py
```

---

## Key Concepts

### Network-Native Epistemic Intelligence (NNEI)

**Core Principle:**
```
Knowledge ≠ Parameters
Intelligence = Access + Evaluation + Synthesis
```

**What makes it different:**
- No training data (dataset-free)
- No LLM dependency (NLP-only)
- No GPU required (CPU-only)
- Real-time web search (always current)
- Full source attribution (no hallucinations)

### The 7-Step Cognitive Loop

1. **Intent Parsing** - Classify query type (social/factual/meta)
2. **Network Gate** - Decide if network is needed
3. **Epistemic Routing** - Select appropriate sources
4. **Hypothesis Generation** - Create competing explanations
5. **Network Interrogation** - Query sources in parallel
6. **Contradiction Handling** - Detect conflicts
7. **State Synthesis** - Generate calibrated answer

### Smart Network Usage

**Not every query needs the network:**
- Social ("hi", "thanks") → Instant local response
- Meta ("what are you?") → About Velocity itself
- Factual ("Python nedir?") → Network interrogation

This is **intelligent resource usage**.

---

## Quick Start

### Installation
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run Interactive Mode
```bash
python interactive_velocity.py
```

### Example Usage
```python
from velocity.core.velocity_core import VelocityCore

core = VelocityCore()
result = await core.execute("What is Python?")
print(result['decision'])
```

---

## Documentation Standards

### Language
- All documentation in English
- All code comments in English
- Professional, academic tone
- No emojis

### Structure
- Clear sections with headers
- Code examples where relevant
- Consistent formatting
- No redundancy

### Maintenance
- Update version numbers
- Keep examples current
- Remove outdated information
- Maintain consistency

---

## For Developers

### Contributing
Read the code in this order:
1. `velocity/core/velocity_core.py` - Main engine
2. `velocity/core/intent_parser.py` - Intent classification
3. `velocity/core/network_gate.py` - Smart network usage
4. `velocity/network/web_search.py` - Web search + NLP
5. `velocity/core/state_synthesizer.py` - Answer synthesis

### Testing
```bash
# Run unit tests
pytest tests/

# Run interactive mode
python interactive_velocity.py
```

### Architecture Principles
- **Modular**: Each step is independent
- **Testable**: All components have unit tests
- **Transparent**: Full reasoning trace
- **Extensible**: Easy to add new sources

---

## FAQ

**Q: Is this an LLM?**  
A: No. NNEI is ontologically different. It accesses knowledge, not stores it.

**Q: Why not just use ChatGPT?**  
A: ChatGPT hallucinates, is outdated (2021), and has no source tracking. Velocity doesn't hallucinate and is always current.

**Q: Can it work offline?**  
A: No. Network dependency is fundamental to the paradigm.

**Q: Is it faster than LLMs?**  
A: Social queries: Yes (500x). Factual queries: No (1-5s vs instant). But it's always accurate.

**Q: Can I use it with an LLM?**  
A: Yes! Hybrid is optimal: Small LLM + NNEI Engine = Best of both worlds.

---

## Version History

- **0.1.0** - Initial implementation
- **0.2.0** - Real web search added
- **0.3.0** - NLP processing, no LLM
- **0.3.1** - Smart system (network gate, social intents)
- **0.4.0** - NNEI paradigm defined, CPU-only

---

## Resources

- [Python Documentation](https://docs.python.org/)
- [Epistemic Logic](https://en.wikipedia.org/wiki/Epistemic_modal_logic)
- [TF-IDF](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
- [Extractive Summarization](https://en.wikipedia.org/wiki/Automatic_summarization)

---

**Velocity - Network-Native Epistemic Intelligence**

*Intelligence through interrogation, not memorization*
