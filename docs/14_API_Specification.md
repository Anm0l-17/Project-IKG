# 14_API_Specification.md

# India Knowledge Graph (IKG)

## REST API Specification

Version: 1.0

Status: Production Draft

Owner: Backend Team

Priority: CRITICAL

---

# Purpose

This document defines every public and internal API used by IKG.

All APIs must follow this specification.

The frontend, AI pipeline and future mobile applications depend on these contracts.

Changing any endpoint requires API versioning.

---

# Base URL

/api/v1

---

# API Standards

Protocol

HTTPS only

Content Type

application/json

Encoding

UTF-8

Authentication

Public APIs

No authentication

Internal APIs

API Key

Admin APIs

JWT (Future)

---

# Standard Response Format

Success

{
    "success": true,
    "data": {},
    "meta": {}
}

Failure

{
    "success": false,
    "error": {
        "code": "EVENT_NOT_FOUND",
        "message": "Requested event does not exist."
    }
}

---

====================================================
HEALTH
====================================================

GET /health

Purpose

Health check

Response

{
    "status":"healthy",
    "version":"1.0.0",
    "database":"connected",
    "redis":"connected",
    "neo4j":"connected",
    "qdrant":"connected"
}

---

====================================================
FEED
====================================================

GET /feed

Description

Latest verified events

Query Parameters

page

limit

category

sort

knowledgeScoreMin

Response

[
  {
      "id":"",
      "title":"",
      "summary":"",
      "category":"",
      "knowledgeScore":95,
      "updatedAt":""
  }
]

---

GET /feed/trending

Purpose

Trending verified events

Ranking

Knowledge Score

Recent Activity

Graph Activity

Recommendation Score

---

====================================================
EVENT
====================================================

GET /events/{id}

Returns

Complete Event

Includes

Summary

Verification

Timeline

Knowledge Score

Primary Entities

Related Events

Sources

Example

GET

/events/f2d9...

---

GET /events/{id}/timeline

Returns

Timeline entries only

Ordered ascending

---

GET /events/{id}/graph

Returns

Nodes

Edges

Cluster

Graph Metadata

---

GET /events/{id}/verification

Returns

Verification details

Sources

Votes

Confidence

Knowledge Score

---

GET /events/{id}/sources

Returns

Original Articles

Publication dates

URLs

Source metadata

---

====================================================
SEARCH
====================================================

GET /search

Query

q

limit

category

sort

Response

Events

Entities

Suggestions

---

GET /search/entities

Returns

Matching entities

---

GET /search/suggestions

Autocomplete

Top 10

---

====================================================
GRAPH
====================================================

GET /graph

Returns

Filtered graph

Query

depth

category

entity

relationship

knowledgeScore

---

GET /graph/entity/{id}

Returns

Neighbourhood

Connected Events

Connected Entities

---

GET /graph/event/{id}

Returns

Subgraph

Maximum Depth

3

---

====================================================
TIMELINE
====================================================

GET /timeline

Query

category

date

page

limit

---

GET /timeline/event/{id}

Timeline only

---

====================================================
RECOMMENDATIONS
====================================================

GET /recommendations/{eventId}

Returns

Top Related Events

Ranking

Graph Distance

Embedding Similarity

Knowledge Score

---

====================================================
CATEGORY
====================================================

GET /categories

Returns

Available Categories

Current Affairs

Parliament

Economics

Trade

Defence

Geopolitics

---

====================================================
STATISTICS
====================================================

GET /stats

Returns

Platform statistics

Example

Verified Events

Pending Events

Average Knowledge Score

Articles Processed

Graph Nodes

Graph Edges

Sources

---

====================================================
ADMIN
====================================================

POST /admin/reverify

Triggers

Manual Verification

---

POST /admin/reindex

Rebuild

Search Index

---

POST /admin/rebuild-graph

Reconstruct

Knowledge Graph

---

GET /admin/jobs

Returns

Running Jobs

Failed Jobs

Queued Jobs

---

====================================================
INTERNAL
====================================================

POST /internal/article

Creates

Raw Article

---

POST /internal/event

Creates

Candidate Event

---

POST /internal/verification

Starts

Voting Pipeline

---

POST /internal/timeline

Adds

Timeline Entry

---

POST /internal/embedding

Stores

Vector

---

POST /internal/graph

Updates

Neo4j

---

====================================================
Pagination
====================================================

Cursor Based

Example

/feed?cursor=abc123

Advantages

Stable

Fast

Infinite Scroll

---

====================================================
Sorting
====================================================

latest

oldest

knowledgeScore

importance

relevance

---

====================================================
Filtering
====================================================

Category

Date Range

Knowledge Score

Verification Status

Source

Entity

---

====================================================
Status Codes
====================================================

200 OK

201 Created

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

409 Conflict

422 Validation Error

429 Too Many Requests

500 Internal Server Error

---

====================================================
Rate Limits
====================================================

Anonymous

60/min

Authenticated

300/min

Internal

Unlimited

---

====================================================
Caching
====================================================

Feed

60 sec

Stats

120 sec

Graph

30 sec

Recommendations

120 sec

Search Suggestions

300 sec

---

====================================================
OpenAPI
====================================================

Every endpoint

Must

Have

Description

Examples

Schema

Error Responses

Authentication

Version

---

# Closing Statement

This specification defines the external contract of IKG.

The frontend must never rely on database structures.

All communication occurs exclusively through these APIs.