# 🇮🇳 India Knowledge Graph (IKG)

> **An AI-powered Event Intelligence & Verification Platform for Indian Affairs**

![Status](https://img.shields.io/badge/Status-Architecture%20Baseline%20Approved-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-v0.1-orange)

---

# Table of Contents

- Introduction
- Problem Statement
- Vision
- Goals
- Key Features
- System Overview
- Architecture
- Verification Workflow
- AI Pipeline
- User Experience
- Technology Stack
- Project Structure
- Development Philosophy
- Roadmap
- Documentation
- Contributors
- License

---

# Introduction

India Knowledge Graph (IKG) is an AI-powered Event Intelligence Platform that transforms daily news into an interconnected knowledge network.

Unlike conventional news portals that display articles in chronological order, IKG identifies **real-world events**, verifies them using multiple trusted publications, tracks their evolution over time, and visualises their relationships using an interactive knowledge graph.

The platform enables users to understand **not only what happened, but why it happened, how it evolved, and what it affects.**

---

# Problem Statement

Today's news platforms suffer from several limitations.

- Information is fragmented across multiple articles.
- Follow-up developments are difficult to track.
- Users repeatedly read duplicate information.
- Context is lost after a few days.
- Relationships between policies, organisations and events remain hidden.
- Readers often need to verify the same information across multiple sources.

For users preparing for competitive examinations, researchers, journalists and policy analysts, this results in information overload instead of knowledge.

---

# Vision

Build India's most reliable AI-powered knowledge platform that converts verified news into structured knowledge.

Instead of asking

> "What happened today?"

The platform answers

> "What is happening, why is it happening, how did we get here, and what is connected to it?"

---

# Core Philosophy

News is temporary.

Knowledge is permanent.

IKG treats articles as **evidence** rather than the primary source of truth.

The primary object within the system is an **Event**.

Multiple articles can describe one event.

One event can evolve over months.

The platform continuously updates that event as new information becomes available.

The approved ontology extends this Event-first model without demoting Events:

```text
Domain → Topic → Story → Event → Claims / Article Evidence
```

Domains and Topics are taxonomy objects. Stories group related Events. Articles remain evidence, and Claims are article-specific assertions belonging to one Event. See [docs/23_Architecture_and_Ontology_Decisions.md](docs/23_Architecture_and_Ontology_Decisions.md) for the governing decisions.

---

# Goals

## Primary Goals

- Build a verified Indian news platform.
- Reduce misinformation through multi-source verification.
- Create a living knowledge graph.
- Maintain timelines for evolving stories.
- Provide concise AI-generated summaries.
- Make information exploration intuitive.

## Secondary Goals

- UPSC preparation
- Research
- Policy analysis
- Academic usage
- Journalism
- Public awareness

---

# Initial Coverage

Version 1 focuses exclusively on:

- Indian Current Affairs
- Indian Parliament
- Indian Defence
- Indian Geopolitics
- Indian Economics
- Indian Trade

Future versions will expand to additional domains.

---

# Key Features

## Traditional News Feed

Users who prefer a conventional experience can browse verified news in a familiar card-based layout.

Each article contains

- Headline
- AI Summary
- Category
- Date
- Verification Status
- Original Source

---

## AI Verification Engine

Every event undergoes independent verification.

Primary discovery source

- GKToday

Independent verification sources

- The Hindu
- The Indian Express

An article contributes to verification **only if the platform determines it is reporting the same underlying event.**

---

## Knowledge Graph

Every verified event becomes part of an interactive graph.

Nodes represent

- Events
- Countries
- Organisations
- Ministries
- Policies
- Companies
- People

Edges represent

- Follow-ups
- Cause & Effect
- Financial Relationships
- Political Decisions
- Policy Connections
- Organisational Relationships

---

## Event Timeline

Instead of reading multiple articles

Users see

Announcement

↓

Discussion

↓

Approval

↓

Implementation

↓

Impact

as a single evolving timeline.

---

## Semantic Search

Searching for

> RBI

returns

- Monetary Policy
- Inflation
- Repo Rate
- Banking Regulations
- Parliament Discussions
- Connected Events

instead of isolated articles.

---

# Verification Workflow

```text
GKToday

↓

New Event

↓

Extract Event Information

↓

Search Trusted Publications

↓

Event Matching

↓

Vote Allocation

↓

Verification

↓

Knowledge Graph

↓

Website
```

---

# AI Pipeline

```text
RSS Feed

↓

Article Collection

↓

Cleaning

↓

Named Entity Recognition

↓

Event Classification

↓

Embedding Generation

↓

Semantic Search

↓

Cross Encoder

↓

LLM Event Matcher

↓

Verification Engine

↓

Knowledge Graph

↓

Frontend
```

---

# Event Verification

The platform does **not** perform factual verification in the journalistic sense.

Instead, it performs **multi-source event verification.**

Process

1. Discover an event.
2. Search trusted publications.
3. Determine whether articles describe the same real-world event.
4. Allocate votes only after successful event matching.
5. Verify the event through majority consensus.

Verification Status

🟢 Verified

🟡 Pending

🔵 Developing

⚫ Archived

---

# User Experience

The platform provides two ways of consuming information.

## Traditional Feed

Ideal for users interested in daily updates.

## Knowledge Graph

Ideal for users exploring relationships between events.

Both views share the same verified event database.

---

# Technology Stack

Frontend

- Next.js
- React
- TailwindCSS
- Three.js
- React Three Fiber
- React Force Graph

Backend

- FastAPI
- PostgreSQL
- Neo4j
- Redis
- Celery

Artificial Intelligence

- Sentence Transformers
- spaCy
- Cross Encoder
- Large Language Models

Infrastructure

- Docker
- GitHub Actions
- Nginx
- Cloud Deployment

---

# Repository Structure

```
india-knowledge-graph/

├── docs/
├── backend/
├── frontend/
├── ai/
├── graph/
├── database/
├── scripts/
├── tests/
├── deployment/
└── README.md
```

---

# Development Philosophy

The project follows six principles.

### 1. Event-first Architecture

Articles are evidence.

Events are primary objects.

---

### 2. Human-centred Design

Powerful enough for researchers.

Simple enough for everyday users.

---

### 3. Explainable AI

Every AI decision should be explainable.

Users should understand

- why events were connected,
- why verification succeeded,
- and why recommendations were made.

---

### 4. Modular Architecture

Every subsystem should be independently replaceable.

---

### 5. AI-assisted Development

Every AI contributor must follow the rules defined in

```
docs/AGENTS.md
```

---

### 6. Documentation-first Development

No implementation begins before documentation is approved.

---

# Roadmap

Version 0.1

- RSS Collection
- News Feed

Version 0.2

- Event Verification

Version 0.3

- Knowledge Graph

Version 0.4

- Timeline Engine

Version 1.0

- Public Launch

---

# Documentation

Complete technical documentation is available inside

```
/docs
```

This repository follows a Documentation-First methodology.

Implementation must always follow approved documentation.

---

# Target Users

- Students
- UPSC Aspirants
- Researchers
- Journalists
- Policy Analysts
- Economists
- Defence Enthusiasts
- General Readers

---

# Project Status

🚧 Planning Phase

The project is currently undergoing architectural design and documentation.

Implementation has not yet begun.

---

# License

MIT License

---

# Acknowledgements

The platform builds upon publicly available information from trusted publications.

Every effort is made to attribute and link users to original reporting where appropriate.

This project generates its own summaries and knowledge representations rather than reproducing original articles.

---

# Final Statement

India Knowledge Graph is not a news website.

It is a knowledge platform.

News informs people.

Knowledge helps people understand.
