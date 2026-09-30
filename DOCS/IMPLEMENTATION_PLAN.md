# Google Photos AI Discovery Engine — Comprehensive Implementation Plan

## Executive Overview
This implementation plan outlines the end-to-end roadmap for the **Google Photos Core Experience** AI Discovery Engine. It guides the project from multi-platform data harvesting and LLM information extraction to primary user research, cognitive failure point mapping, semantic RAG query engine deployment, and executive presentation ahead of the **October 7, 2026** deadline.

---

## Roadmap Timeline & Milestone Overview

```
[Phase 1: Multi-Platform Ingestion] ──► [Phase 2: Quantification & Dashboard] ──► [Phase 3: User Research & Problem Def]
              Week 1                                    Week 1 - 2                                    Week 2
                                                                                                        │
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┘
│
▼
[Phase 4: Semantic RAG Intelligence] ──► [Phase 5: PM Validation & Grounding] ──► [Phase 6: Executive Deck & Reporting]
              Week 2 - 3                                  Week 3                                     Week 3 - 4
```

---

## Phase 1: AI Discovery Engine Setup & Multi-Platform Ingestion
**Objective:** Ingest, clean, and verify authentic voice-of-customer reviews and technical discussions across 5 independent platforms, strictly isolating visual search retrieval experiences.

### Tasks & Deliverables:
1. **Multi-Source Scraping & Harvesting:**
   * Ingested from 5 primary channels:
     * **Google Play Store:** 969 Reviews (Android mass consumer feedback across 10 locales).
     * **Hacker News:** 455 Discussions (Technical critiques of vector embeddings and semantic search).
     * **Apple App Store:** 111 Reviews (iOS search experience and tab navigation).
     * **Reddit:** 54 Discussions (Power user troubleshooting in r/googlephotos and r/GooglePixel).
     * **YouTube:** 27 Critiques (Video teardowns and Ask Photos walkthrough transcripts).
   * **Total Search-Only Corpus:** **1,616 In-Scope Documents**.
2. **Noise & Out-of-Scope Segregation:**
   * Non-search complaints (cloud backup stalls, sync deletion loops, battery drain, subscription paywalls, and tab redesign gripes) were strictly excluded from the active retrieval corpus.
3. **100% Verbatim Quote Grounding:**
   * Enforce character-exact substring matching (`INSTR > 0`) on every evidence quote stored in `data/db.sqlite`.

### Milestone Gate:
- [x] Database contains 1,616 cleaned, verified search retrieval documents across 5 platforms.
- [x] 100.0% of evidence quotes verified as exact substrings in raw source texts.

---

## Phase 2: Metrics Quantification, Cognitive Breakdown Taxonomy & Interactive Dashboard
**Objective:** Quantify the failure points of fuzzy memory retrieval, structure the findings into four cognitive breakdown moments, and deploy the interactive product management dashboard.

### Tasks & Deliverables:
1. **Four Cognitive Retrieval Breakdown Stages:**
   * **Expression Stage (59.0% · 953 mentions):** Users struggle to articulate vague memories into keywords or exact calendar dates.
   * **Interpretation Stage (38.9% · 628 mentions):** Search engine misunderstands queries, fails on synonyms, or generates irrelevant hallucinations.
   * **Recovery Stage (1.6% · 26 mentions):** Zero dynamic suggestions or refinement chips when search yields no hits, forcing endless chronological timeline scrolling.
   * **Evaluation Stage (0.6% · 9 mentions):** Difficulty identifying target pictures in cluttered result grids.
2. **Interactive Next.js PM Dashboard:**
   * Real-time KPI cards with dynamic sparklines and calibrated confidence scores.
   * 10 deep-dive strategic PM inquiry views (`/questions/1` through `/questions/10`).
   * Systemic gap visualizations with toggle between Cognitive Breakdown Stages and Systemic Failure Vectors.

### Milestone Gate:
- [x] Production Next.js dashboard deployed with instant sub-100ms transitions and zero hydration warnings.
- [x] All charts, metrics, and KPI cards synchronized to the 1,616 search corpus.

---

## Phase 3: Qualitative User Research & Problem Definition
**Objective:** Ground the quantitative pipeline findings in primary user research, unpack mental recall models, and define the core problem statement.

### Tasks & Deliverables:
1. **In-Depth User Research Protocol (`DOCS/USER_RESEARCH_GUIDE.md`):**
   * Semi-structured interview protocol with 5–6 participants across 3 archetypes: Memory Custodians, Visual Utility Searchers, and Social Capturers.
   * Think-aloud live retrieval exercises measuring time-to-scroll, search reformulation count, and abandonment behavior.
2. **Target Persona & Core Problem Definition (`DOCS/PROBLEM_DEFINITION.md`):**
   * Detailed persona (*Elena, 34, Working Parent & Family Archivist*).
   * 4-pillar root cause analysis demonstrating why lexical matching fails episodic human memory.

