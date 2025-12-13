"""
RAG Responder for AI-Native Physical AI & Humanoid Robotics Textbook

This module assembles responses from retrieved chunks, applying guardrails
and generating properly cited answers using Gemini LLM.

Responsibilities:
- Check query safety and scope
- Verify confidence threshold
- Generate answers from retrieved context using Gemini LLM
- Inject proper citations (chapter and section)
- Handle failure modes gracefully

Confidence Threshold: 0.72 (fixed for hackathon demo)
"""

import os
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from retriever import Retriever, RetrievalResult

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value

load_env()

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    # Configure Gemini with API key
    api_key = os.environ.get('API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

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
        # Chapter/section references
        r'\b(tell me about|what is|what are)\b.*\b(chapter|section)\b',
        r'^(what is|what are)\s+(chapter|section)\s+\d+',
        r'\b(explain|describe)\b.*\b(chapter|section)\b',
        r'\b(cover|covers|covered)\b.*\b(chapter|section)\b',
        r'^what does (chapter|section)\s+\d+\s+(cover|discuss|explain)',
        # Overview/summary keywords
        r'\b(overview|summarize|summary|introduce|introduction)\b',
        r'\b(give me|provide)\b.*\b(overview|summary|introduction)\b',
        # Key points / highlights
        r'\b(key\s*points?|main\s*points?|highlights?|takeaways?)\b',
        r'\b(key\s*concepts?|main\s*ideas?|main\s*topics?)\b',
        r'\b(briefly|brief)\b.*\b(explain|describe|tell)\b',
        # General chapter questions
        r'\b(what|whats)\b.*\b(chapter\s*\d+|section\s*\d+)\b.*\b(about)\b',
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
    """Generates responses from retrieved context using Gemini LLM."""

    def __init__(self, retriever: Optional[Retriever] = None):
        """Initialize responder with retriever and LLM model."""
        self.retriever = retriever or Retriever()
        self.llm_model = None

        # Initialize Gemini model if available
        if GEMINI_AVAILABLE and os.environ.get('API_KEY'):
            try:
                self.llm_model = genai.GenerativeModel('gemini-2.5-flash')
            except Exception as e:
                print(f"Warning: Could not initialize Gemini model: {e}")

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
        Synthesize an answer from retrieved context using Gemini LLM.

        If Gemini is available, uses LLM to generate a coherent, well-structured answer.
        Falls back to extractive summarization if LLM is unavailable.
        """
        if not results:
            return ""

        # Try LLM-based synthesis first
        if self.llm_model:
            try:
                return self._synthesize_with_llm(query, results)
            except Exception as e:
                print(f"Warning: LLM synthesis failed, falling back to extractive: {e}")

        # Fallback: extractive summarization
        return self._extractive_summarize(results)

    def _synthesize_with_llm(
        self,
        query: str,
        results: List[RetrievalResult]
    ) -> str:
        """Use Gemini LLM to synthesize a coherent answer from retrieved chunks."""
        # Combine context from all results
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Source {i}: {result.chapter} - {result.section}]\n{result.text}"
            )
        context = "\n\n---\n\n".join(context_parts)

        # Create the prompt for Gemini
        prompt = f"""You are a helpful teaching assistant for a Physical AI & Robotics textbook.
Answer the student's question based ONLY on the provided context from the textbook.

RULES:
- Be concise but comprehensive (aim for 150-300 words)
- Use clear, educational language
- Structure your answer with bullet points or numbered lists when appropriate
- Do NOT make up information not in the context
- Do NOT mention "the context" or "the provided text" - speak directly as if teaching
- If the question asks for key points, provide a clear numbered list

CONTEXT FROM TEXTBOOK:
{context}

STUDENT QUESTION: {query}

ANSWER:"""

        # Call Gemini API
        response = self.llm_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=500,
                temperature=0.3,  # Low temperature for factual accuracy
            )
        )

        return response.text.strip()

    def _extractive_summarize(self, results: List[RetrievalResult]) -> str:
        """Fallback: Extract and clean the most relevant text."""
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
        "Key points of chapter 1",
        "Give me an overview of chapter 2",
        "What does chapter 3 cover?",
        "Main takeaways from chapter 4",

        # Precise technical queries (normal behavior)
        "What is the perception-action loop?",
        "How does ROS 2 handle communication between nodes?",
        "What is domain randomization in simulation?",

        # Out of scope
        "What is the price of a Boston Dynamics robot?",

        # Unsafe queries
        "How do I build a real robot arm to pick things up?",
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
