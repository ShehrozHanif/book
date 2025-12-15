"""
AGENTIC RAG Responder for AI-Native Physical AI & Humanoid Robotics Textbook

This module implements TRUE agentic RAG with:
- Explicit chapter intent routing
- Intent classification (SUMMARY / EXPLAIN_SIMPLE / DEFINE / PRECISE)
- Retrieval strategy changes based on intent
- Prompt strategy changes based on intent

Responsibilities:
- Detect chapter references and route accordingly
- Classify user intent for response style adaptation
- Check query safety and scope
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

# ============================================================
# ENVIRONMENT LOADING
# ============================================================

def load_env():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
        except Exception:
            pass  # Fail silently - env vars may be set elsewhere

load_env()

# Try to import Google Generative AI
GEMINI_AVAILABLE = False
genai = None

try:
    import google.generativeai as genai
    api_key = os.environ.get('API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        GEMINI_AVAILABLE = True
except ImportError:
    pass
except Exception:
    pass  # API key configuration failed - continue without LLM

# ============================================================
# CONFIGURATION
# ============================================================

CONFIDENCE_THRESHOLD = 0.72  # Fixed for hackathon demo
MIN_RESULTS_FOR_ANSWER = 1
MAX_CONTEXT_CHUNKS = 5  # Increased for better chapter coverage


# ============================================================
# ENUMS
# ============================================================

class ResponseType(Enum):
    """Types of responses the system can generate."""
    SUCCESS = "success"
    OUT_OF_SCOPE = "out_of_scope"
    LOW_CONFIDENCE = "low_confidence"
    UNSAFE_QUERY = "unsafe_query"
    NO_RESULTS = "no_results"


class AgentIntent(Enum):
    """
    Classification of question intent for agentic response strategy.

    SUMMARY: Broad overview questions - provide structured summaries
    EXPLAIN_SIMPLE: Requests for simplified explanations - use beginner language
    DEFINE: Definition requests - start with clear definition
    PRECISE: Specific technical questions - apply strict thresholds
    """
    SUMMARY = "summary"
    EXPLAIN_SIMPLE = "explain_simple"
    DEFINE = "define"
    PRECISE = "precise"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class Response:
    """Represents a chatbot response."""
    response_type: ResponseType
    answer: str
    citations: List[Dict[str, str]]
    confidence: float
    warning: Optional[str] = None


# ============================================================
# AGENTIC ROUTING FUNCTIONS
# ============================================================

def detect_chapter(query: str) -> Optional[str]:
    """
    Detect explicit chapter reference in query.

    Matches patterns like:
    - "chapter 1", "Chapter 2", "chapter3"
    - "ch 1", "ch. 2"

    Returns:
        Chapter filter string like "Chapter 1" or None if no chapter mentioned
    """
    query_lower = query.lower()

    # Pattern: "chapter X" or "ch X" or "ch. X"
    patterns = [
        r'chapter\s*(\d+)',
        r'ch\.?\s*(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            chapter_num = match.group(1)
            return f"Chapter {chapter_num}"

    return None


def detect_agent_intent(query: str) -> AgentIntent:
    """
    Classify the intent of a user query for response strategy.

    This determines:
    - How to structure the response
    - What prompt template to use
    - Whether to apply confidence thresholds

    Returns:
        AgentIntent enum value
    """
    q = query.lower().strip()

    # DEFINE intent: Definition requests
    define_patterns = [
        r'\bdefine\b',
        r'\bdefinition\s+of\b',
        r'\bmeaning\s+of\b',
        r'^what\s+is\s+(a|an|the)?\s*\w+\??$',  # Simple "what is X?" queries
    ]
    for pattern in define_patterns:
        if re.search(pattern, q):
            return AgentIntent.DEFINE

    # EXPLAIN_SIMPLE intent: Simplified explanation requests
    simple_patterns = [
        r'\bsimple\s+terms?\b',
        r'\bsimply\b',
        r'\beasy\s+to\s+understand\b',
        r'\bbeginner\b',
        r'\bbasic\b.*\bexplain',
        r'\bexplain\b.*\bsimpl',
        r'\beli5\b',  # Explain Like I'm 5
        r'\bin\s+layman',
    ]
    for pattern in simple_patterns:
        if re.search(pattern, q):
            return AgentIntent.EXPLAIN_SIMPLE

    # SUMMARY intent: Overview/summary requests
    summary_patterns = [
        r'\btell\s+me\s+about\b',
        r'\boverview\b',
        r'\bsummary\b',
        r'\bsummarize\b',
        r'\bkey\s*points?\b',
        r'\bmain\s*points?\b',
        r'\bhighlights?\b',
        r'\btakeaways?\b',
        r'\bwhat\s+(does|is)\s+(chapter|section)\s+\d+\s+(cover|about)',
        r'\bbriefly\b',
        r'\bintroduc',
    ]
    for pattern in summary_patterns:
        if re.search(pattern, q):
            return AgentIntent.SUMMARY

    # Default: PRECISE for specific technical questions
    return AgentIntent.PRECISE


# ============================================================
# SAFETY AND SCOPE CHECKERS
# ============================================================

class SafetyChecker:
    """Checks queries for safety concerns."""

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
        """Check if a query is unsafe."""
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

    OUT_OF_SCOPE_TOPICS = [
        r'\b(price|cost|buy|purchase|order)\b.*\b(robot|hardware)\b',
        r'\b(job|career|salary|hiring)\b',
        r'\b(stock|invest|company valuation)\b',
        r'\b(personal|relationship|emotion)\b',
        r'\b(medical|health|diagnosis)\b',
        r'\b(legal|law|regulation)\b(?!.*robot)',
        r'\b(recipe|cooking|food)\b',
        r'\b(sports|game|entertainment)\b(?!.*simulat)',
    ]

    @classmethod
    def is_out_of_scope(cls, query: str) -> Tuple[bool, Optional[str]]:
        """Check if a query is outside the textbook's scope."""
        query_lower = query.lower()

        for pattern in cls.OUT_OF_SCOPE_TOPICS:
            if re.search(pattern, query_lower):
                return True, (
                    "This topic is not covered in the current version of the textbook. "
                    "The textbook focuses on Physical AI concepts, ROS 2 architecture, "
                    "simulation and digital twins, and Vision-Language-Action systems."
                )

        return False, None


