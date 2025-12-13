# Canonical Demo Questions

**Purpose**: These are the pre-validated questions used during hackathon demos to demonstrate the RAG chatbot's capabilities.

**Status**: Frozen for hackathon demo

---

## Positive Test Questions (Expected: Successful Answers)

### Q1: Foundations of Physical AI

**Question**: "What is the perception-action loop?"

**Expected Answer Coverage**:
- Definition of the continuous cycle
- Components: sensors, perception, cognition, action selection, actuators
- Role in autonomous systems
- Citation to Chapter 1

---

### Q2: ROS 2 Architecture

**Question**: "How do ROS 2 nodes communicate with each other?"

**Expected Answer Coverage**:
- Publish-subscribe pattern via topics
- Decentralized architecture (no master)
- DDS middleware
- Citation to Chapter 2

---

### Q3: Simulation & Digital Twins

**Question**: "What is domain randomization and why is it used?"

**Expected Answer Coverage**:
- Definition: training on varied simulation parameters
- Purpose: bridging the reality gap
- Examples of randomized parameters
- Citation to Chapter 3

---

### Q4: VLA Systems

**Question**: "What are Vision-Language-Action systems?"

**Expected Answer Coverage**:
- Integration of vision, language, and action
- Role of foundation models
- Purpose: robots following natural language instructions
- Citation to Chapter 4

---

### Q5: Cross-Chapter Concept

**Question**: "What is embodied intelligence?"

**Expected Answer Coverage**:
- Intelligence emerges from physical interaction
- Body shapes cognition
- Contrast with disembodied AI
- Citation to Chapter 1

---

## Boundary Test Questions (Expected: Appropriate Handling)

### B1: Topic Partially Covered

**Question**: "What specific LiDAR models are best for robotics?"

**Expected Response**: Low confidence answer acknowledging LiDAR is discussed conceptually but specific model recommendations are not in the textbook.

---

### B2: Related but Not Covered

**Question**: "How do I program a drone using Python?"

**Expected Response**: Out-of-scope response directing user to covered topics.

---

## Citation Verification Questions

These questions test that the chatbot correctly cites sources.

### C1: Single Chapter Citation

**Question**: "What is a digital twin?"

**Expected Citation**: Chapter 3 — Simulation, Digital Twins & NVIDIA Isaac

---

### C2: Specific Section Citation

**Question**: "What is the Quality of Service in ROS 2?"

**Expected Citation**: Chapter 2, Section on Quality of Service (QoS)

---

## Demo Flow Recommendation

1. Start with **Q1** (Foundations) — shows basic functionality
2. Ask **Q3** (Simulation) — shows domain-specific knowledge
3. Ask **Q4** (VLA) — demonstrates advanced topic coverage
4. Show **B2** — demonstrates appropriate refusal
5. End with **C1** — highlights citation capability

---

## Notes for Judges

- All answers are constrained to textbook content
- Citations point to specific chapters and sections
- Out-of-scope questions receive explicit refusals
- No hallucination — answers only from indexed content
