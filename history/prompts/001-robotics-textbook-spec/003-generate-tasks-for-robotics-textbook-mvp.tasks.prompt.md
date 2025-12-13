---
id: 003
title: Generate Tasks for Robotics Textbook MVP
stage: tasks
date: 2025-12-13
surface: agent
model: gemini-1.5-pro
feature: 001-robotics-textbook-spec
branch: 001-robotics-textbook-spec
user: user
command: /sp.tasks
labels: [tasks, planning, robotics]
links:
  spec: specs/001-robotics-textbook-spec/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-robotics-textbook-spec/tasks.md
tests:
  (none)
---

## Prompt

# Tasks — AI-Native Physical AI & Humanoid Robotics Textbook **Aligned with Constitution v1.0 · Specification v1.4 · Plan v1.4** **Status:** Hackathon Execution Tasks (Authoritative) --- ## Purpose of This File This file breaks the **Plan** into **concrete, executable tasks** suitable for a hackathon environment. Rules: * Tasks introduce **no new scope** * Each task is independently verifiable * Tasks are ordered by **maximum demo impact first** * Tasks assume **human-in-the-loop execution via CLI (Gemini CLI)** * **Human Project Owner is the accountable owner for all tasks** --- ## Task 0 — Repository & SpecKit Baseline **Goal:** Establish a clean, judge-readable foundation. **Actions:** * Initialize repository * Add locked spec files: * `constitution.md` * `specification.md` * `plan.md` * Add README with: * Project intent * Hackathon framing * Architecture diagram reference **Acceptance Criteria:** * Specs are present, readable, and versioned * README clearly explains *what this system is* **Estimated Effort:** S --- ## Task 1 — Docusaurus Scaffold **Goal:** Create the visible textbook surface. **Actions:** * Initialize Docusaurus site * Configure sidebar navigation * Add placeholder chapter pages **Files:** ``` /docs chapter-1-foundations.md chapter-2-ros2.md chapter-3-simulation.md chapter-4-vla.md ``` **Acceptance Criteria:** * Site builds and deploys locally * Chapters are navigable **Estimated Effort:** S --- ## Task 2 — Agent Prompt Templates **Goal:** Formalize agent behavior. **Actions:** Create: ``` /agents/ content-agent.md reviewer-agent.md ``` Each prompt must: * Reference Constitution + Specification * Define role, inputs, outputs * Include refusal rules **Acceptance Criteria:** * Prompts are human-readable * Executable via Gemini CLI **Estimated Effort:** S --- ## Task 3 — Chapter 1 Content Generation (Foundational) **Goal:** Produce the most important chapter. **Actions:** * Run Content Agent for Chapter 1 * Include: * Learning objectives * Mermaid diagrams * Experimental section * Run Reviewer Agent * Apply human approval * Add **explicit approval marker** in chapter file: * YAML frontmatter or * Visible metadata section **Approval Definition:** A chapter is considered **approved** only when: 1. Reviewer Agent issues a **pass** decision 2. Approval is visible via at least one observable artifact: * Commit message (e.g., `Reviewed & Approved — Chapter 1`) * OR in-file approval marker **Acceptance Criteria:** * Chapter meets length + structure rules * Reviewer approves and approval is visible **Estimated Effort:** M --- ## Task 4 — Additional Chapter Generation (2–4) **Goal:** Expand depth if time permits. **Actions:** * Repeat Task 3 for Chapters 2–4 * Time-box each chapter * **Abort generation immediately** if reviewer flags major issues **Rules:** * Late-stage failures result in **chapter exclusion**, not rushed fixes * Excluded chapters are: * Removed from Docusaurus sidebar * Not indexed for RAG * Demo proceeds with fewer chapters if necessary **Acceptance Criteria:** * At least **2 chapters approved** total **Estimated Effort:** M–L (time-boxed) --- ## Task 5 — Knowledge Index & Chunking **Goal:** Prepare content for RAG. **Actions:** * Parse approved chapters * Chunk by subsection (300–500 tokens) * Attach metadata **Acceptance Criteria:** * Chunks map cleanly to sections **Estimated Effort:** S --- ## Task 6 — RAG Backend (Minimal) **Goal:** Enable constrained QA. **Actions:** * Implement retrieval logic using **simplified or lightweight mechanisms**: * In-memory vector store or lightweight library * Deterministic or heuristic retrieval acceptable * Enforce: * Citation injection (chapter + section) * Explicit refusal behavior * Fixed confidence threshold (no auto-tuning) * Prepare **negative test questions** to validate refusal behavior **Rules:** * Retrieval must remain **spec-correct** * Answers must be **strictly grounded in textbook content** * Infrastructure scale is explicitly out of scope **Acceptance Criteria:** * Canonical questions answered correctly * Out-of-scope questions refused visibly **Estimated Effort:** M --- ## Task 7 — Canonical Demo Questions **Goal:** Guarantee wow moments. **Actions:** Create: ``` /demo/canonical-questions.md ``` Include: * 3 required questions from Specification * Expected answer summaries **Acceptance Criteria:** * Answers are reproducible **Estimated Effort:** S --- ## Task 8 — Demo Script & Fallback Assets **Goal:** Be judge-proof. **Actions:** * Write demo walkthrough * Assign **Human Project Owner** as primary demo narrator * Prepare verbal explanations for: * Architecture * Agent roles * Guardrails * Failure handling * Capture screenshots or recordings for fallback **Acceptance Criteria:** * Demo can proceed without live backend * Human clearly explains system intent and constraints **Estimated Effort:** S --- ## Task 9 — Deployment **Goal:** Public access. **Actions:** * Deploy Docusaurus site * Verify URLs **Acceptance Criteria:** * Publicly accessible textbook **Estimated Effort:** S --- ## Task 10 — Final Validation **Goal:** Ensure submission readiness. **Checklist:** * Specs locked * Chapters approved * Demo rehearsed * Fallback ready **Estimated Effort:** S --- ## Hackathon Survival Rule If time is limited: 1. Finish **Task 0–3** 2. Ensure **one canonical chatbot answer works** 3. Demo architecture + intent confidently --- ## Task Timeboxing & Abandonment Rule * Any task may be **abandoned or deferred** if it: * Risks demo stability * Introduces unreviewed content * Compromises safety or correctness * This does **not** count as failure **Primary success metric:** A credible, spec-aligned end-to-end demo --- **Tasks Status:** Ready for execution 🚀 --- **Version:** v1.3 (Hackathon Edition) **Change Summary:** * Agent prompt approval evidence clarified (via commit history) * Survival-mode RAG success definition made explicit * Canonical demo expectations hierarchy documented

## Response snapshot

I have generated the `tasks.md` file.

*   **Tasks File:** `specs/001-robotics-textbook-spec/tasks.md` has been generated.
*   **Total Tasks:** 21
*   **Tasks per User Story:**
    *   User Story 1: 7 tasks
    *   User Story 2: 5 tasks
*   **Parallel Opportunities:** Identified for agent prompt creation, chapter generation, and review.
*   **MVP Scope:** User Story 1 (Browse Textbook Content), which involves setting up the Docusaurus site, generating at least one chapter, and deploying it.

The project is ready for implementation.

## Outcome

- ✅ Impact: High. Created a detailed, actionable task list for developers.
- 🧪 Tests: None.
- 📁 Files: 1 created.
- 🔁 Next prompts: /sp.implement or start working on the tasks.
- 🧠 Reflection: The hybrid approach of using the user's provided task list as a guide while enforcing the strict template format was successful. This allowed me to respect the user's intent while adhering to the project's standards.

## Evaluation notes (flywheel)

- Failure modes observed: None during this command execution.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
