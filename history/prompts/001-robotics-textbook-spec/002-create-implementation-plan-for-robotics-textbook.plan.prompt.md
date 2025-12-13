---
id: 002
title: Create Implementation Plan for Robotics Textbook
stage: plan
date: 2025-12-13
surface: agent
model: gemini-1.5-pro
feature: 001-robotics-textbook-spec
branch: 001-robotics-textbook-spec
user: user
command: /sp.plan
labels: [plan, architecture, robotics]
links:
  spec: specs/001-robotics-textbook-spec/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-robotics-textbook-spec/plan.md
  - specs/001-robotics-textbook-spec/research.md
  - specs/001-robotics-textbook-spec/data-model.md
  - specs/001-robotics-textbook-spec/contracts/openapi.yaml
tests:
  (none)
---

## Prompt

/sp.plan 
# Plan — AI-Native Physical AI & Humanoid Robotics Textbook

**Aligned with Specification v1.4 (Hackathon Edition)**
**Status:** v1.4 — Locked (Hackathon)

---

## 1. Purpose of This Plan

This plan translates the **Specification** into a **concrete system architecture and execution strategy**.

It defines:

* System components and responsibilities
* Data and control flow
* Agent execution and governance model
* RAG pipeline structure
* Deployment and demo strategy

This plan **does not redefine scope**.
It exists only to **faithfully implement the Specification**.

---

## 2. High-Level System Architecture

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

## 3. Agent Execution Model (Hackathon-Safe)

### 3.1 Agent Runtime Environment

* **Content Agent** and **Reviewer / Verifier Agent** are executed via:

  * CLI-driven AI sessions (e.g., Gemini CLI)
  * Explicit, version-controlled prompt templates
* Agent execution is:

  * Deterministic
  * Human-invoked
  * Spec-governed
* There is **no autonomous or background execution** during the hackathon.

📌 **Rationale:**
Demonstrates *agentic governance*, not automation theater.

---

### 3.2 Agent Prompt Templates (First-Class Artifacts)

* Agent prompt templates are **first-class, version-controlled artifacts**
* Stored under:

```text
/agents/
  content-agent.md
  reviewer-agent.md
```

* Prompts are:

  * Human-authored
  * Spec-governed
  * Executed manually via CLI

**Authority chain:**

Constitution → Specification → Plan → Tasks → Agent Prompts

Prompts **execute behavior**; they do not define scope.

---

## 4. Content Creation Workflow (Agentic)

### 4.1 Chapter Generation Flow

For each chapter:

1. **Inputs**

   * Constitution
   * Specification
   * Chapter learning objectives

2. **Content Agent**

   * Generates:

     * Chapter text
     * Mermaid diagrams
     * Section structure
   * Enforces:

     * Word limits
     * Diagram limits
     * Safety constraints

3. **Reviewer / Verifier Agent**

   * Validates:

     * Technical correctness
     * Spec compliance
     * Conceptual consistency
   * Produces:

     * Pass / Fail decision
     * Internal review notes

4. **Human-in-the-Loop**

   * Required for:

     * Chapter 1
     * New core concepts
     * Final pre-deployment snapshot

5. **Publish Gate**

   * Only **Reviewer-approved** content is published

---

## 5. Textbook Rendering (Frontend)

### Platform Choice

**Docusaurus**

* Markdown-native
* Versionable
* Judge-friendly
* Static and reliable

### Directory Structure

```
/docs
  /chapter-1-foundations.md
  /chapter-2-ros2.md
  /chapter-3-simulation.md
  /chapter-4-vla.md
```

Each chapter file:

* Follows mandatory chapter structure
* Contains Mermaid diagrams
* Includes Further Reading links
* Is indexed for RAG

---

## 6. RAG Chatbot Architecture

### 6.1 Indexing Pipeline

1. Parse chapter Markdown
2. Chunk by **subsection**
3. Enforce:

   * 300–500 token chunks
4. Attach metadata:

   * Chapter
   * Section
   * Concept tags

---

### 6.2 Retrieval Mechanism

* Vector-based similarity search
* Top-k retrieval
* Metadata filtering (chapter + section)
* Vector store implementation is **intentionally abstracted**

---

### 6.3 Confidence Threshold Ownership

* Confidence thresholds are **heuristic-based and fixed for the hackathon**

* Determined by:

  * Retrieval score quality
  * Citation completeness
  * Chunk agreement

* Thresholds:

  * Defined once before demo
  * Not auto-tuned at runtime

* Final authority: **Human system designer**

---

### 6.4 Guardrails

* Out-of-scope → refusal + explanation
* Low-confidence → flagged response
* Unsafe queries → immediate refusal + redirect

---

## 7. RAG Backend Execution Mode

* Implemented as a **single-process, lightweight backend**
* Can run:

  * Locally
  * Or via minimal API
* Priorities:

  * Deterministic behavior
  * Fast startup
  * Demo stability
