# Research for AI-Native Textbook

This document details the research findings for unclear items in the initial plan.

## 1. Testing Strategy

*   **Decision**: For the hackathon MVP, the testing strategy will be as follows:
    *   **Frontend (Docusaurus)**: Manual, exploratory testing of the deployed static site to ensure content renders correctly, links are not broken, and the layout is responsive. Automated end-to-end tests are out of scope.
    *   **Backend (Python RAG Pipeline)**: Unit tests for core logic using the `pytest` framework. Key areas to test include content chunking logic and metadata extraction. Integration tests against a live Gemini API are out of scope.
*   **Rationale**: This approach balances quality assurance with the time constraints of a hackathon. It focuses testing efforts on the most critical and complex part of the system (the RAG backend) while relying on manual checks for the simpler static frontend.
*   **Alternatives Considered**:
    *   **Full End-to-End Testing (e.g., with Playwright or Cypress)**: Rejected as overly complex and time-consuming for a static content site in a hackathon context.
    *   **No backend tests**: Rejected as too risky. The RAG pipeline logic is novel and requires validation to ensure correctness.

## 2. RAG Chatbot Performance Goals

*   **Decision**: The RAG chatbot must have a **p95 response time of under 3 seconds**. This means 95% of user queries should receive a complete answer in less than 3 seconds.
*   **Rationale**: Based on industry standards for conversational AI, response times over 3-4 seconds lead to a poor user experience, making the interaction feel slow and disjointed. A 3-second p95 target ensures the chatbot feels responsive.
*   **Alternatives Considered**:
    *   **No performance goal**: Rejected because performance is a key aspect of user experience, and having a target provides a clear benchmark for success.
    *   **Faster goal (e.g., <1 second)**: Rejected as potentially unachievable within the hackathon constraints, especially when relying on external API calls to the Gemini model. The 3-second goal is ambitious but realistic.
