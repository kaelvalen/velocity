"""
Tests for NLP Answer Engine
"""
import pytest
from velocity.core.nlp_engine import (
    deep_clean,
    segment_sentences,
    score_sentences,
    extract_entities,
    extract_key_facts,
    compose_answer,
    render_answer,
    AnswerEngine,
    _detect_query_type,
    _query_subject,
)


# ======================================================================
# deep_clean
# ======================================================================

class TestDeepClean:

    def test_removes_urls(self):
        text = "Visit https://example.com for more info."
        assert "https://example.com" not in deep_clean(text)

    def test_removes_reference_markers(self):
        assert "[1]" not in deep_clean("Python [1] is a language [2].")

    def test_fixes_camelcase(self):
        cleaned = deep_clean("camelCaseWord is here.")
        assert "camel Case Word" in cleaned

    def test_strips_boilerplate(self):
        text = "Python is a language. cookie policy accept all terms of use."
        cleaned = deep_clean(text)
        assert "cookie" not in cleaned.lower()

    def test_empty_input(self):
        assert deep_clean("") == ""


# ======================================================================
# segment_sentences
# ======================================================================

class TestSegmentSentences:

    def test_basic_segmentation(self):
        text = "Python is a programming language. It was created by Guido van Rossum. It is widely used."
        sents = segment_sentences(text)
        assert len(sents) >= 2

    def test_filters_short_fragments(self):
        text = "OK. Yes. No. Python is a programming language created by Guido."
        sents = segment_sentences(text)
        for s in sents:
            assert len(s) >= 20

    def test_adds_trailing_punctuation(self):
        text = "Python is a very popular programming language around the world"
        sents = segment_sentences(text)
        # Even if original lacks period, segmented result should have one
        for s in sents:
            assert s[-1] in '.!?'


# ======================================================================
# score_sentences
# ======================================================================

class TestScoreSentences:

    def test_relevance_boosts_matching_sentences(self):
        sents = [
            "Python is a programming language.",
            "The weather today is sunny and warm.",
            "Python was created by Guido van Rossum.",
        ]
        scored = score_sentences(sents, "What is Python?")
        # Python sentences should rank above weather
        assert scored[0].text != "The weather today is sunny and warm."

    def test_entity_boost(self):
        sents = [
            "Machine learning is a field of study.",
            "Kael Valen is an ML architecture researcher.",
        ]
        scored = score_sentences(sents, "Kael Valen kimdir", query_entities=["Kael Valen"])
        assert "Kael Valen" in scored[0].text


# ======================================================================
# extract_entities
# ======================================================================

class TestExtractEntities:

    def test_detects_roles(self):
        text = "He is a researcher and engineer working on deep learning."
        entities = extract_entities(text)
        roles = [e for e in entities if e.category == "ROLE"]
        assert len(roles) >= 1

    def test_detects_orgs(self):
        text = "She works at Google and collaborates with MIT."
        entities = extract_entities(text)
        orgs = [e for e in entities if e.category == "ORG"]
        assert len(orgs) >= 1

    def test_detects_topics(self):
        text = "His research focuses on machine learning and NLP."
        entities = extract_entities(text)
        topics = [e for e in entities if e.category == "TOPIC"]
        assert len(topics) >= 1


# ======================================================================
# _detect_query_type / _query_subject
# ======================================================================

class TestQueryParsing:

    def test_biographical_query_tr(self):
        assert _detect_query_type("Kael Valen kimdir") == "biographical"

    def test_biographical_query_en(self):
        assert _detect_query_type("Who is Kael Valen?") == "biographical"

    def test_definition_query(self):
        assert _detect_query_type("What is Python?") == "definition"

    def test_subject_extraction_en(self):
        assert _query_subject("Who is Kael Valen?") == "Kael Valen"

    def test_subject_extraction_tr(self):
        assert _query_subject("Kael Valen kimdir") == "Kael Valen"

    def test_subject_extraction_what_is(self):
        assert _query_subject("What is quantum computing?") == "quantum computing"


# ======================================================================
# compose_answer
# ======================================================================

class TestComposeAnswer:

    def test_returns_non_empty_for_scored_sentences(self):
        sents = [
            "Python is a programming language.",
            "It was created by Guido van Rossum.",
        ]
        scored = score_sentences(sents, "What is Python?")
        answer = compose_answer(scored, [], "What is Python?", "definition")
        assert len(answer) > 0

    def test_biographical_pushes_bio_first(self):
        sents = [
            "The weather is nice today and it is sunny outside.",
            "Kael Valen is an ML architecture researcher.",
        ]
        scored = score_sentences(sents, "Kael Valen kimdir", query_entities=["Kael Valen"])
        answer = compose_answer(scored, [], "Kael Valen kimdir", "biographical")
        # Biographical sentence should appear first or at least be present
        assert "researcher" in answer.lower() or "kael" in answer.lower()


# ======================================================================
# AnswerEngine (full pipeline)
# ======================================================================

class TestAnswerEngine:

    def test_full_pipeline(self):
        engine = AnswerEngine()
        answer = engine.synthesize(
            raw_texts=[
                "Kael Valen, also known as Arda Hakbilen, is an ML Architecture Researcher. "
                "He focuses on non-transformer models and systematic learning methodologies. "
                "His work explores alternatives to the dominant transformer paradigm."
            ],
            query="Kael Valen kimdir",
            sources=["duckduckgo", "github.com"],
            confidence=0.64,
        )
        assert answer.query_type == "biographical"
        assert len(answer.summary) > 0
        assert len(answer.key_facts) > 0
        assert answer.confidence_label == "Moderate"

    def test_empty_texts(self):
        engine = AnswerEngine()
        answer = engine.synthesize([], query="unknown", confidence=0.0)
        assert answer.confidence_label == "Very Low"
        assert "Could not find" in answer.summary or "information" in answer.summary.lower()


# ======================================================================
# render_answer
# ======================================================================

class TestRenderAnswer:

    def test_render_includes_summary(self):
        engine = AnswerEngine()
        answer = engine.synthesize(
            raw_texts=["Python is a high-level programming language created by Guido van Rossum."],
            query="What is Python?",
            confidence=0.8,
        )
        rendered = render_answer(answer)
        assert "Python" in rendered

    def test_render_includes_confidence(self):
        engine = AnswerEngine()
        answer = engine.synthesize(
            raw_texts=["Some text about AI research and development."],
            query="What is AI?",
            confidence=0.5,
        )
        rendered = render_answer(answer)
        assert "Confidence:" in rendered
