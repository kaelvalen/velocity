"""
VELOCITY NLP ENGINE — Pure Algorithmic Answer Synthesis
=======================================================

LLM yok.  Sadece istatistik, pattern-matching ve yapılandırılmış metin.

Pipeline:
    raw_texts  →  clean  →  segment  →  rank  →  extract  →  compose  →  render

Her adım deterministik ve test-edilebilir.

"Intelligence is not in the model — it's in the algorithm."
"""

from __future__ import annotations

import re
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from loguru import logger


# ======================================================================
# DATA CLASSES
# ======================================================================

@dataclass
class Sentence:
    """A scored, classified sentence."""
    text: str
    index: int                  # position in original document
    score: float = 0.0         # final composite score
    relevance: float = 0.0     # query relevance
    position_score: float = 0.0
    length_score: float = 0.0
    entity_score: float = 0.0
    is_definition: bool = False
    is_biographical: bool = False
    source: str = ""


@dataclass
class Entity:
    """An extracted named entity with metadata."""
    name: str
    category: str                         # PERSON, ORG, ROLE, TOPIC, etc.
    aliases: List[str] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class StructuredAnswer:
    """The final algorithmic answer artifact."""
    summary: str                          # 2-5 sentence core answer
    key_facts: List[str]                  # bullet-point facts
    entities: List[Entity]
    sources: List[str]
    query_type: str                       # factual, biographical, comparative…
    confidence_label: str                 # High / Moderate / Low
    confidence: float
    raw_debug: Optional[str] = None       # cleaned combined text (for debugging)


# ======================================================================
# TEXT CLEANING — much more aggressive than the old _clean_evidence_text
# ======================================================================

# Patterns compiled once for speed
_RE_URL = re.compile(r'https?://\S+|www\.\S+')
_RE_REF = re.compile(r'\[\d+\]')
_RE_CAMEL = re.compile(r'([a-z])([A-Z])')
_RE_WORD_NUM = re.compile(r'([A-Za-z])(\d)')
_RE_NUM_WORD = re.compile(r'(\d)([A-Za-z])')
_RE_MULTI_SPACE = re.compile(r'[ \t]+')
_RE_MULTI_NEWLINE = re.compile(r'\n{3,}')
_RE_PARENS_EMPTY = re.compile(r'\(\s*\)')
_RE_NAVIGATION = re.compile(
    r'(?i)\b(menu|breadcrumb|sidebar|skip to|cookie|accept|privacy policy|'
    r'sign in|log in|sign up|subscribe|newsletter|advertisement|'
    r'copyright ©|all rights reserved|terms of (use|service)|'
    r'toggle navigation|search\.\.\.|loading|read more|show more|'
    r'click here|tap to|swipe|download app|install|upgrade)\b'
)
_RE_SENTENCE_SPLIT = re.compile(r'(?<=[.!?])\s+')

# Bullet / separator characters from web layouts
_RE_BULLETS = re.compile(r'[·•|►▸▹▶‣⁃–—]+')

# Common web "boilerplate" markers
_BOILERPLATE_MARKERS = {
    'cookie', 'privacy', 'subscribe', 'newsletter', 'advertisement',
    'copyright', 'terms of use', 'accept all', 'sign in', 'sign up',
    'toggle navigation', 'skip to content', 'loading', 'read more',
    'show more', 'click here', 'download app', 'install now',
    'close this', 'dismiss',
}


