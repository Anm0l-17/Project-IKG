# 12_Knowledge_Network_Architecture.md

# India Knowledge Graph (IKG)

## Knowledge Network Architecture

Version: 1.0

Status: Draft

Priority: CRITICAL

Owner: Knowledge Platform Team

> **Architecture baseline:** This document must be read together with [23_Architecture_and_Ontology_Decisions.md](23_Architecture_and_Ontology_Decisions.md), which is the approved source of truth for the Domain → Topic → Story → Event ontology, evidence rules, lifecycle dimensions, relationship validation, V1 sources, and background processing. Where older text conflicts, the architecture baseline takes precedence.

---

# Purpose

This document defines how India Knowledge Graph represents knowledge.

The Knowledge Network is the heart of the platform.

It stores relationships, context, evolution and interconnected understanding of public affairs.

Unlike traditional databases, the Knowledge Network models reality rather than records.

---

# Philosophy

Information answers:

"What happened?"

Knowledge answers:

"What happened, why, how, and what changed?"

The Knowledge Network exists to answer the second question.

---

# Core Principle

The primary graph contains Domain, Topic, Story, Event, and reusable Entity nodes. Articles and Claims remain evidence/provenance records and are not the primary visual graph nodes.

---

# Node Types

There are two primary node families.

## Event Nodes

Represent real-world occurrences.

Examples

- Union Budget 2026
- India-UK FTA Signed
- Operation Sindoor
- RBI Repo Rate Decision
- Digital Personal Data Protection Rules

Properties

- Event ID
- Title
- Category
- Status
- Knowledge Score
- Verification Status
- Created At
- Updated At

---

## Entity Nodes

Represent reusable concepts.

Examples

Countries

States

Cities

People

Political Parties

Ministries

Bills

Acts

Policies

Companies

Stock Exchanges

Banks

Currencies

Military Branches

Committees

Schemes

Organisations

Courts

International Organisations

---

Properties

Entity ID

Type

Canonical Name

Aliases

Description

Wikipedia Link (future)

Importance

Popularity

---

# Relationship Types

Relationships are directional.

Every edge contains

Type

Confidence

Created At

Last Updated

Evidence Count

Weight

Source

---

Relationship Types

ANNOUNCED_BY

IMPLEMENTED_BY

AFFECTS

FUNDS

REGULATES

LOCATED_IN

PART_OF

CAUSES

RESULTS_IN

SUPPORTS

OPPOSES

REPLACES

AMENDS

REFERENCES

CONNECTED_TO

FOLLOWS

PRECEDES

MENTIONS

COLLABORATES_WITH

SIGNED_WITH

---

# Relationship Confidence

Every edge stores confidence.

Example

India

↓

SIGNED_WITH

↓

United Kingdom

Confidence

0.97

Evidence

3

Knowledge Score

95

---

# Event Evolution

Events are living objects.

Timeline

↓

Knowledge Graph

↓

Knowledge Network

Every timeline update enriches existing nodes.

No duplicate nodes.

---

# Communities

Closely connected nodes form communities.

Examples

Economic Community

↓

RBI

Finance Ministry

Inflation

Repo Rate

GDP

Fiscal Deficit

---

Parliament Community

↓

Lok Sabha

Rajya Sabha

Bills

Standing Committees

President

---

Defence Community

↓

Army

Navy

Air Force

DRDO

HAL

Border Roads Organisation

---

These communities emerge naturally.

They are not manually created.

---

# Node Lifecycle

Nodes are never deleted.

States

Candidate

↓

Verified

↓

Active

↓

Dormant

↓

Archived

Even archived nodes remain searchable.

---

# Edge Lifecycle

Edges evolve.

New Evidence

↓

Higher Confidence

↓

Higher Weight

↓

Stronger Connection

If evidence disappears,

confidence decreases,

but history remains.

---

# Knowledge Score Propagation

Knowledge flows through the graph.

Example

If an Event gains new verified evidence,

connected entities inherit partial confidence updates.

This allows related recommendations to improve automatically.

---

# Graph Algorithms

Version 1

Breadth-First Search

Shortest Path

Connected Components

Neighbour Expansion

---

Version 2

PageRank

Community Detection

Centrality

Betweenness

Node Similarity

Label Propagation

---

Version 3

Graph Neural Networks

Temporal Graph Embeddings

Knowledge Graph Completion

---

# Graph Queries

Supported queries include:

- Show all Events involving RBI.
- Show all policies affecting MSMEs.
- Find shortest path between India and Quad.
- Display all follow-ups to a Bill.
- List events connected to a Ministry.
- Find countries sharing defence agreements.

---

# Graph Update Pipeline

Verified Event

↓

Entity Resolution

↓

Relationship Extraction

↓

Graph Validation

↓

Node Merge

↓

Edge Merge

↓

Knowledge Score Update

↓

Recommendation Refresh

---

# Graph Validation

Before insertion:

- Duplicate node detection
- Alias resolution
- Relationship validation
- Circular relationship checks (where applicable)
- Confidence threshold evaluation

Only validated changes are committed.

---

# Visualisation

The visual graph shown to users is a projection of the Knowledge Network.

Rendering rules:

- Show limited depth by default.
- Cluster related nodes.
- Hide low-confidence edges.
- Animate expansion progressively.
- Colour by category.

The visual graph should never expose the entire database at once.

---

# Knowledge Paths

The network enables guided exploration.

Example

India-UK FTA

↓

Trade Negotiations

↓

Previous Agreements

↓

Affected Industries

↓

Parliament Debate

↓

Implementation Updates

Users traverse knowledge, not hyperlinks.

---

# Temporal Intelligence

Relationships carry time.

Example

RBI

↓

ANNOUNCED

↓

Repo Rate Increase

Date: 15 Jan 2026

AFFECTED

↓

Housing Loans

Date: 20 Jan 2026

The graph understands chronology.

---

# Future Extensions

Future node types may include:

- Research Papers
- Court Judgements
- Government Orders
- Budget Documents
- International Reports
- Election Manifestos

The underlying model remains unchanged.

---

# Architectural Rules

- Every Event must connect to at least one Entity.
- Every Relationship requires evidence.
- Duplicate canonical entities are forbidden.
- Graph updates occur only after verification.
- Knowledge Scores are recalculated after graph updates.
- Every graph mutation is auditable.

---

# Closing Statement

The Knowledge Network is the cognitive layer of India Knowledge Graph.

It transforms isolated facts into connected understanding.

Rather than storing information, it models the evolving structure of India's public affairs, enabling exploration, explanation and long-term contextual reasoning.

---

# Approved Graph Constraints

The user-facing graph is organized as:

```text
Domain → Topic → Story → Event
```

Articles and Claims support Events and relationships but are not the primary visual graph nodes. The approved Event-to-Event relationship types are `PRECEDES`, `CAUSES`, and `RELATED_TO`. Cross-Story relationships are permitted with stricter evidence and confidence requirements. `RELATED_TO` requires two independent supporting Articles. The graph engine validates AI proposals before creating edges and stores relationship status, evidence, confidence, and immutable history.