### Milestone Gate:
- [x] Qualitative interview guide and participant screener criteria established.
- [x] Problem definition approved and aligned with assignment objectives.

---

## Phase 4: Grounded Semantic RAG Engine & Natural Language Query System
**Objective:** Engineer a high-precision Retrieval-Augmented Generation (RAG) query service that empowers product managers to interrogate the customer corpus in plain English.

### Tasks & Deliverables:
1. **FastAPI Semantic Backend (`pipeline/rag/`):**
   * TF-IDF vectorization and cosine similarity retrieval across 1,616 customer reviews.
   * Gemini 3.1 Flash Lite synthesis with automatic Groq fallback for high availability.
   * Strict grounding prompt enforcing that every assertion cites real customer quotes.
2. **Interactive Ask Engine UI (`/ask`):**
   * Natural language query interface with real-time streaming, clickable quote citations, and source platform badges.

### Milestone Gate:
- [x] RAG server running with sub-2ms vector retrieval and verifiable quote grounding.
- [x] Zero-downtime offline fallback integrated into Next.js API route (`/api/ask`).

---

## Phase 5: PM Usability Testing & Discovery Engine Grounding Validation
**Objective:** Validate the Discovery Engine with product management stakeholders, measure query faithfulness, and ensure zero hallucination.

### Tasks & Deliverables:
1. **Grounding & Faithfulness Verification:**
   * Automated verification that 100% of generated responses trace to authentic review quotes.
   * Calibrated confidence scores with standard deviation metrics.
2. **Benchmarking & Latency Audits (`scripts/run_benchmarks.py`):**
   * Validate vector retrieval speed, citation accuracy, and corpus integrity across 50 benchmark queries.

### Milestone Gate:
- [x] 100.0% quote verifiability across all 10 strategic discovery question datasets.
- [x] End-to-end benchmark suite passing with zero regressions.

---

## Phase 6: Success Metrics, Risk Analysis & 10-Slide Executive Presentation
**Objective:** Formulate the metric decomposition framework, analyze technical and operational risks, and produce the final competition slide deck.

### Tasks & Deliverables:
1. **Metric Decomposition & Funnel Formula (`DOCS/BUSINESS_METRIC_DECOMPOSITION.md`):**
   * Mathematical breakdown of search retrieval success into 4 operational drop-off gates.
   * Metric hierarchy: North Star, Leading Behavioral Metrics, and Guardrail Benchmarks.
2. **Executive 10-Slide Deck (`NL_GooglePhotos.pdf` & `DOCS/SLIDE_DECK_BLUEPRINT.md`):**
   * Slide 1: Executive Title & Strategic Mandate (100% Fellow Anonymity).
   * Slide 2: Business Metric Decomposition & Mathematical Formula.
   * Slide 3: AI Discovery Engine Architecture & Ingestion Pipeline.
   * Slide 4: Multi-Platform Empirical Findings & 1,616 Review Corpus.
   * Slide 5: User Research Validation & Think-Aloud Behaviors.
   * Slide 6: Problem Definition, Persona & 4 Cognitive Breakdown Stages.
   * Slide 7: AI-Native Architectural Solutions & Cognitive Anchors.
   * Slide 8: Interactive Discovery Engine Dashboard & Intelligence Architecture.
   * Slide 9: Grounded RAG Validation, PM Usability & Verifiable Insights.
   * Slide 10: Success Metrics Hierarchy, Risk Mitigations & Product Roadmap.

### Milestone Gate:
- [x] Exactly 10 slides, 16:9 widescreen canvas, font size $\ge 14\text{ pt}$, under 40 MB.
- [x] Clickable links to deployed Discovery Engine and documentation hub.

---

## Phase Tracking & Status Summary

| Phase | Description | Deliverable / Output | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Multi-Platform Ingestion | Database of 1,616 search-specific reviews across 5 platforms | ✅ Completed |
| **Phase 2** | Quantification & Dashboard | Interactive Next.js Dashboard, 4 Cognitive Stages, 19 JSON exports | ✅ Completed |
| **Phase 3** | User Research & Problem Def | User Research Guide (`DOCS/USER_RESEARCH_GUIDE.md`), Persona Spec | ✅ Completed |
| **Phase 4** | Semantic RAG Intelligence | FastAPI Query Server, Gemini synthesis, grounded quote citations | ✅ Completed |
| **Phase 5** | PM Validation & Grounding | Certified Audit (`DOCS/DATA_VERIFICATION_REPORT.md`), Benchmarks | ✅ Completed |
| **Phase 6** | Executive Deck & Reporting | 10-Slide Executive Deck (`NL_GooglePhotos.pdf`), Metric Framework | ✅ Completed |
