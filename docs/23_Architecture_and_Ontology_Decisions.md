# India Knowledge Graph (IKG)

## Consolidated Architecture & Ontology Decisions

Version: 1.0  
Status: Approved Decision Baseline  
Owner: Product Management Office / Architecture Team  
Priority: CRITICAL

---

# Purpose

This document consolidates the approved domain, ontology, evidence, verification, graph, AI, and infrastructure decisions for India Knowledge Graph (IKG).

It is the source of truth for reconciling the earlier design documents. Existing documents must be updated against this baseline before implementation expands.

No implementation may introduce a conflicting concept, state, relationship, or ownership rule without an Architecture Decision Record and explicit review.

---

# 1. Product and Domain Principle

IKG is an Event Intelligence Platform, not an article aggregation system.

Events are first-class domain objects.

Articles are evidence.

AI proposes interpretations. Evidence supports them. Deterministic rules validate them. The graph engine creates only validated relationships.

The system must never allow an AI model to freely create arbitrary node-to-node connections.

---

# 2. Canonical Ontology

The approved hierarchy is:

```text
DOMAIN
  └── TOPIC
        └── STORY
              └── EVENT
                    ├── CLAIMS
                    ├── CANONICAL ARTICLE
                    └── SUPPORTING EVIDENCE
```

## Domain

Domain is one of the six fixed, user-facing top-level categories:

- Current Affairs
- Parliament
- Economics
- Trade
- Defence
- Geopolitics

Domains are deterministic taxonomy objects, not news claims.

## Topic

Topic is a reusable subject within a Domain.

Example:

```text
Trade → India–UK Trade Relations
```

Topics may contain multiple Stories over time. Topics do not have verification states. Their validity comes from the approved taxonomy. Topics may have `ACTIVE` or `INACTIVE` lifecycle metadata.

## Story

Story is a long-running, bounded narrative within a Topic.

Example:

```text
Trade
  └── India–UK Trade Relations
        └── India–UK FTA 2026
```

A Story may contain many Events and its own chronological Story Timeline. A Story has one lifecycle:

```text
PENDING → VERIFIED → ARCHIVED
```

`REJECTED` is permitted only for explicitly invalid or incorrect groupings and is not a normal progression state.

A Story requires at least two qualifying Events. Each qualifying Event must have independent source evidence; two Events derived from the same underlying source are insufficient.

Stories may remain active indefinitely. Lack of recent news does not automatically archive a Story.

## Event

Event is a real-world occurrence and the first-class domain object.

Examples include a bill being introduced, an agreement being signed, or a policy being implemented.

An Event has exactly one primary Story when grouped, but may remain independent indefinitely. An Event may also have secondary Topic associations and explicitly validated cross-Story relationships.

## Claim

Claim is a secondary, article-specific representation of an assertion extracted from an Article.

Each Claim belongs to exactly one Event. One Article may contain Claims about multiple Events. Claims from different Articles may describe the same Event differently and must remain separately attributable.

## Article

Article is a publication produced by a Source. Articles are evidence and provenance, not the primary graph object.

An Article may support multiple Events when it genuinely reports multiple distinct developments.

Each Event has exactly one canonical Article pointer at a time. A canonical Article change preserves the previous canonical Article as supporting evidence and records immutable history.

## Evidence

Evidence explicitly connects an Article or Claim to an Event or relationship.

Evidence must record its type, source Article, confidence, timestamp, and reasoning or extraction context.

Supporting Articles may provide evidence for:

- the existence or interpretation of an Event;
- a relationship between two Events;
- a Story grouping;
- a Claim.

---

# 3. Independent Event Dimensions

Grouping and verification answer different questions and must remain separate fields.

## Grouping Status

```text
UNGROUPED | GROUPED
```

`UNGROUPED` is a legitimate Event state. It remains in the normal Event model and may be verified before a Story is identified.

Example:

```text
Grouping Status: UNGROUPED
Verification Status: VERIFIED
```

Once a primary Story is identified:

```text
UNGROUPED + VERIFIED → GROUPED + VERIFIED
```

## Event Verification Status

```text
PENDING | VERIFIED | REJECTED | ARCHIVED
```

Verification measures evidence-backed publication consensus for the Event. It does not mean that the Event has been assigned to a Story.

---

# 4. Verification Sources and Voting

Version 1 uses exactly three trusted publications:

- GKToday
- The Hindu
- The Indian Express

The voting model is two out of three.

A publication receives a vote only after the system determines that its Article describes the same underlying Event. Matching must precede voting.

Times of India is not a V1 verification source.

---

# 5. Article Provenance

Article-to-Article provenance is stored internally for auditability but is not the primary user-facing graph.

Allowed internal provenance types:

- `REPRINT`
- `CITES`
- `UPDATES`
- `CORROBORATES`
- `CONTRADICTS`