# ============================================================
# PROMPT TEMPLATES BY INTENT
# ============================================================

def build_prompt(intent: AgentIntent, query: str, results: List[RetrievalResult]) -> str:
    """
    Build an intent-specific prompt for Gemini LLM.

    Different intents produce different prompt structures to guide
    the LLM toward the appropriate response style.
    """
    # Combine context from all results
    context_parts = []
    for i, result in enumerate(results, 1):
        context_parts.append(
            f"[Source {i}: {result.chapter} - {result.section}]\n{result.text}"
        )
    context = "\n\n---\n\n".join(context_parts)

    # Intent-specific style instructions
    style_instructions = {
        AgentIntent.SUMMARY: (
            "Provide a structured summary with clear headings and bullet points. "
            "Cover the main topics and key concepts. Aim for comprehensive coverage."
        ),
        AgentIntent.EXPLAIN_SIMPLE: (
            "Explain in very simple language, as if teaching a complete beginner. "
            "Avoid jargon. Use analogies and everyday examples where possible. "
            "Keep sentences short and clear."
        ),
        AgentIntent.DEFINE: (
            "Start with a clear, concise definition (1-2 sentences). "
            "Then provide a brief explanation with context. "
            "Keep the definition prominent and distinct."
        ),
        AgentIntent.PRECISE: (
            "Provide a technically accurate and precise answer. "
            "Include relevant details and specifics. "
            "Maintain technical correctness."
        ),
    }

    style = style_instructions.get(intent, style_instructions[AgentIntent.PRECISE])

    prompt = f"""You are an expert teaching assistant for a Physical AI & Robotics textbook.
Answer the student's question based ONLY on the provided textbook content.

RESPONSE STYLE:
{style}

RULES:
- Use ONLY information from the provided textbook content
- Do NOT make up or hallucinate information
- Do NOT mention "the context" or "provided text" - speak directly as a teacher
- Be educational and helpful
- Aim for 150-400 words depending on question complexity

TEXTBOOK CONTENT:
{context}

STUDENT QUESTION: {query}

ANSWER:"""

    return prompt


