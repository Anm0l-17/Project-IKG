# GLOSSARY.md

# India Knowledge Graph (IKG)

## Universal Language Specification (ULS)

Version: 1.0

Status: Active

Last Updated: TBD

---

# Purpose

This document establishes the official vocabulary of the India Knowledge Graph (IKG) project.

Every document, database schema, API, user interface, AI model, engineering discussion and future contribution MUST use the terminology defined here.

The purpose of this document is to eliminate ambiguity.

If two words describe the same concept, only one becomes the official project term.

Every contributor is expected to follow this document.

---

# Naming Principles

The project follows five principles.

## Principle 1

One concept.

One name.

Never create synonyms.

Example

Correct

Event

Incorrect

Story

Incident

Topic

Occurrence

News Item

All of the above refer to the same object.

Only "Event" is allowed.

---

## Principle 2

Business terms take precedence over technical terms.

Users understand

Event

better than

Primary Knowledge Object

Use language people understand.

---

## Principle 3

Database names may differ from UI names.

Example

Database

event_id

User Interface

Event ID

This is acceptable.

---

## Principle 4

Every object has a single owner.

Example

Verification Status

belongs to

Event

NOT

Article

---

## Principle 5

Documentation always wins.

If code and documentation disagree,

documentation is considered the source of truth until reviewed.

---

# Core Concepts

---

## Event

Definition

An Event represents a real-world occurrence.

It is the central object of the platform.

Examples

Union Budget 2026

India-France Defence Agreement

Monetary Policy Announcement

GST Amendment

Important Notes

One Event may have many Articles.

One Event may continue for weeks or months.

Events evolve.

Articles do not.

---

## Article

Definition

A published piece of journalism produced by a news organisation.

Purpose

Articles are evidence.

Articles are NOT the primary knowledge object.

Attributes

Headline

Summary

Publication Date

Author

Source

Content

URL

Image

Relationship

Many Articles

↓

One Event

---

## Source

Definition

An organisation that publishes Articles.

Examples

GKToday

The Hindu

The Indian Express

Future

PIB

RBI

PRS Legislative Research

Ministry of Defence

A Source never creates Events.

Sources publish Articles.

---

## Evidence

Definition

An Article that supports an Event.

An Event becomes stronger as more evidence is attached.

Evidence never exists independently.

It always belongs to an Event.

---

## Verification

Definition

The process of determining whether multiple trusted publications describe the same real-world Event.

Verification is NOT fact checking.

Verification measures publication consensus.

---

## Verification Vote

Definition

A single confirmation assigned to an Event after successful Event Matching.

Rules

A publication receives one vote only if

the platform first determines that it is describing the same Event.

No successful Event Match

↓

No Vote

---

## Verification Status

Official Values

Verified

Pending

Archived

Rejected

Deprecated values

True

False

Confirmed

Approved

Never use these.

---

## Pending Queue

Definition

Temporary storage for Events awaiting verification.

Lifetime

10 Days

Behaviour

Daily re-evaluation.

Automatic removal after expiry.

---

## Event Matching

Definition

The AI process responsible for determining whether two Articles describe the same Event.

Possible Outputs

SAME_EVENT

FOLLOW_UP

RELATED

DIFFERENT_EVENT

These are official enum values.

Do not invent alternatives.

---

## Follow-up

Definition

An update that extends an existing Event.

Examples

Bill Introduced

↓

Committee Review

↓

Parliament Debate

↓

President Approval

↓

Implementation

All belong to the same Event.

---

## Timeline

Definition

An ordered sequence of Follow-ups belonging to one Event.

A Timeline always belongs to exactly one Event.

---

## Entity

Definition

A real-world object identified inside an Article.

Examples

Country

Organisation

Person

Ministry

Policy

Company

City

Date

---

## Entity Extraction

Definition

The NLP process that identifies Entities inside an Article.

Output

Structured Entity Objects.

---

## Relationship

Definition

A semantic connection between two Nodes.

Examples

ANNOUNCED_BY

AFFECTS

CAUSES

FOLLOWS

FUNDS

RELATED_TO

---

## Node

Definition

A vertex inside the Knowledge Graph.

Types

Event

Person

Organisation

Country

Policy

Ministry

Company

---

## Edge

Definition

A relationship connecting two Nodes.

Every Edge has

Direction

Type

Confidence

Source

---

## Knowledge Graph

Definition

The structured network representing Events and their relationships.

Purpose

Knowledge Discovery.

Not visualisation.

Visualisation is only one representation.

---

## Graph View

Definition

The user interface that visualises the Knowledge Graph.

Do not confuse

Knowledge Graph

with

Graph View.

---

## News Feed

Definition

The traditional chronological presentation of verified Events.

Purpose

Daily reading.

---

## Dashboard

Definition

The main application interface containing navigation, statistics and shortcuts.

The Dashboard is not the Graph.

---

## Semantic Search

Definition

Searching by meaning rather than keywords.

Uses

Embeddings.

---

## Embedding

Definition

A numerical vector representing semantic meaning.

Embeddings are never shown to users.

---

## Similarity Score

Definition

A numerical estimate describing semantic similarity.

Higher score

↓

More similar.

---

## Confidence Score

Definition

The system's confidence in an AI prediction.

Confidence is never binary.

Always numerical.

Example

0.92

Not

High

Medium

Low

---

## Cross Encoder

Definition

A neural model used to compare two candidate Events.

Purpose

Re-ranking.

---

## Large Language Model (LLM)

Definition

The reasoning component used only after deterministic and statistical methods.

The LLM is the final stage.

Never the first stage.

---

## Verification Engine

Definition

The subsystem responsible for assigning verification status to Events.

It owns

Vote counting

Pending Queue

Verification Status

---

## Event Intelligence Engine

Definition

The complete AI pipeline responsible for

Extraction

Classification

Matching

Relationship Discovery

Timeline Construction

Verification

---

## Knowledge Engine

Definition

The subsystem responsible for maintaining the Knowledge Graph.

Responsibilities

Node Creation

Relationship Creation

Timeline Updates

Graph Maintenance

---

## Graph Cluster

Definition

A group of highly related Nodes.

Clusters emerge naturally.

They are never manually assigned.

---

## Category

Definition

A high-level classification.

Initial Categories

Current Affairs

Parliament

Economics

Trade

Defence

Geopolitics

---

## Topic

Definition

A user-facing organisational concept.

Example

Economy

contains many Events.

Topics are broader than Categories.

---

## Tag

Definition

A lightweight label used for filtering.

Tags never replace Categories.

---

## Workspace

Definition

The complete running application.

Never use

Portal

Tool

Website

interchangeably.

Official term

Workspace

---

# Reserved Words

The following names are reserved.

Event

Article

Evidence

Verification

Timeline

Knowledge Graph

Node

Edge

Source

Entity

Relationship

Dashboard

Workspace

These names should never be reused for different concepts.

---

# Deprecated Terminology

Never use

Story

News

Incident

Object

Graph Database Item

Document

Knowledge Object

Instead use

Event

---

# Final Rule

Every future document in this repository shall conform to the vocabulary defined in this specification.

If new terminology is introduced,

this document MUST be updated before implementation begins.