# 🌐 VELOCITY - REAL WEB SEARCH + NLP

**"Intelligence lives in the speed of interrogation, not in the size of memory."**

Velocity artık **gerçek web'den arama yapıyor** - LLM yok, sadece NLP!

---

## ✅ Çalışma Prensibi

### Arama Stratejisi (Cascade)

```
1. Real Web Search (Google/Bing/DDG scraping) 🔍
   ↓ (failed)
2. Wikipedia API 📚
   ↓ (failed)
3. DuckDuckGo Instant Answer 🦆
   ↓ (failed)
4. Enhanced Simulated Fallback ⚙️
```

### NLP Processing (NO LLM!)

Tüm text processing **LLM kullanmadan** yapılıyor:

- **TF-IDF** ile keyword extraction
- **Extractive summarization** (en önemli cümleleri seç)
- **Cosine similarity** ile relevance scoring
- **BeautifulSoup** ile HTML parsing

---

## 🚀 Kurulum

### 1. Dependencies Zaten Yüklü

```bash
pip install beautifulsoup4 requests spacy nltk scikit-learn aiohttp
```

✅ Tüm NLP kütüphaneleri yüklü!

### 2. API Keys (Optional)

Daha iyi sonuçlar için API key'ler ekle:

#### Google Custom Search