def deep_clean(text: str) -> str:
    """
    Aggressive text cleaning for web-scraped content.

    Goal: turn noisy HTML-extracted text into clean, readable prose.
    """
    if not text:
        return ""

    # 1. Remove URLs
    text = _RE_URL.sub('', text)

    # 2. Remove reference markers
    text = _RE_REF.sub('', text)

    # 3. Remove empty parens
    text = _RE_PARENS_EMPTY.sub('', text)

    # 4. Replace bullet/separator chars with period + space (they usually delimit items)
    text = _RE_BULLETS.sub('. ', text)

    # 5. Fix camelCase concatenation
    text = _RE_CAMEL.sub(r'\1 \2', text)
    text = _RE_WORD_NUM.sub(r'\1 \2', text)
    text = _RE_NUM_WORD.sub(r'\1 \2', text)

    # 5b. Fix common concatenation patterns from web scraping:
    #     "Researchingnon" → "Researching non"  (lowercase touching lowercase where
    #     a word boundary was lost during HTML→text)
    text = re.sub(r'([a-zçğıöşü]{3,})(non|the|and|for|with|from|into|that|this|are|was|has|had|can|will|not)\b',
                  r'\1 \2', text, flags=re.I)

    # 6. Normalise whitespace
    text = _RE_MULTI_NEWLINE.sub('\n\n', text)
    text = _RE_MULTI_SPACE.sub(' ', text)

    # 7. Fix punctuation spacing
    text = re.sub(r'\s*([,;:!?.])\s*', r'\1 ', text)
    text = re.sub(r'\s+\.', '.', text)        # "word ." → "word."
    text = re.sub(r'\.{2,}', '.', text)        # "..." clusters
    text = re.sub(r'\.\s*\.', '.', text)       # ". ." → "."

    # 8. Remove lines that look like navigation / boilerplate
    cleaned_lines: list[str] = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        lower = line.lower()
        # Skip very short "leftover" lines (menu items, breadcrumbs)
        if len(line) < 15 and not line.endswith('.'):
            continue
        # Skip lines that smell like boilerplate
        if any(m in lower for m in _BOILERPLATE_MARKERS):
            continue
        cleaned_lines.append(line)

    text = ' '.join(cleaned_lines)
    text = _RE_MULTI_SPACE.sub(' ', text).strip()
    return text


# ======================================================================
# SENTENCE SEGMENTATION + SCORING
# ======================================================================

def segment_sentences(text: str) -> List[str]:
    """Split text into sentences, filtering garbage."""
    raw = _RE_SENTENCE_SPLIT.split(text)
    out: list[str] = []
    for s in raw:
        s = s.strip()
        if len(s) < 20:                         # too short to be useful
            continue
        if s.count(' ') < 3:                    # fewer than 4 words
            continue
        if _RE_NAVIGATION.search(s):            # boilerplate leftovers
            continue
        # Capitalise first letter for consistency
        if s and s[0].islower():
            s = s[0].upper() + s[1:]
        # Ensure trailing punctuation
        if not s[-1] in '.!?':
            s += '.'
        out.append(s)
    return out


def _idf_weights(sentences: List[str]) -> Dict[str, float]:
    """Compute IDF weights across sentences (mini-corpus)."""
    n = len(sentences)
    if n == 0:
        return {}
    df: Counter = Counter()
    for s in sentences:
        words = set(s.lower().split())
        for w in words:
            df[w] += 1
    return {w: math.log((n + 1) / (freq + 1)) + 1 for w, freq in df.items()}


def score_sentences(
    sentences: List[str],
    query: str,
    *,
    query_entities: Optional[List[str]] = None,
) -> List[Sentence]:
    """
    Score each sentence on four axes and produce a composite rank.

    Axes:
        1. **query-relevance** — TF-IDF cosine-ish overlap with query tokens
        2. **position**        — earlier sentences get a small bonus
        3. **length**          — medium sentences preferred (20-60 words)
        4. **entity**          — contains entities mentioned in the query
    """
    if not sentences:
        return []

    idf = _idf_weights(sentences)
    query_tokens = set(query.lower().split())

    scored: List[Sentence] = []
    n = len(sentences)

    for idx, text in enumerate(sentences):
        tokens = text.lower().split()
        token_set = set(tokens)

        # --- 1. Relevance ---
        overlap = query_tokens & token_set
        if overlap:
            relevance = sum(idf.get(t, 1.0) for t in overlap) / max(len(query_tokens), 1)
        else:
            relevance = 0.0

        # --- 2. Position (first 30% get a bonus) ---
        pos_ratio = idx / max(n, 1)
        position_score = max(0.0, 1.0 - pos_ratio * 1.2)

        # --- 3. Length (sweet spot ≈ 15-50 words) ---
        wcount = len(tokens)
        if 15 <= wcount <= 50:
            length_score = 1.0
        elif 10 <= wcount < 15 or 50 < wcount <= 80:
            length_score = 0.6
        else:
            length_score = 0.3

        # --- 4. Entity match ---
        entity_score = 0.0
        if query_entities:
            for ent in query_entities:
                if ent.lower() in text.lower():
                    entity_score += 0.5

        # --- Definition / biographical signals ---
        is_def = bool(re.search(
            r'\b(is a|is an|is the|refers to|defined as|are|'
            r'bir|olan|olarak|anlamına gelir|denir|demektir)\b',
            text, re.I
        ))
        is_bio = bool(re.search(
            r'\b(born|founded|created|developed|known for|career|researcher|'
            r'author|architect|engineer|scientist|professor|CEO|developer|'
            r'doğum|kurucu|geliştirici|bilinen|kariyer|araştırmacı|'
            r'mühendis|yazar|bilim insanı|yazılımcı)\b',
            text, re.I
        ))

        # --- Composite ---
        # Weights tuneable: relevance dominates
        composite = (
            relevance    * 0.45 +
            position_score * 0.15 +
            length_score   * 0.10 +
            entity_score   * 0.20 +
            (0.10 if is_def else 0.0) +
            (0.10 if is_bio else 0.0)
        )

        scored.append(Sentence(
            text=text,
            index=idx,
            score=composite,
            relevance=relevance,
            position_score=position_score,
            length_score=length_score,
            entity_score=entity_score,
            is_definition=is_def,
            is_biographical=is_bio,
        ))

    # Sort by composite score DESC
    scored.sort(key=lambda s: s.score, reverse=True)
    return scored