* No distributed infrastructure required

---

## 8. Diagram Rendering Strategy

### Primary Mode

* Mermaid diagrams rendered directly in Docusaurus

### Fallback Mode

If a diagram fails to render:

1. Use surrounding explanatory text
2. Explain diagram verbally during demo
3. Optionally show a static screenshot

📌 **Diagrams are supporting artifacts, not single points of failure.**

---

## 9. Demo Strategy (Hackathon)

### Canonical Demo Questions Authority

* Canonical demo questions are defined in the **Specification**
* Mirrored for convenience in:

```text
/demo/
  canonical-questions.md
```

* Questions are:

  * Frozen during the hackathon
  * Pre-validated for correctness
  * Used in live and fallback demos

---

### Primary Demo Flow

1. Open public textbook site
2. Navigate between chapters
3. Highlight diagrams and explanations
4. Ask canonical chatbot questions
5. Emphasize:

   * Citations
   * Refusals
   * Spec-constrained answers

---

### Fallback Demo Flow (Authority & Trigger)

Fallback demo mode is triggered **only by the Human Project Owner** when:

* Network or hosting instability occurs
* RAG backend stalls or fails
* Repeated low-confidence responses appear
* Any safety or trust risk is detected

Fallback assets include:

* Pre-recorded chatbot answers
* Screenshots of canonical responses
* Walkthrough of Constitution, Specification, and Plan
* Verbal architecture explanation

📌 **Judges evaluate architecture and intent, not uptime.**

---

## 10. Human-in-the-Loop Evidence

Human review is demonstrated through **observable artifacts**:

* Reviewer checklists per chapter
* “Reviewed & Approved” notes in:

  * Commit messages
  * Chapter metadata
* Verbal explanation during demo

---

## 11. Deployment Plan

* Static site hosting:

  * GitHub Pages / Vercel / Netlify
* RAG backend:

  * Local or lightweight API
* No authentication
* No paid infrastructure required

---

## 12. Non-Goals (Reconfirmed)

This plan explicitly excludes:

* Robot hardware control
* ROS execution
* Simulation runtime
* Real-time systems
* Production scalability

---

## 13. Validation Checklist (Pre-Demo)

* [ ] Minimum submission threshold satisfied (see Section 14)
* [ ] Chapter 1 complete and approved
* [ ] Remaining chapters approved or excluded
* [ ] Diagrams render or fallback ready
* [ ] Chatbot cites chapters + sections
* [ ] Unsafe queries refused
* [ ] Canonical demo questions answered flawlessly

---

## 14. Minimum Hackathon Submission Threshold

If time-constrained, the **minimum acceptable submission** consists of:

* Constitution.md (locked)
* Specification.md (locked)
* This Plan.md (locked)
* **At least one fully approved chapter (Chapter 1)**
* Chatbot answering **at least one canonical question** (live or recorded)

Anything beyond this baseline improves score but is **not required for validity**.

---

## 15. Hackathon Execution Sequence (Authoritative)

The authoritative execution order during the hackathon is:

1. Lock Constitution and Specification
2. Generate chapter content via Content Agent
3. Review content via Reviewer Agent
4. Human approval gate
5. Index approved content for RAG
6. Deploy static site
7. Run demo (live or fallback)

Steps must be executed **in order**. Interleaving is discouraged.

---

## 16. Post-Submission Repository Handling

* At submission time, the repository is treated as **frozen**
* No changes are made unless explicitly requested by judges
* Any post-submission edits must be:

  * Clearly disclosed
  * Versioned separately

This ensures evaluation fairness and reproducibility.

---

## 17. Plan Status

**Locked — v1.4 (Hackathon Edition)**

This plan is now sufficient to generate:

* `tasks.md`
* Agent prompt templates
* Judge demo script
* Docusaurus structure mapping

---
## Response snapshot

I have created the implementation plan and associated design artifacts.

- **Branch:** `001-robotics-textbook-spec`
- **Implementation Plan:** `specs/001-robotics-textbook-spec/plan.md`
- **Generated Artifacts:**
    - `specs/001-robotics-textbook-spec/research.md`
    - `specs/001-robotics-textbook-spec/data-model.md`
    - `specs/001-robotics-textbook-spec/contracts/openapi.yaml`
- **Agent Context:** The agent context has been updated.

The project is now ready for the task generation phase (`/sp.tasks`).

## Outcome

- ✅ Impact: High. Defined the technical architecture and created key design artifacts.
- 🧪 Tests: None.
- 📁 Files: 4 created/modified.
- 🔁 Next prompts: /sp.tasks
- 🧠 Reflection: The process of injecting the `Technical Context` and `Constitution Check` into the user-provided plan worked well. The phased approach (Phase 0, Phase 1) is effective for structured design.

## Evaluation notes (flywheel)

- Failure modes observed: None during this command execution.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
