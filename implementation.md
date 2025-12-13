# Implementation — AI-Native Physical AI & Humanoid Robotics Textbook

**Aligned with Constitution v1.0 · Specification v1.4 · Plan v1.4 · Tasks v1.3**

**Status:** v1.3 — Locked (Hackathon)

---

## 1. Purpose of This Document

This document defines the **concrete implementation details** for the hackathon MVP.

It answers:

* How each task is executed in practice
* How agents are run via CLI (Gemini CLI)
* How RAG is wired in a minimal, safe way
* How the demo is executed reliably

This file:

* Introduces **no new scope**
* Is **replaceable post-hackathon**
* Exists purely to help humans and judges understand execution

---

## 2. Repository Structure (Final)

```text
/
├─ constitution.md
├─ specification.md
├─ plan.md
├─ tasks.md
├─ implementation.md
├─ README.md
├─ /agents
│   ├─ content-agent.md
│   └─ reviewer-agent.md
├─ /docs
│   ├─ chapter-1-foundations.md
│   ├─ chapter-2-ros2.md
│   ├─ chapter-3-simulation.md
│   └─ chapter-4-vla.md
├─ /rag
│   ├─ indexer.py
│   ├─ retriever.py
│   └─ responder.py
├─ /demo
│   ├─ canonical-questions.md
│   ├─ demo-script.md
│   └─ negative-tests.md
└─ /assets
    └─ screenshots/
```

---

## 3. Agent Prompt Execution (Gemini CLI)

### 3.1 Content Agent Execution

**Purpose:** Generate chapter content strictly from specs.

**Invocation Pattern (Example):**

```bash
gemini run agents/content-agent.md \
  --input constitution.md specification.md plan.md \
  --chapter "Chapter 1 — Foundations of Physical AI"
```

**Expected Output:**

* Markdown chapter content
* Mermaid diagrams
* Structured sections

**Post-step:**

* Save output into `/docs/chapter-x-*.md`
* Do **not** publish yet

---


### 3.2 Reviewer Agent Execution

**Purpose:** Validate correctness and spec compliance.

**Invocation Pattern:**

```bash
gemini run agents/reviewer-agent.md \
  --input docs/chapter-1-foundations.md specification.md
```

**Expected Output:**

* PASS or FAIL
* Short justification

**Rules:**

* FAIL → fix or exclude chapter
* PASS → proceed to approval

---


### 3.3 Human Approval Marker

Once approved, add **one visible artifact** inside the chapter file.

**Canonical source of truth:** a **YAML frontmatter approval block** at the top of the chapter file.

* Inline approval blocks are **not allowed**
* Commit messages are **supporting evidence only**
* If a discrepancy exists, the in-file YAML frontmatter **takes precedence**

```markdown


Chapters **without** this frontmatter block are treated as **not approved** and are excluded from RAG indexing and demo navigation.

---
approval:
  reviewer: PASS
  approved_by: Human Project Owner
  date: 2025-XX-XX
---
```

---

## 4. Docusaurus Implementation

### 4.1 Setup

```bash
npx create-docusaurus@latest textbook classic
cd textbook
npm start
```

### 4.2 Sidebar Configuration

Only **approved chapters** are listed in `sidebars.js`.

Excluded chapters:

* Are removed from sidebar
* Are not indexed for RAG

---

## 5. RAG Implementation (Minimal & Safe)

### 5.1 Indexing (`rag/indexer.py`)

Responsibilities:

* Load **only approved** chapter markdown files
* Approval is verified via in-file approval marker
* Split by headings
* Chunk into 300–500 tokens
* Attach metadata

Indexing is **manually triggered** by the **Human Project Owner** and is never automatic.

Manual trigger example:

```bash
python rag/indexer.py
```

```python
{
  "text": "...",
  "chapter": "Chapter 1",
  "section": "Embodied Intelligence",
  "tags": ["physical-ai", "embodiment"]
}
```

---


### 5.2 Retrieval (`rag/retriever.py`)

Responsibilities:

* Vector or heuristic similarity search
* Return top-k chunks
* Filter by metadata

**Note:**
Tooling choice is intentionally abstracted.

---


### 5.3 Response Assembly (`rag/responder.py`)

Responsibilities:

* Check scope safety
* Verify confidence threshold
* Generate answer
* Inject citations

**Confidence Threshold:**

```python
CONFIDENCE_THRESHOLD = 0.72  # Fixed for hackathon demo
```

Example response format:

```text
Answer:
... 

Source:
- Chapter 2 — ROS 2 & Robotics System Architecture
  Section: Distributed Systems Model
```

---


## 6. Guardrails & Failure Handling

### Out-of-Scope

```text
This topic is not covered in the current version of the textbook.
```

### Low Confidence

```text
⚠️ Low confidence: available material does not fully support this answer.
```

### Unsafe Query

* Immediate refusal
* Redirect to conceptual explanation

---


## 7. Demo Execution

### 7.1 Demo Script Authority

`/demo/demo-script.md` is the **authoritative demo flow** for hackathon judging.

* Live demo follows this script
* Fallback demo mirrors the same structure
* Deviations are allowed only for:

  * Time constraints
  * Technical failure

---


### 7.2 Live Demo Flow

1. Open deployed Docusaurus site
2. Navigate Chapter 1
3. Show diagrams
4. Ask canonical questions
5. Highlight citations + refusals

---


### 7.3 Negative RAG Tests

Refusal behavior is demonstrated via explicit negative tests:

```text
/demo/negative-tests.md
```

This file contains:

* Out-of-scope questions
* Unsafe queries
* Expected refusal responses

Judges are shown this file during demo walkthrough.

---


### 7.4 Fallback Demo (Authoritative)

If anything fails:

* Open `/demo/demo-script.md`
* Show screenshots
* Walk judges through:

  * Constitution
  * Specification
  * Plan
  * Tasks

---


## 8. Task → Implementation Traceability

This section provides **lightweight traceability** between Tasks and implementation artifacts.

* **Task 3** → `/docs/chapter-1-foundations.md` + YAML approval frontmatter
* **Task 6** → `/rag/indexer.py`, `/rag/retriever.py`, `/rag/responder.py`
* **Task 8** → `/demo/demo-script.md`, `/assets/screenshots/`

This mapping exists for **judge clarity only**.

---


## 9. What Judges Should Notice

* Specs control AI behavior
* Agents are governed, not autonomous
* RAG is constrained and honest
* Failures are explicit, not hidden
* Architecture is reusable beyond this project

---


## 10. Model Training & Fine-Tuning Statement

* **No model training or fine-tuning occurs** in this project
* All behavior is governed by:

  * Prompt constraints
  * Retrieval over textbook content

This system demonstrates **spec-driven orchestration**, not model modification.

---


## 11. Non-Goals (Reconfirmed)

* No robotics execution
* No hardware control
* No real-time systems
* No production scaling

---


## 12. Implementation Mutability & Status

`implementation.md` is **mutable during the hackathon** for:

* Clarity improvements
* Execution detail fixes

Changes must **not**:

* Redefine scope
* Contradict Constitution, Specification, or Plan

Authoritative constraints always live in higher-order documents.

---


## 13. Implementation Status

**Complete — Hackathon MVP Ready**

This file closes the SpecKit execution loop.

---
