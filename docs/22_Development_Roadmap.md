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
SPRINT 8 (COMPLETED — Session 9)
====================================================

Knowledge Graph Engine & Relationship Inference

Tasks

✓ EventRelationship Model & Alembic Migration 003
✓ Deterministic Graph Edge Inference Rules (PRECEDES, CAUSES, RELATED_TO)
✓ Subgraph & Global Graph REST APIs (GET /api/v1/graph, GET /api/v1/events/{id}/graph)
✓ Interactive SVG Knowledge Graph Visualizer & Inspector (KnowledgeGraphViewer.tsx)
✓ Dedicated /graph Explorer Page & Event Detail Subgraph View
✓ Automated Unit & Integration Tests (test_graph_engine.py, test_api_graph.py)

Deliverable

Interactive Knowledge Network Live

---

====================================================
SPRINT 9 (COMPLETED — Session 10)
====================================================

Story Clustering & Narrative Evolution

Tasks

✓ StoryClusteringService with clustering and multi-source consensus verification
✓ Multi-source verification evaluation (>= 2 events, >= 2 independent publications)
✓ Story REST API schemas & endpoints (GET /api/v1/stories, GET /api/v1/stories/{id}, POST /api/v1/stories/cluster)
✓ Frontend Stories Directory (/stories) & Story Dossier (/stories/[id])
✓ Narrative progression timeline and event grouping indicators
✓ Automated Unit & Integration Tests (test_story_clustering.py, test_api_story.py)

Deliverable

Automated Story Clustering & Narrative Evolution Live

---

====================================================
SESSION 11 (COMPLETED)
====================================================

Semantic & Hybrid Search via pgvector

Tasks

✓ VectorType TypeDecorator supporting dense vector embeddings (384-dim)
✓ Event embedding column and Alembic migration 004 (HNSW + Full-Text Search indexing)
✓ HybridSearchService: Lexical scoring + Dense Vector Cosine Similarity + Reciprocal Rank Fusion
✓ Filtering by Category, Verification Status, and Topic
✓ Enhanced Search APIs: GET /api/v1/search and POST /api/v1/search/backfill-embeddings
✓ Interactive Frontend /search Page with Match Type Badges (Hybrid, Semantic, Exact), filters & scores
✓ Automated Unit & API Integration Tests (test_hybrid_search.py, test_api_search.py)

Deliverable

Production-Grade Semantic & Hybrid Search Live

---

====================================================
SESSION 12 (COMPLETED)
====================================================

Distributed Background Processing (Redis / ARQ & Async Pipeline)

Tasks

✓ Unified TaskDispatcher supporting Redis/ARQ distributed queue with in-process async fallback
✓ Background worker task definitions (task_ingest_rss, task_verification_consensus, task_infer_relationships, task_cluster_stories, task_backfill_embeddings)
✓ ARQ Worker configuration (WorkerSettings) for scalable multi-worker deployment
✓ Admin / Operations task management APIs (GET /api/v1/tasks/status, POST /api/v1/tasks/trigger)
✓ Automated Unit & API Integration Tests (test_background_workers.py, test_api_tasks.py)

Deliverable

Resilient Distributed Background Processing Pipeline Live

---

====================================================
SESSION 13 (COMPLETED)
====================================================

Monitoring, Observability & Security

Tasks

✓ Structured telemetry logging with correlation IDs (X-Request-ID) and response time tracking
✓ In-memory MetricsCollector recording throughput, status distributions, popular routes, and error rates
✓ System metrics API (GET /api/v1/metrics) reporting telemetry & live platform database statistics
✓ OWASP SecurityHeadersMiddleware (nosniff, DENY, XSS protection, HSTS, Referrer-Policy)
✓ RateLimiterMiddleware (sliding window IP throttling) protecting against endpoint abuse
✓ Enhanced health probes: Liveness (/api/v1/health) & Deep Readiness probe (/api/v1/ready)
✓ Automated Unit & API Integration Tests (test_observability.py)

Deliverable

Hardened Production Observability & Security Framework Live

---

====================================================
SESSION 14 (COMPLETED)
====================================================

Containerization, CI/CD & Production Deployment

Tasks

✓ Multi-stage production backend Dockerfile (Python 3.13-slim, unprivileged user, healthcheck)
✓ Multi-stage production frontend Dockerfile (Next.js 15, Node 20-alpine, unprivileged user)
✓ Full-stack docker-compose.yml (PostgreSQL + pgvector, Redis, Neo4j, Qdrant, MinIO, Backend, Worker, Frontend)
✓ Production Nginx reverse proxy & rate limiting configuration (deploy/nginx/nginx.conf & docker-compose.prod.yml)
✓ Automated GitHub Actions CI workflow (.github/workflows/ci.yml)
✓ Continuous Deployment workflow (.github/workflows/deploy.yml)
✓ Production deployment automation script (scripts/deploy.sh)

Deliverable

Production-Ready Containerized Deployment & Automated CI/CD Live

---

====================================================
PROJECT STATUS: ALL SESSIONS & ROADMAP COMPLETE (1.0)
====================================================

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
