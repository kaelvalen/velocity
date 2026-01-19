# Hybrid System Setup Guide

**Get Velocity + LLM running in 5 minutes**

---

## Quick Setup (Recommended: Ollama)

### Step 1: Install Velocity

```bash
git clone https://github.com/reicalasso/velocity.git
cd velocity
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Install Ollama (Local LLM)

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from: https://ollama.com/download

### Step 3: Pull Model

```bash
# Start Ollama (if not auto-started)
ollama serve

# Pull Mistral 7B (recommended)
ollama pull mistral:7b

# Or try other models:
# ollama pull llama3:8b
# ollama pull phi3:mini
```

### Step 4: Configure

```bash
cp env.example .env

# Edit .env:
ENABLE_LLM=true
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral:7b
```

### Step 5: Test

```bash
python test_hybrid_system.py
```

**Expected output:**
```
MODE 2: HYBRID with OLLAMA (Local LLM)
========================================

Query: "What is Python?"

[NATURAL ANSWER] (LLM-synthesized)
Python is a high-level, versatile programming language created 
in 1991, widely used for web development, data science, and 
automation due to its simplicity and extensive library ecosystem.

[METADATA]
Mode: hybrid
LLM Used: True
Time: 4.52s
Confidence: 87%

✓ Success!
```

---

## Alternative: Groq (Cloud LLM - Fastest)

### Step 1: Get API Key

1. Go to https://console.groq.com
2. Sign up (free)
3. Create API key

### Step 2: Configure

```bash
# Set environment variable
export GROQ_API_KEY="your_key_here"

# Or in .env:
ENABLE_LLM=true
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
GROQ_MODEL=mixtral-8x7b-32768
```

### Step 3: Test

```bash
python -c "
import asyncio
from velocity.core.velocity_core import VelocityCore
from velocity.synthesis.llm_synthesizer import SynthesisConfig, LLMProvider

async def test():
    config = SynthesisConfig(
        provider=LLMProvider.GROQ,
        model='mixtral-8x7b-32768',
        groq_api_key='your_key_here'
    )
    core = VelocityCore(llm_config=config, enable_llm=True)
    result = await core.execute('What is Python?')
    print(result['decision'])

asyncio.run(test())
"
```

---

## Usage Examples

### Interactive Mode (Hybrid)

```bash
python interactive_velocity.py
```

The system will auto-detect if Ollama is running and use hybrid mode.

### Python Script

```python
import asyncio
from velocity.core.velocity_core import VelocityCore

async def main():
    # Hybrid mode (auto-detects Ollama)
    core = VelocityCore(enable_llm=True)
    
    # Query
    result = await core.execute("Explain quantum computing")
    
    # Natural answer
    print(result['decision'])
    
    # Sources
    for evidence in result['evidence']:
        print(f"- {evidence['source']}")

asyncio.run(main())
```

---

## Troubleshooting

### Problem: "Ollama not running"

**Solution:**
```bash
# Check if running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve

# Or on Windows, launch Ollama app
```

### Problem: "Model not found"

**Solution:**
```bash
# List installed models
ollama list

# Pull missing model
ollama pull mistral:7b
```

### Problem: "LLM synthesis failed"

**Don't worry!** System automatically falls back to raw NNEI output.

**Check logs:**
```python
result['execution_metadata']['llm_used']  # False = fallback used
```

### Problem: "Too slow"

**Solutions:**
1. Use smaller model: `ollama pull phi3:mini` (2GB vs 4GB)
2. Use Groq (cloud): Faster than local
3. Disable LLM: `enable_llm=False` (fastest)

---

## Model Comparison

| Model | Size | Speed | Quality | Privacy |
|-------|------|-------|---------|---------|
| Mistral 7B | 4GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| LLaMA 3 8B | 5GB | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Phi-3 Mini | 2GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Mixtral (Groq) | Cloud | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**Recommendation:** Start with **Mistral 7B** (best balance)

---

## Performance Expectations

### Pure NNEI (No LLM)
```
Speed: 3-5s
Output: Raw facts
Quality: ⭐⭐⭐
```

### Hybrid Ollama (Local)
```
Speed: 4-7s
Output: Natural language
Quality: ⭐⭐⭐⭐⭐
Privacy: ⭐⭐⭐⭐⭐
Cost: $0
```

### Hybrid Groq (Cloud)
```
Speed: 3-5s
Output: Natural language
Quality: ⭐⭐⭐⭐⭐
Privacy: ⭐⭐⭐
Cost: ~$0.01/query (free tier available)
```

---

## FAQ

**Q: Do I need a GPU?**  
A: No! Ollama runs on CPU. GPU speeds it up but not required.

**Q: How much RAM?**  
A: Minimum 8GB. Recommended 16GB for smooth operation.

**Q: Can I use without LLM?**  
A: Yes! Set `enable_llm=False` for pure NNEI mode.

**Q: Is it private?**  
A: Yes! Ollama runs locally, no data sent to cloud.

**Q: Which is better: Ollama or Groq?**  
A: Ollama for production (privacy), Groq for demos (speed).

**Q: Can I use OpenAI/Anthropic?**  
A: Not yet, but easy to add. PRs welcome!

---

## Next Steps

1. ✅ Get hybrid running (this guide)
2. 📖 Read [HYBRID_ARCHITECTURE.md](./HYBRID_ARCHITECTURE.md) for details
3. 🧪 Run `python test_hybrid_system.py` for validation
4. 🚀 Build your application with Velocity

---

## Support

- Issues: https://github.com/reicalasso/velocity/issues
- Ollama docs: https://ollama.com/docs
- Groq docs: https://console.groq.com/docs

---

**Ready to build? Let's go! 🚀**
