# Tasks: AI-Native Physical AI & Humanoid Robotics Textbook

**Input**: Design documents from `specs/001-robotics-textbook-spec/`
**Prerequisites**: plan.md, spec.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure.

- [x] T001 Initialize Git repository and add spec files (`constitution.md`, `specs/001-robotics-textbook-spec/spec.md`, `specs/001-robotics-textbook-spec/plan.md`).
- [x] T002 [P] Create `README.md` with project intent and architecture overview.
- [x] T003 [P] Create agent prompt templates in `agents/content-agent.md` and `agents/reviewer-agent.md`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

- [x] T004 Initialize Docusaurus site in a `/docusaurus` directory.
- [x] T005 Configure Docusaurus sidebar navigation for 4 chapters in `docusaurus/sidebars.js`.
- [x] T006 Create placeholder chapter files in `docusaurus/docs/` (e.g., `chapter-1.md`, `chapter-2.md`, etc.).

---

## Phase 3: User Story 1 - Browse Textbook Content (Priority: P1) 🎯 MVP

**Goal**: Allow users to read the textbook content on a publicly accessible website.

**Independent Test**: The Docusaurus site can be built and served locally, showing the generated chapter content.

- [x] T007 [US1] Generate content for Chapter 1 using the Content Agent.
- [x] T008 [US1] Review and approve Chapter 1 content using the Reviewer Agent and human-in-the-loop, adding an approval marker to the file.
- [x] T009 [P] [US1] Generate content for Chapter 2.
- [x] T010 [P] [US1] Generate content for Chapter 3.
- [x] T011 [P] [US1] Generate content for Chapter 4.
- [x] T012 [P] [US1] Review and approve Chapters 2-4.
- [x] T013 [US1] Configure deployment to static hosting (GitHub Pages, Vercel, Netlify configs created).

---

## Phase 4: User Story 2 - Get Answers from the Chatbot (Priority: P2)

**Goal**: Enable users to ask questions and get answers from the textbook content.

**Independent Test**: The RAG backend can be tested via its API, sending questions and verifying the correctness and citation of the answers.

- [x] T014 [US2] Implement a Python script (`rag/indexer.py`) to parse approved chapter markdown files and chunk them into 300-500 token segments with metadata.
- [x] T015 [US2] Implement a minimal RAG backend in Python (`rag/retriever.py`, `rag/responder.py`) using keyword-based retrieval.
- [x] T016 [US2] Implement a simple API endpoint (`/ask`) in the RAG backend using FastAPI (`rag/api.py`).
- [x] T017 [US2] Create the list of canonical demo questions in `demo/canonical-questions.md`.
- [x] T018 [US2] Integrate the RAG backend with the Docusaurus frontend to create the chatbot UI (`src/components/ChatBot/`).

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final preparations for the hackathon demo.

- [x] T019 Write a detailed demo script in `demo/demo-script.md`.
- [x] T020 Prepare fallback assets directory (`assets/screenshots/`) for the demo.
- [x] T021 Create pre-demo validation checklist (`demo/pre-demo-checklist.md`).

---

## Dependencies & Execution Order

- **Phase 1 (Setup)** must be completed first.
- **Phase 2 (Foundational)** depends on Phase 1.
- **Phase 3 (User Story 1)** and **Phase 4 (User Story 2)** depend on Phase 2. They can be worked on in parallel, but US1 is the MVP.
- **Phase 5 (Polish)** depends on the completion of all desired features for the demo.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1.  Complete Phase 1 & 2.
2.  Complete tasks T007 and T008 to get Chapter 1 content.
3.  Complete task T013 to deploy the site with one chapter.
4.  **STOP and VALIDATE**: The core textbook is readable online.

### Incremental Delivery
1.  Deliver the MVP.
2.  Add more chapters (T009-T012).
3.  Implement the RAG backend and chatbot UI (Phase 4).
