"""
RAG Retriever for AI-Native Physical AI & Humanoid Robotics Textbook

This module handles searching the indexed textbook content to find
relevant chunks for answering user questions.

Responsibilities:
- Load the index created by indexer.py
- Perform similarity search on queries
- Return top-k relevant chunks with metadata
- Filter by metadata when appropriate

Note: This implementation uses a simple keyword-based search for the hackathon.
For production, replace with vector embeddings (e.g., ChromaDB, FAISS).
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Configuration
INDEX_PATH = Path(__file__).parent / "index.json"
DEFAULT_TOP_K = 5


@dataclass
class RetrievalResult:
    """Represents a retrieval result with relevance score."""
    chunk_id: str
    text: str
    chapter: str
    section: str
    tags: List[str]
    score: float
    source_file: str


class Retriever:
    """Retrieves relevant chunks from the textbook index."""

    def __init__(self, index_path: Path = INDEX_PATH):
        """Initialize retriever with index."""
        self.index_path = index_path
        self.chunks = []
        self.metadata = {}
        self._load_index()

    def _load_index(self) -> None:
        """Load index from JSON file."""
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"Index not found at {self.index_path}. "
                "Run indexer.py first to create the index."
            )

        with open(self.index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.chunks = data.get("chunks", [])
        self.metadata = data.get("metadata", {})

        print(f"Loaded index with {len(self.chunks)} chunks")

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for keyword matching."""
        # Convert to lowercase and extract words
        words = re.findall(r'\b\w+\b', text.lower())
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
            'between', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
            'on', 'off', 'over', 'under', 'again', 'further', 'then',
            'once', 'here', 'there', 'when', 'where', 'why', 'how',
            'all', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
            'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or',
            'because', 'as', 'until', 'while', 'what', 'which', 'who',
            'this', 'that', 'these', 'those', 'i', 'me', 'my', 'we',
            'our', 'you', 'your', 'it', 'its', 'they', 'them', 'their'
        }
        return [w for w in words if w not in stop_words and len(w) > 2]

    def _compute_relevance(self, query_tokens: List[str], chunk: Dict) -> float:
        """Compute relevance score between query and chunk."""
        chunk_text = chunk.get("text", "").lower()
        chunk_section = chunk.get("section", "").lower()
        chunk_chapter = chunk.get("chapter", "").lower()
        chunk_tags = [t.lower() for t in chunk.get("tags", [])]

        score = 0.0

        for token in query_tokens:
            # Exact word match in text (weighted by frequency)
            text_matches = len(re.findall(rf'\b{re.escape(token)}\b', chunk_text))
            score += text_matches * 1.0

            # Match in section title (higher weight)
            if token in chunk_section:
                score += 3.0

            # Match in chapter title (medium weight)
            if token in chunk_chapter:
                score += 2.0

            # Match in tags (highest weight)
            for tag in chunk_tags:
                if token in tag or tag in token:
                    score += 5.0

        # Normalize by query length to prevent bias toward long queries
        if query_tokens:
            score /= len(query_tokens)

        return score

    def retrieve(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        chapter_filter: Optional[str] = None,
        tag_filter: Optional[List[str]] = None
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: The user's question
            top_k: Number of results to return
            chapter_filter: Optional filter for specific chapter
            tag_filter: Optional filter for specific tags

        Returns:
            List of RetrievalResult objects sorted by relevance
        """
        if not self.chunks:
            return []

        query_tokens = self._tokenize(query)

        if not query_tokens:
            return []

        # Score all chunks
        scored_chunks = []
        for chunk in self.chunks:
            # Apply filters
            if chapter_filter:
                if chapter_filter.lower() not in chunk.get("chapter", "").lower():
                    continue

            if tag_filter:
                chunk_tags = [t.lower() for t in chunk.get("tags", [])]
                if not any(t.lower() in chunk_tags for t in tag_filter):
                    continue

            score = self._compute_relevance(query_tokens, chunk)

            if score > 0:
                scored_chunks.append((chunk, score))

        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        # Return top-k results
        results = []
        for chunk, score in scored_chunks[:top_k]:
            results.append(RetrievalResult(
                chunk_id=chunk.get("id", ""),
                text=chunk.get("text", ""),
                chapter=chunk.get("chapter", ""),
                section=chunk.get("section", ""),
                tags=chunk.get("tags", []),
                score=score,
                source_file=chunk.get("source_file", "")
            ))

        return results

    def get_all_chapters(self) -> List[str]:
        """Get list of all indexed chapters."""
        chapters = set()
        for chunk in self.chunks:
            chapters.add(chunk.get("chapter", ""))
        return sorted(chapters)

    def get_all_tags(self) -> List[str]:
        """Get list of all tags in the index."""
        tags = set()
        for chunk in self.chunks:
            tags.update(chunk.get("tags", []))
        return sorted(tags)


def main():
    """Test the retriever with sample queries."""
    print("=" * 60)
    print("RAG Retriever - Test Mode")
    print("=" * 60)

    try:
        retriever = Retriever()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return

    print(f"\nIndexed chapters: {retriever.get_all_chapters()}")
    print(f"Available tags: {retriever.get_all_tags()}")

    # Test queries
    test_queries = [
        "What is the perception-action loop?",
        "How does ROS 2 work?",
        "What is domain randomization?",
        "Explain VLA systems",
        "What are digital twins?"
    ]

    for query in test_queries:
        print(f"\n{'=' * 60}")
        print(f"Query: {query}")
        print("-" * 60)

        results = retriever.retrieve(query, top_k=3)

        if not results:
            print("No relevant results found.")
            continue

        for i, result in enumerate(results, 1):
            print(f"\nResult {i} (score: {result.score:.2f}):")
            print(f"  Chapter: {result.chapter}")
            print(f"  Section: {result.section}")
            print(f"  Tags: {result.tags}")
            print(f"  Text preview: {result.text[:150]}...")


if __name__ == "__main__":
    main()







 changes






# """
# RAG Retriever for AI-Native Physical AI & Humanoid Robotics Textbook
# """

# import json
# import re
# from pathlib import Path
# from typing import List, Optional
# from dataclasses import dataclass

# INDEX_PATH = Path(__file__).parent / "index.json"
# DEFAULT_TOP_K = 5


# @dataclass
# class RetrievalResult:
#     chunk_id: str
#     text: str
#     chapter: str
#     section: str
#     tags: List[str]
#     score: float
#     source_file: str


# class Retriever:
#     def __init__(self, index_path: Path = INDEX_PATH):
#         self.index_path = index_path
#         self.chunks = []
#         self.metadata = {}
#         self._load_index()

#     def _load_index(self):
#         if not self.index_path.exists():
#             raise FileNotFoundError("index.json not found. Run indexer.py first.")

#         with open(self.index_path, "r", encoding="utf-8") as f:
#             data = json.load(f)

#         self.chunks = data.get("chunks", [])
#         self.metadata = data.get("metadata", {})
#         print(f"[Retriever] Loaded {len(self.chunks)} chunks")

#     # ---------- NEW (CRITICAL) ----------
#     def _extract_chapter_number(self, chapter_name: str) -> Optional[str]:
#         """
#         Extracts chapter number from:
#         'Chapter 2: ROS 2 & Robotics System Architecture'
#         """
#         match = re.search(r'chapter\s*(\d+)', chapter_name.lower())
#         return match.group(1) if match else None
#     # -----------------------------------

#     def _tokenize(self, text: str) -> List[str]:
#         words = re.findall(r'\b\w+\b', text.lower())
#         stop_words = {
#             'the','is','are','a','an','and','or','of','to','in','on','for','with',
#             'about','what','how','why','does','do','did','this','that'
#         }
#         return [w for w in words if w not in stop_words and len(w) > 2]

#     def _compute_relevance(self, tokens: List[str], chunk: dict) -> float:
#         score = 0.0
#         text = chunk["text"].lower()
#         section = chunk["section"].lower()
#         chapter = chunk["chapter"].lower()
#         tags = [t.lower() for t in chunk.get("tags", [])]

#         for t in tokens:
#             score += text.count(t)
#             if t in section:
#                 score += 3
#             if t in chapter:
#                 score += 2
#             if any(t in tag for tag in tags):
#                 score += 5

#         return score / max(len(tokens), 1)

#     def retrieve(
#         self,
#         query: str,
#         top_k: int = DEFAULT_TOP_K,
#         chapter_filter: Optional[str] = None
#     ) -> List[RetrievalResult]:

#         tokens = self._tokenize(query)
#         if not tokens:
#             return []

#         scored = []

#         for chunk in self.chunks:
#             # ---------- HARD CHAPTER FILTER ----------
#             if chapter_filter:
#                 chunk_ch = self._extract_chapter_number(chunk["chapter"])
#                 if chunk_ch != chapter_filter:
#                     continue
#             # ---------------------------------------

#             score = self._compute_relevance(tokens, chunk)
#             if score > 0:
#                 scored.append((chunk, score))

#         scored.sort(key=lambda x: x[1], reverse=True)

#         return [
#             RetrievalResult(
#                 chunk_id=c["id"],
#                 text=c["text"],
#                 chapter=c["chapter"],
#                 section=c["section"],
#                 tags=c.get("tags", []),
#                 score=s,
#                 source_file=c.get("source_file", "")
#             )
#             for c, s in scored[:top_k]
#         ]

#     def get_all_chapters(self) -> List[str]:
#         return sorted({c["chapter"] for c in self.chunks})

#     def get_all_tags(self) -> List[str]:
#         tags = set()
#         for c in self.chunks:
#             tags.update(c.get("tags", []))
#         return sorted(tags)
