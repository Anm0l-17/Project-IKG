Philosophy

Everything entering IKG is

INFORMATION

Everything leaving IKG is

KNOWLEDGE

Everything in between

↓

Knowledge Refinery

The Pipeline
                    INFORMATION

                          │

                          ▼

              Discovery & Collection

                          │

                          ▼

                Cleaning & Normalisation

                          │

                          ▼

                  Event Candidate Creation

                          │

                          ▼

                  Entity Extraction (NER)

                          │

                          ▼

              Event Classification

                          │

                          ▼

             Semantic Embedding Generation

                          │

                          ▼

          Candidate Event Retrieval (Vector Search)

                          │

                          ▼

          Cross Encoder Similarity Ranking

                          │

                          ▼

           LLM Event Reasoning & Decision

                          │

                SAME / FOLLOW-UP /
             RELATED / NEW / DIFFERENT

                          │

                          ▼

              Majority Verification Engine

                          │

             Pending Queue (if required)

                          │

                          ▼

                 Timeline Construction

                          │

                          ▼

              Knowledge Graph Update

                          │

                          ▼

                 Search Index Update

                          │

                          ▼

              Recommendation Update

                          │

                          ▼

              Knowledge Score Calculation

                          │

                          ▼

                    VERIFIED EVENT

                          │

                          ▼

                     USER FEED
This is the biggest improvement I'd make.

Instead of

Verification

↓

Graph

I would insert

Knowledge Score

Every Event receives

Trust Score
Freshness Score
Context Score
Relationship Score
Completeness Score

Then combine them into

Knowledge Score

Example

Trust

40%

Freshness

20%

Context

15%

Relationships

15%

Completeness

10%

↓

Knowledge Score

91/100

This becomes useful later for ranking search results and recommendations.

Stage 1 — Discovery

Sources

RSS
Future APIs
PDFs
PIB
Gazette
Parliament
RBI
Press Releases

Output

Raw Article
Stage 2 — Normalisation

Removes

HTML
Ads
Tracking links
Duplicated whitespace
Boilerplate

Extracts

Headline
Date
Author
Body
Images
Stage 3 — Event Candidate Creation

Everything becomes

Candidate Event

Notice

NOT

News
Stage 4 — Entity Extraction

Example

India signs logistics agreement with France.

Extract

India

France

Agreement

Defence

Indian Navy

These become reusable graph nodes.

Stage 5 — Classification

Domain

↓

Defence

Subdomain

↓

International Cooperation

Tags

↓

France

Indian Navy

Strategic Partnership

Stage 6 — Embeddings

Sentence Transformer

↓

768-dimensional vector

↓

Stored in Qdrant

No LLM required.

Very fast.

Stage 7 — Candidate Retrieval

Instead of comparing against every Event,

retrieve only the Top-20 semantically similar candidates.

This reduces complexity from approximately:

1,000,000 comparisons

↓

20 comparisons

This optimisation is what makes the system scalable.

Stage 8 — Cross Encoder

Take the Top-20 candidates.

Run a stronger similarity model.

Return the Top-3 most likely matches.

Stage 9 — LLM Reasoning

This is where intelligence happens.

The LLM does not search.

It decides.

Prompt

Event A

Event B

Entities

Timeline

Publication dates

Determine

Same?

Follow-up?

Related?

Different?

Explain your reasoning.

Output

FOLLOW_UP

Confidence

0.93

Reason

Both describe the same policy at different stages.
Stage 10 — Verification

This is your original idea, improved.

Every publication gets one vote only after successful Event Matching.

Example

GKToday

↓

Event Match

↓

Vote

✓

No match?

No vote.

This prevents unrelated articles from influencing verification.

Stage 11 — Pending Queue

If only one trusted source reports an Event,

place it in a 10-day verification queue.

A scheduled worker revisits pending Events daily.

If another trusted source matches the same Event within the window, verification proceeds automatically.

Stage 12 — Timeline Engine

If the Event already exists,

append the new development to its timeline.

Do not create a duplicate Event.

Stage 13 — Knowledge Graph

Create or update:

Event node
Entity nodes
Relationships
Clusters
Stage 14 — Search

Update:

PostgreSQL indexes
Qdrant embeddings
Neo4j traversal metadata

The Event is now searchable immediately.

Stage 15 — Recommendations

Generate:

Related Events
Connected Policies
Same Ministry
Same Companies
Same Countries
Future Follow-ups
Stage 16 — Knowledge Score

Compute a composite score.

Metric	Weight
Verification Confidence	40%
Evidence Count	20%
Timeline Completeness	15%
Relationship Density	15%
Freshness	10%

The score is recalculated whenever new evidence arrives.

Stage 17 — Publication

Only now does the Event become visible in:

News Feed
Dashboard
Graph View
Search
API

The user never sees an Event in an intermediate processing state unless they are using an internal moderation interface.

A new concept I'd introduce: Event DNA

Every Event carries a compact "fingerprint" that represents its identity over time.

Instead of identifying an Event only by title or embedding, define an internal structure such as:

Event DNA

• Canonical Title
• Primary Entities
• Category
• Initial Discovery Date
• Stable Event ID
• Embedding Signature
• Timeline Length
• Verification History

The Event DNA evolves as new information arrives, but the Stable Event ID never changes.

This makes merging, deduplication and long-term tracking far more reliable than relying on article text alone.

Pipeline Design Principles

Every stage must:

Accept well-defined input.
Produce well-defined output.
Be independently testable.
Be retryable without side effects (idempotent where possible).
Emit audit logs.
Publish domain events for downstream modules.

No stage should assume knowledge about future stages.