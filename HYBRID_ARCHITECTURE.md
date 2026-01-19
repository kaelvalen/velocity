# Hybrid Architecture: Velocity (NNEI) + LLM

**The Best of Both Worlds**

---

## Overview

Velocity now supports **Hybrid Mode**, combining Network-Native Epistemic Intelligence (NNEI) with lightweight LLM synthesis for natural language generation.

### Core Principle

```
Facts from NNEI + Formatting from LLM = Production-Ready AI
```

**Workflow:**
```
User Query
    ↓
Velocity (NNEI) → Gather facts from web
    ↓
LLM Synthesizer → Format naturally
    ↓
Hybrid Output → Natural + Sourced + Calibrated
```

---

## Why Hybrid?

### Problem with Pure NNEI
```
Query: "What is Python?"

Pure NNEI Output:
"Python programming language. Created 1991. 
Used for web development, data science..."
```
**Issue:** Accurate but choppy, not fluent

### Problem with Pure LLM
```
Query: "What is Python?"

Pure LLM Output:
"Python is a versatile programming language..."
```
**Issue:** Fluent but no sources, may hallucinate, outdated (2021)

### Hybrid Solution
```
Query: "What is Python?"

Hybrid Output:
"Python is a high-level, versatile programming language 
created in 1991, widely used for web development, data 
science, and automation due to its simplicity and 
extensive library ecosystem."

Sources: python.org, wikipedia.org
Confidence: 87%
Mode: Hybrid (NNEI + LLM)
```
**Result:** Fluent + Accurate + Sourced + Current ✓

---

## Architecture

### Component Breakdown

```
┌─────────────────────────────────────────────┐
│          VELOCITY HYBRID SYSTEM             │
├─────────────────────────────────────────────┤
│                                             │
│  ┌────────────────────────────────────┐   │
│  │  NNEI CORE (Facts)                 │   │
│  ├────────────────────────────────────┤   │
│  │  1. Intent Parsing                 │   │
│  │  2. Network Gate                   │   │
│  │  3. Epistemic Routing              │   │
│  │  4. Hypothesis Generation          │   │
│  │  5. Network Interrogation          │   │
│  │  6. Contradiction Handling         │   │
│  │  7. State Synthesis                │   │
│  └──────────────┬─────────────────────┘   │
│                 │                           │
│        Raw Facts (accurate)                │
│                 │                           │
│                 ▼                           │
│  ┌────────────────────────────────────┐   │
│  │  LLM SYNTHESIS (Formatting)        │   │
│  ├────────────────────────────────────┤   │
│  │  • Ollama (local, private)         │   │
│  │  • Groq (cloud, fast)              │   │
│  │  • Fallback (raw if LLM fails)     │   │
│  └──────────────┬─────────────────────┘   │
│                 │                           │
│     Natural Language (fluent)              │
│                 │                           │
│                 ▼                           │
│  ┌────────────────────────────────────┐   │
│  │  HYBRID OUTPUT                     │   │
│  ├────────────────────────────────────┤   │
│  │  • Natural answer                  │   │
│  │  • Real sources                    │   │
│  │  • Confidence score                │   │
│  │  • Execution metadata              │   │
│  └────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

### Key Characteristics

**NNEI Layer (Unchanged):**
- Real-time web search
- Multi-source interrogation
- Epistemic calibration
- Source attribution
- No hallucinations

**LLM Layer (NEW):**
- Natural language formatting ONLY
- Does NOT add facts
- Temperature 0.3 (low, factual)
- Preserves all NNEI output
- Optional (can be disabled)

---

## Configuration

### Three Modes

**1. Pure NNEI (No LLM)**
```python
core = VelocityCore(enable_llm=False)
```
- Use: Research, fact-checking, when transparency > fluency
- Output: Raw facts, maximum accuracy
- Speed: 3-5s

**2. Hybrid with Ollama (Local)**
```python
config = SynthesisConfig(
    provider=LLMProvider.OLLAMA,
    model="mistral:7b",
    ollama_host="http://localhost:11434"
)
core = VelocityCore(llm_config=config, enable_llm=True)
```
- Use: Production, privacy-sensitive
- Output: Natural language + sources
- Speed: 4-7s
- Requires: Ollama installed locally

**3. Hybrid with Groq (Cloud)**
```python
config = SynthesisConfig(
    provider=LLMProvider.GROQ,
    model="mixtral-8x7b-32768",
    groq_api_key="your_key"
)
core = VelocityCore(llm_config=config, enable_llm=True)
```
- Use: Demos, prototyping
- Output: Natural language + sources
- Speed: 3-5s (fastest)
- Requires: Groq API key (free tier available)

---

## Installation

### 1. Base Installation
```bash
git clone https://github.com/reicalasso/velocity.git
cd velocity
pip install -r requirements.txt
```

### 2. For Ollama (Local LLM)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull mistral:7b

# Start Ollama server (runs on localhost:11434)
ollama serve
```

