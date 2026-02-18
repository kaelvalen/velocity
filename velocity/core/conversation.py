"""
Conversation Memory - Context buffer for multi-turn sessions

Velocity'nin tek-turn'lük sorgu yapısını çok-turlu konuşmaya
dönüştürür.  Her `execute()` çağrısına geçmiş konuşma bağlamı eklenir.

Architecture:
    user  → VelocityCore.execute(user_input, session_id="...")
                               ↓
                    ConversationBuffer.build_context()
                               ↓
              context-enriched input → interrogation pipeline
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Turn:
    """A single conversation turn (user + assistant)."""
    role: str           # "user" | "assistant"
    content: str
    timestamp: float = field(default_factory=time.monotonic)
    confidence: Optional[float] = None  # Only set for assistant turns


@dataclass
class Session:
    """A conversation session identified by a unique session_id."""
    session_id: str
    turns: List[Turn] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    # ------------------------------------------------------------------ #
    # Public helpers                                                       #
    # ------------------------------------------------------------------ #

    def add_user(self, content: str) -> None:
        self.turns.append(Turn(role="user", content=content))

    def add_assistant(self, content: str, confidence: Optional[float] = None) -> None:
        self.turns.append(Turn(role="assistant", content=content, confidence=confidence))

    def last_n(self, n: int) -> List[Turn]:
        """Return the last *n* turns (most recent first is preserved)."""
        return self.turns[-n:]

    def build_context(self, max_turns: int = 6) -> str:
        """
        Format recent conversation history into a compact context string
        that can be prepended to the current query.

        Example output::

            [Previous conversation]
            User: What is Python?
            Assistant: Python is a high-level programming language...
            User: Who created it?
            Assistant: Guido van Rossum created Python...
        """
        recent = self.last_n(max_turns)
        if not recent:
            return ""

        lines = ["[Previous conversation]"]
        for turn in recent:
            role_label = "User" if turn.role == "user" else "Assistant"
            lines.append(f"{role_label}: {turn.content}")
        lines.append("")  # trailing newline for clean concatenation
        return "\n".join(lines)

    @property
    def num_turns(self) -> int:
        return len(self.turns)


class ConversationBuffer:
    """
    Multi-session conversation memory.

    Keepsessions in memory.  Sessions are automatically pruned when
    ``max_sessions`` is reached (LRU-style: oldest session removed).

    Usage with VelocityCore::

        buffer = ConversationBuffer()
        session_id = "user-abc"

        buffer.add_user_turn(session_id, "What is Python?")
        result = await core.execute(
            buffer.enrich_query(session_id, "What is Python?")
        )
        buffer.add_assistant_turn(
            session_id,
            result["decision"],
            confidence=result["confidence"]
        )
    """

    def __init__(
        self,
        max_sessions: int = 100,
        max_turns_per_session: int = 50,
        context_window: int = 6,
    ) -> None:
        self.max_sessions = max_sessions
        self.max_turns_per_session = max_turns_per_session
        self.context_window = context_window
        self._sessions: Dict[str, Session] = {}
        self._access_order: List[str] = []  # for LRU eviction

    # ------------------------------------------------------------------ #
    # Session management                                                   #
    # ------------------------------------------------------------------ #

    def get_or_create(self, session_id: str) -> Session:
        """Return existing session or create a new one."""
        if session_id not in self._sessions:
            self._ensure_capacity()
            self._sessions[session_id] = Session(session_id)

        # Update LRU order
        if session_id in self._access_order:
            self._access_order.remove(session_id)
        self._access_order.append(session_id)
        return self._sessions[session_id]

    def delete_session(self, session_id: str) -> bool:
        """Explicitly delete a session. Returns True if it existed."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            if session_id in self._access_order:
                self._access_order.remove(session_id)
            return True
        return False

    # ------------------------------------------------------------------ #
    # Turn recording                                                       #
    # ------------------------------------------------------------------ #

    def add_user_turn(self, session_id: str, content: str) -> None:
        session = self.get_or_create(session_id)
        session.add_user(content)
        self._trim_session(session)

    def add_assistant_turn(
        self,
        session_id: str,
        content: str,
        confidence: Optional[float] = None,
    ) -> None:
        session = self.get_or_create(session_id)
        session.add_assistant(content, confidence)
        self._trim_session(session)

    # ------------------------------------------------------------------ #
    # Context enrichment                                                   #
    # ------------------------------------------------------------------ #

    def enrich_query(self, session_id: str, current_query: str) -> str:
        """
        Prepend conversation context to the current query.

        If there is no history (first turn), returns the raw query unchanged.
        """
        session = self._sessions.get(session_id)
        if session is None or session.num_turns == 0:
            return current_query

        context = session.build_context(max_turns=self.context_window)
        if not context:
            return current_query

        return f"{context}Current question: {current_query}"

    # ------------------------------------------------------------------ #
    # Stats                                                                #
    # ------------------------------------------------------------------ #

    @property
    def active_sessions(self) -> int:
        return len(self._sessions)

    def session_info(self, session_id: str) -> Optional[Dict]:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        return {
            "session_id": session_id,
            "num_turns": session.num_turns,
            "created_at": session.created_at,
        }

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _ensure_capacity(self) -> None:
        """Evict oldest session if at capacity."""
        while len(self._sessions) >= self.max_sessions and self._access_order:
            oldest = self._access_order.pop(0)
            self._sessions.pop(oldest, None)

    def _trim_session(self, session: Session) -> None:
        """Keep turns within max_turns_per_session to bound memory."""
        if session.num_turns > self.max_turns_per_session:
            # Drop oldest turns (keep the most recent half)
            keep = self.max_turns_per_session // 2
            session.turns = session.turns[-keep:]
