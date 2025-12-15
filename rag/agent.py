# rag/agent.py

import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class TaskType(Enum):
    SUMMARY = "summary"
    EXPLAIN = "explain"
    DEFINE = "define"
    GENERAL = "general"


@dataclass
class AgentDecision:
    task_type: TaskType
    chapter_filter: Optional[str]
    simple_mode: bool


class AgentRouter:
    """
    Agent layer that decides HOW to answer before retrieval.
    """

    CHAPTER_REGEX = re.compile(r'chapter\s*(\d+)', re.IGNORECASE)

    def route(self, query: str) -> AgentDecision:
        q = query.lower()

        # ---- Chapter detection ----
        chapter_filter = None
        match = self.CHAPTER_REGEX.search(q)
        if match:
            chapter_filter = f"Chapter {match.group(1)}"

        # ---- Task type ----
        if any(x in q for x in ["tell me about", "summary", "overview"]):
            task = TaskType.SUMMARY
        elif any(x in q for x in ["explain", "break down"]):
            task = TaskType.EXPLAIN
        elif any(x in q for x in ["define", "what is", "meaning of"]):
            task = TaskType.DEFINE
        else:
            task = TaskType.GENERAL

        # ---- Simplicity ----
        simple_mode = any(x in q for x in ["simple", "easy", "beginner"])

        return AgentDecision(
            task_type=task,
            chapter_filter=chapter_filter,
            simple_mode=simple_mode
        )
