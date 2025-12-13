# Plan — AI-Native Physical AI & Humanoid Robotics Textbook

**Aligned with Specification v1.4 (Hackathon Edition)**
**Status:** v1.4 — Locked (Hackathon)

---

## 1. Summary
This plan translates the Specification into a concrete system architecture and execution strategy. It defines system components, data flow, agent execution models, the RAG pipeline, and deployment strategy, all in faithful implementation of the Specification.

## 2. Technical Context

*   **Language/Version**: `JavaScript (Docusaurus)` for frontend, `Python 3.11` for backend/agent execution.
*   **Primary Dependencies**: `Docusaurus`, `React`, `Python`, `Gemini API`. For the RAG backend, a framework like `LangChain` with a vector store such as `ChromaDB`.
*   **Storage**: Vector Store (`ChromaDB`) for the RAG index. Content is stored as Markdown files in a Git repository.
*   **Testing**: `NEEDS CLARIFICATION: Testing strategy for Docusaurus and Python backend not defined.`
*   **Target Platform**: Web (Static Site).
*   **Project Type**: Web application with an AI backend.
*   **Performance Goals**: `NEEDS CLARIFICATION: Response time goals for the RAG chatbot are not specified.`
*   **Constraints**: Must be deployable on free static hosting (e.g., GitHub Pages, Vercel). The RAG backend must be lightweight. No autonomous agent execution is permitted.
*   **Scale/Scope**: 3-4 chapters for a hackathon MVP.

## 3. Constitution Check

This plan adheres to the following core principles from the project constitution:

*   **Spec-First Development**: All system logic is driven by the explicit feature specification.
*   **AI as a Team Member**: AI agents (Content, Reviewer) are treated as collaborators with defined roles.
*   **Educational Integrity**: The architecture prioritizes correctness and clarity of content.
*   **Reusability**: The agentic workflow is designed to be reusable for future content.
*   **Transparency & Accountability**: The entire process is designed to be traceable and auditable through specs and version control.

---

## 4. High-Level System Architecture

The system consists of **five primary layers**:

```
┌────────────────────────────┐
│  Docusaurus Frontend       │
│  (Textbook + Chat UI)      │
└──────────────┬─────────────┘
               │
┌──────────────▼─────────────┐
│  RAG Orchestration Layer   │
│  (Retrieval + Guardrails)  │
└──────────────┬─────────────┘
               │
┌──────────────▼─────────────┐
│  Knowledge Index           │
│  (Chunked Textbook)        │
└──────────────┬─────────────┘
               │
┌──────────────▼─────────────┐
│  AI Agent Layer            │
│  (Content + Reviewer)      │
└──────────────┬─────────────┘
               │
┌──────────────▼─────────────┐
│  Spec Files (Source Truth) │
│  Constitution / Spec /    │
│  Plan / Tasks              │
└────────────────────────────┘
```

---

## 5. Agent Execution Model (Hackathon-Safe)

### 5.1 Agent Runtime Environment

*   **Content Agent** and **Reviewer / Verifier Agent** are executed via CLI-driven AI sessions (e.g., Gemini CLI) with explicit, version-controlled prompt templates.
*   Agent execution is deterministic, human-invoked, and spec-governed.
*   There is **no autonomous or background execution** during the hackathon.

📌 **Rationale:** Demonstrates *agentic governance*, not automation theater.

---

### 5.2 Agent Prompt Templates (First-Class Artifacts)

*   Agent prompt templates are first-class, version-controlled artifacts stored under `/agents/`.
*   Prompts are human-authored, spec-governed, and executed manually via CLI.
*   **Authority chain:** Constitution → Specification → Plan → Tasks → Agent Prompts. Prompts **execute behavior**; they do not define scope.

---

## 6. Content Creation Workflow (Agentic)

### 6.1 Chapter Generation Flow

For each chapter:
1.  **Inputs**: Constitution, Specification, Chapter learning objectives.
2.  **Content Agent**: Generates chapter text, Mermaid diagrams, and section structure, enforcing word limits, diagram limits, and safety constraints.
3.  **Reviewer / Verifier Agent**: Validates technical correctness, spec compliance, and conceptual consistency, producing a Pass/Fail decision.
4.  **Human-in-the-Loop**: Required for Chapter 1, new core concepts, and the final pre-deployment snapshot.
5.  **Publish Gate**: Only **Reviewer-approved** content is published.

---

## 7. Textbook Rendering (Frontend)

