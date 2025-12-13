# Data Model for AI-Native Textbook

This document defines the key data entities for the project, based on the feature specification.

## 1. Textbook

The top-level container for all educational content.

*   **Attributes**:
    *   `title` (string): The main title of the textbook. E.g., "AI-Native Physical AI & Humanoid Robotics Textbook".
    *   `version` (string): The version of the textbook. E.g., "v1.4 (Hackathon Edition)".
*   **Relationships**:
    *   Has many `Chapters`.

## 2. Chapter

A self-contained unit of learning on a specific topic.

*   **Attributes**:
    *   `title` (string): The title of the chapter. E.g., "Foundations of Physical AI & Embodied Intelligence".
    *   `word_count` (integer): The total number of words in the chapter.
    *   `source_file` (string): The path to the source Markdown file. E.g., `/docs/chapter-1-foundations.md`.
*   **Relationships**:
    *   Belongs to one `Textbook`.
    *   Has many `Sections`.
    *   Has many `Diagrams`.
    *   Has many `LearningObjectives`.

## 3. Section

A distinct part of a chapter focusing on a sub-topic.

*   **Attributes**:
    *   `title` (string): The title of the section.
    *   `content` (string): The text content of the section.
*   **Relationships**:
    *   Belongs to one `Chapter`.

## 4. AI Agent

A role within the content generation pipeline.

*   **Attributes**:
    *   `role` (string): The role of the agent. E.g., "Content Agent", "Reviewer/Verifier Agent".
    *   `prompt_template` (string): The path to the prompt template file for this agent.

## 5. Chatbot

The RAG-based conversational interface.

*   **Attributes**:
    *   `knowledge_index` (VectorStore): The indexed content of the textbook.
    *   `confidence_threshold` (float): The threshold for providing an answer.
