# Google Photos AI Discovery Engine — Phase-Wise Implementation Plan

## Executive Overview
This implementation plan outlines the end-to-end roadmap for the **Google Photos Core Experience** project. It guides the project from raw data ingestion and AI classification to primary user research, functional AI-native MVP deployment, and final executive slide deck submission ahead of the **October 7, 2026** deadline.

---

## Roadmap Timeline & Milestone Overview

```
[Phase 1: Engine Foundation] ──► [Phase 2: Quantification & Metric Funnel] ──► [Phase 3: User Research & Problem Def]
          Week 1                               Week 1 - 2                                    Week 2
                                                                                               │
┌──────────────────────────────────────────────────────────────────────────────────────────────┘
│
▼
[Phase 4: AI-Native MVP Build] ──► [Phase 5: User Testing & Telemetry] ──► [Phase 6: Deck & Deliverables]
          Week 2 - 3                                Week 3                                  Week 3 - 4
```

---

## Phase 1: AI Discovery Engine Setup & Data Ingestion (Part 1 of Brief)
**Objective:** Stand up the ingestion pipeline, configure data scrapers, clean reviews, and execute LLM batch classification.

### Tasks & Deliverables:
1. **Engine Compilation:**
   * Run `python setup_engine.py` to compile `discovery_config.yaml` into pipeline scrapers, prompts, schemas, and dashboard constants.
   * Verify generated files in `pipeline/classification/` and `dashboard/lib/constants.ts`.
2. **Environment & Keys Configuration:**
   * Configure `.env` with Gemini API key (primary classifier), Groq key (fallback), YouTube API key, and Reddit/Apify tokens.
3. **Database Initialization & Scraping:**
   * Initialize SQLite database (`python run_pipeline.py --mode init-db`).
   * Run multi-source crawlers (`python run_pipeline.py --mode scrape --limit 200` per source):
     * Google Play Store (`com.google.android.apps.photos`)
     * Apple App Store (`962194608`)
     * Reddit (`r/googlephotos`, `r/GooglePixel`, `r/techsupport`, `r/iphone`, `r/degoogle`)
     * YouTube Comments & Google Support threads.
4. **Cleaning & Relevance Filtering:**
   * Run `python run_pipeline.py --mode clean` to strip bot spam and filter by the 37 Google Photos domain keywords.
5. **LLM Batch Classification:**
   * Run `python run_pipeline.py --mode classify` to tag records with:
     * 21 retrieval friction tags (e.g., `forgot_exact_date`, `query_too_literal`, `endless_scrolling_fatigue`, `screenshot_and_junk_clutter`, `face_recognition_misidentification`).
     * Intent categories, segment signals, factor mentions, and verbatim unmet need quotes.

### Milestone Gate:
- [ ] Database contains at least 500+ cleaned and classified real user reviews/comments.
- [ ] Classification outputs pass schema validation with evidence quotes preserved.

---

## Phase 2: Metrics Quantification & Interactive Dashboard (Part 1 & 2)
**Objective:** Transform unstructured LLM classifications into statistical distributions, deploy the interactive PM dashboard, and decompose the business metric.

### Tasks & Deliverables:
1. **Aggregations & JSON Export:**
   * Run `python run_pipeline.py --mode export` to compute:
     * Friction tag frequency and impact scores ($$\text{Impact} = \text{Freq} \times \text{Confidence} \times \text{Severity}$$).
     * Platform cross-tabulation (Android vs. iOS complaints).
     * Temporal trend lines across app versions.
2. **Launch Interactive Next.js Dashboard:**
   * Build & run the Next.js decision frontend (`cd dashboard && npm run dev`).
   * Verify all 10 discovery question tabs, KPI cards, Sankey user flow diagrams, and the quote viewer.
3. **Launch RAG Semantic Search Service:**
   * Spin up FastAPI vector engine (`python run_pipeline.py --mode rag-server`).
   * Test natural language PM queries (e.g. *"Why do users give up searching for medicine bottles vs. vacation trips?"*).
