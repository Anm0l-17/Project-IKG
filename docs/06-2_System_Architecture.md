# 06_System_Architecture.md

# Part 2 — C4 Context & Container Architecture

Version: 1.0

Status: Draft

Owner: Chief Architect

Priority: CRITICAL

> **Architecture baseline:** This document must be read together with [23_Architecture_and_Ontology_Decisions.md](23_Architecture_and_Ontology_Decisions.md), which is the approved source of truth for the Domain → Topic → Story → Event ontology, evidence rules, lifecycle dimensions, relationship validation, V1 sources, and background processing. Where older text conflicts, the architecture baseline takes precedence.

---

# Purpose

This section defines the overall system structure using the C4 Model.

The C4 Model describes software architecture at four progressively detailed levels:

1. Context
2. Container
3. Component
4. Code

This document covers the first two levels.

---

# Why C4?

Traditional architecture diagrams quickly become unreadable as systems grow.

The C4 Model solves this by presenting the system at multiple abstraction levels.

Each stakeholder sees only the level of detail they require.

Examples:

Product Manager → Context

Backend Engineer → Container

Service Owner → Component

Developer → Code

---

=========================================================

LEVEL 1 — SYSTEM CONTEXT

=========================================================

The India Knowledge Graph (IKG) platform exists within a broader ecosystem of users, trusted information sources, AI services, and infrastructure.

```
                             +------------------------+
                             |        Users           |
                             |------------------------|
                             | UPSC Aspirants         |
                             | Researchers            |
                             | Journalists            |
                             | Professionals          |
                             +-----------+------------+
                                         |
                                         |
                                 Uses Website
                                         |
                                         ▼
                    +----------------------------------------+
                    |     India Knowledge Graph (IKG)        |
                    |----------------------------------------|
                    | Event Intelligence Platform            |
                    | Verification                           |
                    | Timelines                              |
                    | Knowledge Graph                        |
                    +-----------+----------------------------+
                                |
        -------------------------------------------------------------
        |              |               |               |             |
        ▼              ▼               ▼               ▼             ▼
+-------------+ +--------------+ +-------------+ +-------------+ +--------------+
| GKToday RSS | | The Hindu    | | Indian      | | Future Govt | | AI Models    |
|             | |              | | Express     | | Sources     | | (Open Source)|
+-------------+ +--------------+ +-------------+ +-------------+ +--------------+
```

---

# External Actors

## Primary Users

Users interact only with the frontend.

They never directly communicate with AI engines or databases.

---

## Trusted Sources

Version 1

• GKToday

• The Hindu

• Indian Express

Future

• PIB

• RBI

• Parliament

• PRS

• Gazette

These sources provide Articles.

They never create Events.

---

## AI Models

Examples

Embedding Model

Cross Encoder

NER Model

LLM

The AI models provide intelligence.

They do not own business logic.

---

=========================================================

LEVEL 2 — CONTAINER DIAGRAM

=========================================================

The platform consists of multiple independent containers.

```
                        ┌──────────────────────┐
                        │      Frontend        │
                        │ Next.js + React      │
                        └──────────┬───────────┘
                                   │
                          REST / WebSocket
                                   │
                        ┌──────────▼──────────┐
                        │     API Gateway     │
                        └──────────┬──────────┘
                                   │
                 ┌─────────────────┼──────────────────┐
                 │                 │                  │
                 ▼                 ▼                  ▼

      Discovery Engine   Event Intelligence   Verification Engine
                               Engine

                 ▼                 ▼                  ▼

            Timeline Engine   Knowledge Engine   Search Engine

                         ▼            ▼
                    Analytics     Recommendation

                              ▼
                      Repository Layer

            PostgreSQL | Neo4j | Redis | Vector DB
```

---

# Container Responsibilities

---

## Frontend

Technology

Next.js

Responsibilities

• User Interface

• Event View

• Timeline View

• Knowledge Graph

• Search

• Dashboard

Owns

Presentation.

Never owns business logic.

---

## API Gateway

Purpose

Single entry point.

Responsibilities

Authentication

Rate limiting

Validation

Routing

Logging

Response shaping

Future

GraphQL Federation

---

## Discovery Engine

Purpose

Collect information.

Responsibilities

RSS

HTML

Future PDFs

Future APIs

Output

Event Candidates

---

## Event Intelligence Engine

Purpose

Transform information into structured knowledge.

Modules

NER

Classification

Summarisation

Embeddings

Similarity Search