# ============================================================
# MAIN RESPONDER CLASS
# ============================================================

class Responder:
    """
    Agentic RAG Responder with intent-aware retrieval and generation.

    This responder:
    1. Detects chapter references for targeted retrieval
    2. Classifies user intent for response style adaptation
    3. Applies safety and scope checks
    4. Generates contextual answers using Gemini LLM
    5. Provides accurate citations
    """

    def __init__(self, retriever: Optional[Retriever] = None):
        """Initialize responder with retriever and LLM model."""
        self.retriever = retriever or Retriever()
        self.llm_model = None

        # Initialize Gemini model if available
        if GEMINI_AVAILABLE and genai is not None:
            try:
                self.llm_model = genai.GenerativeModel('gemini-2.0-flash')
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
        results: List[RetrievalResult],
        intent: AgentIntent
    ) -> str:
        """
        Synthesize an answer from retrieved context using Gemini LLM.

        Uses intent-specific prompts for appropriate response styling.
        Falls back to extractive summarization if LLM is unavailable.
        """
        if not results:
            return ""

        # Try LLM-based synthesis first
        if self.llm_model:
            try:
                return self._synthesize_with_llm(query, results, intent)
            except Exception as e:
                print(f"Warning: LLM synthesis failed, falling back to extractive: {e}")

        # Fallback: extractive summarization
        return self._extractive_summarize(results)

    def _synthesize_with_llm(
        self,
        query: str,
        results: List[RetrievalResult],
        intent: AgentIntent
    ) -> str:
        """Use Gemini LLM to synthesize an intent-aware answer."""
        prompt = build_prompt(intent, query, results)

        # Adjust generation config based on intent
        temperature = 0.3 if intent == AgentIntent.PRECISE else 0.4
        max_tokens = 700 if intent == AgentIntent.SUMMARY else 500

        response = self.llm_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
        )

        return response.text.strip()

    def _extractive_summarize(self, results: List[RetrievalResult]) -> str:
        """Fallback: Extract and clean the most relevant text."""
        primary_result = results[0]

        answer_text = primary_result.text.strip()

        # Remove markdown formatting
        answer_text = re.sub(r'^#+\s*', '', answer_text, flags=re.MULTILINE)
        answer_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', answer_text)

        # Truncate if too long
        max_length = 800
        if len(answer_text) > max_length:
            truncated = answer_text[:max_length]
            last_period = truncated.rfind('.')
            if last_period > max_length // 2:
                answer_text = truncated[:last_period + 1]
            else:
                answer_text = truncated + "..."

        return answer_text

    def generate_response(self, query: str) -> Response:
        """
        Generate an agentic response for a user query.

        This method implements TRUE agentic RAG:
        1. Detects chapter reference for targeted retrieval
        2. Classifies intent for response style adaptation
        3. Checks for unsafe/out-of-scope queries
        4. Retrieves with chapter filter if applicable
        5. Applies confidence thresholds (PRECISE intent only)
        6. Generates intent-aware answer with citations

        Returns:
            Response object with answer, citations, and metadata
        """
        # Step 1: Detect chapter reference (CRITICAL for routing)
        chapter_filter = detect_chapter(query)

        # Step 2: Classify intent for response strategy
        intent = detect_agent_intent(query)

        # Step 3: Safety check
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

        # Step 4: Scope check
        is_out_of_scope, scope_suggestion = ScopeChecker.is_out_of_scope(query)
        if is_out_of_scope:
            return Response(
                response_type=ResponseType.OUT_OF_SCOPE,
                answer=scope_suggestion,
                citations=[],
                confidence=0.0
            )

        # Step 5: Retrieve with chapter filter (AGENTIC ROUTING)
        results = self.retriever.retrieve(
            query=query,
            top_k=MAX_CONTEXT_CHUNKS,
            chapter_filter=chapter_filter  # THIS IS THE KEY FIX
        )

        if not results:
            # If chapter filter returned nothing, provide helpful message
            if chapter_filter:
                return Response(
                    response_type=ResponseType.NO_RESULTS,
                    answer=(
                        f"I couldn't find information about this topic in {chapter_filter}. "
                        "Please check the chapter number or try a more general question."
                    ),
                    citations=[],
                    confidence=0.0
                )
            return Response(
                response_type=ResponseType.NO_RESULTS,
                answer=(
                    "I couldn't find information about this topic in the textbook. "
                    "The textbook covers:\n"
                    "- Chapter 1: Foundations of Physical AI & Embodied Intelligence\n"
                    "- Chapter 2: ROS 2 & Robotics System Architecture\n"
                    "- Chapter 3: Simulation, Digital Twins & NVIDIA Isaac\n"
                    "- Chapter 4: Vision-Language-Action (VLA) Systems\n\n"
                    "Please try rephrasing your question or ask about one of these topics."
                ),
                citations=[],
                confidence=0.0
            )

        # Step 6: Calculate confidence
        top_score = results[0].score
        confidence = self._normalize_score(top_score)

        # Step 7: Check confidence threshold (PRECISE intent only)
        # SUMMARY, EXPLAIN_SIMPLE, DEFINE bypass low-confidence warnings
        # as they can be honestly answered with partial coverage
        if intent == AgentIntent.PRECISE and confidence < CONFIDENCE_THRESHOLD:
            return Response(
                response_type=ResponseType.LOW_CONFIDENCE,
                answer=(
                    "Low confidence: The available material does not fully "
                    "support a complete answer to this question.\n\n"
                    f"Based on the most relevant content I found:\n\n"
                    f"{self._synthesize_answer(query, results[:1], intent)}"
                ),
                citations=self._format_citations(results[:1]),
                confidence=confidence,
                warning="Response below confidence threshold"
            )

        # Step 8: Generate successful response with intent-aware synthesis
        answer = self._synthesize_answer(query, results, intent)
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

        output.append(response.answer)

        if response.citations:
            output.append("\n\n---\n**Source:**")
            for citation in response.citations:
                output.append(f"- {citation['chapter']}")
                output.append(f"  Section: {citation['section']}")

        if response.warning:
            output.append(f"\n\n*[{response.warning}]*")

        return "\n".join(output)


