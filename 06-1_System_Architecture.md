# 06_System_Architecture.md

# India Knowledge Graph (IKG)

## System Architecture

Version: 1.0

Status: Draft

Owner: Chief Architect

Priority: CRITICAL

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