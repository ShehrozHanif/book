# Demo Script — AI-Native Physical AI & Humanoid Robotics Textbook

**Purpose**: Authoritative demo flow for hackathon judging

**Duration**: 5-7 minutes

---

## Pre-Demo Checklist

- [ ] Textbook site is accessible (deployed or local)
- [ ] RAG backend is running
- [ ] `canonical-questions.md` is open for reference
- [ ] Browser is in presentation mode (zoomed appropriately)

---

## Demo Flow

### Part 1: Introduction (30 seconds)

**Say**:
> "This is an AI-native textbook for Physical AI and Humanoid Robotics. Unlike traditional static textbooks, this is a living, intelligent system where AI agents generate content from specifications, and users can interact with the material through a RAG-powered chatbot."

---

### Part 2: Architecture Overview (1 minute)

**Show**: README.md or architecture diagram

**Say**:
> "The system has five layers:
> 1. **Spec files** serve as the source of truth
> 2. **AI agents** (Content Agent and Reviewer Agent) generate and validate content
> 3. **Knowledge Index** stores chunked, tagged content
> 4. **RAG Orchestration** retrieves relevant chunks and applies guardrails
> 5. **Docusaurus Frontend** renders the textbook with an embedded chatbot"

---

### Part 3: Textbook Navigation (1 minute)

**Action**: Navigate to the deployed textbook site

**Show**:
1. Landing page
2. Sidebar with chapter list
3. Chapter 1: Foundations of Physical AI
4. Scroll to show a Mermaid diagram

**Say**:
> "The textbook contains four deep chapters on Physical AI, ROS 2, Simulation, and VLA systems. Each chapter follows a consistent structure with learning objectives, core content with diagrams, and an 'Experimental/Evolving' section for cutting-edge topics."

---

### Part 4: Chatbot Demo — Successful Query (1.5 minutes)

**Action**: Open chatbot interface

**Ask**: "What is the perception-action loop?"

**Wait for response**

**Point out**:
1. The answer content (accurate, from textbook)
2. The citation (Chapter 1, specific section)
3. Confidence level (if displayed)

**Say**:
> "The chatbot retrieves relevant chunks from the indexed textbook content and assembles an answer with proper citations. It only knows what's in the textbook — no hallucination."

---

### Part 5: Chatbot Demo — Domain Knowledge (1 minute)

**Ask**: "What is domain randomization?"

**Point out**:
1. Answer explains sim-to-real technique
2. Citation points to Chapter 3

**Say**:
> "This demonstrates knowledge of simulation concepts — a key topic for Physical AI development."

---

### Part 6: Chatbot Demo — Refusal Behavior (1 minute)

**Ask**: "What is the price of a Boston Dynamics robot?"

**Point out**:
1. Chatbot refuses to answer
2. Explains the topic is out of scope
3. Redirects to covered topics

**Say**:
> "This is intentional. The chatbot has guardrails — it only answers from the textbook content. Questions outside scope get explicit refusals, not fabricated answers."

---

### Part 7: Spec-Driven Architecture (1 minute)

**Show**: Open `constitution.md` or `spec.md` briefly

**Say**:
> "What makes this AI-native is the spec-driven workflow. The Constitution defines project principles. The Specification defines requirements. AI agents execute these specifications to generate content. This ensures consistency, auditability, and reusability."

**Show**: Agent prompt templates (`agents/content-agent.md`)

**Say**:
> "Agents are governed by explicit prompts that reference the specs. They don't operate autonomously — they execute defined behavior."

---

### Part 8: Closing (30 seconds)

**Say**:
> "This project demonstrates a new paradigm for technical education:
> - Specifications as the source of truth
> - AI agents as governed collaborators
> - RAG for constrained, citation-backed answers
> - A reusable blueprint for AI-native learning systems
>
> Thank you. Questions?"

---

## Fallback Procedures

### If the site is down:
1. Show screenshots from `/assets/screenshots/`
2. Walk through the architecture diagram
3. Explain the spec-driven workflow

### If the chatbot fails:
1. Show the RAG code structure
2. Explain how retrieval and response generation work
3. Show pre-recorded demo responses

### If time is short:
1. Skip Part 5 (domain knowledge demo)
2. Combine Parts 4 and 6 into one chatbot demo
3. Keep architecture explanation brief

---

## Key Messages for Judges

1. **Specifications control AI behavior** — not ad-hoc prompting
2. **Agents are governed, not autonomous** — defined roles and boundaries
3. **RAG is constrained** — only textbook knowledge, explicit refusals
4. **The architecture is reusable** — template for other domains
5. **This is a paradigm demonstration** — not just a chatbot demo
