# 10_Product_Experience_and_Frontend_Architecture.md

# India Knowledge Graph (IKG)

## Product Experience & Frontend Architecture

Version: 1.0

Status: Draft

Priority: CRITICAL

Owner: Product & Frontend Team

> **Architecture baseline:** This document must be read together with [23_Architecture_and_Ontology_Decisions.md](23_Architecture_and_Ontology_Decisions.md), which is the approved source of truth for the Domain → Topic → Story → Event ontology, evidence rules, lifecycle dimensions, relationship validation, V1 sources, and background processing. Where older text conflicts, the architecture baseline takes precedence.

---

# Vision

IKG is not designed to maximise clicks.

It is designed to maximise understanding.

Every interface should reduce cognitive load while revealing relationships between events.

The interface should feel closer to a knowledge workspace than a traditional news portal.

---

# Product Design Principles

1. Knowledge before headlines.
2. Context before chronology.
3. Verification before publication.
4. Exploration before endless scrolling.
5. Simplicity over visual clutter.
6. Explainability over mystery.
7. Progressive disclosure—show more detail only when requested.

---

# Information Hierarchy

The interface exposes information in four layers.

Layer 1: Dashboard

↓

Layer 2: Feed

↓

Layer 3: Event

↓

Layer 4: Knowledge Graph

Users move naturally from overview to detail.

---

# Primary Navigation

- Home
- Explore
- Categories
- Search
- Knowledge Graph
- Timeline
- About

Future:

- Workspace
- Saved Events
- Compare
- AI Assistant

---

# Home Page

Purpose

Provide a daily overview of India.

Sections

1. Today in India
2. Live Knowledge Graph
3. Latest Verified Events
4. Category Overview
5. Trending Timelines
6. Recommended Reading Paths

---

## Today in India

Displays high-level statistics.

Example

Verified Events Today

New Follow-ups

Parliament Activity

Economic Developments

Defence Updates

Average Knowledge Score

These are summaries, not headlines.

---

## Live Knowledge Graph

Purpose

Provide an immediate visual impression of connected knowledge.

Features

- Force-directed graph
- Animated node expansion
- Colour-coded categories
- Hover tooltips
- Click to explore
- Zoom and pan
- Cluster highlighting

Nodes

Events

Entities

Policies

Countries

Edges

Relationships

The graph should remain readable even with hundreds of nodes.

---

## Latest Verified Events

Cards display

- Event title
- Category
- Verification status
- Knowledge Score
- Timeline progress
- Last updated
- Related event count
- Trusted sources

Cards prioritise clarity over density.

---

## Categories

Version 1

- Indian Current Affairs
- Parliament
- Geopolitics
- Economics
- Trade
- Defence

Future categories can be added without redesign.

---

# Event Detail Page

The Event page is the core experience.

Sections

1. Overview
2. Summary
3. Timeline
4. Verification
5. Connected Entities
6. Knowledge Graph
7. Related Events
8. Sources
9. AI Explanation

---

## Event Header

Contains

Title

Category

Verification Badge

Knowledge Score

Last Updated

Timeline Status

Bookmark

Share

---

## AI Summary

A concise explanation generated after verification.

The summary should explain:

- What happened?
- Why it matters?
- Who is affected?
- What comes next?

---

## Timeline View

Interactive vertical timeline.

Each update shows

Date

Description

Evidence

Source

Impact

Users can expand individual timeline entries.

---

## Verification Panel

Displays

Votes

Participating sources

Confidence

Evidence count

Reason for verification

The goal is transparency.

---

## Knowledge Graph Panel

Displays nearby nodes only.

Controls

Depth selector

Relationship filter

Category filter

Search within graph

Double-click expands the graph.

---

## Related Events

Ranked using

- Semantic similarity
- Shared entities
- Timeline proximity
- Graph distance

---

## Source Panel

Lists trusted publications supporting the Event.

Each source links to the original article.

The platform clearly distinguishes:

Original reporting

↓

IKG knowledge representation

---

# Search Experience

Supports

- Keyword search
- Semantic search
- Entity search
- Timeline search

Results grouped by type.

---

# Visual Language

Primary colours

Neutral background

Single accent colour

Minimal gradients

High contrast

Generous whitespace

Typography should favour readability over decoration.

---

# Responsive Design

Desktop

Primary experience.

Tablet

Graph collapses into panels.

Mobile

Timeline first.

Graph opens full screen.

---

# Accessibility

WCAG AA compliant.

Keyboard navigation.

Screen reader support.

High-contrast mode.

Reduced motion mode.

---

# Performance Targets

Initial page load

<2 seconds

Navigation

<200 ms

Search suggestions

<100 ms

Graph interaction

60 FPS target

---

# Frontend Stack

- Next.js
- React
- TypeScript
- Tailwind CSS
- React Query
- Zustand
- React Flow / Cytoscape.js (graph)
- Framer Motion (subtle animations)
- D3.js (advanced graph layouts if needed)

---

# State Management

Server state

React Query

Client state

Zustand

Avoid unnecessary global state.

---

# Error Handling

Graceful loading states.

Skeleton screens.

Retry actions.

Meaningful error messages.

Never expose internal failures.

---

# Closing Statement

The frontend exists to transform structured knowledge into human understanding.

Every interaction should answer not only "What happened?" but also "How does it connect?" and "Why does it matter?"

The primary exploration path is Domain → Topic → Story → Event. Story Timelines contain Events; Articles and Claims appear as supporting evidence under the relevant Event. Relationship explanations must show evidence, confidence, status, and reason.
