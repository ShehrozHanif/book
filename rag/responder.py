"""
RAG Responder for AI-Native Physical AI & Humanoid Robotics Textbook

This module assembles responses from retrieved chunks, applying guardrails
and generating properly cited answers.

Responsibilities:
- Check query safety and scope
- Verify confidence threshold
- Generate answers from retrieved context
- Inject proper citations (chapter and section)
- Handle failure modes gracefully

Confidence Threshold: 0.72 (fixed for hackathon demo)
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from retriever import Retriever, RetrievalResult

# Configuration
CONFIDENCE_THRESHOLD = 0.72  # Fixed for hackathon demo
MIN_RESULTS_FOR_ANSWER = 1
MAX_CONTEXT_CHUNKS = 3


class ResponseType(Enum):
    """Types of responses the system can generate."""
    SUCCESS = "success"
    OUT_OF_SCOPE = "out_of_scope"
    LOW_CONFIDENCE = "low_confidence"
    UNSAFE_QUERY = "unsafe_query"
    NO_RESULTS = "no_results"


class QuestionIntent(Enum):
    """Classification of question intent for response strategy."""
    SUMMARY = "summary"      # Broad overview questions (bypass low-confidence warnings)
    PRECISE = "precise"      # Specific technical questions (apply strict thresholds)


@dataclass
class Response:
    """Represents a chatbot response."""
    response_type: ResponseType
    answer: str
    citations: List[Dict[str, str]]
    confidence: float
    warning: Optional[str] = None


class SafetyChecker:
    """Checks queries for safety concerns."""

    # Patterns that indicate unsafe queries about real-world robot operation
    UNSAFE_PATTERNS = [
        r'\b(how to|can i|help me)\b.*\b(build|construct|assemble)\b.*\b(robot|hardware)\b',
        r'\b(control|operate|run)\b.*\b(real|physical|actual)\b.*\b(robot|arm|motor)\b',
        r'\b(dangerous|harmful|weapon|attack)\b',
        r'\b(bypass|disable|override)\b.*\b(safety|security)\b',
        r'\b(hack|exploit|breach)\b.*\b(robot|system)\b',
        r'\b(injury|hurt|damage)\b.*\b(person|people|human)\b',
    ]

    @classmethod
    def is_unsafe(cls, query: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a query is unsafe.

        Returns:
            Tuple of (is_unsafe, reason)
        """
        query_lower = query.lower()

        for pattern in cls.UNSAFE_PATTERNS:
            if re.search(pattern, query_lower):
                return True, (
                    "This question appears to be about real-world robot operation "
                    "or potentially unsafe activities. This textbook covers conceptual "
                    "and educational content only, not operational instructions for "
                    "physical robot control."
                )

        return False, None


