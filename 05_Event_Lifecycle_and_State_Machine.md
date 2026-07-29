# 05_Event_Lifecycle_and_State_Machine.md

# India Knowledge Graph (IKG)

## Event Lifecycle & State Machine

Version: 1.0

Status: Active

Owner: Core Platform Architecture

Priority: CRITICAL

Dependencies:
- 04_Domain_Model.md
- GLOSSARY.md

---

# Purpose

This document defines the complete lifecycle of an Event.

Every Event created within India Knowledge Graph MUST follow the lifecycle described here.

No service may invent new states.

No service may skip states.

Every subsystem must respect the Event Lifecycle.

---

# Philosophy

An Event is not static.

It is a living object.

It is born.

It gathers evidence.

It becomes trusted.

It evolves.

Eventually it becomes historical.

The platform exists to continuously update Events instead of creating duplicate ones.

---

# Lifecycle Overview

```

NEW ARTICLE

↓

EVENT CANDIDATE

↓

ENTITY EXTRACTION

↓

EVENT MATCHING

↓

VOTING

↓

VERIFICATION

↓

PUBLICATION

↓

FOLLOW-UP DETECTION

↓

GRAPH UPDATE

↓

ARCHIVE

```

---

# Official Event States

There are exactly nine states.

```

DISCOVERED

↓

NORMALISED

↓

MATCHING

↓

PENDING

↓

VERIFIED

↓

ACTIVE

↓

HISTORICAL

↓

ARCHIVED

↓

DEPRECATED

```

---

# State Definitions

---

## DISCOVERED

Description

An Article has been collected.

An Event Candidate has been created.

Known Information

• Raw Article

• Source

• URL

• Timestamp

No AI has executed.

Visible?

No.

---

## NORMALISED

Purpose

Convert raw article into structured data.

Processes

Headline cleaning

Body extraction

Language detection

Date parsing

NER

Category prediction

Output

Structured Event Candidate

Visible?

No.

---

## MATCHING

Purpose

Determine whether this Event already exists.

Inputs

Entities

Embeddings

Date

Category

Title

Summary

Output

Existing Event

or

New Event

Possible Outcomes

SAME_EVENT

FOLLOW_UP

RELATED

NEW_EVENT

DIFFERENT

---

## PENDING

Meaning

Not enough evidence.

Current Vote Count

1/3

Behaviour

Wait.

Recheck daily.

Maximum Duration

10 Days

Possible Outcomes

Verified

Rejected

Expired

---

## VERIFIED

Requirement

Minimum

2 Votes

Verification Engine stores

Vote Sources

Confidence

Matching Evidence

Reason

Timestamp

Visible?

Yes.

---

## ACTIVE

Meaning

Publicly available.

Timeline grows.

Graph expands.

Follow-ups attach here.

Most user interaction occurs here.

---

## HISTORICAL

Meaning

No significant activity.

Still searchable.

Still explorable.

Timeline frozen unless new developments occur.

---

## ARCHIVED

Meaning

No expected future updates.

Graph remains.

Search remains.

Timeline locked.

Cannot receive manual edits.

---

## DEPRECATED

Meaning

Created by mistake.

Merged into another Event.

Duplicate.

Never shown to users.

Preserved for audit purposes.

---

# State Transition Rules

```

DISCOVERED

↓

NORMALISED

↓

MATCHING

↓

┌───────────────┐

│Existing Event │

└──────┬────────┘

↓

FOLLOW-UP

↓

ACTIVE

or

↓

┌───────────────┐

│New Event │

└──────┬────────┘

↓

PENDING

↓

VERIFIED

↓

ACTIVE

↓

HISTORICAL

↓

ARCHIVED

```

---

# Invalid Transitions

Forbidden

DISCOVERED

↓

ACTIVE

Impossible.

---

VERIFIED

↓

DISCOVERED

Impossible.

---

ARCHIVED

↓

PENDING

Impossible.

---

ACTIVE

↓

MATCHING

Impossible.

---

# Ownership

Every state has exactly one owner.

DISCOVERED

RSS Service

NORMALISED

NLP Service

MATCHING

Matching Engine

PENDING

Verification Engine

VERIFIED

Verification Engine

ACTIVE

Knowledge Engine

HISTORICAL

Lifecycle Manager

ARCHIVED

Lifecycle Manager

---

# Retry Strategy

Every failed AI operation retries.

Strategy

Attempt 1

↓

Retry after 5 minutes

↓

Retry after 30 minutes

↓

Retry after 6 hours

↓

Retry after 24 hours

↓

Mark Failed

Maximum Retries

5

---

# Pending Queue Rules

Every Pending Event

runs daily verification.

Maximum Lifetime

10 Days

Possible Outcomes

2 Votes

↓

Verified

No Votes

↓

Rejected

Still One Vote

↓

Expired

---

# Event Merge Rules

Sometimes

two Events become one.

Example

Two newspapers describe the same event differently.

System later determines

same Event.

Result

Merge.

Keep

Old IDs

Redirect

Evidence

Timeline

Relationships

Graph

Audit Log

Delete?

Never.

---

# Event Split Rules

Rare.

Occurs when

one Article

contains

multiple independent Events.

System creates

Event A

Event B

Both retain reference

to original Article.

---

# Follow-up Rules

A Follow-up

never creates

a new Timeline.

It extends

an existing Timeline.

Examples

Bill introduced

↓

Committee review

↓

Lok Sabha

↓

Rajya Sabha

↓

President

↓

Implementation

One Timeline.

One Event.

---

# Audit Trail

Every state transition creates

Event ID

Old State

New State

Timestamp

Actor

Reason

Confidence

Source

Nothing is overwritten.

History is immutable.

---

# Event Expiry

Pending Events

expire after

10 Days

unless

verification succeeds.

Expired Events

remain searchable internally.

Never shown publicly.

---

# AI Responsibilities

NER

↓

Entity Extraction

Embedding Model

↓

Similarity

Cross Encoder

↓

Ranking

LLM

↓

Reasoning

Verification Engine

↓

Decision

Knowledge Engine

↓

Graph Update

---

# Human Intervention

Humans may

Merge Events

Split Events

Approve

Reject

Restore

Archive

Every manual action

creates

Audit Record.

---

# Event Health

Every Event has

Health Score

based on

Verification

Freshness

Evidence Count

Relationship Density

Timeline Completeness

Health is internal only.

Not displayed.

---

# Failure Recovery

If AI fails

↓

Retry

If Matching fails

↓

Pending

If Graph fails

↓

Queue

If Verification fails

↓

Retry

If Timeline fails

↓

Log

Nothing is silently discarded.

---

# Sequence Diagram

```

RSS

↓

Article

↓

Normalisation

↓

NER

↓

Matching

↓

Verification

↓

Knowledge Graph

↓

Frontend

↓

User

```

---

# Lifecycle Guarantees

An Event

cannot exist

without

Source Evidence.

An Event

cannot become

Verified

without

matching.

An Event

cannot become

Active

without

Verification.

An Event

cannot disappear.

It only changes state.

---

# Design Principles

Events are immutable in identity.

Mutable in knowledge.

Every update enriches the same Event.

Never duplicate reality.

---

# Closing Statement

The Event Lifecycle is the operational backbone of India Knowledge Graph.

Every service, API, AI model, database table and user interface component relies on the guarantees established in this document.

Changes to the lifecycle require architectural review and may impact every subsystem.

No implementation may violate this state machine.