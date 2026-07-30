# 04_Domain_Model.md

# India Knowledge Graph (IKG)

## Core Domain Model

Version: 1.0

Status: Active

Owner: Chief Architect

Priority: CRITICAL

Dependencies

- README.md
- AGENTS.md
- GLOSSARY.md
- 00_Project_Vision.md
- 01_Product_Principles.md
- 02_State_of_the_Industry.md
- 03_User_Personas_and_User_Journeys.md

---

# Purpose

This document defines the conceptual world of India Knowledge Graph.

It does NOT define

• databases

• APIs

• programming languages

• frontend

Instead,

it defines how reality is represented inside the system.

Every future implementation must conform to this model.

---

# Philosophy

The system models reality.

Not articles.

Not websites.

Not databases.

Reality consists of

Events

People

Organisations

Policies

Countries

Laws

Relationships

Everything else exists to describe them.

---

# Core Domain

```
                    INDIA

                       │

      ─────────────────────────────────

      │              │               │

   Parliament     Economy        Defence

      │              │               │

      ─────────────────────────────────

                      │

                  EVENTS

                      │

      ─────────────────────────────────

      │              │               │

   Articles      Timeline      Knowledge Graph
```

Events are the centre of the universe.

Everything connects to Events.

---

# Domain Objects

The platform contains only ten primary domain objects.

Nothing else should become a first-class object without architectural review.

---

## 1. Event

Definition

A real-world occurrence that changes the state of one or more entities.

Examples

Budget

Policy

Treaty

Election

Cabinet Decision

Bill

Judgement

Trade Agreement

Military Exercise

Economic Report

Government Scheme

An Event may continue for years.

An Event is never deleted.

It only changes state.

---

Properties

ID

Title

Description

Category

Status

Created Date

Updated Date

Verification Status

Importance Score

Confidence Score

Timeline

Relationships

Evidence

Entities

---

Responsibilities

Owns Timeline

Owns Verification

Owns Relationships

Owns Evidence

Owns State

---

Never owns

UI

Database IDs

Source Formatting

HTML

---

## Event Lifecycle

```
Candidate

↓

Discovered

↓

Matching

↓

Pending

↓

Verified

↓

Active

↓

Historical

↓

Archived
```

No Event may skip a state.

---

## Event State Rules

Candidate

↓

Created from RSS

---

Discovered

↓

Metadata extracted

---

Matching

↓

Looking for evidence

---

Pending

↓

Waiting for confirmation

---

Verified

↓

2 of 3 votes

---

Active

↓

Visible

---

Historical

↓

No longer changing

---

Archived

↓

Frozen

---

# 2. Article

Definition

A publication describing an Event.

Articles exist only to provide evidence.

Multiple Articles

↓

One Event

---

Properties

Headline

Body

Source

Author

Published Date

URL

Image

Raw Content

Summary

---

Rules

Articles never own verification.

Articles never own timeline.

Articles never own graph.

---

# 3. Source

Definition

A trusted publication.

Version 1

GKToday

The Hindu

Indian Express

Future

PIB

RBI

PRS

Ministry Portals

---

Properties

Name

Type

Reliability

RSS

Website

Update Frequency

---

Responsibilities

Publish Articles.

Nothing else.

---

# 4. Evidence

Definition

A verified relationship between an Article and an Event.

Evidence contains

Article

Matching Score

Vote

Confidence

Timestamp

Evidence may expire.

Events do not.

---

# 5. Entity

Definition

A real-world object mentioned in an Event.

Types

Country

Organisation

Person

Policy

Company

Ministry

Law

Committee

Scheme

Currency

Institution

City

State

District

Military Branch

---

Rules

Entities are reusable.

One Entity may belong to thousands of Events.

---

# 6. Timeline

Definition

Chronological evolution of an Event.

Timeline Entry

Date

Description

Source

Importance

Type

Examples

Announcement

Discussion

Approval

Implementation

Result

Review

---

Rules

Timeline belongs only to one Event.

---

# 7. Relationship

Definition

Meaningful connection between two Nodes.

---

Relationship Types

CAUSES

FOLLOWS

RELATED_TO

IMPLEMENTS

ANNOUNCED_BY

FUNDS

REGULATES

LOCATED_IN

PART_OF

AFFECTS

REPLACES

SUPPORTS

OPPOSES

REFERENCES

CONNECTED_TO

---

Rules

Every relationship has

Direction

Confidence

Source

Reason

Timestamp

---

# 8. Knowledge Graph

Definition

The living representation of India's public affairs.

The graph contains

Nodes

Edges

Communities

Clusters

Graph never stores Articles directly.

Only references.

---

# 9. Verification

Definition

Consensus generated through independent publications.

Verification Object

Votes

Confidence

Evidence

Last Checked

Status

---

States

Pending

Verified

Rejected

Expired

---

# Verification Rule

Vote

↓

Only after Event Match

Never before.

---

# 10. User Workspace

Definition

The personalised interface presented to the user.

Contains

Feed

Graph

Search

Bookmarks

History

Preferences

Workspace never changes domain data.

---

# Domain Relationships

```
Source

│

publishes

│

Article

│

supports

│

Evidence

│

belongs to

│

Event

│

contains

│

Timeline

│

contains

│

Relationships

│

connects

│

Entities

│

form

│

Knowledge Graph
```

---

# Cardinality

One Source

↓

Many Articles

One Event

↓

Many Articles

One Event

↓

One Timeline

One Event

↓

Many Entities

One Entity

↓

Many Events

One Event

↓

Many Relationships

One Relationship

↓

Exactly Two Nodes

---

# Invariants

These rules can never be broken.

Event always exists before Timeline.

Article always belongs to a Source.

Evidence always belongs to an Event.

Verification always belongs to an Event.

Timeline never exists independently.

Relationships always connect Nodes.

Nodes never connect directly without Relationships.

---

# Anti-Patterns

The following are forbidden.

Article owning Timeline.

Article owning Verification.

Duplicate Events.

Circular Timeline.

Relationship without confidence.

Anonymous Source.

Deleted Event.

---

# Extensibility

Future versions may introduce

Court Cases

Government Orders

Research Papers

Judgements

Budget Documents

Cabinet Notes

International Reports

without changing the Event model.

---

# Closing Statement

Every database table, every API, every AI model, every user interface component and every background worker in India Knowledge Graph must be traceable to the domain model defined in this document.

If future implementations diverge from this model, the implementation should be reconsidered before the model is changed.

The domain model represents reality.

The software merely implements it.