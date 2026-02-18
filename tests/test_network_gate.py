"""
Tests for NetworkGate
"""
import pytest
from velocity.core.network_gate import NetworkGate, generate_local_response
from velocity.core.intent_parser import IntentParser, DecisionType


def _intent(text: str):
    return IntentParser().parse(text)


class TestNetworkGate:

    def test_social_intent_skips_network(self):
        gate = NetworkGate()
        intent = _intent("Hello, how are you?")
        decision = gate.should_interrogate(intent)
        # Social intents should never hit the network
        if intent.decision_type == DecisionType.SOCIAL:
            assert decision['interrogate'] is False
            assert decision['reason'] == 'social_intent'

    def test_factual_intent_uses_network(self):
        gate = NetworkGate()
        intent = _intent("What is the speed of light?")
        decision = gate.should_interrogate(intent)
        if intent.decision_type == DecisionType.FACTUAL:
            assert decision['interrogate'] is True

    def test_creative_intent_declined_by_default(self):
        gate = NetworkGate(allow_creative=False)
        # Inject a CREATIVE intent directly
        intent = _intent("Write me a poem about the stars")
        intent.decision_type = DecisionType.CREATIVE
        decision = gate.should_interrogate(intent)
        assert decision['interrogate'] is False
        assert decision['reason'] == 'creative_intent'

    def test_creative_intent_allowed_when_configured(self):
        gate = NetworkGate(allow_creative=True)
        intent = _intent("Write me a poem about the stars")
        intent.decision_type = DecisionType.CREATIVE
        decision = gate.should_interrogate(intent)
        assert decision['interrogate'] is True
        assert decision['reason'] == 'creative_allowed'

    def test_high_local_confidence_skips_network(self):
        gate = NetworkGate()
        intent = _intent("What is 2 + 2?")
        decision = gate.should_interrogate(intent, local_confidence=0.95)
        assert decision['interrogate'] is False
        assert decision['reason'] == 'high_local_confidence'


class TestGenerateLocalResponse:

    def test_social_response(self):
        intent = _intent("Hello")
        intent.decision_type = DecisionType.SOCIAL
        response = generate_local_response(intent, 'local_social')
        assert isinstance(response, str)
        assert len(response) > 0

    def test_meta_response(self):
        intent = _intent("What is Velocity?")
        intent.decision_type = DecisionType.META
        response = generate_local_response(intent, 'local_meta')
        assert "Velocity" in response

    def test_decline_creative_message_contains_hint(self):
        intent = _intent("Write a poem")
        intent.decision_type = DecisionType.CREATIVE
        response = generate_local_response(intent, 'local_decline')
        assert "allow_creative" in response or "factual" in response.lower()
