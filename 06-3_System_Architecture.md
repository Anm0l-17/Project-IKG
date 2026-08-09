# 06_System_Architecture.md

## Part 3 — Internal Modular Architecture

Version: 1.0

Status: Draft

Priority: CRITICAL

> **Architecture baseline:** This document must be read together with [23_Architecture_and_Ontology_Decisions.md](23_Architecture_and_Ontology_Decisions.md), which is the approved source of truth for the Domain → Topic → Story → Event ontology, evidence rules, lifecycle dimensions, relationship validation, V1 sources, and background processing. Where older text conflicts, the architecture baseline takes precedence.

---

# Purpose

This document defines the internal architecture of the India Knowledge Graph (IKG) application.

IKG follows a **Modular Monolith** architecture.

Modules are isolated by responsibility but execute within the same deployable application.

Communication between modules occurs through domain events and well-defined interfaces rather than direct database access.

The objective is to maximise maintainability while avoiding the operational complexity of microservices during the early stages of the project.

---

# Why a Modular Monolith?

The platform has one primary business domain:

**Event Intelligence**

The modules are tightly related and frequently exchange information.

Keeping them within a single application provides:

- Simpler development
- Easier debugging
- Shared transactions
- Lower infrastructure costs
- Faster feature delivery
- Easier local development
- Future migration path to microservices

The architecture is designed so that any module can later be extracted into an independent service if required.

---

# Module Dependency Rules

Every module must follow these principles:

1. Modules communicate through public interfaces or domain events.
2. Modules never access another module's database layer directly.
3. Modules share the Domain Model but not implementation details.
4. Circular dependencies are prohibited.
5. Business logic never lives in controllers or UI components.

---

# Module Overview

```
                        API Layer
                            │
                            ▼
                 Application Layer
                            │
    ┌───────────────────────────────────────┐
    │           Domain Layer                │
    ├───────────────────────────────────────┤
    │ Discovery Module                      │
    │ Event Intelligence Module             │
    │ Verification Module                   │
    │ Timeline Module                       │
    │ Knowledge Module                      │
    │ Search Module                         │
    │ Recommendation Module                 │
    │ Analytics Module                      │
    └───────────────────────────────────────┘
                            │
                     Repository Layer
                            │
          PostgreSQL | Neo4j | Redis | Qdrant
```

---

# Shared Domain Layer

Every module depends on the same core domain objects:

- Event
- Article
- Source
- Entity
- Relationship
- Timeline
- Verification
- Evidence

No module may redefine these objects.

---

# Discovery Module

## Responsibility

Acquire information from external sources.

### Inputs

- RSS feeds
- Future APIs
- Future government portals

### Outputs

- Raw Article
- EventCandidateCreated event

### Owns

- Feed configuration
- Source scheduling
- Fetch history
- Deduplication of raw articles

### Does Not Own

- Verification
- AI processing
- Graph generation

---

# Event Intelligence Module

## Responsibility

Transform raw information into structured knowledge.

### Pipeline

- Text normalisation
- Entity extraction
- Categorisation
- Embedding generation
- Candidate matching
- LLM summarisation

### Outputs

- EntitiesExtracted
- EventMatched
- SummaryGenerated

---

# Verification Module

## Responsibility

Implement the majority voting model.

### Owns

- Vote records
- Pending queue
- Re-verification scheduler
- Confidence calculation

### Outputs

- EventVerified
- EventRejected
- VerificationExpired

---

# Timeline Module

## Responsibility

Maintain chronological evolution of Events.

### Owns

- Timeline entries
- Follow-up ordering
- Duplicate prevention
- Event chronology

### Outputs

- TimelineUpdated

---

# Knowledge Module

## Responsibility

Maintain the knowledge graph.

### Owns

- Graph nodes
- Graph edges
- Relationship inference
- Cluster updates

### Outputs

- KnowledgeGraphUpdated

---

# Search Module

## Responsibility

Provide unified retrieval.

### Supports

- Keyword search
- Semantic search
- Graph-aware search
- Timeline search

---

# Recommendation Module

## Responsibility

Surface relevant knowledge.

### Generates

- Related events
- Similar policies
- Connected entities
- Suggested reading paths

---

# Analytics Module

## Responsibility

Measure platform health.

### Tracks

- Pipeline latency
- Verification rate
- Match precision
- Graph density
- Event freshness
- Knowledge Score

---

# Domain Events

Modules communicate using events.

Examples:

- ArticleDiscovered
- ArticleNormalised
- EventCandidateCreated
- EntitiesExtracted
- EventMatched
- VerificationCompleted
- TimelineUpdated
- KnowledgeGraphUpdated
- SearchIndexUpdated

Events are immutable and stored in the audit log.

---

# Architectural Constraints

- One module owns one responsibility.
- One database transaction should not span unrelated modules.
- Shared utilities must remain infrastructure-only.
- Modules must be independently testable.
- Module boundaries are enforced by code reviews and package structure.

---

# Migration Strategy

If future scale demands it, modules can be extracted into microservices in the following order:

1. Discovery Module
2. Search Module
3. Analytics Module
4. Recommendation Module
5. Event Intelligence Module
6. Verification Module
7. Knowledge Module

The extraction order prioritises modules with the fewest dependencies.

---

# Closing Statement

The Modular Monolith architecture provides a balance between engineering discipline and delivery speed.

It allows IKG to evolve rapidly while maintaining clear boundaries, ensuring that future growth can be accommodated without sacrificing maintainability or introducing unnecessary operational complexity.

The modular monolith must include explicit interfaces for taxonomy, Stories, Claims, Evidence, ontology validation, and relationship history. Celery tasks handle asynchronous work; the graph module alone may project validated relationships.