4. **Business Metric Mathematical Decomposition (Part 2):**
   * Formulate the mathematical equation decomposing:
     $$\text{Successful Vague Retrieval Rate} = P(\text{Recall Intent Formulated}) \times P(\text{Query Expressed}) \times P(\text{Semantic Match}) \times P(\text{Visual Recognition}) \times P(\text{Refinement Success})$$
   * Identify the drop-off bottlenecks supported by quantitative evidence from the dashboard.

### Milestone Gate:
- [ ] Working public/local link to the AI Discovery Engine Dashboard.
- [ ] Completed mathematical decomposition document in `DOCS/BUSINESS_METRIC_DECOMPOSITION.md`.

---

## Phase 3: Primary User Research & Problem Definition (Parts 3 & 4)
**Objective:** Validate AI-surfaced hypotheses with real human respondents and define the core problem with precision.

### Tasks & Deliverables:
1. **User Interview Protocol Design:**
   * Create interview guide focusing on critical incident recall: *"Think of the last time you remembered a photo existed but couldn't find it."*
   * Document screening criteria in `DOCS/USER_RESEARCH_GUIDE.md`.
2. **Conduct 5–6 User Interviews:**
   * Segment respondents: 2 power parents/family archivists, 2 utility/document searchers, 2 casual young adults.
   * Observe actual retrieval journeys: note initial search queries, cognitive pauses, scrolling behaviors, and workarounds.
3. **Triangulate Findings:**
   * Compare qualitative interview findings against the 10 Discovery Engine question aggregates.
4. **Synthesize Problem Definition Document (Part 4):**
   * Articulate:
     * Target User Segment & Persona.
     * Specific Retrieval Scenario (e.g. episodic context search with missing timestamp/location).
     * Root Cause of Failure (Semantic gap: lexical keyword matching vs. associative episodic memory).
     * Existing User Workarounds (scrolling WhatsApp chats, asking relatives, manual timeline scrolling).
     * Value proposition & business justification for Google Photos.
   * Save in `DOCS/PROBLEM_DEFINITION.md`.

### Milestone Gate:
- [ ] 5–6 completed user interview transcripts and synthesis matrix.
- [ ] Problem definition document approved and aligned with assignment rubric.

---

## Phase 4: AI-Native MVP Architecture, Prototyping & Deployment (Part 5)
**Objective:** Design, engineer, and deploy a functional, public-facing AI-native retrieval prototype.

### Tasks & Deliverables:
1. **MVP Solution Architecture:**
   * Select the form factor based on research:
     * **Option A:** Associative Episodic Memory Search Assistant (Conversational agent with multi-clue reasoning).
     * **Option B:** Multimodal Filter & Clutter-Free Visual Timeline (Dynamic visual anchors, relative time sliders, meme/receipt separator).
     * **Option C:** Natural Language Refinement & Query Disambiguation Workflow.
2. **Prototype Engineering:**
   * Build a lightweight, responsive web app (Next.js/React + FastAPI backend).
   * Integrate sample photo library with rich multimodal embeddings (CLIP / Gemini multimodal embeddings).
   * Implement smart associative querying: allows users to search using vague memories (*"small café Goa yellow table 2 years ago"*).
3. **Deployment:**
   * Deploy MVP on Vercel / Railway / Hugging Face Spaces.
   * Ensure publicly accessible URL that can be tested by anyone without login friction.

### Milestone Gate:
- [ ] Live, publicly accessible URL for the functional MVP.
- [ ] Retrieval task can be completed by a third party.

---

## Phase 5: User Testing & MVP Iteration (Part 6)
**Objective:** Put the functional MVP in front of users, measure task success rate, and document learnings.

### Tasks & Deliverables:
1. **Test MVP with $\ge 3$ Target Users:**
   * Provide representative retrieval scenarios uncovered in Phase 1 & 3 (e.g. *"Find the picture of the medicine you took last winter without using the date"*).
   * Record time-to-retrieval, task success rate, and qualitative user feedback.
2. **Document Findings & Iteration Roadmap:**
   * What worked well (e.g., conversational prompt suggestions, associative color/companion filtering).
   * What failed (e.g., latency, ambiguous result sorting).
   * Document what would be changed in V2.
   * Save in `DOCS/USER_TESTING_REPORT.md`.