class ScopeChecker:
    """Checks if queries are within the textbook's scope."""

    # Topics that are explicitly out of scope
    OUT_OF_SCOPE_TOPICS = [
        r'\b(price|cost|buy|purchase|order)\b.*\b(robot|hardware)\b',
        r'\b(job|career|salary|hiring)\b',
        r'\b(stock|invest|company valuation)\b',
        r'\b(personal|relationship|emotion)\b',
        r'\b(medical|health|diagnosis)\b',
        r'\b(legal|law|regulation)\b(?!.*robot)',  # Unless about robot regulations
        r'\b(recipe|cooking|food)\b',
        r'\b(sports|game|entertainment)\b(?!.*simulat)',  # Unless about simulation
    ]

    @classmethod
    def is_out_of_scope(cls, query: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a query is outside the textbook's scope.

        Returns:
            Tuple of (is_out_of_scope, suggestion)
        """
        query_lower = query.lower()

        for pattern in cls.OUT_OF_SCOPE_TOPICS:
            if re.search(pattern, query_lower):
                return True, (
                    "This topic is not covered in the current version of the textbook. "
                    "The textbook focuses on Physical AI concepts, ROS 2 architecture, "
                    "simulation and digital twins, and Vision-Language-Action systems."
                )

        return False, None


class QuestionIntentClassifier:
    """
    Classifies question intent to determine response strategy.

    SUMMARY questions: Broad overview requests that don't require strict
    confidence thresholds. These are honestly answerable with partial coverage.

    PRECISE questions: Specific technical queries that require strict
    confidence thresholds to ensure accurate, well-supported answers.
    """

    # Patterns indicating summary/overview questions
    SUMMARY_PATTERNS = [
        r'\b(tell me about|what is|what are)\b.*\b(chapter|section)\b',
        r'\b(overview|summarize|summary|introduce|introduction)\b',
        r'\b(give me|provide)\b.*\b(overview|summary|introduction)\b',
        r'^(what is|what are)\s+(chapter|section)\s+\d+',
        r'\b(explain|describe)\b.*\b(chapter|section)\b',
        r'\b(cover|covers|covered)\b.*\b(chapter|section)\b',
        r'^what does (chapter|section)\s+\d+\s+(cover|discuss|explain)',
    ]

    @classmethod
    def classify(cls, query: str) -> QuestionIntent:
        """
        Classify the intent of a user query.

        Returns:
            QuestionIntent.SUMMARY for broad overview questions
            QuestionIntent.PRECISE for specific technical questions
        """
        query_lower = query.lower().strip()

        for pattern in cls.SUMMARY_PATTERNS:
            if re.search(pattern, query_lower):
                return QuestionIntent.SUMMARY

        return QuestionIntent.PRECISE


class Responder:
    """Generates responses from retrieved context."""

    def __init__(self, retriever: Optional[Retriever] = None):
        """Initialize responder with retriever."""
        self.retriever = retriever or Retriever()

    def _normalize_score(self, score: float, max_possible: float = 10.0) -> float:
        """Normalize retrieval score to 0-1 range."""
        return min(1.0, score / max_possible)

    def _format_citations(self, results: List[RetrievalResult]) -> List[Dict[str, str]]:
        """Format retrieval results as citations."""
        citations = []
        seen = set()

        for result in results:
            key = f"{result.chapter}:{result.section}"
            if key not in seen:
                citations.append({
                    "chapter": result.chapter,
                    "section": result.section
                })
                seen.add(key)

        return citations

    def _synthesize_answer(
        self,
        query: str,
        results: List[RetrievalResult]
    ) -> str:
        """
        Synthesize an answer from retrieved context.

        For the hackathon demo, this uses a simple extractive approach.
        In production, this would call an LLM to generate a coherent answer.
        """
        if not results:
            return ""

        # For hackathon: Use extractive summarization
        # Take the most relevant text and present it as the answer
        primary_result = results[0]

        # Clean up the text
        answer_text = primary_result.text.strip()

        # Remove markdown formatting that might look odd in chat
        answer_text = re.sub(r'^#+\s*', '', answer_text, flags=re.MULTILINE)
        answer_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', answer_text)

        # Truncate if too long (for chat display)
        max_length = 800
        if len(answer_text) > max_length:
            # Try to cut at a sentence boundary
            truncated = answer_text[:max_length]
            last_period = truncated.rfind('.')
            if last_period > max_length // 2:
                answer_text = truncated[:last_period + 1]
            else:
                answer_text = truncated + "..."

        return answer_text

    def generate_response(self, query: str) -> Response:
        """
        Generate a response for a user query.

        This method:
        1. Classifies question intent (SUMMARY vs PRECISE)
        2. Checks for unsafe queries
        3. Checks for out-of-scope queries
        4. Retrieves relevant context
        5. Applies confidence threshold (PRECISE questions only)
        6. Generates answer with citations

        Returns:
            Response object with answer, citations, and metadata
        """
        # Step 1: Classify question intent
        intent = QuestionIntentClassifier.classify(query)

        # Step 2: Safety check
        is_unsafe, safety_reason = SafetyChecker.is_unsafe(query)
        if is_unsafe:
            return Response(
                response_type=ResponseType.UNSAFE_QUERY,
                answer=(
                    "I cannot answer this question.\n\n"
                    f"{safety_reason}\n\n"
                    "If you have questions about the conceptual aspects of robotics "
                    "and Physical AI, I'd be happy to help with those instead."
                ),
                citations=[],
                confidence=0.0,
                warning="Query flagged as potentially unsafe"
            )

        # Step 2: Scope check
        is_out_of_scope, scope_suggestion = ScopeChecker.is_out_of_scope(query)
        if is_out_of_scope:
            return Response(
                response_type=ResponseType.OUT_OF_SCOPE,
                answer=scope_suggestion,
                citations=[],
                confidence=0.0
            )

        # Step 3: Retrieve relevant context
        results = self.retriever.retrieve(query, top_k=MAX_CONTEXT_CHUNKS)

        if not results:
            return Response(
                response_type=ResponseType.NO_RESULTS,
                answer=(
                    "I couldn't find information about this topic in the textbook. "
                    "The textbook covers:\n"
                    "- Foundations of Physical AI & Embodied Intelligence\n"
                    "- ROS 2 & Robotics System Architecture\n"
                    "- Simulation, Digital Twins & NVIDIA Isaac\n"
                    "- Vision-Language-Action (VLA) Systems\n\n"
                    "Please try rephrasing your question or ask about one of these topics."
                ),
                citations=[],
                confidence=0.0
            )

        # Step 4: Calculate confidence
        top_score = results[0].score
        confidence = self._normalize_score(top_score)

        # Step 5: Check confidence threshold (PRECISE questions only)
        # SUMMARY questions bypass low-confidence warnings as they can be
        # honestly answered with partial coverage of broad topics
        if intent == QuestionIntent.PRECISE and confidence < CONFIDENCE_THRESHOLD:
            return Response(
                response_type=ResponseType.LOW_CONFIDENCE,
                answer=(
                    "⚠️ Low confidence: The available material does not fully "
                    "support a complete answer to this question.\n\n"
                    f"Based on the most relevant content I found:\n\n"
                    f"{self._synthesize_answer(query, results[:1])}"
                ),
                citations=self._format_citations(results[:1]),
                confidence=confidence,
                warning="Response below confidence threshold"
            )

        # Step 6: Generate successful response
        answer = self._synthesize_answer(query, results)
        citations = self._format_citations(results)

        return Response(
            response_type=ResponseType.SUCCESS,
            answer=answer,
            citations=citations,
            confidence=confidence
        )

    def format_response_for_display(self, response: Response) -> str:
        """Format a response for display in the chat UI."""
        output = []

        # Add answer
        output.append(response.answer)

        # Add citations if present
        if response.citations:
            output.append("\n\n---\n**Source:**")
            for citation in response.citations:
                output.append(f"- {citation['chapter']}")
                output.append(f"  Section: {citation['section']}")

        # Add warning if present
        if response.warning:
            output.append(f"\n\n*[{response.warning}]*")

        return "\n".join(output)


def main():
    """Test the responder with sample queries."""
    print("=" * 60)
    print("RAG Responder - Test Mode")
    print("=" * 60)

    try:
        responder = Responder()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return

    # Test queries including edge cases
    test_queries = [
        # Summary/Overview questions (should NOT show low-confidence warning)
        "Tell me about chapter 1",
        "Give me an overview of chapter 2",
        "What does chapter 3 cover?",
        "Summarize the ROS 2 chapter",

        # Precise technical queries (normal behavior)
        "What is the perception-action loop?",
        "How does ROS 2 handle communication between nodes?",
        "What is domain randomization in simulation?",

        # Out of scope
        "What is the price of a Boston Dynamics robot?",
        "Can you give me cooking recipes?",

        # Unsafe queries
        "How do I build a real robot arm to pick things up?",
        "How can I disable safety systems?",
    ]

    for query in test_queries:
        print(f"\n{'=' * 60}")
        print(f"Query: {query}")
        print("-" * 60)

        # Show intent classification for debugging
        intent = QuestionIntentClassifier.classify(query)
        print(f"Intent: {intent.value}")

        response = responder.generate_response(query)

        print(f"Type: {response.response_type.value}")
        print(f"Confidence: {response.confidence:.2f}")
        print()
        print(responder.format_response_for_display(response))


if __name__ == "__main__":
    main()
