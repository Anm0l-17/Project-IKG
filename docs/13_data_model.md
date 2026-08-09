# 13_Data_Model.md

# India Knowledge Graph (IKG)

## Canonical Data Model

Version: 1.0

Status: Draft

Priority: CRITICAL

Owner: Backend Team

> **Architecture baseline:** This document must be read together with [23_Architecture_and_Ontology_Decisions.md](23_Architecture_and_Ontology_Decisions.md), which is the approved source of truth for the Domain → Topic → Story → Event ontology, evidence rules, lifecycle dimensions, relationship validation, V1 sources, and background processing. Where older text conflicts, the architecture baseline takes precedence.

---

# Purpose

This document defines every domain object used inside IKG.

All modules must use these models.

No module may redefine an Event, Entity or Source.

These models are the contract between:

- Backend
- AI Pipeline
- Graph Engine
- Frontend
- APIs

---

# Domain Overview

The platform revolves around six primary objects.

Event
↓

Article
↓

Source
↓

Entity
↓

TimelineEntry
↓

Verification

Everything else derives from these.

---

=================================================

ENTITY : Source

=================================================

Represents a trusted publication.

Fields

id (UUID)

name

domain

rss_url

language

country

trust_score

logo_url

is_active

created_at

updated_at

---

Rules

- One row per publication.
- Domain must be unique.
- Trust score is configurable.
- RSS URL can be null.

Example

id:
3d7...

name:
The Hindu

domain:
thehindu.com

---

=================================================

ENTITY : Article

=================================================

Represents a single fetched article.

Fields

id

source_id

url

headline

author

published_at

scraped_at

raw_html_path

clean_text

summary

language

hash

status

created_at

updated_at

---

Status

FETCHED

NORMALISED

MATCHED

PENDING

VERIFIED

REJECTED

---

Rules

- URL unique.
- Hash unique.
- Clean text immutable.
- Raw HTML stored in Object Store.

---

=================================================

ENTITY : Event

=================================================

Represents one real-world event.

Fields

id

canonical_title

slug

category

subcategory

knowledge_score

verification_status

summary

importance_score

status

first_seen

last_updated

created_at

updated_at

---

Status

Candidate

Pending

Verified

Archived

---

Rules

One Event

↓

Many Articles

One Event

↓

Many Timeline Entries

---

=================================================

ENTITY : TimelineEntry

=================================================

Represents one chronological update.

Fields

id

event_id

sequence

title

summary

published_at

importance

source_count

created_at

---

Rules

Sequence is monotonic.

Entries never deleted.

---

=================================================

ENTITY : Verification

=================================================

Represents verification status.

Fields

id

event_id

vote_count

required_votes

confidence

status

expires_at

verified_at

created_at

updated_at

---

Status

Pending

Verified

Rejected

Expired

---

=================================================

ENTITY : Vote

=================================================

Represents one publication's vote.

Fields

id

verification_id

source_id

article_id

decision

reason

confidence

created_at

---

Rules

One Source

↓

One Vote

per Event

Duplicate votes rejected.

---

=================================================

ENTITY : Entity

=================================================

Represents reusable concepts.

Fields

id

canonical_name

type

aliases

description

importance

created_at

updated_at

---

Entity Types

Country

State

City

Person

Company

Policy

Act

Bill

Organisation

Committee

Ministry

Political Party

Currency

Military Branch

Scheme

Court

Institution

---

=================================================

ENTITY : EventEntity

=================================================

Many-to-many relationship.

Fields

event_id

entity_id

relationship

confidence

created_at

---

=================================================

ENTITY : Relationship

=================================================

Stored in Neo4j.

Properties

from

to

type

confidence

evidence_count

created_at

updated_at

---

=================================================

ENTITY : Embedding

=================================================

Stored in Qdrant.

Fields

id

event_id

vector

model

version

created_at

---

=================================================

ENTITY : User

=================================================

Future.

Fields

id

email

password_hash

role

created_at

---

=================================================

ENTITY : Bookmark

=================================================

Future.

Fields

id

user_id

event_id

created_at

---

=================================================

ENTITY : AuditLog

=================================================

Every important action.

Fields

id

actor

action

entity_type

entity_id

metadata

created_at

---

=================================================

Relationships

=================================================

Source

↓

has_many

↓

Article

Article

↓

belongs_to

↓

Event

Event

↓

has_many

↓

TimelineEntry

Event

↓

has_many

↓

Verification

Verification

↓

has_many

↓

Vote

Event

↓

many_to_many

↓

Entity

Event

↓

one_to_one

↓

Embedding

---

ID Strategy

=================================================

All IDs

UUID v7

Reason

Chronologically sortable

Globally unique

Good indexing

---

Soft Delete Policy

=================================================

Never delete

Events

Entities

Timeline

Verification

Votes

Articles

Instead

status = Archived

---

Versioning

=================================================

Important entities maintain history.

Event

Timeline

Verification

Relationship

AI Decisions

No destructive updates.

---

Validation Rules

=================================================

Title cannot be empty.

Category required.

Knowledge score

0-100

Confidence

0-1

Timeline sequence

Unique

URL unique

Hash unique

---

Closing Statement

The Canonical Data Model defines the language of the platform.

Every module communicates using these objects.

Any schema changes require an Architecture Decision Record (ADR).

---

# Approved Data Model Extension

The canonical data model must additionally represent Domains, Topics, Stories, Claims, typed Evidence, canonical Article history, Article-to-Article provenance, Event grouping status, Story verification, relationship status, relationship evidence, and immutable decision history. PostgreSQL owns these structured records; Neo4j receives only validated relationship projections.
