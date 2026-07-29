PostgreSQL
Neo4j
Redis
Qdrant


                 Storage Layer

─────────────────────────────────────

Operational Store

↓

Knowledge Store

↓

Semantic Store

↓

Cache Store

↓

Object Store


# 08_Database_Architecture.md

# India Knowledge Graph

## Database & Storage Architecture

Version 1.0

Status: Draft

Priority: CRITICAL

---

# Purpose

This document defines the complete storage architecture of India Knowledge Graph.

The platform follows a Polyglot Persistence architecture.

Different storage technologies are used because different data have different access patterns.

There is no "single database."

Instead,

the system contains specialised storage engines.

---

# Storage Philosophy

One responsibility.

One storage engine.

One source of truth.

Each storage engine owns one type of data.

No duplication unless explicitly designed.

---

# Storage Layers

```

Application

↓

Repository Layer

↓

Storage Layer

↓

Infrastructure

```

---

# Layer 1

Operational Store

Technology

PostgreSQL

Purpose

Store structured business data.

Examples

Events

Articles

Sources

Users

Verification

Bookmarks

Settings

Metadata

Audit Logs

---

Characteristics

ACID

Relational

Strong consistency

Transactional

---

Never store

Embeddings

Graphs

Large files

Images

---

# Layer 2

Knowledge Store

Technology

Neo4j

Purpose

Store relationships.

Examples

Event

↓

Ministry

↓

Organisation

↓

Policy

↓

Country

↓

Committee

↓

Budget

↓

Trade Agreement

---

Nodes

Event

Entity

Policy

Country

Company

Ministry

Committee

Person

Organisation

---

Relationships

AFFECTS

CAUSES

FOLLOWS

PART_OF

RELATED_TO

ANNOUNCED_BY

FUNDS

REGULATES

IMPLEMENTS

---

Optimised For

Relationship traversal

Community detection

Path finding

Graph exploration

---

Never store

Authentication

Sessions

Raw HTML

Images

---

# Layer 3

Semantic Store

Technology

Qdrant

Purpose

Store vector embeddings.

Used For

Semantic Search

Candidate Retrieval

Recommendations

Similarity Search

Duplicate Detection

---

Stored Objects

Embedding

Event ID

Metadata

Model Version

Timestamp

---

Never store

Raw articles

User data

Relationships

---

# Layer 4

Cache Store

Technology

Redis

Purpose

Temporary information.

Examples

Dashboard cache

Trending cache

Session cache

Rate limiting

Background queues

Job state

API cache

Search cache

---

TTL

Configurable

---

Never rely on Redis

for permanent storage.

---

# Layer 5

Object Store

Technology

MinIO

Future

AWS S3

Azure Blob

Purpose

Large files.

Examples

Images

PDFs

Raw HTML

Exports

Backups

Documents

Screenshots

---

Never query directly.

Always access

through the Repository Layer.

---

===================================================

Repository Layer

===================================================

The Repository Layer isolates the application from databases.

```

Module

↓

Repository

↓

Storage Engine

```

Advantages

Database independence.

Mock testing.

Migration.

Caching.

Versioning.

---

===================================================

Database Ownership

===================================================

Only one repository owns one entity.

Example

EventRepository

↓

PostgreSQL

KnowledgeRepository

↓

Neo4j

EmbeddingRepository

↓

Qdrant

CacheRepository

↓

Redis

ObjectRepository

↓

MinIO

No module bypasses its repository.

---

===================================================

Data Ownership Matrix

===================================================

| Data | Storage |
|------|----------|
| Events | PostgreSQL |
| Articles | PostgreSQL |
| Sources | PostgreSQL |
| Users | PostgreSQL |
| Bookmarks | PostgreSQL |
| Audit Logs | PostgreSQL |
| Relationships | Neo4j |
| Graph Nodes | Neo4j |
| Embeddings | Qdrant |
| Search Cache | Redis |
| Sessions | Redis |
| Images | MinIO |
| PDFs | MinIO |
| Raw HTML | MinIO |

---

===================================================

Synchronization Strategy

===================================================

PostgreSQL

↓

Source of Truth

↓

Domain Events

↓

Neo4j

↓

Qdrant

↓

Redis

The graph never updates PostgreSQL.

PostgreSQL publishes domain events.

Other storage engines consume them.

---

===================================================

Consistency Model

===================================================

PostgreSQL

Strong Consistency

Neo4j

Eventual Consistency

Qdrant

Eventual Consistency

Redis

Temporary

MinIO

Immutable objects

---

===================================================

Backup Strategy

===================================================

PostgreSQL

Daily snapshot

Point-in-time recovery

Neo4j

Nightly backup

Weekly full export

Qdrant

Snapshot every six hours

Redis

No backup required

MinIO

Versioned objects

Cross-region backup (future)

---

===================================================

Performance Targets

===================================================

Event lookup

<50 ms

Timeline

<100 ms

Graph query

<250 ms

Semantic search

<500 ms

Dashboard load

<2 seconds

Search suggestions

<100 ms

---

===================================================

Future Expansion

===================================================

Possible additions

TimescaleDB

↓

Economic indicators

ElasticSearch

↓

Full-text analytics

DuckDB

↓

Offline analytics

Apache Iceberg

↓

Data lake

No existing architecture changes required.

---

===================================================

Storage Rules

===================================================

Never duplicate ownership.

Never bypass repositories.

Never expose database schema to frontend.

Never couple business logic to SQL.

Every migration must be reversible.

Every storage engine must be independently replaceable.

---

# Closing Statement

The storage architecture of India Knowledge Graph follows the principle of "best tool for each responsibility."

Rather than forcing every problem into one database, the platform assigns each storage technology a clearly defined role.

This separation improves maintainability, scalability, performance and future adaptability while preserving a single, coherent domain model.