1. [Google Cloud Console](https://console.cloud.google.com/) → Create API Key
2. [Custom Search Engine](https://programmablesearchengine.google.com/) → Create CSE

```bash
export GOOGLE_API_KEY="your-api-key"
export GOOGLE_CSE_ID="your-cse-id"
```

#### Bing Search

1. [Azure Portal](https://portal.azure.com/) → Create Bing Search Resource

```bash
export BING_API_KEY="your-bing-key"
```

---

## 💡 Kullanım

### Otomatik (API keys varsa kullanır, yoksa DDG scraping yapar)

```python
from velocity.core.velocity_core import VelocityCore

# API keys environment variable'lardan okunur
core = VelocityCore()

result = await core.execute("quantum computing nedir")
```

### Manuel Control

```python
from velocity.network.interrogator import NetworkInterrogator

# Real web search enabled (default)
interrogator = NetworkInterrogator(use_real_search=True)

# Disabled (sadece Wikipedia/DDG API)
interrogator = NetworkInterrogator(use_real_search=False)
```

---

## 📊 Arama Kaynakları

### 1. Google Custom Search ⭐

**장점**:
- En kapsamlı
- En doğru results
- Custom filters

**단점**:
- API key gerekli
- Rate limited (100 queries/day free)

### 2. Bing Search ⭐

**장점**:
- Hızlı
- Güvenilir
- Bing Index

**단점**:
- API key gerekli
- Ücretli (after free tier)

### 3. DuckDuckGo HTML Scraping 🆓

**장점**:
- ✅ API key gerekmez!
- Privacy-focused
- Her zaman çalışır

**단점**:
- HTML parsing (kırılgan)
- Rate limit riski
- Daha yavaş

### 4. GitHub Code Search 💻

**Generative queries** için:
- Public repos
- Code örnekleri
- No auth for limited requests

### 5. StackOverflow API 💻

**Generative queries** için:
- Programming Q&A
- Accepted answers
- Community-driven

---

## 🎯 Örnekler

### Factual Query

```python
result = await core.execute("What is quantum computing?")

# Output:
# - Real web search: Google/Bing/DDG
# - NLP summarization (extractive)
# - Keywords: quantum, computing, qubits, superposition
# - Relevance: 0.87
```

### Code Generation Query

```python
result = await core.execute("python fibonacci kodu yaz")

# Output:
# - Search: GitHub + StackOverflow
# - Real code examples
# - No LLM generation!
```

### Comparison Query

```python
result = await core.execute("Python vs JavaScript karşılaştır")

# Output:
# - Multiple sources
# - Extractive summary from each
# - Combined with NLP
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Optional - for best results
export GOOGLE_API_KEY="your-key"
export GOOGLE_CSE_ID="your-cse-id"
export BING_API_KEY="your-key"

# Run Velocity
python interactive_velocity.py
```

### Without API Keys

API key yoksa **DuckDuckGo HTML scraping** otomatik devreye girer:

```
🔍 Real web search: query
  → Google (no key, skipped)
  → Bing (no key, skipped)
  → DuckDuckGo HTML (✅ working!)
  → GitHub (✅ no auth needed)
  → StackOverflow (✅ no auth needed)
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│   User Query                        │
└──────────────┬──────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│   Intent Parser (7 types)            │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│   Epistemic Router                   │
│   (Select search strategies)         │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│   Real Web Search Engine             │
│   ├─ Google Custom Search            │
│   ├─ Bing Search                     │
│   ├─ DuckDuckGo HTML Scraping        │
│   ├─ GitHub Code Search              │
│   └─ StackOverflow API               │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│   NLP Processor (NO LLM!)            │
│   ├─ TF-IDF Keyword Extraction       │
│   ├─ Extractive Summarization        │
│   ├─ Cosine Similarity Scoring       │
│   └─ HTML Content Extraction         │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│   Synthesized Response               │
└──────────────────────────────────────┘
```

---

## 📈 Performance

### With API Keys

```
Query: "quantum computing"
  ✅ Google Search: 450ms
  ✅ NLP Processing: 120ms
  ✅ Total: 570ms
  
  Sources: 3 web pages
  Keywords: quantum, computing, qubits, superposition, entanglement
  Summary: 3 sentences (extractive)
  Confidence: 87%
```

### Without API Keys (DDG Scraping)

```
Query: "quantum computing"
  ⚠️ Google (no key)
  ⚠️ Bing (no key)
  ✅ DuckDuckGo HTML: 950ms
  ✅ NLP Processing: 120ms
  ✅ Total: 1070ms
  
  Sources: 3 web pages
  Keywords: quantum, computing, qubits
  Summary: 3 sentences
  Confidence: 72%
```

---

## 🎉 Key Benefits

### ✅ No LLM Dependency

- Tamamen **NLP-based** processing
- TF-IDF, cosine similarity, extractive summarization
- **No hallucinations!**

### ✅ Real Web Search

- Google, Bing, DuckDuckGo
- GitHub, StackOverflow
- Always up-to-date

### ✅ Epistemically Sound

- Multiple sources
- Confidence scoring
- Source tracking

### ✅ Works Without API Keys

- DuckDuckGo HTML scraping (free!)
- Wikipedia API (free!)
- GitHub public repos (free!)
- StackOverflow API (free!)

---

## 🚧 Limitations

### Rate Limits

- Google: 100 queries/day (free tier)
- Bing: Pay per query
- DDG scraping: May be blocked if abused

### HTML Scraping Fragility

- DuckDuckGo HTML structure değişebilir
- Fallback mechanisms var

### No LLM = No Generation

- **Extractive** summarization (seçiyor)
- NOT **abstractive** (yeni metin yazmıyor)
- Kod generation için gerçek examples bulur

---

## 🔮 Future Enhancements

### Short Term

- [ ] More search engines (Brave, Startpage)
- [ ] Better code search (GitLab, Bitbucket)
- [ ] Cached results (avoid redundant queries)

### Long Term

- [ ] Semantic search integration
- [ ] Knowledge graph building
- [ ] Multi-language NLP support

---

## 📝 Summary

**Velocity artık:**

1. ✅ **Gerçek web'den arama yapıyor** (Google/Bing/DDG)
2. ✅ **NLP ile processing** (TF-IDF, extractive summarization)
3. ✅ **LLM kullanmıyor** (no hallucinations!)
4. ✅ **API key opsiyonel** (DDG scraping fallback)
5. ✅ **Kod örnekleri buluyor** (GitHub/StackOverflow)
6. ✅ **7 adımlı cognitive loop** (her soruda)

---

*"Intelligence lives in the speed of interrogation, not in the size of memory."*

**Velocity 0.3.0 - Real Web Search + NLP** 🌐✨