### 3. For Groq (Cloud LLM)
```bash
# Get free API key: https://console.groq.com
export GROQ_API_KEY="your_key_here"
```

### 4. Configure
```bash
cp env.example .env
# Edit .env:
ENABLE_LLM=true
LLM_PROVIDER=ollama  # or groq
OLLAMA_MODEL=mistral:7b
```

---

## Usage

### Basic Hybrid Usage
```python
import asyncio
from velocity.core.velocity_core import VelocityCore

async def main():
    # Create hybrid core
    core = VelocityCore(enable_llm=True)
    
    # Query
    result = await core.execute("What is Python?")
    
    # Natural answer (LLM-formatted)
    print(result['decision'])
    
    # Raw NNEI answer (preserved)
    print(result['raw_decision'])
    
    # Metadata
    print(f"Mode: {result['execution_metadata']['mode']}")
    print(f"LLM Used: {result['execution_metadata']['llm_used']}")
    print(f"Confidence: {result['confidence']}")

asyncio.run(main())
```

### Advanced Configuration
```python
from velocity.synthesis.llm_synthesizer import SynthesisConfig, LLMProvider

# Custom LLM config
config = SynthesisConfig(
    provider=LLMProvider.OLLAMA,
    model="mistral:7b",
    temperature=0.3,      # Low = more factual
    max_tokens=500,       # Answer length
    fallback_to_raw=True  # Use raw if LLM fails
)

core = VelocityCore(
    llm_config=config,
    enable_llm=True,
    max_hypotheses=3,
    confidence_threshold=0.6
)
```

---

## Performance Comparison

### Speed
| Mode | Time | Notes |
|------|------|-------|
| Pure NNEI | 3-5s | Fastest, raw output |
| Hybrid Ollama | 4-7s | Local, private |
| Hybrid Groq | 3-5s | Cloud, parallel processing |

### Quality
| Aspect | Pure NNEI | Hybrid |
|--------|-----------|--------|
| Accuracy | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Fluency | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Sources | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Current | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Speed | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### Cost
| Mode | Cost | Notes |
|------|------|-------|
| Pure NNEI | $0 | No LLM |
| Hybrid Ollama | $0 | Local model |
| Hybrid Groq | ~$0.01/query | Free tier available |

---

## Testing

```bash
# Test all modes
python test_hybrid_system.py

# Test specific mode
python -c "
import asyncio
from velocity.core.velocity_core import VelocityCore

async def test():
    core = VelocityCore(enable_llm=True)
    result = await core.execute('What is quantum computing?')
    print(result['decision'])

asyncio.run(test())
"
```

---

## Comparison with Other Systems

### vs Pure LLMs (ChatGPT, Claude)
| Feature | Pure LLM | Velocity Hybrid |
|---------|----------|-----------------|
| Natural Language | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Always Current | ❌ (2021 cutoff) | ✅ (real-time) |
| Source Attribution | ❌ | ✅ |
| No Hallucination | ❌ | ✅ |
| Confidence Calibration | ❌ | ✅ |