### Platform Choice: Docusaurus
*   Markdown-native, versionable, judge-friendly, static, and reliable.

### Directory Structure
```
/docs
  /chapter-1-foundations.md
  /chapter-2-ros2.md
  /chapter-3-simulation.md
  /chapter-4-vla.md
```
Each chapter file follows the mandatory chapter structure, contains Mermaid diagrams, includes "Further Reading" links, and is indexed for RAG.

---

## 8. RAG Chatbot Architecture

### 8.1 Indexing Pipeline
1.  Parse chapter Markdown.
2.  Chunk by **subsection** (300–500 token chunks).
3.  Attach metadata: Chapter, Section, Concept tags.

### 8.2 Retrieval Mechanism
*   Vector-based similarity search, top-k retrieval, and metadata filtering. Vector store implementation is **intentionally abstracted**.

### 8.3 Confidence Threshold Ownership
*   Confidence thresholds are **heuristic-based and fixed for the hackathon**, determined by retrieval score, citation completeness, and chunk agreement. Final authority is the **Human system designer**.

### 8.4 Guardrails
*   Out-of-scope → refusal + explanation
*   Low-confidence → flagged response
*   Unsafe queries → immediate refusal + redirect

---

## 9. RAG Backend Execution Mode
*   Implemented as a **single-process, lightweight backend** (local or minimal API).
*   Priorities are deterministic behavior, fast startup, and demo stability. No distributed infrastructure is required.

---

## 10. Diagram Rendering Strategy
*   **Primary Mode**: Mermaid diagrams rendered directly in Docusaurus.
*   **Fallback Mode**: If rendering fails, use explanatory text and verbal explanation. Diagrams are supporting artifacts, not single points of failure.

---

## 11. Demo Strategy (Hackathon)

### Canonical Demo Questions Authority
*   Canonical demo questions are defined in the Specification and mirrored in `/demo/canonical-questions.md`. They are frozen, pre-validated, and used in all demos.

### Primary Demo Flow
1.  Open public textbook site.
2.  Navigate between chapters, highlighting diagrams.
3.  Ask canonical chatbot questions, emphasizing citations, refusals, and spec-constrained answers.

### Fallback Demo Flow (Authority & Trigger)
*   Triggered **only by the Human Project Owner** in case of instability.
*   Assets include pre-recorded answers, screenshots, and walkthroughs of the project's architecture. Judges evaluate **architecture and intent, not uptime.**

---

## 12. Human-in-the-Loop Evidence
*   Human review is demonstrated through observable artifacts like reviewer checklists, "Reviewed & Approved" notes in commit messages, and verbal explanations during the demo.

---

## 13. Deployment Plan
*   **Static site hosting**: GitHub Pages / Vercel / Netlify.
*   **RAG backend**: Local or lightweight API.
*   No authentication or paid infrastructure is required.

---

## 14. Non-Goals (Reconfirmed)
This plan explicitly excludes robot hardware control, ROS execution, simulation runtime, real-time systems, and production scalability.

---

## 15. Validation Checklist (Pre-Demo)
*   [ ] Minimum submission threshold satisfied (see Section 16)
*   [ ] Chapter 1 complete and approved
*   [ ] Remaining chapters approved or excluded
*   [ ] Diagrams render or fallback ready
*   [ ] Chatbot cites chapters + sections
*   [ ] Unsafe queries refused
*   [ ] Canonical demo questions answered flawlessly

---

## 16. Minimum Hackathon Submission Threshold
The **minimum acceptable submission** consists of: Constitution.md, Specification.md, this Plan.md, **at least one fully approved chapter (Chapter 1)**, and a chatbot answering **at least one canonical question** (live or recorded). Anything beyond this baseline improves the score but is **not required for validity**.

---

## 17. Hackathon Execution Sequence (Authoritative)
1.  Lock Constitution and Specification.
2.  Generate chapter content via Content Agent.
3.  Review content via Reviewer Agent.
4.  Human approval gate.
5.  Index approved content for RAG.
6.  Deploy static site.
7.  Run demo (live or fallback).
Steps must be executed **in order**.

---

## 18. Post-Submission Repository Handling
*   The repository is treated as **frozen** at submission time. No changes are made unless explicitly requested by judges. Any post-submission edits must be clearly disclosed and versioned separately.

---

## 19. Plan Status
**Locked — v1.4 (Hackathon Edition)**
This plan is now sufficient to generate `tasks.md`, agent prompt templates, a judge demo script, and the Docusaurus structure mapping.