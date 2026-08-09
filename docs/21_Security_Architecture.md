# 21_Security_Architecture.md

# India Knowledge Graph (IKG)

## Security Architecture

Version: 1.0

Status: Production Ready

Priority: CRITICAL

Owner: Security Team

> **Architecture baseline:** This document must be read together with [23_Architecture_and_Ontology_Decisions.md](23_Architecture_and_Ontology_Decisions.md), which is the approved source of truth for the Domain → Topic → Story → Event ontology, evidence rules, lifecycle dimensions, relationship validation, V1 sources, and background processing. Where older text conflicts, the architecture baseline takes precedence.

---

# Purpose

This document defines the complete security architecture for IKG.

Security objectives include:

- Infrastructure Security
- API Security
- AI Security
- Data Security
- User Security
- Operational Security

Every component must follow the principle of least privilege.

---

# Security Principles

1. Never Trust Input

2. Verify Everything

3. Least Privilege

4. Defense in Depth

5. Secure by Default

6. Audit Everything

---

====================================================
SYSTEM SECURITY
====================================================

Deployment

Docker Containers

↓

Private Docker Network

↓

Reverse Proxy

↓

HTTPS

↓

Backend

↓

Databases

Only ports 80 and 443 are publicly exposed.

---

====================================================
NETWORK SECURITY
====================================================

Frontend

↓

HTTPS

↓

Nginx

↓

Backend API

↓

Internal Services

Databases are never publicly accessible.

---

====================================================
AUTHENTICATION
====================================================

Public APIs

No Authentication

Internal APIs

API Key

Admin Dashboard

JWT Authentication

Future

OAuth2

Google Login

GitHub Login

---

====================================================
AUTHORIZATION
====================================================

Roles

Guest

Reader

Moderator

Administrator

System Worker

Permissions

Every endpoint validates permissions.

Never trust frontend role checks.

---

====================================================
API SECURITY
====================================================

Rate Limiting

Anonymous

60 requests/min

Authenticated

300 requests/min

Internal

Unlimited

---

Headers

Strict-Transport-Security

Content-Security-Policy

X-Frame-Options

X-Content-Type-Options

Referrer-Policy

---

Input Validation

Pydantic

Zod

Sanitise

Search

Filters

Pagination

Query Parameters

---

====================================================
DATABASE SECURITY
====================================================

PostgreSQL

Parameterized Queries

Connection Pooling

Encrypted Backups

No Raw SQL

---

Neo4j

Parameterized Cypher

Read/Write Separation

Role-based Access

---

Qdrant

Private Network Only

Authentication Enabled

---

Redis

Password Protected

Internal Access Only

---

====================================================
SECRET MANAGEMENT
====================================================

Secrets

API Keys

JWT Secret

Database Passwords

LLM Keys

Stored Only In

Environment Variables

Production

Secret Manager (Future)

Never commit secrets to Git.

---

====================================================
AI SECURITY
====================================================

LLMs cannot:

- Invent sources
- Modify verification
- Override votes
- Access secrets
- Execute code

Prompt Rules

JSON Output Only

No Chain-of-Thought Storage

Evidence Required

Temperature = 0

---

====================================================
DATA INTEGRITY
====================================================

Every Event stores:

Creation Time

Source Articles

Verification Status

Knowledge Score

Timeline History

Audit Trail

No destructive updates.

---

====================================================
AUDIT LOGGING
====================================================

Log

User Actions

Admin Actions

Verification Decisions

Graph Updates

Configuration Changes

AI Decisions

Every audit record includes:

Timestamp

Actor

Action

Affected Resource

Result

---

====================================================
FILE SECURITY
====================================================

Allowed Types

JSON

CSV

Images

Maximum Upload Size

10 MB

Virus Scan (Future)

Reject Executables

---

====================================================
DEPENDENCY SECURITY
====================================================

Every Pull Request

↓

Dependency Scan

↓

License Check

↓

Known Vulnerability Scan

↓

Merge

Tools

Dependabot

Trivy

GitHub Security

---

====================================================
CONTAINER SECURITY
====================================================

Non-root Containers

Minimal Base Images

Read-only File System (where possible)

Image Signing (Future)

Regular Image Updates

---

====================================================
LOG SECURITY
====================================================

Never Log

Passwords

JWT Tokens

API Keys

Environment Variables

Cookies

PII

---

====================================================
BACKUP SECURITY
====================================================

Encrypted

Versioned

Off-site Storage

Daily Verification

Monthly Restore Test

---

====================================================
SECURITY HEADERS
====================================================

Content Security Policy

Strict Transport Security

Frame Protection

MIME Protection

Referrer Policy

Permissions Policy

---

====================================================
ATTACK MITIGATION
====================================================

SQL Injection

Parameterized Queries

---

XSS

HTML Escaping

Content Security Policy

---

CSRF

CSRF Tokens (future)

SameSite Cookies

---

Brute Force

Rate Limiting

IP Blocking

---

DDoS

Reverse Proxy

CDN (Future)

---

====================================================
AI-SPECIFIC THREATS
====================================================

Prompt Injection

Mitigation

- Never pass external instructions directly to LLMs.
- Strip HTML and embedded prompts.
- Use structured prompts only.

---

Hallucination

Mitigation

- Evidence-first reasoning.
- JSON-only outputs.
- Human review for low-confidence cases.

---

Model Drift

Mitigation

- AI Regression Test Suite.
- Model Registry.
- Versioned prompts.

---

====================================================
MANUAL REVIEW SYSTEM
====================================================

Events requiring manual review:

- Confidence below threshold
- Conflicting source votes
- Graph merge conflicts
- AI decision disagreement
- Failed verification after retries

Manual review actions are audited.

---

====================================================
SECURITY MONITORING
====================================================

Monitor

Failed Logins

API Abuse

Queue Failures

Database Access

Admin Actions

Unexpected AI Output

Large Error Spikes

Alerts integrated with Monitoring Dashboard.

---

====================================================
INCIDENT RESPONSE
====================================================

Detect

↓

Contain

↓

Investigate

↓

Recover

↓

Postmortem

Every security incident receives a documented report.

---

====================================================
SECURITY TESTING
====================================================

Static Analysis

Dependency Scanning

Penetration Testing

OWASP Top 10

API Security Testing

AI Prompt Injection Tests

Regression Tests

---

====================================================
SECURITY CHECKLIST
====================================================

✓ HTTPS Enabled

✓ Secrets Protected

✓ Rate Limiting Enabled

✓ Parameterized Queries

✓ Input Validation

✓ CSP Configured

✓ Audit Logging Enabled

✓ AI Restrictions Enforced

✓ Backups Verified

✓ Monitoring Enabled

---

====================================================
DEFINITION OF SECURE RELEASE
====================================================

A release is secure only if:

- Security scans pass
- No critical vulnerabilities exist
- Secrets are verified
- Dependencies are up to date
- AI regression tests pass
- Manual review queue is empty

---

# Closing Statement

Security in IKG protects both infrastructure and knowledge.

The platform is designed to ensure that verified information cannot be silently altered, AI systems cannot bypass verification rules, and every important action is traceable through comprehensive audit logs.

Security controls must protect immutable evidence, canonical Article history, Article provenance, Claim attribution, relationship decision history, and taxonomy administration. AI-generated relationship proposals must not have direct graph-write privileges.
