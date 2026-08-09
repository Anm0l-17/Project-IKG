# 19_Testing_Strategy.md

# India Knowledge Graph (IKG)

## Testing Strategy

Version: 1.0

Status: Production Ready

Priority: HIGH

Owner: QA Team

> **Architecture baseline:** This document must be read together with [23_Architecture_and_Ontology_Decisions.md](23_Architecture_and_Ontology_Decisions.md), which is the approved source of truth for the Domain → Topic → Story → Event ontology, evidence rules, lifecycle dimensions, relationship validation, V1 sources, and background processing. Where older text conflicts, the architecture baseline takes precedence.

---

# Purpose

This document defines the complete testing strategy for IKG.

Testing ensures:

- Correctness
- Reliability
- Performance
- AI Quality
- API Stability
- Frontend Consistency

Testing is mandatory before every release.

---

# Testing Pyramid

                 E2E Tests
                     ▲
              Integration Tests
                     ▲
                Unit Tests

Distribution

Unit Tests        70%

Integration       20%

End-to-End        10%

---

# Testing Principles

1. Every feature must have tests.

2. Bugs require regression tests.

3. AI outputs must be measurable.

4. Tests must be deterministic.

5. CI must fail on broken tests.

---

# Test Types

## Unit Tests

Purpose

Verify individual functions.

Examples

✓ Event Matching

✓ Knowledge Score Calculation

✓ Vote Counting

✓ Timeline Ordering

✓ RSS Parser

✓ Graph Builder

Target Coverage

95%

---

## Integration Tests

Purpose

Verify module interaction.

Examples

RSS

↓

Parser

↓

Embedding

↓

Matching

↓

Verification

↓

Graph

↓

Database

Test

Entire pipeline.

---

## API Tests

Framework

Pytest

Test

GET /feed

GET /events

GET /graph

GET /timeline

GET /search

GET /stats

Verify

Status Codes

JSON Structure

Pagination

Filtering

Sorting

Authentication

---

## Database Tests

Verify

Insert

Update

Delete

Transactions

Rollback

Indexes

Foreign Keys

---

## Neo4j Tests

Verify

Node Creation

Relationship Creation

Duplicate Prevention

Shortest Path Queries

Community Queries

Temporal Queries

---

## Qdrant Tests

Verify

Embedding Storage

Similarity Search

Latency

Top-K Retrieval

Duplicate Embeddings

---

## Redis Tests

Verify

Caching

Expiry

Invalidation

Queue Operations

---

# AI Testing

## NER

Dataset

Annotated Articles

Metrics

Precision

Recall

F1

Minimum

F1 > 0.90

---

## Category Classification

Metric

Accuracy

Target

95%

---

## Embedding

Verify

Nearest Neighbour Quality

Duplicate Detection

Latency

Target

<150ms

---

## Cross Encoder

Evaluate

Match Precision

False Positives

False Negatives

Threshold

0.82

Review quarterly.

---

## LLM Evaluation

Dataset

Manually labelled event pairs.

Expected Output

SAME_EVENT

FOLLOW_UP

RELATED

NEW_EVENT

DIFFERENT

Metrics

Accuracy

Consistency

JSON Validity

Hallucination Rate

Target

Hallucination = 0

---

# Voting Engine Tests

Test Cases

✓ 3/3 Agreement

✓ 2/3 Agreement

✓ 1/3 Agreement

✓ No Match

✓ Pending Queue

✓ Expiry after 10 Days

---

# Knowledge Score Tests

Verify

Score Range

0-100

Weight Calculation

Recalculation

Edge Cases

---

# Timeline Tests

Verify

Chronological Order

Duplicate Prevention

Follow-up Insertion

Archived Events

---

# Knowledge Graph Tests

Verify

Node Merge

Relationship Merge

Duplicate Entity Detection

Confidence Updates

Graph Traversal

---

# Frontend Testing

Framework

Vitest

React Testing Library

Playwright

---

## Component Tests

Event Card

Timeline

Search

Graph

Verification Panel

Navigation

Filters

---

## UI Tests

Responsive Layout

Desktop

Tablet

Mobile

---

## Accessibility Tests

Keyboard Navigation

ARIA Labels

Contrast Ratio

Screen Readers

Focus Indicators

---

# End-to-End Tests

Framework

Playwright

Scenarios

Open Homepage

↓

Open Event

↓

View Timeline

↓

Open Graph

↓

Search Event

↓

Filter Category

↓

Navigate Back

↓

Verify No Errors

---

# Performance Testing

Tool

k6

Test

100

500

1000

Concurrent Users

Metrics

Latency

Throughput

Error Rate

Memory

CPU

---

# Load Testing

Feed API

Graph API

Search API

Recommendation API

Target

Response Time

<500ms

---

# Security Testing

Dependency Scan

OWASP Top 10

SQL Injection

XSS

CSRF

Rate Limiting

Authentication

Secrets Exposure

---

# Regression Testing

Executed

Every Pull Request

Every Release

Every Model Upgrade

---

# Test Data

Use

Synthetic Data

Mock RSS

Mock Articles

Mock Events

Never test with production data.

---

# Continuous Integration

Pipeline

Lint

↓

Type Check

↓

Unit Tests

↓

Integration Tests

↓

API Tests

↓

Frontend Tests

↓

E2E Tests

↓

Coverage Report

↓

Build

Deployment blocked if any stage fails.

---

# Coverage Targets

Backend

95%

Frontend

90%

AI Modules

90%

Critical Services

100%

---

# Bug Severity

Critical

Platform unusable

High

Major feature broken

Medium

Incorrect behaviour

Low

UI or cosmetic issue

---

# Release Criteria

A release is approved only if:

✓ All tests pass

✓ Coverage targets met

✓ AI evaluation successful

✓ Performance targets met

✓ Security scan passes

✓ Manual QA completed

---

# Definition of Done

A feature is complete only if:

- Unit tests written
- Integration tests written
- Documentation updated
- CI passes
- Code reviewed
- No critical bugs

---

# Closing Statement

Testing is not a separate phase of development.

It is an integral part of the engineering process and must accompany every feature from design through deployment.

The test plan must cover ontology permission matrices, Claim-to-Event cardinality, one canonical Article per Event, canonical Article history, independent Story verification evidence, grouping/verification independence, relationship evidence thresholds, relationship lifecycle transitions, and idempotent Celery retries.