# ======================================================================
# ENTITY EXTRACTION — lightweight, regex-based
# ======================================================================

# Common role / title patterns (EN + TR)
_ROLE_PATTERNS = re.compile(
    r'\b(researcher|engineer|developer|scientist|professor|architect|'
    r'founder|co-founder|CEO|CTO|author|designer|director|manager|'
    r'specialist|analyst|consultant|expert|lead|principal|senior|'
    r'araştırmacı|mühendis|geliştirici|bilim insanı|yazılımcı|kurucu|yazar|'
    r'uzman|danışman|lider|kıdemli|baş|müdür)\b',
    re.IGNORECASE
)

# Organisation patterns
_ORG_PATTERNS = re.compile(
    r'\b(Google|Meta|Microsoft|Apple|Amazon|OpenAI|DeepMind|Anthropic|'
    r'MIT|Stanford|Harvard|Berkeley|Oxford|Cambridge|'
    r'Mozilla|GitHub|IBM|NVIDIA|Tesla|SpaceX|'
    r'Hugging\s*Face|PyTorch|TensorFlow|Keras|'
    r'Twitter|LinkedIn|Facebook|YouTube|Reddit)\b'
)

# Topic / field patterns
_FIELD_PATTERNS = re.compile(
    r'\b(machine learning|deep learning|artificial intelligence|'
    r'natural language processing|NLP|computer vision|'
    r'non-transformer|transformer|neural network|'
    r'blockchain|quantum computing|robotics|'
    r'reinforcement learning|generative AI|'
    r'large language model|diffusion model|'
    r'systematic learning|architecture research|'
    r'ML|AI|CV|LLM|AGI|GPT|BERT)\b',
    re.IGNORECASE
)


def extract_entities(text: str) -> List[Entity]:
    """Extract entities from text using regex heuristics."""
    entities: list[Entity] = []
    seen: set[str] = set()

    # Roles
    for m in _ROLE_PATTERNS.finditer(text):
        name = m.group(0)
        key = name.lower()
        if key not in seen:
            seen.add(key)
            entities.append(Entity(name=name, category="ROLE"))

    # Orgs
    for m in _ORG_PATTERNS.finditer(text):
        name = m.group(0)
        key = name.lower()
        if key not in seen:
            seen.add(key)
            entities.append(Entity(name=name, category="ORG"))

    # Fields / topics
    for m in _FIELD_PATTERNS.finditer(text):
        name = m.group(0)
        key = name.lower()
        if key not in seen:
            seen.add(key)
            entities.append(Entity(name=name, category="TOPIC"))

    # Capitalised Name patterns (simple: 2-3 capitalised words)
    for m in re.finditer(r'\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+(?:\s+[A-ZÇĞİÖŞÜ][a-zçğıöşü]+){1,2})\b', text):
        name = m.group(1)
        key = name.lower()
        if key not in seen and len(name) > 4:
            # Filter out sentence starters by checking preceding char
            start = m.start()
            if start > 0 and text[start-1] in '.!?\n':
                continue  # likely sentence start, not person name
            seen.add(key)
            entities.append(Entity(name=name, category="PERSON"))

    return entities


# ======================================================================
# KEY FACT EXTRACTION
# ======================================================================

