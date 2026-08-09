# 01_Product_Principles.md

# India Knowledge Graph (IKG)

## Product Principles

Version: 1.0

Status: Active

Priority: Critical

> **Architecture baseline:** This document must be read together with [23_Architecture_and_Ontology_Decisions.md](23_Architecture_and_Ontology_Decisions.md), which is the approved source of truth for the Domain → Topic → Story → Event ontology, evidence rules, lifecycle dimensions, relationship validation, V1 sources, and background processing. Where older text conflicts, the architecture baseline takes precedence.

---

# Purpose

This document defines the immutable principles that guide every product decision made within the India Knowledge Graph (IKG).

Unlike requirements, these principles should remain stable throughout the lifetime of the project.

Features may change.

Technology may change.

Frameworks may change.

These principles should not.

Whenever there is uncertainty, these principles take precedence over implementation preferences.

---

# Core Product Belief

IKG exists to improve understanding.

Not consumption.

Every decision should help users understand India better.

---

# Principle 1 — Events are the Source of Truth

## Problem

Traditional news platforms revolve around articles.

This creates duplication.

Each article is treated as a separate object even when multiple publications are discussing the same real-world occurrence.

## Decision

The Event is the primary object.

Articles are evidence attached to Events.

The entire platform is designed around this model.

### Why?

Reality consists of Events.

Journalism consists of Articles.

The platform models reality.

Not journalism.

### Implications

Timeline belongs to Event.

Verification belongs to Event.

Graph belongs to Event.

Relationships belong to Event.

Articles never own these concepts.

---

# Principle 2 — Verification Before Visibility

Speed should never be prioritised over trust.

An Event should become publicly visible only after passing the verification workflow.

Verification must be explainable.

Users should always understand why an Event has a particular verification status.

Verification is not binary.

States include:

Verified

Pending

Archived

Rejected

Future verification models may change.

The user-facing principle never changes.

Trust comes first.

---

# Principle 3 — AI Assists, Humans Understand

Artificial Intelligence should reduce effort.

It should never reduce transparency.

Users should always understand

- why Events were connected
- why verification succeeded
- why follow-ups were grouped
- why recommendations exist

The platform should never ask users to trust a black box.

---

# Principle 4 — Context is More Valuable Than Headlines

Knowing that an Event happened is useful.

Understanding

- what caused it,
- what changed,
- who is involved,
- what follows next,

is significantly more valuable.

Every interface should prioritise context over chronology.

---

# Principle 5 — Relationships Create Knowledge

Knowledge emerges when information is connected.

The platform should continuously discover relationships between:

Events

Policies

Countries

Ministries

Companies

People

Institutions

Schemes

Acts

Committees

Organisations

A graph is not merely a visualisation.

It is the platform's underlying knowledge model.

---

# Principle 6 — Simplicity Wins

Users should never experience the complexity of the backend.

Advanced AI.

Graph databases.

Embeddings.

Background workers.

Vector search.

These are implementation details.

The interface should feel calm, intuitive and predictable.

---

# Principle 7 — Explain Every Important Decision

Every important system decision should have an explanation.

Examples:

Why is this Event verified?

Which publications confirmed it?

Why are these two Events connected?

Why was this article attached to this Event?

Why is this relationship shown?

Opaque decisions reduce trust.

---

# Principle 8 — Build for Longevity

IKG is intended to become a long-term knowledge platform.

Every architectural decision should support years of accumulated information.

Optimise for maintainability over short-term convenience.

Temporary shortcuts become permanent technical debt.

---

# Principle 9 — Separate Responsibilities

Each subsystem owns exactly one responsibility.

Examples:

RSS Service

Collects articles.

Verification Engine

Determines verification.

Knowledge Engine

Builds graph relationships.

Frontend

Presents information.

Subsystems communicate.

They do not absorb each other's responsibilities.

---

# Principle 10 — Automation Before Manual Work

The platform should automate repetitive tasks.

Examples:

Event extraction

Relationship discovery

Timeline updates

Duplicate detection

Verification scheduling

Manual intervention should be exceptional.

Not routine.

---

# Principle 11 — Every Feature Must Reduce Cognitive Load

Adding information is easy.

Reducing mental effort is difficult.

Every feature proposal must answer:

"Does this make understanding easier?"

If not,

do not build it.

Examples of reducing cognitive load:

✓ AI summaries

✓ Timelines

✓ Relationship graphs

✓ Verification badges

✓ Source explanations

Examples of increasing cognitive load:

✗ Duplicate cards

✗ Excessive colour usage

✗ Multiple navigation paths

✗ Unnecessary metrics

---

# Principle 12 — Neutrality Above All

IKG is not an editorial platform.

It does not promote political viewpoints.

It does not rank Events by ideology.

It does not generate opinions.

Its responsibility is to organise verified information.

Interpretation belongs to the reader.

---

# Principle 13 — Performance is a Feature

Slow systems reduce trust.

Users should never wait while expensive AI models execute.

AI processing should happen asynchronously.

Browsing should feel immediate.

Background processing is preferred over blocking interactions.

---

# Principle 14 — Modular by Default

Every subsystem should be replaceable.

Future developers should be able to replace:

Embedding model

LLM

Database

Graph library

UI framework

without redesigning the entire platform.

Loose coupling is preferred over convenience.

---

# Principle 15 — Documentation is Part of the Product

Documentation is not an afterthought.

Every major architectural decision must be documented.

Every public API must be documented.

Every AI workflow must be documented.

A feature without documentation is incomplete.

---

# Product Decision Framework

Before approving any new feature, answer these questions:

### 1.

Does this improve understanding?

If no,

reject.

---

### 2.

Does this improve trust?

If no,

reconsider.

---

### 3.

Can the system explain this feature?

If no,

redesign.

---

### 4.

Does this reduce cognitive load?

If no,

reject.

---

### 5.

Does this fit the Event-first architecture?

If no,

reject.

---

### 6.

Will this still make sense five years from now?

If no,

simplify.

---

# Product Quality Checklist

Every completed feature should satisfy:

☐ Event-first

☐ Explainable

☐ Verified

☐ Accessible

☐ Responsive

☐ Documented

☐ Tested

☐ Maintainable

☐ Scalable

☐ Secure

---

# Closing Statement

Product quality is rarely determined by the number of features.

It is determined by the consistency of decisions.

The purpose of these principles is to ensure that every future contribution—whether made by a human developer or an AI agent—moves India Knowledge Graph in the same direction.

If two implementation options are technically valid, choose the one that best aligns with these principles, even if it requires more effort.

Consistency compounds over time.

That is how reliable products are built.