# ============================================================
# TEST / DEBUG ENTRYPOINT
# ============================================================

def main():
    """Test the agentic responder with sample queries."""
    print("=" * 60)
    print("AGENTIC RAG Responder - Test Mode")
    print("=" * 60)

    try:
        responder = Responder()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return

    # Test queries for chapter routing and intent classification
    test_queries = [
        # Chapter routing tests (CRITICAL)
        ("Tell me about chapter 1", "SUMMARY", "Chapter 1"),
        ("Tell me about chapter 2", "SUMMARY", "Chapter 2"),
        ("What does chapter 3 cover?", "SUMMARY", "Chapter 3"),
        ("Key points of chapter 4", "SUMMARY", "Chapter 4"),

        # Intent classification tests
        ("Define embodied intelligence", "DEFINE", None),
        ("Explain the perception-action loop in simple terms", "EXPLAIN_SIMPLE", None),
        ("Give me an overview of ROS 2", "SUMMARY", None),
        ("How does domain randomization work?", "PRECISE", None),

        # Edge cases
        ("What is the price of a robot?", "OUT_OF_SCOPE", None),
    ]

    for query_tuple in test_queries:
        query = query_tuple[0]
        expected_intent = query_tuple[1]
        expected_chapter = query_tuple[2]

        print(f"\n{'=' * 60}")
        print(f"Query: {query}")
        print("-" * 60)

        # Show routing decisions
        detected_chapter = detect_chapter(query)
        detected_intent = detect_agent_intent(query)

        print(f"Detected Chapter: {detected_chapter} (expected: {expected_chapter})")
        print(f"Detected Intent: {detected_intent.value} (expected: {expected_intent})")

        response = responder.generate_response(query)

        print(f"Response Type: {response.response_type.value}")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Citations: {[c['chapter'] for c in response.citations]}")
        print()
        print("Answer preview:", response.answer[:300] + "..." if len(response.answer) > 300 else response.answer)


if __name__ == "__main__":
    main()