def extract_key_facts(
    scored_sentences: List[Sentence],
    query: str,
    max_facts: int = 5,
) -> List[str]:
    """
    Pull out concise key facts from the top ranked sentences.

    Strategy: take top-scored sentences, deduplicate, and trim.
    """
    facts: list[str] = []
    seen_tokens: set[frozenset] = set()

    for sent in scored_sentences:
        if len(facts) >= max_facts:
            break
        tokens = frozenset(sent.text.lower().split())
        # Simple dedup: reject if >60% token overlap with existing fact
        is_dup = False
        for existing in seen_tokens:
            overlap = len(tokens & existing) / max(len(tokens), 1)
            if overlap > 0.60:
                is_dup = True
                break
        if is_dup:
            continue
        seen_tokens.add(tokens)

        # Trim to one sentence
        first_sentence = _RE_SENTENCE_SPLIT.split(sent.text)[0].strip()
        if first_sentence and len(first_sentence) > 15:
            if not first_sentence[-1] in '.!?':
                first_sentence += '.'
            facts.append(first_sentence)

    return facts


# ======================================================================
# ANSWER COMPOSITION — query-type aware
# ======================================================================

def _detect_query_type(query: str) -> str:
    """Light-weight intent detection for answer shaping."""
    q = query.lower()
    if re.search(r'\b(kimdir|who is|who was|who are)\b', q):
        return 'biographical'
    if re.search(r'\b(nedir|what is|what are|define|tanımla)\b', q):
        return 'definition'
    if re.search(r'\bvs\b|\bcompare\b|\bkarşılaştır\b|\bfark\b|\bdifference\b', q):
        return 'comparative'
    if re.search(r'\bhow to\b|\bnasıl\b|\bsteps\b|\badımlar\b', q):
        return 'procedural'
    if re.search(r'\bwhy\b|\bneden\b|\bsebep\b', q):
        return 'causal'
    return 'general'


def _query_subject(query: str) -> str:
    """Best-effort extract of the main subject from the query."""
    q = query.strip()
    # "who is X" / "X kimdir"
    m = re.search(r'(?:who is|who was)\s+(.+)', q, re.I)
    if m:
        return m.group(1).strip().rstrip('?.')
    m = re.search(r'(.+?)\s+kimdir', q, re.I)
    if m:
        return m.group(1).strip()
    # "what is X" / "X nedir"
    m = re.search(r'(?:what is|what are)\s+(.+)', q, re.I)
    if m:
        return m.group(1).strip().rstrip('?.')
    m = re.search(r'(.+?)\s+nedir', q, re.I)
    if m:
        return m.group(1).strip()
    # Fallback: return whole query stripped of question marks
    return q.rstrip('?.!').strip()


def compose_answer(
    scored: List[Sentence],
    entities: List[Entity],
    query: str,
    query_type: str,
    max_sentences: int = 5,
) -> str:
    """
    Compose a fluent, structured answer from scored sentences.

    Respects query type:
    - biographical → lead with "who they are" sentence
    - definition  → lead with "X is …" sentence
    - comparative → list both sides
    - procedural  → ordered steps
    - general     → best sentences, original order
    """
    subject = _query_subject(query)

    # ---- Pick top N non-duplicate sentences ----
    selected: list[Sentence] = []
    seen: set[frozenset] = set()
    for sent in scored:
        if len(selected) >= max_sentences:
            break
        tokens = frozenset(sent.text.lower().split())
        is_dup = any(
            len(tokens & ex) / max(len(tokens), 1) > 0.55
            for ex in seen
        )
        if is_dup:
            continue
        seen.add(tokens)
        selected.append(sent)

    if not selected:
        return f"No clear information found for '{subject}'."

    # ---- Sort selected back into original document order ----
    selected.sort(key=lambda s: s.index)

    # ---- Type-specific ordering tweaks ----
    if query_type == 'biographical':
        # Push biographical / definition sentences to front
        bio_first = sorted(selected, key=lambda s: (
            -(s.is_biographical or s.is_definition),
            s.index
        ))
        selected = bio_first

    elif query_type == 'definition':
        def_first = sorted(selected, key=lambda s: (
            -s.is_definition,
            s.index
        ))
        selected = def_first

    # ---- Assemble prose ----
    paragraphs: list[str] = []
    for sent in selected:
        text = sent.text.strip()
        # Ensure capitalised start
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        # Ensure punctuation end
        if text and text[-1] not in '.!?':
            text += '.'
        paragraphs.append(text)

    return ' '.join(paragraphs)


# ======================================================================
# MAIN PUBLIC API — AnswerEngine
# ======================================================================

