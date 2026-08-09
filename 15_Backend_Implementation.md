# 15_Backend_Implementation.md

# India Knowledge Graph (IKG)

## Backend Implementation Guide

Version: 1.0

Status: Production Ready

Owner: Backend Team

Priority: CRITICAL

> **Architecture baseline:** This document must be read together with [23_Architecture_and_Ontology_Decisions.md](23_Architecture_and_Ontology_Decisions.md), which is the approved source of truth for the Domain → Topic → Story → Event ontology, evidence rules, lifecycle dimensions, relationship validation, V1 sources, and background processing. Where older text conflicts, the architecture baseline takes precedence.

---

# Purpose

This document defines the implementation standards for the backend.

Every developer and AI coding agent must follow this guide.

The goal is to maintain a clean, modular and scalable codebase.

---

# Technology Stack

Framework
- FastAPI

Language
- Python 3.13+

Dependency Management
- uv

ORM
- SQLAlchemy 2.x

Database Migration
- Alembic

Validation
- Pydantic v2

Authentication (Future)
- JWT

Task Queue
- Celery

Caching
- Redis

Object Storage
- MinIO

Logging
- Structlog

Configuration
- Pydantic Settings

Testing
- Pytest

---

# Project Structure

backend/

    app/

        api/
            v1/

                feed.py
                event.py
                graph.py
                search.py
                timeline.py
                recommendation.py
                admin.py

        core/

            config.py
            logger.py
            security.py
            constants.py

        models/

            event.py
            article.py
            entity.py
            verification.py
            timeline.py
            source.py

        schemas/

            event.py
            article.py
            search.py
            graph.py

        repositories/

            postgres/
            neo4j/
            qdrant/
            redis/

        services/

            ingestion/
            matching/
            verification/
            graph/
            search/
            recommendation/

        ai/

            embeddings/
            summariser/
            ner/
            classifier/
            reranker/

        workers/

            ingest_worker.py
            verification_worker.py
            graph_worker.py
            search_worker.py

        events/

            publisher.py
            subscriber.py

        db/

            postgres.py
            neo4j.py
            redis.py
            qdrant.py

        utils/

        tests/

main.py

---

# Layered Architecture

API Layer

↓

Service Layer

↓

Repository Layer

↓

Database

Business logic belongs ONLY in the Service Layer.

---

# API Layer

Responsibilities

- Validate request
- Call service
- Return DTO

Must NOT

- Execute SQL
- Call Neo4j
- Generate embeddings
- Perform AI inference

---

# Service Layer

Responsibilities

- Business logic
- Orchestration
- Transactions
- Event publishing

Every service exposes public methods only.

Example

EventService

SearchService

VerificationService

TimelineService

---

# Repository Layer

Responsibilities

- Database access only

Repositories

EventRepository

ArticleRepository

EntityRepository

GraphRepository

EmbeddingRepository

---

# Dependency Injection

Use FastAPI Depends()

Never instantiate services manually.

Example

API

↓

Depends()

↓

Service

↓

Repository

---

# Configuration

Environment variables only.

No hardcoded values.

.env

↓

Pydantic Settings

↓

Application

---

# Background Workers

Worker 1

RSS Ingestion

Every 15 minutes

---

Worker 2

Pending Verification

Daily

---

Worker 3

Graph Update

Triggered by EventVerified

---

Worker 4

Embedding Generation

Triggered after Event creation

---

Worker 5

Recommendation Refresh

Triggered after Graph update

---

# Event Bus

Use internal domain events.

Example

ArticleFetched

↓

EventMatched

↓

EventVerified

↓

TimelineUpdated

↓

GraphUpdated

↓

RecommendationUpdated

Modules communicate only through events.

---

# Error Handling

Use custom exceptions.

Examples

EventNotFound

DuplicateArticle

VerificationFailed

EntityConflict

Return standard API errors.

---

# Logging

Every request gets

- Request ID
- Timestamp
- User Agent
- Endpoint
- Duration

Log Levels

INFO

WARNING

ERROR

CRITICAL

---

# Validation

Pydantic models validate

- Requests
- Responses
- Internal events

Validation never occurs inside repositories.

---

# Naming Conventions

Classes

PascalCase

Functions

snake_case

Variables

snake_case

Constants

UPPER_CASE

Files

snake_case.py

---

# Transactions

Only Service Layer opens transactions.

Repositories never begin transactions.

---

# Security

Never trust user input.

Validate everything.

Sanitise search input.

Escape HTML.

Prevent SQL injection.

Use parameterised queries only.

---

# Performance Rules

No N+1 queries.

Batch database operations.

Lazy-load expensive resources.

Cache frequently accessed data.

---

# Testing Structure

tests/

    unit/

    integration/

    api/

    ai/

    graph/

Coverage target

>90%

---

# Environment Variables

DATABASE_URL

REDIS_URL

NEO4J_URI

QDRANT_URL

MINIO_ENDPOINT

OPENAI_API_KEY

HF_API_KEY

LOG_LEVEL

APP_ENV

---

# Docker Services

backend

postgres

redis

neo4j

qdrant

minio

worker

scheduler

frontend

---

# CI Pipeline

1. Lint

2. Type Check

3. Unit Tests

4. Integration Tests

5. Docker Build

6. Security Scan

7. Deploy

---

# Code Review Checklist

✓ No business logic in API

✓ No SQL outside repositories

✓ Type hints everywhere

✓ Tests included

✓ Logging added

✓ Events published

✓ Documentation updated

---

# Definition of Done

A feature is complete only if:

- Code implemented
- Tests passing
- Documentation updated
- API documented
- Logs added
- Metrics added
- Reviewed
- Merged

---

# Closing Statement

The backend is designed as a modular monolith with event-driven communication.

Every implementation must preserve module boundaries and maintain deterministic, testable business logic.

---

# Approved Implementation Changes

The approved architecture adds Domain, Topic, Story, Claim, Evidence, canonical Article history, Article provenance, grouping status, and relationship history to the implementation plan. These objects must be introduced through migrations and repository interfaces before the corresponding workflows are implemented.

V1 background processing uses **Celery with Redis**. Replace older ARQ/task-queue guidance with Celery workers and scheduled tasks. Tasks must be idempotent, retryable, logged, and auditable.
