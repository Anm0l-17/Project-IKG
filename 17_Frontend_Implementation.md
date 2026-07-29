# 17_Frontend_Implementation.md

# India Knowledge Graph (IKG)

## Frontend Implementation Guide

Version: 1.0

Status: Production Ready

Priority: CRITICAL

Owner: Frontend Team

---

# Purpose

This document defines the implementation architecture for the frontend.

The frontend is responsible for presenting verified knowledge in an intuitive, responsive and interactive interface.

It communicates exclusively with the Backend API.

No direct database access is permitted.

---

# Technology Stack

Framework
- Next.js 15 (App Router)

Language
- TypeScript

Styling
- Tailwind CSS

Component Library
- shadcn/ui

Icons
- Lucide React

State Management
- Zustand

Server State
- TanStack Query

Forms
- React Hook Form

Validation
- Zod

Graph Visualisation
- React Flow (v1)
- Cytoscape.js (future)
- D3.js (future)

Charts
- Recharts

Animations
- Framer Motion

Markdown Rendering
- react-markdown

Date Utilities
- date-fns

---

# Folder Structure

frontend/

    app/

        (public)/

            page.tsx

            feed/

            event/

            graph/

            timeline/

            search/

            category/

            about/

        api/

        globals.css

        layout.tsx

    components/

        common/

        dashboard/

        graph/

        timeline/

        search/

        cards/

        navigation/

        ui/

    hooks/

    lib/

    services/

    store/

    types/

    utils/

    constants/

    public/

---

# Routing

/

Homepage

/feed

Verified News Feed

/event/[id]

Event Details

/category/[slug]

Category Page

/graph

Knowledge Graph

/timeline

Timeline Explorer

/search

Search Results

/about

About IKG

---

# Global Layout

Navbar

↓

Main Content

↓

Footer

Persistent Components

Search

Theme

Notifications

User Menu (Future)

---

# Navigation Bar

Contains

Logo

Home

Categories

Graph

Timeline

Search

About

Responsive Menu

Mobile Drawer

---

# Homepage

Sections

1. Hero Banner

2. Today in India

3. Live Statistics

4. Latest Verified Events

5. Trending Events

6. Mini Knowledge Graph

7. Categories

8. Recent Timeline Updates

9. Footer

---

# Feed Page

Purpose

Display latest verified events.

Components

Filter Sidebar

Search

Sort

Event Cards

Pagination

Infinite Scroll

---

# Event Detail Page

Sections

Header

Summary

Timeline

Verification Panel

Knowledge Graph

Related Events

Sources

Share

Bookmark (Future)

---

# Category Page

Displays

Category Overview

Latest Events

Trending

Statistics

Related Categories

---

# Timeline Page

Interactive chronological view.

Supports

Date Filter

Category Filter

Search

Expand Event

---

# Graph Page

Purpose

Interactive exploration.

Features

Zoom

Pan

Expand Node

Collapse Node

Search Node

Highlight Relationships

Filter by Category

Filter by Entity Type

Depth Selection

---

# Search Page

Supports

Keyword Search

Semantic Search

Entity Search

Suggestions

Recent Searches

---

# Component Architecture

Common Components

Button

Input

Badge

Card

Modal

Tooltip

Skeleton

Loading Spinner

Empty State

---

Dashboard Components

Stats Card

Event Card

Category Card

Trend Card

Graph Preview

---

Graph Components

Graph Canvas

Node

Edge

Legend

Controls

Mini Map

Zoom Controls

Search Overlay

---

Timeline Components

Timeline Card

Timeline Item

Date Divider

Expand Button

---

Verification Components

Source Badge

Confidence Meter

Knowledge Score

Vote Indicator

Evidence List

---

# State Management

Global State

Theme

Sidebar

Search

Notifications

Graph Settings

User Preferences

Server State

Events

Graph

Timeline

Categories

Statistics

Recommendations

Managed using

TanStack Query

---

# API Layer

services/

feed.ts

event.ts

graph.ts

timeline.ts

search.ts

category.ts

stats.ts

recommendation.ts

Each file exports strongly typed API methods.

---

# Type Definitions

types/

event.ts

entity.ts

timeline.ts

graph.ts

api.ts

category.ts

user.ts

Never use "any".

---

# Error Handling

Global Error Boundary

404 Page

500 Page

Offline Mode

Retry Button

Skeleton Loading

Meaningful Messages

---

# Responsive Design

Desktop

Full Experience

Tablet

Collapsible Sidebar

Mobile

Bottom Navigation

Simplified Graph

Drawer Menu

---

# Accessibility

Keyboard Navigation

Screen Reader Support

Focus Indicators

ARIA Labels

Reduced Motion Support

WCAG AA Compliance

---

# Theme

Default

Light

Future

Dark Mode

System Theme

---

# Performance Targets

First Contentful Paint

<1.5 sec

Largest Contentful Paint

<2.5 sec

Interaction Delay

<100 ms

Graph FPS

60

Bundle Size

<300 KB (initial)

---

# Optimisation

Image Optimisation

Dynamic Imports

Code Splitting

Lazy Loading

API Caching

Prefetch Routes

Memoised Components

Virtualised Lists

---

# Testing

Unit Tests

Vitest

Component Tests

React Testing Library

End-to-End

Playwright

Coverage Target

>90%

---

# Coding Standards

Functional Components Only

Strict TypeScript

Reusable Components

No Inline Styles

No Business Logic in Components

Hooks for Shared Logic

Atomic Component Design

---

# Future Features

Authentication

Bookmarks

Collections

Notes

AI Chat Assistant

Graph Collaboration

Offline Reading

Mobile App

---

# Definition of Done

A frontend feature is complete only if:

✓ Responsive

✓ Accessible

✓ Typed

✓ Tested

✓ Documented

✓ Connected to API

✓ Performance Optimised

---

# Closing Statement

The frontend is designed as a modern, modular and highly interactive application that enables users to explore India's public affairs through verified events, timelines and an evolving knowledge graph.

Every interface should reduce complexity while increasing understanding.


# IMPORTANT
I would make one major architectural improvement before writing a single React component.

Adopt a Feature-Based Folder Structure

Instead of organising by file type:

components/
hooks/
services/

organise by feature:

src/

features/

    feed/

        components/
        hooks/
        services/
        types/

    event/

        components/
        hooks/
        services/

    graph/

        components/
        hooks/
        services/

shared/

    ui/
    lib/
    hooks/
    types/