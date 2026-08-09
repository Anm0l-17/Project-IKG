# 16_AI_Pipeline_Implementation.md

# India Knowledge Graph (IKG)

## AI Pipeline Implementation Guide

Version: 2.0

Status: Production Ready

Priority: CRITICAL

Owner: AI Team

> **Architecture baseline:** This document must be read together with [23_Architecture_and_Ontology_Decisions.md](23_Architecture_and_Ontology_Decisions.md), which is the approved source of truth for the Domain → Topic → Story → Event ontology, evidence rules, lifecycle dimensions, relationship validation, V1 sources, and background processing. Where older text conflicts, the architecture baseline takes precedence.

---

# Purpose

This document defines the complete AI implementation workflow for IKG.

The objective is to transform raw news articles into verified, structured, explainable knowledge while maintaining deterministic behaviour wherever possible.

This document specifies:

- Pipeline architecture
- AI workflows
- Queue orchestration
- Event matching
- Verification
- Retry strategies
- Model registry
- Failure handling
- Performance requirements

---

# AI Philosophy

The platform follows four principles.

1. Deterministic before Generative
2. Evidence before Intelligence
3. Multiple Small Models over One Large Model
4. Every AI Decision must be Explainable

Large Language Models are **never** the source of truth.

They reason over evidence.

---

# High Level Architecture

                Fast Pipeline
                      │
                      ▼
          Event Candidate Creation
                      │
               Pending Knowledge
                      │
                      ▼
            Intelligence Pipeline
                      │
                      ▼
             Verified Knowledge

The AI system consists of two independent pipelines.

---

==========================================================
PIPELINE A
FAST INGESTION PIPELINE
==========================================================

Goal

Low latency.

Target

<15 seconds from RSS to Pending Event.

Stages

RSS

↓

Fetch

↓

Cleaning

↓

Metadata Extraction

↓

NER

↓

Classification

↓

Embedding

↓

Candidate Retrieval

↓

Cross Encoder

↓

Event Candidate

↓

Pending Queue

No LLM is used here.

This pipeline should be CPU friendly.

---

==========================================================
PIPELINE B
INTELLIGENCE PIPELINE
==========================================================

Goal

High confidence.

Runs asynchronously.

Stages

Pending Event

↓

Evidence Collection

↓

LLM Reasoning

↓

Voting Engine

↓

Timeline Update

↓

Graph Update

↓

Recommendation Refresh

↓

Knowledge Score

↓

Publish

---

==========================================================
STAGE 1
RSS DISCOVERY
==========================================================

Input

RSS Feed

Supported Sources

GKToday

The Hindu

Indian Express

Future

PIB

RBI

PRS India

Press Information Bureau

Output

Raw Article

Implementation

feedparser

Retry

3

Duplicate Detection

SHA256(URL)

---

==========================================================
STAGE 2
ARTICLE CLEANING
==========================================================

Library

BeautifulSoup

Extract

Headline

Author

Publication Date

Body

Canonical URL

Remove

Navigation

Ads

Footers

Scripts

Store

Raw HTML → MinIO

Clean Text → PostgreSQL

---

==========================================================
STAGE 3
ENTITY EXTRACTION
==========================================================

Primary

GLiNER

Fallback

spaCy

Extract

Countries

States

People

Ministries

Companies

Bills

Acts

Policies

Schemes

Currencies

Military Organisations

Political Parties

Output

Structured JSON

Confidence Threshold

0.75

---

==========================================================
STAGE 4
CATEGORY CLASSIFICATION
==========================================================

Purpose

Assign exactly one primary category.

Categories

Current Affairs

Parliament

Economics

Trade

Defence

Geopolitics

Output

Category

Confidence

Threshold

0.70

---

==========================================================
STAGE 5
EMBEDDING GENERATION
==========================================================

Primary Model

BAAI/bge-large-en-v1.5

Fallback

intfloat/e5-large-v2

Storage

Qdrant

Output

Embedding

Metadata

Model Version

Embedding ID

---

==========================================================
STAGE 6
CANDIDATE RETRIEVAL
==========================================================

Purpose

Find possible matching Events.

Method

Approximate Nearest Neighbour Search

Retrieve

Top 20

Latency Target

<150 ms

---

==========================================================
STAGE 7
CROSS ENCODER
==========================================================

Purpose

Reduce Top-20

↓

Top-3

Model

cross-encoder/ms-marco-MiniLM-L-6-v2

Threshold

0.82

Below threshold

↓

Create New Candidate Event

---

==========================================================
STAGE 8
AI DECISION ENGINE
==========================================================

This is NOT an LLM.

This is an orchestration layer.

Inputs

Current Article

Top Candidates

Timeline

Entities

Metadata

Similarity Scores

Decision Matrix

If Similarity > 0.95

↓

Same Event

If Timeline indicates continuation

↓

Follow-up

If Shared Entities but Different Context

↓

Related Event

Else

↓

New Event

Only uncertain cases proceed to the LLM.

---

==========================================================
STAGE 9
LLM REASONING
==========================================================

Purpose

