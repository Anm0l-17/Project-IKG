# 06_System_Architecture.md

# India Knowledge Graph (IKG)

## System Architecture

Version: 1.0

Status: Draft

Owner: Chief Architect

Priority: CRITICAL

> **Architecture baseline:** This document must be read together with [23_Architecture_and_Ontology_Decisions.md](23_Architecture_and_Ontology_Decisions.md), which is the approved source of truth for the Domain → Topic → Story → Event ontology, evidence rules, lifecycle dimensions, relationship validation, V1 sources, and background processing. Where older text conflicts, the architecture baseline takes precedence.

---

# Purpose

This document defines the complete technical architecture of India Knowledge Graph (IKG).

It describes how information enters the platform, how it is processed into structured knowledge, how it is stored, and how it is delivered to users.

Unlike the Domain Model, which represents reality, this document represents the software system that implements that reality.

Every service, database, queue, AI model, worker, API and frontend component must conform to this architecture.

---

# Architectural Vision

IKG is not a news website.

IKG is an Event Intelligence Platform.

The platform continuously transforms fragmented information into verified, structured and interconnected knowledge.

The architecture therefore revolves around one core object:

EVENT

Everything else either creates, enriches, verifies or presents Events.

---

# High-Level Architecture

                     Users
                        │
            ┌─────────────────────┐
            │ Next.js Frontend    │
            └─────────────────────┘
                        │
                 API Gateway / BFF
                        │
        ┌─────────────────────────────────────┐
        │      Event Management Layer         │
        └─────────────────────────────────────┘
                        │
 ┌─────────────────────────────────────────────────────────────┐
 │                  Core Platform Engines                      │
 ├─────────────────────────────────────────────────────────────┤
 │ Discovery Engine                                            │
 │ Event Intelligence Engine                                   │
 │ Verification Engine                                         │
 │ Timeline Engine                                             │
 │ Knowledge Engine                                            │
 │ Search Engine                                               │
 │ Recommendation Engine                                       │
 │ Analytics Engine                                            │
 └─────────────────────────────────────────────────────────────┘
                        │
                Event Repository Layer
                        │
 ┌─────────────────────────────────────────────────────────────┐
 │ PostgreSQL                                                  │
 │ Neo4j                                                       │
 │ Redis                                                       │
 │ Vector Database                                              │
 │ Object Storage                                               │
 └─────────────────────────────────────────────────────────────┘
                        │
                Infrastructure Layer

---

# Approved Architecture Boundary

The platform implements the approved Domain → Topic → Story → Event ontology as a modular monolith. Articles, Claims, and Evidence are supporting records. V1 background execution uses Celery with Redis; graph writes occur only after ontology and evidence validation.
