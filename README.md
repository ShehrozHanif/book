# AI-Native Physical AI & Humanoid Robotics Textbook

This project aims to create an AI-native, agent-powered textbook and learning system for Physical AI and Humanoid Robotics, redefining how advanced technical education is authored, delivered, and consumed.

This repository contains the full source and specifications for the textbook, which is built using a spec-driven, agentic workflow.

## High-Level System Architecture

The system consists of five primary layers:

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