Resolve ambiguous cases only.

Model

Configurable

Temperature

0

Output

Strict JSON

Allowed Decisions

SAME_EVENT

FOLLOW_UP

RELATED

NEW_EVENT

DIFFERENT

Every response must include

Decision

Confidence

Explanation

Referenced Evidence

---

Prompt Requirements

Never ask open-ended questions.

Never allow free-text output.

Return JSON only.

Never invent entities.

Never invent sources.

---

==========================================================
STAGE 10
EVENT MATCHING
==========================================================

An article matches an Event only if:

✓ Embedding Similarity passes threshold

AND

✓ Cross Encoder passes threshold

AND

✓ Entity overlap exceeds threshold

OR

✓ LLM confirms ambiguous match

Otherwise

↓

New Event

---

==========================================================
STAGE 11
VOTING ENGINE
==========================================================

Each publication receives exactly one vote.

Rule

Publication

↓

Matched Event

↓

Vote

No Match

↓

No Vote

Sources

GKToday

The Hindu

Indian Express

Required Majority

2 / 3

---

==========================================================
PENDING QUEUE
==========================================================

Condition

Votes < 2

↓

Pending

Maximum Duration

10 Days

Retry

Daily

If second source confirms

↓

Verified

Otherwise

↓

Expired

---

==========================================================
STAGE 12
TIMELINE ENGINE
==========================================================

Decision

FOLLOW_UP

↓

Append Timeline Entry

Decision

NEW_EVENT

↓

Create Timeline

Timeline Entries

Never deleted

Never reordered

---

==========================================================
STAGE 13
KNOWLEDGE GRAPH
==========================================================

Entity Resolution

↓

Merge Existing Nodes

↓

Create Missing Nodes

↓

Relationship Extraction

↓

Relationship Validation

↓

Graph Update

---

==========================================================
STAGE 14
SUMMARY GENERATION
==========================================================

Generate

Citizen Summary

Executive Summary

Timeline Summary

Requirements

Fact-based

Evidence-backed

No speculation

---

==========================================================
STAGE 15
KNOWLEDGE SCORE
==========================================================

Verification Confidence

40%

Evidence Count

20%

Graph Connectivity

15%

Timeline Completeness

15%

Freshness

10%

Range

0–100

Recalculated after every verified update.

---

==========================================================
QUEUE ARCHITECTURE
==========================================================

rss_fetch

↓

clean_article

↓

extract_entities

↓

generate_embedding

↓

candidate_retrieval

↓

cross_encoder

↓

decision_engine

↓

llm_reasoning (conditional)

↓

verification

↓

timeline

↓

graph

↓

recommendation

↓

publish

Dead Letter Queue

Enabled

---

==========================================================
MODEL REGISTRY
==========================================================

Every model stores

Model Name

Version

Task

Provider

Deployment Date

Latency

Accuracy

Rollback Version

Evaluation Results

No model may be replaced without updating the registry.

---

==========================================================
OBSERVABILITY
==========================================================

Track

RSS Processing Time

NER Latency

Embedding Latency

Matching Accuracy

Cross Encoder Accuracy

LLM Usage

Average Cost per Event

Verification Success Rate

Timeline Growth

Knowledge Graph Growth

Recommendation Click Rate

---

==========================================================
FAILURE POLICY
==========================================================

RSS Failure

↓

Retry

NER Failure

↓

Fallback

Embedding Failure

↓

Retry

Cross Encoder Failure

↓

Retry

LLM Failure

↓

Skip

↓

Manual Review

Graph Failure

↓

Retry

↓

Dead Letter Queue

No silent failures.

---

==========================================================
PERFORMANCE TARGETS
==========================================================

RSS Processing

<5 sec

NER

<2 sec

Embedding

<1 sec

Candidate Retrieval

<150 ms

Cross Encoder

<500 ms

Decision Engine

<100 ms

LLM

<8 sec

Complete Fast Pipeline

<15 sec

Complete Intelligence Pipeline

<60 sec

---

==========================================================
VERSIONING
==========================================================

Version independently:

Prompt Templates

NER Models

Embedding Models

Cross Encoders

Classification Models

Decision Rules

Knowledge Score Formula

Every change must be recorded in the Model Registry and Architecture Decision Records (ADRs).

---

# Closing Statement

The AI pipeline is designed as a deterministic, event-driven intelligence system rather than a sequence of isolated AI calls.

Its primary objective is to create trustworthy, explainable knowledge by combining traditional software engineering, machine learning and controlled LLM reasoning into a reproducible workflow.

---

# Approved Ontology Integration

The pipeline must classify and validate information against:

```text
Domain → Topic → Story → Event → Claim / Article Evidence
```

AI may propose Claims, Event matches, Story assignments, and relationship candidates. The ontology and evidence engine validates them; only the graph engine writes approved relationships. Article-to-article provenance is retained internally and is not the primary graph.

The Event model stores `grouping_status` independently from `verification_status`, allowing `UNGROUPED + VERIFIED`. A Story is verified only when at least two qualifying Events each have independent source evidence.
