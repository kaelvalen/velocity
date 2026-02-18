"""
Tests for ConversationBuffer
"""
import pytest
from velocity.core.conversation import ConversationBuffer, Session, Turn


class TestSession:

    def test_empty_session_context(self):
        s = Session("s1")
        assert s.build_context() == ""

    def test_add_turns(self):
        s = Session("s1")
        s.add_user("Hello")
        s.add_assistant("Hi!")
        assert s.num_turns == 2

    def test_build_context_format(self):
        s = Session("s1")
        s.add_user("What is Python?")
        s.add_assistant("Python is a programming language.")
        ctx = s.build_context()
        assert "[Previous conversation]" in ctx
        assert "User: What is Python?" in ctx
        assert "Assistant: Python is a programming language." in ctx

    def test_last_n_limits_context(self):
        s = Session("s1")
        for i in range(10):
            s.add_user(f"q{i}")
            s.add_assistant(f"a{i}")
        ctx = s.build_context(max_turns=2)
        # Should only contain the last 2 turns
        assert "q9" in ctx or "a9" in ctx


class TestConversationBuffer:

    def test_session_created_on_demand(self):
        buf = ConversationBuffer()
        buf.add_user_turn("alice", "hello")
        info = buf.session_info("alice")
        assert info is not None
        assert info["num_turns"] == 1

    def test_enrich_query_no_history(self):
        buf = ConversationBuffer()
        result = buf.enrich_query("new_session", "What is AI?")
        assert result == "What is AI?"

    def test_enrich_query_with_history(self):
        buf = ConversationBuffer()
        buf.add_user_turn("alice", "What is Python?")
        buf.add_assistant_turn("alice", "Python is a language.")
        enriched = buf.enrich_query("alice", "Who created it?")
        assert "[Previous conversation]" in enriched
        assert "What is Python?" in enriched
        assert "Current question: Who created it?" in enriched

    def test_lru_session_eviction(self):
        buf = ConversationBuffer(max_sessions=2)
        buf.add_user_turn("s1", "q")
        buf.add_user_turn("s2", "q")
        buf.add_user_turn("s3", "q")  # should evict s1
        assert buf.session_info("s1") is None
        assert buf.session_info("s2") is not None
        assert buf.session_info("s3") is not None

    def test_delete_session(self):
        buf = ConversationBuffer()
        buf.add_user_turn("alice", "hi")
        assert buf.delete_session("alice") is True
        assert buf.session_info("alice") is None
        assert buf.delete_session("alice") is False

    def test_max_turns_trim(self):
        buf = ConversationBuffer(max_turns_per_session=4)
        for i in range(10):
            buf.add_user_turn("s", f"q{i}")
        session = buf.get_or_create("s")
        # After trimming, turns should be <= max_turns_per_session
        assert session.num_turns <= 4

    def test_active_sessions_count(self):
        buf = ConversationBuffer()
        assert buf.active_sessions == 0
        buf.add_user_turn("s1", "hi")
        buf.add_user_turn("s2", "hi")
        assert buf.active_sessions == 2