Meaningful semantic relationships are projected to the Event/Story graph only after ontology validation.

---

# 6. Allowed Knowledge Relationships

The graph engine, not the AI model, creates graph relationships.

## Event-to-Event Relationships

The approved relationship set is:

- `PRECEDES`
- `CAUSES`
- `RELATED_TO`

Relationships may cross primary Stories.

Every relationship must retain:

- source Article evidence;
- evidence type;
- confidence;
- verification status;
- reason;
- created and updated timestamps;
- immutable decision history.

## Relationship Evidence Rules

### PRECEDES

May be established through strong temporal and event evidence. Two independent Articles are not mandatory when the chronology and evidence are sufficiently authoritative.

### CAUSES

Requires stronger evidence: preferably two independent supporting sources or explicit authoritative evidence.

### RELATED_TO

Requires at least two independent supporting Articles and a confidence threshold. Shared entities alone are insufficient.

Cross-Story relationships require stricter confidence and evidence requirements than relationships within the same Story.

## Relationship Lifecycle

```text
PROPOSED → VERIFIED → REINFORCED
                 ↓
             DISPUTED
                 ↓
             REJECTED
```

Relationship decisions are never silently overwritten. Confidence, evidence, status, and history are versioned.

---

# 7. Story and Event Timelines

A Story Timeline consists primarily of its child Events ordered chronologically.

An Event retains its own Event Timeline for developments belonging to that Event.

Articles appear beneath the relevant Event as evidence. Articles do not become timeline nodes in the primary knowledge graph.

An Event must have one primary Story association when grouped. It must never become a child timeline Event of multiple Stories. Secondary Story associations are represented only through explicitly validated weaker relationships such as `RELATED_TO`.

---

# 8. AI and Ontology Responsibilities

The pipeline follows this division:

```text
AI proposes
  ↓
Evidence supports
  ↓
Ontology and deterministic rules validate
  ↓
Graph engine creates the relationship
```

AI may propose:

- Domain and Topic classification;
- Story and Event candidates;
- Claims;
- Event matching decisions;
- relationship candidates;
- confidence and explanation;
- summaries.

AI may not:

- bypass verification;
- create arbitrary graph edges;
- invent sources or evidence;
- change canonical history silently;
- recursively traverse the graph to create further relationships.

Candidate matching is bounded: retrieve a finite candidate set, rank it, make one decision, and stop. Graph expansion is controlled by explicit depth and relationship rules.

---

# 9. LLM Provider Architecture

The system uses a provider abstraction.

- Gemini Pro is the primary cloud model for ambiguous reasoning and high-quality summaries.
- Ollama with Qwen3:8B supports local development, offline testing, and fallback operation.

LLMs are invoked only after deterministic and specialized statistical stages have prepared evidence. LLM outputs must be structured, confidence-bearing, and auditable.

---

# 10. Background Processing

V1 background processing uses Celery with Redis.

Celery is responsible for scheduled and asynchronous work including:

- RSS ingestion;
- article normalization;
- entity and category processing;
- matching;
- summarization;
- verification;
- 10-day pending rechecks;
- timeline updates;
- graph validation and updates.

The architecture must keep task boundaries idempotent and retryable. Failed work must be logged and recoverable; no stage may fail silently.

---

# 11. Design Invariants

The following invariants are mandatory:

1. Events are first-class; Articles are evidence.
2. A Claim belongs to exactly one Event.
3. One Article may support multiple Events.
4. An Event has exactly one canonical Article at a time.
5. Canonical Article changes preserve history.
6. An Event has at most one primary Story.
7. An Event may remain `UNGROUPED` indefinitely.
8. Topics are taxonomy objects and are not verification subjects.
9. Stories require two independently evidenced qualifying Events before verification.
10. Every graph relationship has typed evidence, confidence, status, and history.
11. AI proposes; ontology rules validate; the graph engine writes.
12. No article, event, story, topic, claim, or relationship is silently deleted.

---

# 12. Implementation Sequence

Before feature implementation proceeds:

1. Reconcile the domain model and glossary with this document.
2. Reconcile the canonical data model and lifecycle definitions.
3. Update API contracts and response schemas.
4. Update backend implementation guidance for Celery and Redis.
5. Add database structures for Domains, Topics, Stories, Claims, Evidence, canonical Article history, provenance, relationship history, and grouping status.
6. Add ontology validation and evidence-threshold tests.
7. Only then implement ingestion, matching, verification, timeline, and graph workflows against the reconciled model.

---

# Closing Statement

IKG models a structured, evidence-backed knowledge system. Its reliability depends on maintaining clear boundaries between Articles, Claims, Events, Stories, Topics, Domains, and graph relationships. The ontology engine and evidence rules are the safeguards that keep AI-assisted knowledge explainable, bounded, and auditable.
