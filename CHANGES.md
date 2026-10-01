# 📝 CHANGES & Architecture Decisions Log

## Overview
This document tracks all recent architecture updates, bug fixes, test improvements, and datastore alignment decisions made across the India Knowledge Graph (IKG) platform.

---

## 1. Datastore Alignment & Roadmap Strategy

In strict adherence to the project constitution and product roadmap:

### Roadmap Schedule
* **v0.1 (Current Baseline):**
  * **Structured Data & Core Relationships:** PostgreSQL is the single source of truth.
  * **Graph Model:** Persisted and queried in PostgreSQL via `EventRelationship`, `Domain`, `Topic`, `Story`, and `Event` tables.
  * **Embeddings & Search:** In-process dense vector generation (`all-MiniLM-L6-v2` / deterministic TF-IDF fallback) and hybrid ranking in Python.
  * **Neo4j / Qdrant:** **Not active** in the v0.1 runtime. `NEO4J_URI` and `QDRANT_URL` are marked optional/future in `config.py`. Docker Compose configures `neo4j` and `qdrant` under the `future-infra` profile so they do not start by default or consume system resources.
* **Beta 0.5 (Upcoming):**
  * PostgreSQL `pgvector` native indexing for vector retrieval. No external Qdrant dependency.
* **Release 1.0 (Future Projection):**
  * Native Neo4j projections for complex graph analytics and traversals.

---

## 2. Testing Profiles: SQLite vs. PostgreSQL

### Strategy Split
* **Fast Unit Tests (Default):**
  * Uses in-memory SQLite (`sqlite+aiosqlite:///:memory:`) for models, services, and API endpoints. Provides instant developer feedback without container overhead.
* **PostgreSQL / pgvector Integration Profile:**
  * Activated by configuring the `TEST_DATABASE_URL` environment variable:
    ```bash
    TEST_DATABASE_URL=postgresql+asyncpg://ikg_user:ikg_password@localhost:5432/ikg_test pytest backend/tests
    ```
  * Validates dialect parity, native JSON/vector storage, migrations, upserts, and indexes.
* **CI Integration:**
  * CI pipelines run both suites: the SQLite unit test suite for rapid pre-commit validation, and the PostgreSQL container test suite for full dialect regression protection.

---

## 3. Bug Fixes & Code Improvements

### Security & Infrastructure
* **[BUG-001] Strict Production CORS Policy:**
  * `main.py`: Locked down CORS. In production (`APP_ENV != "development"`), `settings.ALLOWED_ORIGINS` must be explicitly declared; missing origins trigger a `RuntimeError` rather than defaulting to `["*"]`.
* **[BUG-003] Stdlib Logging Interpolation:**
  * `middleware/security.py`: Fixed `logger.warning` to use standard `%s` formatting instead of structlog-style kwargs so IP and route arguments are properly logged.
* **[BUG-012] RFC 9562-Compliant UUIDv7:**
  * `models/base.py`: Corrected version and variant bit-packing masks (`0x7 << 76`, `0b10 << 62`).

### AI & Pipeline Accuracy
* **[BUG-011] NER Entity Type Mapping:**
  * `ai/ner.py`: Corrected spaCy `GPE` entity classification from `"Organization"` to `"Location"`.
* **[BUG-004] Verification Queue Expiry Window:**
  * `services/events/verification.py`: Scoped pending candidate event retrieval to `created_at >= NOW - 10 days` to prevent queue starvation.
* **Domain Classification Precision:**
  * `services/events/candidate_generation.py`: Added word-boundary matching (`\b{term}\b`) to eliminate false-positive substring classifications.
* **Graph Inference Fallback Score:**
  * `services/graph/engine.py`: Lowered semantic score threshold for fallback embedding models to ensure deterministic `CAUSES` link inference when CrossEncoder is unavailable.

### Database & Testing Isolation
* **[TEST-002] Background Task Session Injection:**
  * `workers/tasks.py`: Added `_get_db(ctx, db)` context manager across all background tasks (`task_ingest_rss`, `task_verification_consensus`, `task_infer_relationships`, `task_cluster_stories`, `task_backfill_embeddings`), allowing test runners to inject the active test session and prevent real PostgreSQL network dials during testing.
* **Router Prefix Cleanup:**
  * `api/v1/event.py`: Normalized ego-subgraph route from `/{id}/graph` to `/events/{id}/graph`.

### Test Suite Cleanliness & Deprecation Resolution
* **Resolved Circular Foreign Key Warnings:**
  * Added `use_alter=True, name="fk_events_canonical_article_id"` to the `canonical_article_id` column in `Event` (`models/event.py`), eliminating 40 SQLAlchemy circular dependency warnings on table drops across tests.
* **Modernized API Test Suite to `AsyncClient`:**
  * Replaced synchronous `TestClient` in `tests/test_api.py` with `httpx.AsyncClient` fixture, resolving event loop collisions and Starlette testclient deprecation warnings.
* **Test Verification Results:**
  * **66 of 66 tests passing with 0 errors and 0 warnings (100% clean).**