### Milestone Gate:
- [ ] Usability testing notes and quotes from 3 real user sessions.
- [ ] Clear list of changes and learnings for next iteration.

---

## Phase 6: Metric Framework, Risk Analysis & 10-Slide Deck (Parts 7, 8 & Submission)
**Objective:** Define post-launch metric hierarchy, articulate failure risks and mitigations, and assemble the final 10-slide executive presentation.

### Tasks & Deliverables:
1. **Define Success Metrics Framework (Part 7):**
   * **North Star Metric:** % of vague-memory retrieval sessions completed successfully within 60 seconds.
   * **Leading Metrics:** Query refinement drop-off rate, average time spent scrolling timeline per query, reformulation attempts per session.
   * **Diagnostic / Guardrail Metrics:** False positive rate, search latency (p95 < 800ms), cloud compute cost per query.
2. **Risk & Mitigation Analysis (Part 8):**
   * Hallucination / False Retrieval Risk $\rightarrow$ Visual confidence thresholds and explicit disambiguation prompts.
   * Privacy / Sensitivity Risk $\rightarrow$ On-device indexing vs. encrypted cloud embeddings.
   * Clutter / Non-Memory Noise $\rightarrow$ Automatic quarantine of receipts, documents, and memes from memory feeds.
3. **Build the 10-Slide Deck:**
   * **Slide 1:** Title & Strategic Goal (Succinct headline, zero mention of Fellow name).
   * **Slide 2:** Business Metric Decomposition (Mathematical breakdown & failure points).
   * **Slide 3:** AI Discovery Engine Architecture & Methodology.
   * **Slide 4:** Discovery Engine Insights & Quantified Review Findings.
   * **Slide 5:** User Research Validation (Interviews, observed retrieval behaviors).
   * **Slide 6:** Problem Definition, Target Persona & Root Cause.
   * **Slide 7:** Solution Rationale & AI-Native Product Concept.
   * **Slide 8:** MVP Walkthrough & Architecture (Live link included).
   * **Slide 9:** MVP User Testing Results & Iteration Learnings.
   * **Slide 10:** Success Metrics Framework, Risks & Mitigations.
4. **Strict Presentation Compliance Verification:**
   * Maximum 10 slides.
   * No fellow name present.
   * Minimum font size 14 (PPT/Slides) or 26 (Figma) or 22 (Canva).
   * File size < 40 MB.
   * Working links to Discovery Engine and MVP.
   * Naming format: `NL_[Topic/Name].pdf`.

### Milestone Gate:
- [ ] Completed, verified 10-slide deck meeting all submission standards.
- [ ] Exported PDF under 40 MB ready for submission prior to October 7, 2026 3:59 PM IST.

---

## Phase Tracking & Status Dashboard

| Phase | Description | Deliverable / Output | Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Engine Pipeline Setup & Ingestion | Configured `discovery_config.yaml`, DB (2,223 documents across 5 sources), 4-bucket triage | ✅ Completed |
| **Phase 2** | Dashboard & Metric Decomposition | Next.js Dashboard live, 19 reconciled JSON data files, `DOCS/BUSINESS_METRIC_DECOMPOSITION.md` | ✅ Completed |
| **Phase 3** | User Research & Problem Definition | Interview Protocol (`DOCS/USER_RESEARCH_GUIDE.md`), `DOCS/PROBLEM_DEFINITION.md` | ✅ Completed |
| **Phase 4** | AI-Native MVP Architecture & Spec | PRD (`DOCS/MVP_PRD.md`), FastAPI RAG service, interactive prototype specs | ✅ Completed |
| **Phase 5** | MVP Testing Protocol & Telemetry | Testing Protocol (`DOCS/USER_TESTING_PROTOCOL.md`), 3 tasks, telemetry & learnings | ✅ Completed |
| **Phase 6** | Success Metrics, Risks & 10-Slide Deck | Deck Blueprint (`DOCS/SLIDE_DECK_BLUEPRINT.md`), `DOCS/TERMINOLOGY.md`, compliance checks | ✅ Completed |
