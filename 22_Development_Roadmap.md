# 22_Development_Roadmap.md

# India Knowledge Graph (IKG)

## Development Roadmap

Version: 1.0

Status: Active

Priority: CRITICAL

Owner: Product Team

> **Architecture baseline:** This document must be read together with [23_Architecture_and_Ontology_Decisions.md](23_Architecture_and_Ontology_Decisions.md), which is the approved source of truth for the Domain → Topic → Story → Event ontology, evidence rules, lifecycle dimensions, relationship validation, V1 sources, and background processing. Where older text conflicts, the architecture baseline takes precedence.

---

# Purpose

This document defines the implementation roadmap for IKG.

It specifies:

- Milestones
- Sprint Planning
- Deliverables
- MVP Scope
- Version Releases
- Success Criteria

The roadmap follows Agile principles with iterative development.

---

# Development Philosophy

Build the smallest working system first.

Then improve.

Priorities

Correctness

↓

Reliability

↓

Performance

↓

AI Sophistication

↓

New Features

Never optimise a feature that does not yet exist.

---

# Overall Timeline

Phase 0

Project Setup

↓

Phase 1

Backend Foundation

↓

Phase 2

Frontend Foundation

↓

Phase 3

News Ingestion

↓

Phase 4

Event Matching

↓

Phase 5

Verification Engine

↓

Phase 6

Knowledge Graph

↓

Phase 7

AI Enhancement

↓

Phase 8

Testing

↓

Phase 9

Production Launch

---

# MVP Definition

Version

0.1

Must Include

✓ RSS ingestion

✓ Article cleaning

✓ PostgreSQL

✓ Event creation

✓ Event detail page

✓ Feed

✓ Search

✓ Timeline

✓ Manual verification

No AI.

Goal

Working news platform.

---

# Version 0.2

Add

Entity Extraction

Category Classification

Embeddings

Semantic Search

Recommendation Engine

Still

No LLM

Goal

Intelligent retrieval.

---

# Version 0.3

Add

Cross Encoder

Automatic Event Matching

Pending Queue

Voting Engine

Knowledge Score

Goal

Verified Event Intelligence.

---

# Version 0.4

Add

Neo4j

Relationship Extraction

Knowledge Graph

Graph Page

Related Events

Goal

Knowledge Network.

---

# Version 0.5

Add

LLM Reasoning

Citizen Summaries

Executive Summaries

Timeline Summaries

Goal

AI-Assisted Knowledge.

---

# Version 1.0

Public Release

Includes

Frontend

Backend

AI Pipeline

Knowledge Graph

Monitoring

Security

Testing

Deployment

Documentation

---

====================================================
SPRINT 1
====================================================

Project Initialisation

Tasks

Repository

Docker

Backend Skeleton

Frontend Skeleton

CI

Coding Standards

Deliverables

Running project

---

====================================================
SPRINT 2
====================================================

Backend APIs

Tasks

Feed

Event

Category

Search

Database Models

Migrations

Deliverable

REST API

---

====================================================
SPRINT 3
====================================================

Frontend Foundation

Tasks

Homepage

Navbar

Feed

Event Page

Responsive Layout

Deliverable

Working UI

---

====================================================
SPRINT 4
====================================================

RSS Ingestion

Tasks

RSS Parser

Cleaning

Storage

Scheduler

Duplicate Detection

Deliverable

Automatic Article Collection

---

====================================================
SPRINT 5
====================================================

Verification System

Tasks

Voting

Pending Queue

Admin Review

Timeline

Deliverable

Verified Events

---

====================================================
SPRINT 6
====================================================

AI Foundation

Tasks

NER

Classification

Embeddings

Semantic Search

Deliverable

AI-assisted indexing

---

====================================================
SPRINT 7
====================================================

Matching

Tasks

Candidate Retrieval

Cross Encoder

Decision Engine

Timeline Merge

Deliverable

Automatic Event Matching

---

====================================================
SPRINT 8
====================================================

Knowledge Graph

Tasks

Neo4j

Graph Builder

Relationship Extraction

Graph API

Graph Visualisation

Deliverable

Interactive Graph

---

====================================================
SPRINT 9
====================================================

LLM Integration

Tasks

Summaries

Reasoning

Recommendations

Prompt Registry

Deliverable

AI Features

---

====================================================
SPRINT 10
====================================================

Quality

Tasks

Testing

Monitoring

Security

Optimisation

Bug Fixes

Documentation

Deliverable

Release Candidate

---

# Git Workflow

main

Production

develop

Integration

feature/*

Individual features

release/*

Release preparation

hotfix/*

Critical fixes

---

# Pull Request Rules

Every PR must include

Description

Linked Issue

Tests

Documentation Updates

Review Approval

CI Passing

---

# Issue Labels

backend

frontend

ai

graph

bug

enhancement

documentation

performance

security

testing

good first issue

---

# Milestones

Milestone 1

Backend APIs Complete

Milestone 2

Frontend Functional

Milestone 3

RSS Working

Milestone 4

Verification Operational

Milestone 5

Knowledge Graph Live

Milestone 6

AI Integration Complete

Milestone 7

Production Ready

---

# Risks

Risk

RSS Structure Changes

Mitigation

Parser Abstraction

---

Risk

Model Performance

Mitigation

Model Registry

---

Risk

API Rate Limits

Mitigation

Caching

---

Risk

Graph Growth

Mitigation

Pagination

Depth Limits

---

Risk

Infrastructure Costs

Mitigation

Self-hosting

---

# Success Metrics

System

99.9% uptime

Feed latency

<2 sec

Graph load

<3 sec

AI Pipeline

<60 sec

API

P95 <300 ms

Coverage

>90%

---

# Definition of MVP

The MVP is complete when a user can:

- Visit the website.
- Browse verified events.
- Read event timelines.
- Search events.
- Explore categories.
- View verification status.
- Navigate related events.

Advanced AI features are **not required** for MVP completion.

---

# Definition of Version 1.0

Version 1.0 is complete when:

✓ AI Pipeline operational

✓ Knowledge Graph operational

✓ Monitoring enabled

✓ Security complete

✓ CI/CD operational

✓ Production deployment complete

✓ Documentation complete

✓ Testing targets achieved

---

# Post-1.0 Roadmap

Version 1.1

Authentication

Bookmarks

Saved Collections

---

Version 1.2

Hindi Support

Regional Languages

---

Version 1.3

Public API

Developer Portal

---

Version 2.0

Mobile App

Graph Collaboration

AI Research Assistant

Predictive Event Analysis

---

# Closing Statement

IKG should be developed incrementally.

Each sprint must produce a usable improvement.

The objective is not simply to complete features, but to build a maintainable, reliable and trustworthy knowledge platform that can evolve over time.

The approved implementation sequence inserts an ontology/data-model reconciliation milestone before expanding ingestion, verification, AI, or graph work. That milestone covers Domain, Topic, Story, Claim, Evidence, grouping status, canonical Article history, provenance, relationship validation, and Celery/Redis infrastructure.
