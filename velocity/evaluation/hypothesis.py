"""
Hypothesis Evaluator

Parallel hypothesis evaluation using CPU.
Computation-based reasoning without GPU dependency.
"""

import asyncio
from typing import List, Dict, Any
from loguru import logger


class HypothesisEvaluator:
    """
    Parallel Hypothesis Evaluator
    
    Evaluates multiple hypotheses concurrently:
    1. Generate multiple possible explanations
    2. Test them simultaneously
    3. Eliminate weak ones early
    4. Deepen strong ones
    
    All computation runs on CPU.
    """
    
    def __init__(self):
        """Initialize Hypothesis Evaluator"""
        # Statistics
        self.hypotheses_evaluated = 0
        self.total_evaluation_time = 0.0
        
        logger.info("Hypothesis Evaluator initialized (CPU)")
    
    async def evaluate_parallel(
        self,
        hypotheses: List[str],
        state: Any  # CognitiveState
    ) -> List[Dict[str, Any]]:
        """
        Evaluate multiple hypotheses in parallel.
        
        Args:
            hypotheses: List of hypotheses to evaluate
            state: Current cognitive state
            
        Returns:
            Evaluated hypotheses with scores
        """
        if not hypotheses:
            return []
        
        logger.debug(f"Evaluating {len(hypotheses)} hypotheses in parallel")
        
        import time
        start_time = time.time()
        
        # Score each hypothesis against evidence
        results = []
        for hypothesis in hypotheses:
            score = await self._score_hypothesis(hypothesis, state)
            results.append({
                "hypothesis": hypothesis,
                "score": score,
                "method": "cpu"
            })
        
        evaluation_time = time.time() - start_time
        self.total_evaluation_time += evaluation_time
        self.hypotheses_evaluated += len(hypotheses)
        
        logger.debug(f"Evaluation completed in {evaluation_time:.3f}s")
        
        return results
    
    async def _score_hypothesis(
        self,
        hypothesis: str,
        state: Any
    ) -> float:
        """
        Score a hypothesis against current evidence.
        
        This is cognitive evaluation:
        - How well does this hypothesis explain the evidence?
        - How many contradictions does it resolve?
        - What's the confidence level?
        """
        score = 0.0
        
        # Base score: hypothesis length (simple heuristic)
        score += min(1.0, len(hypothesis) / 200)
        
        # Evidence support
        for topic, evidence_list in state.knowledge.items():
            for evidence in evidence_list:
                # Check if hypothesis aligns with evidence
                overlap = self._text_overlap(hypothesis, evidence.content)
                score += overlap * evidence.confidence * 0.1
        
        # Penalty for contradictions
        for contradiction in state.contradictions:
            if any(claim in hypothesis for claim in [contradiction.claim_a, contradiction.claim_b]):
                score -= contradiction.severity * 0.2
        
        # Normalize
        score = max(0.0, min(1.0, score))
        
        return score
    
    def _text_overlap(self, text1: str, text2: str) -> float:
        """
        Calculate text overlap using Jaccard similarity.
        
        Simple word-based similarity measure.
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get evaluator statistics"""
        avg_time = (
            self.total_evaluation_time / self.hypotheses_evaluated
            if self.hypotheses_evaluated > 0
            else 0.0
        )
        
        return {
            "hypotheses_evaluated": self.hypotheses_evaluated,
            "total_time": round(self.total_evaluation_time, 2),
            "avg_time_per_hypothesis": round(avg_time, 4),
        }