Cross Encoder

Reasoning

Outputs

Entities

Summary

Candidate Matches

---

## Verification Engine

Purpose

Implement

Majority Voting

Pending Queue

Re-verification

Confidence Calculation

Outputs

Verified Events

---

## Timeline Engine

Purpose

Maintain Event history.

Responsibilities

Timeline ordering

Follow-up insertion

Duplicate prevention

Historical state updates

---

## Knowledge Engine

Purpose

Maintain Neo4j.

Responsibilities

Node creation

Relationship creation

Relationship updates

Cluster discovery

Graph maintenance

---

## Search Engine

Purpose

Unified search.

Combines

Keyword Search

Semantic Search

Graph Search

Timeline Search

---

## Recommendation Engine

Purpose

Discover related knowledge.

Examples

Related Events

Similar Policies

Connected Ministries

Previous Developments

Future Follow-ups

---

## Analytics Engine

Purpose

Internal metrics.

Examples

Knowledge Score

Verification Rate

Pending Queue Size

Matching Accuracy

System Health

Latency

No user-facing logic.

---

=========================================================

REPOSITORY LAYER

=========================================================

This layer hides storage complexity.

No engine should communicate directly with a database.

```
Engine

↓

Repository Interface

↓

Database
```

Advantages

Database replacement

Testing

Caching

Versioning

Migration

---

Storage Responsibilities

PostgreSQL

Structured data.

Neo4j

Relationships.

Redis

Caching.

Queues.

Sessions.

Vector Database

Embeddings.

Similarity Search.

Object Storage

Images.

Raw Documents.

Backups.

---

=========================================================

COMMUNICATION MODEL

=========================================================

The architecture follows an Event-Driven approach.

Example

```
Article Collected

↓

Article Normalised

↓

Entities Extracted

↓

Candidate Event Created

↓

Matching Completed

↓

Votes Updated

↓

Verification Completed

↓

Timeline Updated

↓

Knowledge Graph Updated

↓

Search Index Updated

↓

Frontend Cache Invalidated
```

No service should synchronously call five other services.

Instead,

publish events.

Subscribers react independently.

---

=========================================================

SYNCHRONOUS VS ASYNCHRONOUS

=========================================================

Synchronous

✓ User Login

✓ Search

✓ Dashboard

✓ Event Details

Asynchronous

✓ Summarisation

✓ Embeddings

✓ Verification

✓ Matching

✓ Timeline Construction

✓ Recommendation Updates

✓ Graph Maintenance

---

=========================================================

SERVICE OWNERSHIP

=========================================================

Every service owns exactly one responsibility.

| Service | Owns |
|----------|------|
| Discovery Engine | Information ingestion |
| Event Intelligence Engine | AI processing |
| Verification Engine | Trust |
| Timeline Engine | Event evolution |
| Knowledge Engine | Graph |
| Search Engine | Retrieval |
| Recommendation Engine | Discovery |
| Analytics Engine | Metrics |

No ownership overlaps are permitted.

---

=========================================================

SCALABILITY

=========================================================

Every container should be independently scalable.

High CPU

↓

AI Engine

High Memory

↓

Neo4j

High IO

↓

Discovery Engine

High Requests

↓

API Gateway

Independent scaling reduces infrastructure cost.

---

=========================================================

ARCHITECTURAL RULES

=========================================================

Frontend never accesses databases.

AI never updates Neo4j directly.

Verification never modifies articles.

Knowledge Engine never scrapes websites.

Discovery Engine never performs AI reasoning.

Every service communicates through defined interfaces.

---

# Closing Statement

The C4 Context and Container architecture establishes the structural boundaries of India Knowledge Graph.

Every future component, API, worker and deployment unit must fit within these boundaries.

Maintaining strict separation of responsibilities ensures that the platform remains scalable, maintainable and adaptable as new data sources, AI models and product features are introduced.







# One architectural change I strongly recommend


Discovery Engine
        │
        ▼
   Event Bus (Kafka / RabbitMQ / NATS)
        │
 ┌──────┼────────┬─────────┬──────────┐
 ▼      ▼        ▼         ▼          ▼
AI   Verification Timeline Knowledge Search

---

# Approved Container Clarification

The container design is implemented initially as a modular monolith with Celery/Redis workers. The approved resource hierarchy is Domain → Topic → Story → Event. Any future event-bus or microservice extraction must preserve the ontology, evidence rules, and graph-engine ownership defined in the architecture baseline.
