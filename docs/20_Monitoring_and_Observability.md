# 20_Monitoring_and_Observability.md

# India Knowledge Graph (IKG)

## Monitoring & Observability

Version: 1.0

Status: Production Ready

Priority: HIGH

Owner: DevOps + Backend Team

---

# Purpose

This document defines the monitoring, logging, metrics, tracing and alerting strategy for IKG.

Every critical component must expose operational metrics.

Every production issue should be diagnosable using collected telemetry.

---

# Observability Goals

The platform must answer:

✓ Is the system healthy?

✓ Is data flowing correctly?

✓ Is the AI behaving correctly?

✓ Is the graph updating?

✓ Are users experiencing issues?

✓ Can failures be diagnosed quickly?

---

# Three Pillars

Metrics

↓

Logs

↓

Distributed Traces

---

====================================================
SYSTEM METRICS
====================================================

Collect

CPU

Memory

Disk

Network

Container Health

Database Storage

Worker Utilisation

Queue Size

Disk I/O

Restart Count

Collection Interval

15 seconds

---

====================================================
APPLICATION METRICS
====================================================

Backend

Request Count

Requests/sec

Latency

P95

P99

Error Rate

Response Size

Active Connections

Cache Hit Ratio

Database Query Time

---

====================================================
AI METRICS
====================================================

RSS Articles Fetched

Articles Processed

NER Success Rate

Classification Accuracy

Embedding Latency

Candidate Retrieval Time

Cross Encoder Latency

LLM Calls

Average LLM Cost

Average Tokens

Vote Success Rate

Pending Queue Size

Expired Events

Knowledge Score Distribution

Timeline Growth

Graph Updates

Recommendation Refresh Time

---

====================================================
GRAPH METRICS
====================================================

Nodes

Edges

Average Node Degree

Communities

Relationship Growth

Graph Update Duration

Merge Conflicts

Duplicate Entities Prevented

---

====================================================
DATABASE METRICS
====================================================

PostgreSQL

Connections

Transactions

Slow Queries

Lock Waits

Database Size

---

Neo4j

Query Time

Node Count

Relationship Count

Memory Usage

---

Qdrant

Collections

Vector Count

ANN Query Time

Index Size

---

Redis

Memory

Cache Hits

Cache Misses

Queue Length

Evictions

---

====================================================
LOGGING
====================================================

Structured JSON Logging

Every Log Contains

Timestamp

Request ID

Trace ID

Service

Environment

Log Level

Message

Duration

User Agent

---

Log Levels

DEBUG

INFO

WARNING

ERROR

CRITICAL

---

Never Log

Passwords

API Keys

Secrets

JWT Tokens

Personal Data

---

====================================================
DISTRIBUTED TRACING
====================================================

Every request receives

Trace ID

↓

Backend

↓

AI Workers

↓

Databases

↓

Response

This enables complete request tracing.

---

====================================================
ALERTS
====================================================

Critical Alerts

Backend Down

Database Down

Neo4j Down

Redis Down

Queue Failure

RSS Failure

Worker Crash

LLM Failure Rate >10%

Graph Update Failure

Disk >90%

Memory >90%

CPU >90%

---

Warning Alerts

Pending Queue Growing

RSS Delay

Slow API

High Latency

Large Error Rate

Recommendation Delay

---

====================================================
DASHBOARDS
====================================================

Dashboard 1

Infrastructure

CPU

RAM

Disk

Containers

---

Dashboard 2

Backend

Requests

Errors

Latency

Database

---

Dashboard 3

AI Pipeline

Articles

Embeddings

Matching

Voting

LLM Usage

Knowledge Score

---

Dashboard 4

Knowledge Graph

Nodes

Edges

Communities

Timeline Growth

Graph Updates

---

Dashboard 5

User Activity

Visitors

Popular Categories

Popular Events

Search Terms

API Usage

---

====================================================
QUEUE MONITORING
====================================================

Track

rss_fetch

clean_article

entity_extraction

embedding

matching

verification

timeline

graph

recommendation

publish

Metrics

Waiting

Running

Failed

Retrying

Completed

---

====================================================
ERROR TRACKING
====================================================

Capture

Unhandled Exceptions

API Errors

Worker Failures

AI Failures

Database Failures

Graph Failures

Frontend Errors

Every error includes

Stack Trace

Trace ID

Environment

Version

---

====================================================
HEALTH ENDPOINTS
====================================================

/health

Basic Status

---

/health/live

Liveness Probe

---

/health/ready

Readiness Probe

---

/health/dependencies

PostgreSQL

Neo4j

Redis

Qdrant

MinIO

Workers

---

====================================================
RETENTION
====================================================

Logs

30 Days

Metrics

90 Days

Traces

14 Days

Audit Logs

1 Year

---

====================================================
RECOMMENDED STACK
====================================================

Metrics

Prometheus

Visualisation

Grafana

Logs

Loki

Tracing

OpenTelemetry

Error Tracking

Sentry

Status Page

Uptime Kuma

---

====================================================
INCIDENT RESPONSE
====================================================

Detect

↓

Alert

↓

Investigate

↓

Mitigate

↓

Recover

↓

Postmortem

Every production incident should produce a documented postmortem.

---

====================================================
SERVICE LEVEL OBJECTIVES (SLOs)
====================================================

Frontend Availability

99.9%

Backend Availability

99.9%

RSS Processing Success

99%

Verification Success

99%

API Response Time

P95 < 300 ms

Graph Update

<5 sec

Fast AI Pipeline

<15 sec

Intelligence Pipeline

<60 sec

---

====================================================
DEFINITION OF HEALTHY SYSTEM
====================================================

✓ All services running

✓ Queue backlog within limits

✓ Database healthy

✓ AI pipeline operational

✓ Graph updates succeeding

✓ No critical alerts

✓ API latency within target

✓ Error rate below 1%

---

# Closing Statement

Monitoring is not optional.

Every service, model and workflow must expose measurable telemetry so that operational issues, AI regressions and infrastructure failures can be detected and resolved before they impact users.