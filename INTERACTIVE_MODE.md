# 🎮 VELOCITY - INTERACTIVE MODE

Velocity'yi terminal'den interaktif olarak kullan!

---

## 🚀 Nasıl Kullanılır?

### Yöntem 1: Interactive Mode (Soru-Cevap Döngüsü)

```bash
cd velocity
.\venv\Scripts\activate
python interactive_velocity.py
```

Sonra terminal'de:

```
[1] Sorunuz: What is quantum computing?
[2] Sorunuz: Compare Python vs Java
[3] Sorunuz: Should I learn machine learning?
```

### Yöntem 2: Tek Soru (Command Line)

```bash
python interactive_velocity.py "What is artificial intelligence?"
```

Direkt yanıt alırsın, döngü başlamaz.

---

## 📋 Komutlar

Interactive mode'dayken:

- **Soru yaz** → Velocity yanıt verir
- **`help`** → Yardım göster
- **`exit`** veya **`quit`** → Çık
- **Ctrl+C** → Hızlı çıkış

---

## 💡 Örnek Sorular

### Factual (Gerçek Bilgi)
```
What is blockchain?
Who invented the internet?
What is photosynthesis?
```

### Comparative (Karşılaştırma)
```
Compare Bitcoin vs Ethereum
Python vs JavaScript for beginners
Mac vs PC for programming
```

### Strategic (Karar)
```
Should I learn Rust or Go?
Is cloud computing worth it?
Should I use microservices?
```

### Procedural (Nasıl Yapılır)
```
How to learn programming?
How to deploy a web app?
How does encryption work?
```

---

## 🎯 Her Soruda

Velocity otomatik olarak **7 adım** uygular:

1. **Intent Parsing** - Soruyu analiz eder
2. **Epistemic Routing** - En iyi kaynakları seçer
3. **Hypothesis Generation** - Paralel hipotezler üretir
4. **Network Interrogation** - Kaynakları sorgular
5. **Contradiction Handling** - Çelişkileri yönetir
6. **Hypothesis Elimination** - Zayıfları eler
7. **State Synthesis** - Final yanıtı sentezler

---

## 📊 Yanıt Formatı

Her yanıt şunları içerir:

```
[YANIT]
<Velocity'nin cevabi>

[DETAYLAR]
  Guven: 54.0%
  Belirsizlik: MEDIUM
  Kanit sayisi: 2 parca
  Kaynaklar:
    - knowledge_base:topic: 2 sorgu
```

### Güven Seviyeleri

- **70%+**: Yüksek güven (çok kanıt var)
- **50-70%**: Orta güven (yeterli kanıt)
- **<50%**: Düşük güven (sınırlı kanıt)

### Belirsizlik Seviyeleri

- **LOW**: Çok net, kesin
- **MEDIUM**: Orta belirsizlik
- **HIGH**: Yüksek belirsizlik
- **VERY_HIGH**: Çok belirsiz
- **UNKNOWN**: Bilinmeyen

---

## 🎨 Özellikler

### ✅ Network-Native

Her soru için:
- Wikipedia API dener
- DuckDuckGo dener
- Knowledge base fallback

### ✅ Paralel İşlem

- 2+ hipotez eşzamanlı
- Hızlı yanıt süresi
- Optimal kaynak kullanımı

### ✅ Epistemik Dürüstlük

- Güven skoru kalibre
- Belirsizlik explicit
- Kaynaklar gösteriliyor

### ✅ State-Driven

- Her hipotez kendi state'i
- Dinamik sorgu seçimi
- Contradiction forking

---

## 🔧 Konfigürasyon

`interactive_velocity.py` içinde değiştirebilirsin:

```python
core = VelocityCore(
    max_hypotheses=2,           # Paralel hipotez sayısı
    confidence_threshold=0.6,   # Min güven eşiği
    max_iterations=3,           # Max iterasyon
    budget_per_hypothesis=3.0   # Maliyet limiti
)
```

---

## 📈 Performance

- **Yanıt süresi**: 2-4 saniye
- **Paralel işlem**: 2 hipotez
- **Network timeout**: 10 saniye
- **Memory**: Minimal (state-driven)

---

## 🎯 Kullanım Örnekleri

### Örnek 1: Hızlı Soru

```bash
python interactive_velocity.py "What is Rust programming language?"
```

Tek yanıt, sonra çık.

### Örnek 2: Uzun Session

```bash
python interactive_velocity.py
```

Sonra:
```
[1] Sorunuz: What is machine learning?
[2] Sorunuz: Compare supervised vs unsupervised learning
[3] Sorunuz: How to start with ML?
[4] Sorunuz: exit
```

### Örnek 3: Help

```
[1] Sorunuz: help
[HELP]
Velocity'ye herhangi bir soru sorabilirsin...
```

---

## 🚨 Notlar

### Wikipedia API

Şu anda **HTTP 403** (rate limit) alıyor. Çözümler:

1. User-Agent header ekle
2. API key kullan
3. Fallback çalışıyor (knowledge base)

### DuckDuckGo API

**MIME type issue** var. Fallback aktif.

### Fallback System

Her iki API başarısız olsa bile:
- Enhanced knowledge base kullanılır
- Simüle edilmiş içerik döner
- Güven skoru düşer (%54)

---

## 💡 Tips

1. **Net sorular sor**: "What is X?" > "Tell me about X"
2. **Spesifik ol**: "Compare A vs B" > "A and B"
3. **Context ver**: "For beginners" ekle
4. **Help kullan**: Sıkışırsan `help` yaz

---

## 🎉 Demo

```bash
# Start interactive mode
python interactive_velocity.py

# Velocity başladı!
[1] Sorunuz: What is blockchain?

[PROCESSING...] Velocity dusunuyor...

[YANIT]
Blockchain is a distributed ledger technology...

[DETAYLAR]
  Guven: 54.0%
  Belirsizlik: MEDIUM
  Kanit sayisi: 1 parca
  Kaynaklar:
    - knowledge_base:blockchain: 2 sorgu

[2] Sorunuz: exit

[BYE] Velocity kapatiliyor...
Toplam 1 soru soruldu.
```

---

## 🏆 Özet

**Interactive Velocity** şimdi hazır!

- ✅ Terminal'den soru sor
- ✅ Gerçek zamanlı yanıt al
- ✅ Sınırsız soru
- ✅ 7 adımlık cognitive loop
- ✅ Network-native intelligence
- ✅ Epistemik dürüstlük

**Hemen dene!**

```bash
python interactive_velocity.py
```

---

*Intelligence lives in the speed of interrogation, not in the size of memory.*

**Velocity - Interactive Mode** 🚀