class AnswerEngine:
    """
    Pure-algorithmic answer synthesis engine.

    No LLM.  No neural network.  Just NLP math.

    Usage::

        engine = AnswerEngine()
        answer = engine.synthesize(
            raw_texts=["...scraped page 1...", "...scraped page 2..."],
            query="Kael Valen kimdir",
            sources=["duckduckgo", "wikipedia"],
            confidence=0.64,
        )
        print(answer.summary)
    """

    def __init__(
        self,
        max_summary_sentences: int = 5,
        max_key_facts: int = 5,
    ):
        self.max_summary_sentences = max_summary_sentences
        self.max_key_facts = max_key_facts

    def synthesize(
        self,
        raw_texts: List[str],
        query: str,
        sources: Optional[List[str]] = None,
        confidence: float = 0.5,
    ) -> StructuredAnswer:
        """
        Full pipeline: clean → segment → score → extract → compose → render.
        """
        sources = sources or []
        query_type = _detect_query_type(query)
        subject = _query_subject(query)
        query_entities = [subject] if subject else []

        logger.debug(f"AnswerEngine: type={query_type}, subject='{subject}'")

        # --- 1. Clean ---
        cleaned_texts = [deep_clean(t) for t in raw_texts if t]
        combined = ' '.join(cleaned_texts)

        if not combined.strip():
            return self._empty_answer(query, query_type, sources, confidence)

        # --- 2. Segment ---
        sentences = segment_sentences(combined)
        if not sentences:
            return self._empty_answer(query, query_type, sources, confidence)

        # --- 3. Score ---
        scored = score_sentences(
            sentences, query, query_entities=query_entities
        )

        # --- 4. Entities ---
        entities = extract_entities(combined)

        # --- 5. Key facts ---
        key_facts = extract_key_facts(scored, query, max_facts=self.max_key_facts)

        # --- 6. Compose ---
        summary = compose_answer(
            scored, entities, query, query_type,
            max_sentences=self.max_summary_sentences,
        )

        # --- 7. Confidence label ---
        confidence_label = self._confidence_label(confidence)

        return StructuredAnswer(
            summary=summary,
            key_facts=key_facts,
            entities=entities,
            sources=sources,
            query_type=query_type,
            confidence_label=confidence_label,
            confidence=confidence,
            raw_debug=combined[:500] if combined else None,
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _confidence_label(c: float) -> str:
        if c >= 0.8:
            return "High"
        if c >= 0.55:
            return "Moderate"
        if c >= 0.3:
            return "Low"
        return "Very Low"

    def _empty_answer(self, query, query_type, sources, confidence):
        subject = _query_subject(query)
        return StructuredAnswer(
            summary=f"Could not find enough information about '{subject}'.",
            key_facts=[],
            entities=[],
            sources=sources,
            query_type=query_type,
            confidence_label="Very Low",
            confidence=0.0,
        )


# ======================================================================
# OUTPUT RENDERER — final presentation layer
# ======================================================================

def render_answer(answer: StructuredAnswer, *, verbose: bool = False) -> str:
    """
    Render StructuredAnswer into a polished, terminal-friendly string.

    Example output::

        Arda Hakbilen (Kael Valen) is an ML Architecture Researcher
        focused on non-transformer models and systematic learning.

        Key Facts:
          • Researches non-transformer architectures
          • Focuses on systematic implementation methodologies
          • Works on ML architecture innovation

        Sources: duckduckgo, github.com
        Confidence: Moderate (0.64)
    """
    parts: list[str] = []

    # Main summary
    if answer.summary:
        parts.append(answer.summary)

    # Key facts
    if answer.key_facts:
        parts.append("")
        parts.append("Key Facts:")
        for fact in answer.key_facts:
            # Clean up fact text
            fact = fact.strip()
            if not fact:
                continue
            parts.append(f"  • {fact}")

    # Entities (only in verbose mode)
    if verbose and answer.entities:
        parts.append("")
        parts.append("Entities:")
        for ent in answer.entities:
            parts.append(f"  [{ent.category}] {ent.name}")

    # Sources
    if answer.sources:
        # Clean up source labels
        clean_sources: list[str] = []
        seen: set[str] = set()
        for s in answer.sources:
            label = s
            # Extract domain from URL-like sources
            if '://' in s:
                label = s.split('://')[1].split('/')[0].replace('www.', '')
            elif ':' in s:
                label = s.split(':')[0]
            label = label.strip()
            if label and label not in seen:
                seen.add(label)
                clean_sources.append(label)
        if clean_sources:
            parts.append("")
            parts.append(f"Sources: {', '.join(clean_sources[:4])}")

    # Confidence
    parts.append(f"Confidence: {answer.confidence_label} ({answer.confidence:.2f})")

    return '\n'.join(parts)
