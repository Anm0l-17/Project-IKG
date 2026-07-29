# AGENTS.md

# India Knowledge Graph (IKG)

## AI Development Constitution

Version: 1.0

Status: Active

Author: Product Management Office

---

# Purpose

This repository is designed to be developed by both humans and AI coding agents.

Every contributor MUST follow this document before modifying any file.

Failure to follow these rules may introduce architectural inconsistencies.

This document overrides implementation preferences.

---

# Mission Statement

The mission of this repository is not to build another news website.

The mission is to build India's most reliable AI-powered Event Intelligence Platform.

Every engineering decision must improve one or more of the following:

- Trust
- Context
- Knowledge Discovery
- User Understanding
- Maintainability

If a proposed feature does not improve one of these goals,
it should not be implemented.

---

# Golden Rule

Events are first-class citizens.

Articles are evidence.

Never design any feature that treats articles as the primary object.

Everything revolves around Events.

---

# Before Writing Code

Every AI MUST complete this checklist.

## Step 1

Read

README.md

---

## Step 2

Read every document inside

/docs

that is relevant to the task.

---

## Step 3

Summarise your understanding.

---

## Step 4

List assumptions.

---

## Step 5

List ambiguities.

---

## Step 6

Ask questions.

If ambiguity exists,

STOP.

Wait for clarification.

Never guess.

---

## Step 7

Only after approval

begin implementation.

---

# Mandatory Development Loop

Understand

↓

Research

↓

Design

↓

Review

↓

Ask Questions

↓

Wait

↓

Implement

↓

Self Review

↓

Testing

↓

Generate Report

↓

Stop

Never skip a stage.

---

# Self Review

Every implementation must answer

Did I violate architecture?

Did I duplicate logic?

Can this be simplified?

Did I break APIs?

Is documentation updated?

Can another developer understand this?

---

# Project Philosophy

The project follows

Documentation First Development.

Documentation

↓

Architecture

↓

Implementation

↓

Testing

↓

Deployment

Never reverse this order.

---

# Architecture Principles

## Single Responsibility

Every module has one responsibility.

Example

RSS Fetcher

does NOT

perform AI.

AI

does NOT

perform database writes.

Graph Engine

does NOT

perform verification.

Every module owns one problem.

---

## Event First

Bad

Article

↓

Timeline

Good

Event

↓

Timeline

↓

Articles

---

## AI as Decision Support

AI never decides alone.

Every important decision should be explainable.

Confidence values should always be available.

---

## Human Readability

Readable code

>

Short code

Always optimise for maintainability.

---

# Coding Standards

Use

Python

FastAPI

Type Hints

Pydantic

Docstrings

Meaningful names

Never abbreviate variable names.

Bad

evt

Good

event

---

# API Rules

Every endpoint

must

have

- request schema

- response schema

- validation

- error handling

- documentation

No exceptions.

---

# UI Philosophy

Never impress.

Always communicate.

Animations must improve understanding.

Not decoration.

Avoid clutter.

Avoid unnecessary gradients.

Avoid dashboard syndrome.

Whitespace is good.

---

# Accessibility

Support

Keyboard navigation

Colour contrast

Reduced motion

Responsive layout

Readable typography

Accessibility is mandatory.

---

# AI Rules

Use AI only when deterministic algorithms are insufficient.

Preferred order

Rules

↓

NLP

↓

Embeddings

↓

Cross Encoder

↓

LLM

LLM is always the last option.

---

# Performance Rules

Never call an LLM

inside

user interaction.

All expensive work

must happen

offline.

---

# Database Rules

PostgreSQL

owns

structured data.

Neo4j

owns

relationships.

Vector Database

owns

embeddings.

Never mix responsibilities.

---

# Git Rules

One feature

=

One branch

One PR

One review

One merge

---

# Documentation Rules

Every feature

must update

documentation.

Documentation debt

is forbidden.

---

# Testing Rules

Every feature

must include

Unit Test

Integration Test

Edge Cases

Failure Cases

Performance Considerations

---

# Logging

Every background worker

must produce logs.

Every AI decision

must produce reasoning.

Every verification

must produce evidence.

---

# Error Handling

Never silently fail.

Every failure

must

- log

- explain

- recover

when possible.

---

# Security

Never trust user input.

Always validate.

Never expose secrets.

Never hardcode credentials.

---

# Dependencies

Before adding a dependency

ask

Do we already have something
that solves this?

Prefer fewer dependencies.

---

# Forbidden Behaviours

Do NOT

Rename APIs

Change database schema

Replace frameworks

Rewrite architecture

Remove documentation

without approval.

---

# Definition of Done

A task is complete only if

Implementation

Tests

Documentation

Review

Pass

A feature without documentation

is incomplete.

---

# Final Rule

If you are uncertain,

do not invent.

Ask.

The quality of this project depends on disciplined engineering,
not speed.
