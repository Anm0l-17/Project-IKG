# 18_Deployment_Architecture.md

# India Knowledge Graph (IKG)

## Deployment Architecture

Version: 1.0

Status: Production Ready

Priority: HIGH

Owner: DevOps Team

> **Architecture baseline:** This document must be read together with [23_Architecture_and_Ontology_Decisions.md](23_Architecture_and_Ontology_Decisions.md), which is the approved source of truth for the Domain → Topic → Story → Event ontology, evidence rules, lifecycle dimensions, relationship validation, V1 sources, and background processing. Where older text conflicts, the architecture baseline takes precedence.

---

# Purpose

This document defines the deployment architecture for IKG.

It covers:

- Local Development
- Staging
- Production
- Containerisation
- CI/CD
- Infrastructure
- Monitoring
- Backups
- Scaling

The deployment process must be reproducible and automated.

---

# Infrastructure Overview

                    Internet
                        │
                        ▼
                Reverse Proxy (Nginx)
                        │
          ┌─────────────┴─────────────┐
          │                           │
          ▼                           ▼
      Next.js Frontend          FastAPI Backend
                                          │
                ┌─────────────────────────┴────────────────────────┐
                │               │              │                   │
                ▼               ▼              ▼                   ▼
          PostgreSQL        Redis         Neo4j              Qdrant
                │
                ▼
             MinIO
                │
                ▼
           Background Workers

---

# Deployment Environments

Development

Purpose

Local development

Characteristics

- Docker Compose
- Debug logging
- Hot reload
- Test databases

---

Staging

Purpose

Internal testing

Characteristics

- Production-like environment
- Automatic deployment
- Test data
- Monitoring enabled

---

Production

Purpose

Public deployment

Characteristics

- HTTPS
- Autoscaling (future)
- Monitoring
- Daily backups
- Security hardening

---

# Container Architecture

Services

frontend

backend

worker

scheduler

postgres

neo4j

qdrant

redis

minio

nginx

Each service runs in its own container.

---

# Docker Compose

docker-compose.yml

Contains

Frontend

Backend

Redis

PostgreSQL

Neo4j

Qdrant

MinIO

Workers

Scheduler

Networks

Volumes

---

# Networking

Internal Docker Network

All backend services communicate privately.

Only exposed ports

80

443

No database should be publicly accessible.

---

# Persistent Storage

PostgreSQL

Named Volume

Neo4j

Named Volume

MinIO

Named Volume

Redis

Optional persistence

Backups stored externally.

---

# Environment Variables

Frontend

NEXT_PUBLIC_API_URL

Backend

DATABASE_URL

REDIS_URL

NEO4J_URI

QDRANT_URL

MINIO_ENDPOINT

OPENAI_API_KEY

HF_API_KEY

JWT_SECRET

LOG_LEVEL

APP_ENV

No secrets committed to Git.

---

# CI/CD Pipeline

Trigger

Push to main

↓

Lint

↓

Type Check

↓

Unit Tests

↓

Integration Tests

↓

Docker Build

↓

Security Scan

↓

Deploy to Staging

↓

Manual Approval

↓

Deploy to Production

---

# Git Strategy

main

Production-ready

develop

Integration branch

feature/*

New features

hotfix/*

Emergency fixes

release/*

Release preparation

---

# Reverse Proxy

Nginx Responsibilities

HTTPS termination

Compression

Static asset caching

API routing

Rate limiting

Security headers

---

# SSL

Provider

Let's Encrypt

Renewal

Automatic

TLS Version

1.3

HTTPS enforced.

---

# Monitoring

Metrics

CPU

Memory

Disk

Container Health

API Latency

Worker Queue Size

Database Connections

Graph Update Time

LLM Usage

---

# Logging

Application Logs

Structured JSON

Request Logs

Worker Logs

System Logs

Retention

30 Days

---

# Health Checks

Frontend

/

Backend

/health

Redis

PING

PostgreSQL

Connection Test

Neo4j

Cypher Query

Qdrant

Health Endpoint

Workers

Heartbeat

---

# Backup Strategy

PostgreSQL

Daily

Neo4j

Daily

MinIO

Weekly

Configuration

Git Repository

Backup Verification

Monthly restore test

---

# Disaster Recovery

Failure

↓

Alert

↓

Restore Backup

↓

Validate Services

↓

Resume Traffic

Recovery Point Objective (RPO)

24 Hours

Recovery Time Objective (RTO)

2 Hours

---

# Security

HTTPS only

Firewall enabled

Database not publicly exposed

Environment variables encrypted

Container images scanned

Least privilege access

---

# Scaling Strategy

Current

Single Server

Phase 2

Dedicated Database Server

Phase 3

Separate AI Workers

Phase 4

Kubernetes

Horizontal scaling supported.

---

# Recommended Hosting

Frontend

Vercel

Backend

Railway / Hetzner VPS

Databases

Self-hosted Docker

Future

AWS / GCP / Azure

---

# Release Checklist

✓ Tests passing

✓ Docker builds

✓ Migrations complete

✓ Environment variables verified

✓ Backups completed

✓ Monitoring active

✓ Health checks green

✓ Documentation updated

---

# Definition of Production Ready

The platform is production-ready only if:

- All services healthy
- HTTPS enabled
- Monitoring operational
- Backups configured
- CI/CD passing
- Security review completed
- Documentation up to date

---

# Closing Statement

The deployment architecture is designed to support local development, continuous delivery and future horizontal scaling while maintaining operational simplicity during the initial release.

V1 deployment includes Celery workers and Celery Beat backed by Redis for ingestion, matching, verification, summarization, and scheduled rechecks. PostgreSQL remains the structured source of truth and Neo4j a validated graph projection.
