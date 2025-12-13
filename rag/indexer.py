"""
RAG Indexer for AI-Native Physical AI & Humanoid Robotics Textbook

This module handles parsing approved chapter markdown files and creating
a searchable index for the RAG chatbot.

Responsibilities:
- Load ONLY approved chapter markdown files
- Verify approval status via in-file YAML frontmatter
- Split content by headings into sections
- Chunk sections into 300-500 token segments
- Attach metadata (chapter, section, tags)
- Build vector index for retrieval

Manual trigger: python rag/indexer.py
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

# Configuration
DOCS_PATH = Path(__file__).parent.parent / "docusaurus" / "docs"
INDEX_PATH = Path(__file__).parent / "index.json"
CHUNK_MIN_TOKENS = 300
CHUNK_MAX_TOKENS = 500
APPROX_CHARS_PER_TOKEN = 4  # Rough approximation


@dataclass
class Chunk:
    """Represents a chunk of textbook content for indexing."""
    id: str
    text: str
    chapter: str
    section: str
    tags: List[str]
    token_count: int
    source_file: str


def estimate_tokens(text: str) -> int:
    """Estimate token count from text (rough approximation)."""
    return len(text) // APPROX_CHARS_PER_TOKEN


def extract_frontmatter(content: str) -> Tuple[Dict, str]:
    """Extract YAML frontmatter from markdown content."""
    frontmatter = {}
    body = content

    # Match YAML frontmatter between --- delimiters
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        frontmatter_text = match.group(1)
        body = content[match.end():]

        # Simple YAML parsing for our specific format
        for line in frontmatter_text.split('\n'):
            if ':' in line:
                # Handle nested keys like "approval:"
                if line.strip().endswith(':'):
                    continue
                # Handle simple key-value pairs
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip("'\"")
                frontmatter[key] = value

    return frontmatter, body


def is_approved(frontmatter: Dict) -> bool:
    """Check if a chapter is approved based on frontmatter."""
    # Check for approval marker in frontmatter
    reviewer = frontmatter.get('reviewer', '').upper()
    approved_by = frontmatter.get('approved_by', '')

    return reviewer == 'PASS' and bool(approved_by)


def extract_chapter_title(content: str) -> str:
    """Extract chapter title from markdown content."""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Unknown Chapter"


def split_by_sections(content: str) -> List[Tuple[str, str]]:
    """Split content into sections based on markdown headings."""
    sections = []
    current_section = "Introduction"
    current_content = []

    for line in content.split('\n'):
        # Match ## headings (sections)
        heading_match = re.match(r'^##\s+(.+)$', line)
        if heading_match:
            # Save previous section
            if current_content:
                sections.append((current_section, '\n'.join(current_content)))
            current_section = heading_match.group(1).strip()
            current_content = []
        else:
            current_content.append(line)

    # Don't forget the last section
    if current_content:
        sections.append((current_section, '\n'.join(current_content)))

    return sections


def chunk_text(text: str, section: str, chapter: str, source_file: str) -> List[Chunk]:
    """Split text into chunks of appropriate size."""
    chunks = []

    # Split by paragraphs first
    paragraphs = re.split(r'\n\s*\n', text)

    current_chunk = []
    current_tokens = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_tokens = estimate_tokens(para)

        # If this paragraph alone exceeds max, split it further
        if para_tokens > CHUNK_MAX_TOKENS:
            # Save current chunk first
            if current_chunk:
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append(create_chunk(chunk_text, section, chapter, source_file))
                current_chunk = []
                current_tokens = 0

            # Split large paragraph by sentences
            sentences = re.split(r'(?<=[.!?])\s+', para)
            for sentence in sentences:
                sent_tokens = estimate_tokens(sentence)
                if current_tokens + sent_tokens > CHUNK_MAX_TOKENS and current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    chunks.append(create_chunk(chunk_text, section, chapter, source_file))
                    current_chunk = []
                    current_tokens = 0
                current_chunk.append(sentence)
                current_tokens += sent_tokens

        # Check if adding this paragraph would exceed max
        elif current_tokens + para_tokens > CHUNK_MAX_TOKENS and current_chunk:
            # Save current chunk and start new one
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append(create_chunk(chunk_text, section, chapter, source_file))
            current_chunk = [para]
            current_tokens = para_tokens
        else:
            current_chunk.append(para)
            current_tokens += para_tokens

    # Don't forget the last chunk
    if current_chunk:
        chunk_text = '\n\n'.join(current_chunk)
        # Only add if it has meaningful content
        if current_tokens >= CHUNK_MIN_TOKENS // 2:  # Allow smaller final chunks
            chunks.append(create_chunk(chunk_text, section, chapter, source_file))

    return chunks


def create_chunk(text: str, section: str, chapter: str, source_file: str) -> Chunk:
    """Create a Chunk object with metadata."""
    # Generate unique ID from content hash
    chunk_id = hashlib.md5(f"{chapter}:{section}:{text[:100]}".encode()).hexdigest()[:12]

    # Extract tags from content (simple keyword extraction)
    tags = extract_tags(text, chapter)

    return Chunk(
        id=chunk_id,
        text=text,
        chapter=chapter,
        section=section,
        tags=tags,
        token_count=estimate_tokens(text),
        source_file=source_file
    )


def extract_tags(text: str, chapter: str) -> List[str]:
    """Extract relevant tags from text content."""
    # Define keyword patterns for tagging
    tag_patterns = {
        'physical-ai': r'\bphysical ai\b',
        'embodiment': r'\bembodied?\b',
        'perception': r'\bperception\b',
        'action': r'\baction\b|\bactuator',
        'ros2': r'\bros\s*2\b',
        'simulation': r'\bsimulat',
        'digital-twin': r'\bdigital twin',
        'nvidia-isaac': r'\bisaac\b',
        'vla': r'\bvla\b|vision.language.action',
        'foundation-model': r'\bfoundation model',
        'llm': r'\bllm\b|language model',
        'robot-learning': r'\brobot.?learning|imitation|reinforcement',
        'sensor': r'\bsensor',
        'control': r'\bcontrol\b',
        'planning': r'\bplanning\b',
        'navigation': r'\bnavigation\b',
    }

    tags = []
    text_lower = text.lower()

    for tag, pattern in tag_patterns.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            tags.append(tag)

    # Add chapter-based tag
    if 'foundation' in chapter.lower():
        tags.append('foundations')
    elif 'ros' in chapter.lower():
        tags.append('ros2-architecture')
    elif 'simulation' in chapter.lower():
        tags.append('simulation-twins')
    elif 'vla' in chapter.lower():
        tags.append('vla-systems')

    return list(set(tags))


def process_chapter(file_path: Path) -> List[Chunk]:
    """Process a single chapter file and return chunks."""
    print(f"Processing: {file_path.name}")

    content = file_path.read_text(encoding='utf-8')
    frontmatter, body = extract_frontmatter(content)

    # Check approval status
    if not is_approved(frontmatter):
        print(f"  SKIPPED: Not approved (missing approval marker)")
        return []

    print(f"  APPROVED: Processing content...")

    # Extract chapter title
    chapter_title = extract_chapter_title(body)

    # Split into sections
    sections = split_by_sections(body)

    # Generate chunks
    all_chunks = []
    for section_name, section_content in sections:
        # Skip certain sections
        if any(skip in section_name.lower() for skip in ['further reading', 'learning objectives']):
            continue

        chunks = chunk_text(section_content, section_name, chapter_title, file_path.name)
        all_chunks.extend(chunks)

    print(f"  Generated {len(all_chunks)} chunks")
    return all_chunks


def build_index() -> Dict:
    """Build the complete index from all approved chapters."""
    print("=" * 60)
    print("RAG Indexer - AI-Native Physical AI Textbook")
    print("=" * 60)
    print(f"Docs path: {DOCS_PATH}")
    print()

    all_chunks = []

    # Find all chapter files
    chapter_files = sorted(DOCS_PATH.glob("chapter-*.md"))

    if not chapter_files:
        print("ERROR: No chapter files found!")
        return {"chunks": [], "metadata": {"total_chunks": 0}}

    print(f"Found {len(chapter_files)} chapter files")
    print()

    for file_path in chapter_files:
        chunks = process_chapter(file_path)
        all_chunks.extend(chunks)

    print()
    print("=" * 60)
    print(f"Total chunks indexed: {len(all_chunks)}")
    print("=" * 60)

    # Build index structure
    index = {
        "chunks": [asdict(chunk) for chunk in all_chunks],
        "metadata": {
            "total_chunks": len(all_chunks),
            "chapters_processed": len(chapter_files),
            "index_version": "1.0"
        }
    }

    return index


def save_index(index: Dict) -> None:
    """Save index to JSON file."""
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"Index saved to: {INDEX_PATH}")


def main():
    """Main entry point for indexer."""
    index = build_index()
    save_index(index)

    # Print sample chunk for verification
    if index["chunks"]:
        print()
        print("Sample chunk:")
        print("-" * 40)
        sample = index["chunks"][0]
        print(f"Chapter: {sample['chapter']}")
        print(f"Section: {sample['section']}")
        print(f"Tags: {sample['tags']}")
        print(f"Tokens: {sample['token_count']}")
        print(f"Text preview: {sample['text'][:200]}...")


if __name__ == "__main__":
    main()
