# 11_AI_Architecture.md

# India Knowledge Graph (IKG)

## Artificial Intelligence Architecture

Version: 1.0

Status: Draft

Priority: CRITICAL

Owner: AI Platform Team

---

# Purpose

This document defines the Artificial Intelligence architecture of India Knowledge Graph.

AI is responsible for transforming raw information into structured knowledge.

The architecture prioritises explainability, reproducibility, efficiency and modularity.

AI never replaces business rules.

AI supports them.

---

# AI Philosophy

IKG does not use one large AI model.

Instead,

multiple specialised models cooperate.

Each model performs one task.

The outputs are combined into verified knowledge.

---

# Intelligence Stack

```

                LLM Layer

────────────────────────────────

        Cross Encoder Layer

────────────────────────────────

       Embedding Layer

────────────────────────────────

 Entity Extraction Layer

────────────────────────────────

 Metadata Layer

────────────────────────────────

 Raw Articles

```

Every higher layer depends on the quality of the lower layers.

---

# Design Principles

## 1. Modular Models

Every model performs exactly one responsibility.

No monolithic AI.

---

## 2. Explainability

Every AI decision stores

- model
- version
- confidence
- timestamp
- reasoning

---

## 3. Human Override

Every AI decision can be reviewed.

Nothing is irreversible.

---

## 4. Deterministic First

Use rules where possible.

Use AI only when necessary.

---

=================================================

MODEL 1

Metadata Extraction

=================================================

Purpose

Extract

Title

Date

Author

URL

Publication

Language

Category Hint

Complexity

Very Low

Preferred

Rules

Regex

BeautifulSoup

---

=================================================

MODEL 2

Named Entity Recognition

=================================================

Purpose

Extract

Countries

People

Organisations

Policies

Bills

Acts

Committees

Schemes

Companies

Currencies

Military branches

Outputs

Entity Objects

Confidence

Mention Frequency

Preferred Models

GLiNER

spaCy

Future

Fine-tuned model

---

=================================================

MODEL 3

Category Classification

=================================================

Purpose

Predict

Current Affairs

Parliament

Economics

Trade

Defence

Geopolitics

Outputs

Category

Sub-category

Confidence

Preferred

Small Transformer

---

=================================================

MODEL 4

Embedding Generator

=================================================

Purpose

Convert Events into vectors.

Requirements

Fast

Deterministic

Low latency

Candidate Models

BGE

E5

Instructor

Outputs

Embedding Vector

Model Version

Timestamp

Embedding ID

Stored In

Semantic Store

(Qdrant)

---

=================================================

MODEL 5

Candidate Retrieval

=================================================

Purpose

Retrieve Top-K similar Events.

Method

Approximate Nearest Neighbour Search

Input

Embedding

Output

Top 20 Candidate Events

No LLM required.

---

=================================================

MODEL 6

Cross Encoder

=================================================

Purpose

Deep semantic comparison.

Input

Candidate Event

Current Event

Output

Similarity Score

Explanation

Only Top-K candidates are processed.

---

=================================================

MODEL 7

LLM Reasoning

=================================================

Purpose

Determine

SAME_EVENT

FOLLOW_UP

RELATED

NEW_EVENT

DIFFERENT

Input

Candidate

Entities

Timeline

Cross Encoder Score

Output

Decision

Confidence

Natural language reasoning

The LLM never searches.

It reasons over prepared evidence.

---

=================================================

MODEL 8

Summarisation

=================================================

Purpose

Generate

Short Summary

Detailed Summary

Timeline Summary

Citizen Explanation

Different summary styles may coexist.

---

=================================================

MODEL 9

Relationship Discovery

=================================================

Purpose

Suggest graph edges.

Example

Policy

↓

Affects

↓

Economy

Confidence threshold required before insertion.

---

=================================================

MODEL 10

Recommendation Ranking

=================================================

Purpose

Rank

Related Events

Learning Paths

Entity Recommendations

Uses

Hybrid ranking

Graph signals

Embeddings

Knowledge Score

---

# AI Orchestration

Every AI stage produces structured outputs.

```
Article

↓

NER

↓

Classification

↓

Embedding

↓

Retrieval

↓

Cross Encoder

↓

LLM

↓

Verification

↓

Knowledge
```

No stage skips another.

---

# Prompt Design

Prompts must

- define task
- define constraints
- request structured output
- prohibit hallucination
- request reasoning

Output format

JSON

Never free text.

---

# Model Registry

Every model is registered.

Stores

Name

Version

Provider

Task

Evaluation

Deployment Date

Rollback Version

Performance Metrics

---

# Evaluation

Every model is continuously evaluated.

Metrics

Precision

Recall

F1 Score

Latency

Cost

Confidence Calibration

Hallucination Rate (LLMs)

Regression tests are mandatory before upgrades.

---

# Observability

Track

Inference time

Token usage

Embedding latency

Retrieval accuracy

Match accuracy

Decision confidence

Model failures

---

# Safety

LLMs cannot:

- invent sources
- fabricate relationships
- bypass verification
- create Events without evidence

All generated content must be traceable to verified inputs.

---

# Future Enhancements

- Multilingual models (Hindi, Tamil, Bengali, etc.)
- Domain-specific fine-tuning
- On-device inference for lightweight tasks
- Active learning with human feedback
- Automated prompt optimisation
- Self-hosted LLMs for sensitive deployments

---

# Closing Statement

The AI architecture of IKG is designed as a cooperative intelligence system.

Specialised models perform focused tasks.

Deterministic algorithms provide structure.

Large Language Models contribute reasoning rather than authority.

The final product is not AI-generated news, but AI-assisted, evidence-backed knowledge.