# 09_API_and_BFF_Architecture.md

# India Knowledge Graph

## API & Backend-for-Frontend (BFF) Architecture

Version: 1.0

Status: Draft

Priority: CRITICAL

Owner: Platform Team

---

# Purpose

This document defines the public interface of India Knowledge Graph (IKG).

The API layer exists to expose verified knowledge to clients while hiding the complexity of the underlying modules and storage systems.

Rather than exposing internal services directly, IKG adopts a Backend-for-Frontend (BFF) architecture.

The BFF acts as the single entry point for all client applications.

---

# Why BFF?

The frontend should focus on presentation, not orchestration.

Without a BFF:

Browser
↓

Multiple API calls
↓

Merge responses
↓

Handle failures

This increases latency and complexity.

With a BFF:

Browser
↓

One request
↓

BFF orchestrates modules
↓

Single response

---

# Architectural Overview

```
                Browser

                   │

                   ▼

          Next.js Frontend

                   │

                   ▼

          Backend for Frontend

────────────────────────────────

│

├── Event Module

├── Timeline Module

├── Search Module

├── Recommendation Module

├── Graph Module

├── Verification Module

│

────────────────────────────────

Repository Layer

↓

Storage
```

---

# Responsibilities

The BFF owns:

- Request validation
- Response composition
- Authentication (future)
- Rate limiting
- Response caching
- Error handling
- API versioning
- Pagination
- DTO mapping

The BFF does **not** own business logic.

---

# API Design Principles

## 1. Resource-Oriented

Expose domain resources.

Examples:

- Events
- Timelines
- Entities
- Search
- Graphs
- Sources

---

## 2. Read Optimised

IKG is primarily a read-heavy platform.

Public APIs are designed for fast retrieval.

Write operations are internal.

---

## 3. Stable Contracts

API responses must remain backwards compatible.

Breaking changes require a new version.

---

## 4. Thin Controllers

Controllers only:

- Validate
- Authorise
- Delegate
- Return DTOs

Business logic belongs in modules.

---

# Public API Groups

## Event API

Purpose

Retrieve Events.

Endpoints

GET /events

GET /events/{id}

GET /events/{id}/timeline

GET /events/{id}/graph

GET /events/{id}/verification

GET /events/{id}/related

---

## Search API

Purpose

Unified search.

Endpoints

GET /search

GET /search/suggestions

GET /search/entities

GET /search/categories

Supports:

- Keyword
- Semantic
- Hybrid search

---

## Feed API

Purpose

Latest verified Events.

Endpoints

GET /feed

GET /feed/{category}

GET /feed/trending

GET /feed/latest

Supported categories:

- Indian Current Affairs
- Parliament
- Geopolitics
- Economics
- Trade
- Defence

---

## Knowledge Graph API

Purpose

Visualise connected knowledge.

Endpoints

GET /graph/event/{id}

GET /graph/entity/{id}

GET /graph/subgraph

Response:

Nodes

Edges

Clusters

Metadata

---

## Timeline API

Purpose

Chronological view.

Endpoints

GET /timeline/{eventId}

GET /timeline/latest

GET /timeline/category/{category}

---

## Recommendation API

Purpose

Return related knowledge.

Endpoints

GET /recommendations/{eventId}

GET /recommendations/trending

GET /recommendations/entity/{entityId}

---

# Internal APIs

Used only by modules.

Examples:

POST /internal/events

POST /internal/verification

POST /internal/timeline

POST /internal/graph

POST /internal/index

These endpoints are not exposed publicly.

---

# Response Envelope

Every response follows a common structure:

```json
{
  "success": true,
  "timestamp": "2026-08-01T10:15:00Z",
  "data": {},
  "meta": {},
  "errors": []
}
```

---

# Pagination

Cursor-based pagination for feeds.

Example:

GET /feed?cursor=abc123&limit=20

Advantages:

- Stable ordering
- Efficient large datasets
- Better performance than offset pagination

---

# Caching Strategy

Cache:

- Homepage
- Feed
- Trending
- Popular graph queries
- Recommendations

Do not cache:

- Admin endpoints
- Verification queue
- Internal processing APIs

---

# Error Handling

Use consistent error responses.

Example:

```json
{
  "success": false,
  "error": {
    "code": "EVENT_NOT_FOUND",
    "message": "The requested event does not exist."
  }
}
```

---

# API Versioning

Version via URL.

Examples:

/api/v1/events

/api/v2/events

Avoid breaking existing clients.

---

# Rate Limiting

Anonymous:

60 requests/minute

Authenticated (future):

300 requests/minute

Internal modules:

Unlimited

---

# Security

Public APIs:

Read-only

Internal APIs:

Protected

Admin APIs:

Role-based access

Future:

OAuth2

JWT

API Keys

---

# Documentation

All public APIs must be documented using OpenAPI.

Interactive documentation generated automatically.

---

# Future APIs

Version 2 may introduce:

- Public GraphQL endpoint
- WebSocket subscriptions
- Streaming updates
- Mobile-specific BFF
- External developer API

---

# Closing Statement

The API and BFF architecture separates presentation concerns from business logic.

Clients receive a stable, efficient interface while internal modules remain free to evolve independently, ensuring long-term maintainability and scalability.