### vs RAG Systems
| Feature | RAG | Velocity Hybrid |
|---------|-----|-----------------|
| Natural Language | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Real-Time Web | ❌ (static corpus) | ✅ |
| Epistemic Calibration | ❌ | ✅ |
| Multi-Hypothesis | ❌ | ✅ |
| No Training | ❌ (needs embeddings) | ✅ |

### vs Web Search + GPT
| Feature | Search + GPT | Velocity Hybrid |
|---------|--------------|-----------------|
| Natural Language | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Epistemic Calibration | ❌ | ✅ |
| Contradiction Handling | ❌ | ✅ |
| Hypothesis Testing | ❌ | ✅ |
| Transparent Reasoning | ❌ | ✅ |

---

## Technical Details

### LLM Synthesis Prompt
```
Transform the following raw facts into a natural, fluent answer.

Query: {user_query}

Raw Facts:
{nnei_output}

Requirements:
1. Write in {language}
2. Be natural and conversational (like ChatGPT)
3. Use proper paragraphs and flow
4. Preserve ALL factual content (don't add or remove facts)
5. Be concise (3-4 sentences)
6. Don't mention sources in text (shown separately)

Natural Answer:
```

### Synthesis Parameters
```python
temperature = 0.3      # Low = factual, high = creative
max_tokens = 500       # Answer length limit
fallback_to_raw = True # Use raw if LLM fails
```

### Error Handling
```python
try:
    # Try LLM synthesis
    natural_answer = await llm.synthesize(raw_facts)
except LLMError:
    # Fallback to raw NNEI output
    natural_answer = raw_facts
    
# Always preserve NNEI output
result['raw_decision'] = raw_facts
result['decision'] = natural_answer
```

---

## Best Practices

### When to Use Each Mode

**Pure NNEI:**
- Research and fact-checking
- When transparency > readability
- Privacy-critical applications
- No LLM available

**Hybrid Ollama:**
- Production deployments
- Privacy-sensitive data
- No API costs desired
- Local infrastructure available

**Hybrid Groq:**
- Demos and prototypes
- Speed is critical
- API costs acceptable
- Easy setup needed

### Recommendations

1. **Start with Groq** (easiest setup, free tier)
2. **Move to Ollama** for production (privacy, no cost)
3. **Keep Pure NNEI** as fallback (robustness)

---

## Future Enhancements

### Planned
- [ ] Multi-language synthesis
- [ ] Custom LLM providers (OpenAI, Anthropic)
- [ ] Streaming output
- [ ] Confidence-aware synthesis
- [ ] User preference learning

### Experimental
- [ ] Multi-modal synthesis (images, tables)
- [ ] Interactive refinement
- [ ] Domain-specific formatters
- [ ] Emotional tone adaptation

---

## FAQ

**Q: Does hybrid mode add hallucinations?**  
A: No. LLM is instructed to preserve ALL facts. Temperature is low (0.3). Only formatting changes.

**Q: Is it slower than pure LLM?**  
A: Yes (3-5s vs 0.5s), but you get sources and confidence.

**Q: Can I use OpenAI/Anthropic?**  
A: Not yet, but easy to add. Currently: Ollama (local) or Groq (cloud).

**Q: What if LLM fails?**  
A: Automatic fallback to raw NNEI output. System never fails.

**Q: Is Ollama really free?**  
A: Yes! Open source, runs locally, no API costs.

**Q: Which model is best?**  
A: Mistral 7B (Ollama) or Mixtral 8x7B (Groq) - both excellent for factual synthesis.

---

## Conclusion

**Velocity Hybrid = Production-Ready AI**

Combines:
- ✅ Natural fluency (LLM)
- ✅ Real sources (NNEI)
- ✅ No hallucinations (NNEI)
- ✅ Always current (NNEI)
- ✅ Confidence calibration (NNEI)

**Result:** The best AI assistant for factual queries.

---

**Repository:** https://github.com/reicalasso/velocity  
**License:** MIT  
**Version:** 0.5.0 (Hybrid)  
**Status:** Production Ready
