# Project Documentation Index — Google Photos AI Discovery Engine & MVP

Welcome to the **Google Photos AI Discovery Engine & AI-Native Retrieval MVP** project documentation repository.

This directory houses the complete, end-to-end product management and engineering documentation required for the Google Photos Core Experience assignment ahead of the **October 7, 2026** submission deadline.

---

## Complete Document Catalog

| Document | Purpose & Brief Alignment | Key Highlights |
| :--- | :--- | :--- |
| **[`PROBLEM_STATEMENT.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/PROBLEM_STATEMENT.md)** | Full Problem Brief (`PROBLEM STATEMENT 2 .pdf`) | Strategic mandate, all 8 parts, required deliverables, deck constraints, and submission rules. |
| **[`AI_POWERED_DISCOVERY_ENGINE_BRIEF.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/AI_POWERED_DISCOVERY_ENGINE_BRIEF.md)** | Part 1 Project Brief (`AI-Powered Discovery Engine 2.pdf`) | Permitted AI stacks, data sources, initial discovery questions, and quality standards. |
| **[`architecture.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/architecture.md)** | System Technical Architecture | Mermaid flowcharts, 6-stage pipeline details, database ER diagram, and code references. |
| **[`DATA_VERIFICATION_REPORT.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/DATA_VERIFICATION_REPORT.md)** | Certified Data Verification Audit | Multi-platform dataset (2,223 clean docs), 98.3% quote grounding, 0.0% contamination, 4,602 question mappings. |
| **[`BUSINESS_METRIC_DECOMPOSITION.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/BUSINESS_METRIC_DECOMPOSITION.md)** | Part 2 Metric Decomposition | Mathematical funnel formula, 4 core drop-off points, behavioral matrix, and telemetry hierarchy. |
| **[`USER_RESEARCH_GUIDE.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/USER_RESEARCH_GUIDE.md)** | Part 3 Primary Research Protocol | 5–6 participant screening criteria, critical incident interview script, live think-aloud tasks, and synthesis matrix. |
| **[`PROBLEM_DEFINITION.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/PROBLEM_DEFINITION.md)** | Part 4 Problem Definition & Persona | 5-step thinking evolution, Elena persona, root-cause 4-pillar analysis, user workarounds, and business justification. |
| **[`MVP_PRD.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/MVP_PRD.md)** | Part 5 AI-Native MVP Specification | "MemorySense" product specs, conversational query parser, clutter quarantine, API contracts, and architecture. |
| **[`USER_TESTING_PROTOCOL.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/USER_TESTING_PROTOCOL.md)** | Part 6 User Validation & Learnings | 3 standardized tasks, 3 user testing telemetry (88.9% TSR, 81% faster), verbatim quotes, and V2 iteration backlog. |
| **[`SLIDE_DECK_BLUEPRINT.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/SLIDE_DECK_BLUEPRINT.md)** | Final Deliverable Presentation | Exact 10-slide storyboard, action-oriented titles, layout guides, chart blueprints, and strict compliance checklist. |
| **[`NL_GooglePhotos.pdf`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/NL_GooglePhotos.pdf)** | Executive 10-Slide Competition Deck | Exactly 10 slides, 16:9 widescreen, 100% fellow anonymity, >=14pt fonts, working clickable prototype links. |
| **[`EDGECASES.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/EDGECASES.md)** | Failure Mode & Edge Case Analysis | Pipeline anomalies, human memory decay (temporal drift, false location), media clutter, and OCR/face recognition edge cases. |
| **[`EVALS.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/EVALS.md)** | Evaluation Framework & Benchmarks | LLM classification F1 scores, 100% quote check, RAGAS faithfulness, IR metrics (Recall@K, MRR), and 50-query golden test set. |
| **[`QUICK_START.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/QUICK_START.md)** | Developer Run Guide | Commands to compile engine, run crawlers, classify data, and launch dashboard and RAG servers. |
| **[`CONFIG_REFERENCE.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/CONFIG_REFERENCE.md)** | YAML Schema Reference | Complete configuration dictionary for `discovery_config.yaml`. |

---

## Project Structure Overview

```
├── DOCS/                                     <── Comprehensive documentation hub
│   ├── README.md                             <── Index (this file)
│   ├── PROBLEM_STATEMENT.md                  <── Assignment Brief
│   ├── AI_POWERED_DISCOVERY_ENGINE_BRIEF.md  <── Part 1 Brief
│   ├── architecture.md                       <── System Architecture
│   ├── IMPLEMENTATION_PLAN.md                <── 6-Phase Project Roadmap
│   ├── BUSINESS_METRIC_DECOMPOSITION.md      <── Part 2 Deliverable Guide
│   ├── USER_RESEARCH_GUIDE.md                <── Part 3 Interview Guide & Protocol
│   ├── PROBLEM_DEFINITION.md                 <── Part 4 Problem Definition
│   ├── MVP_PRD.md                            <── Part 5 AI-Native MVP Spec
│   ├── USER_TESTING_PROTOCOL.md              <── Part 6 User Validation Report
│   ├── SLIDE_DECK_BLUEPRINT.md               <── 10-Slide Final Deck Storyboard
│   ├── EDGECASES.md                          <── Edge Cases & Failure Modes
│   ├── EVALS.md                              <── Evaluation Suite & IR Benchmarks
│   ├── QUICK_START.md                        <── Execution Commands
│   └── CONFIG_REFERENCE.md                   <── YAML Config Reference
│
├── ai-discovery-engine-template/             <── Codebase
│   └── ai-discovery-engine-template/
│       ├── discovery_config.yaml             <── Tailored Google Photos Config
│       ├── setup_engine.py                   <── Code Compiler
│       ├── pipeline/                         <── Scrapers, Cleaner, Classifier, RAG
│       └── dashboard/                        <── Next.js Insights Frontend
```
