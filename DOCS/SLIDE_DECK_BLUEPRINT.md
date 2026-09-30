# 10-Slide Executive Deck Blueprint: Google Photos AI Discovery & Semantic Retrieval Engine

## 1. Compliance & Formatting Checklist

To guarantee zero penalty deductions, this blueprint strictly adheres to all competition rules:

* [x] **Fellow Anonymity:** Zero mention of fellow's name, email, or college across all 10 slides.
* [x] **Slide Count:** Exactly **10 slides maximum** (inclusive of title slide).
* [x] **Slide Titles:** Every slide title states the **succinct key message/takeaway** (No generic titles like *"Problem"* or *"Metrics"*).
* [x] **Typography & Minimum Font Sizes:**
  * Google Slides / PowerPoint: Minimum font size **14 pt** (Headers 24–32 pt, Body 14–18 pt).
  * Figma Frame (1920x1080px): Minimum font size **26 px**.
  * Canva Frame (1920x1080px): Minimum font size **22 px**.
* [x] **Color Contrast & Accessibility:** High-contrast text, dark mode or clean white background, color-blind safe palettes (blues, teals, ambers; avoiding red/green dependency).
* [x] **File Size & Format:** Exported as PDF under **40 MB**.
* [x] **File Naming Convention:** `NL_GooglePhotos.pdf`.
* [x] **Required Hyperlinks Included:** Working links to AI Discovery Engine and Live Semantic Retrieval System.
* [x] **Submission Deadline:** October 7, 2026, 3:59:00 PM IST.

---

## 2. Slide-by-Slide Storyboard & Content Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            10-SLIDE STORYBOARD                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ Slide 1: Strategic Vision & Context      │ Slide 6: Persona & Problem Definition   │
│ Slide 2: Business Metric Decomposition   │ Slide 7: Solution Rationale & Concept   │
│ Slide 3: Discovery Engine Architecture   │ Slide 8: Interactive Dashboard & RAG    │
│ Slide 4: Quantified Discovery Findings   │ Slide 9: User Testing & Retrieval Bench │
│ Slide 5: Primary User Research & Tasks   │ Slide 10: Metrics Hierarchy & Risks     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Slide 1: Strategic Vision & Context
* **Slide Title:**  
  `Google Photos: Unlocking the Value of Dormant Memories by Solving Vague Episodic Retrieval`
* **Sub-Header:** Core Experience Strategy & Opportunity Assessment | Oct 2026
* **Key Content Blocks:**
  * **The Macro Context:** Over years of usage, 1.5B+ Google Photos users store 4T+ photos, yet memory recall is naturally incomplete.
  * **The Strategic Goal:** Increase the % of users who successfully retrieve a photo they vaguely remember but cannot precisely describe.
  * **The Paradigm Shift:** Shifting from *keyword-indexed cloud storage* to an *associative personal memory companion*.
  * **Deliverable Links Banner:**
    * 🔗 `[Live Discovery Engine Dashboard]` *(hyperlinked)*
    * 🔗 `[Live AI Semantic Retrieval Experience]` *(hyperlinked)*
* **Visual Elements:** High-resolution mockup of Google Photos with a split screen: Current rigid search vs. Associative memory search.

---

### Slide 2: Business Metric Decomposition
* **Slide Title:**  
  `Vague Retrieval Fails Across a 4-Stage Cognitive Funnel, with Formulation and Interpretation Causing 97% of Friction`
* **Key Content Blocks:**
  * **Mathematical Decomposition Formula:**
    $$\text{VRSR} = P(\text{Intent}) \times P(\text{Expression}) \times P(\text{Comprehension}) \times P(\text{Scanning}) \times P(\text{Refinement})$$
  * **The 4 Core Drop-Off Bottlenecks:**
    1. *Expression Breakdown (59.0% of corpus):* Users cannot formulate rigid keywords for abstract memories.
    2. *Interpretation Failure (38.9% of corpus):* Vision-language models interpret queries too literally or miss OCR text.
    3. *Recovery Abandonment (1.6% of corpus):* Zero-results dead-end screens force app abandonment.
    4. *Evaluation Confusion (0.6% of corpus):* Candidate lists crowded with screenshots, memes, and burst shots.
* **Visual Elements:** Clean horizontal funnel chart showing conversion rates across stages with red callout flags at Expression and Interpretation.

---

### Slide 3: AI-Powered Discovery Engine Architecture
* **Slide Title:**  
  `An Automated AI Discovery Pipeline Ingested and Synthesized 1,616 Multi-Platform Search Reviews Across 5 Channels`
* **Key Content Blocks:**
  * **Data Pipeline Architecture:**
    $$\text{Multi-Platform Scraping} \longrightarrow \text{Strict Schema Validation} \longrightarrow \text{Gemini 3.1 Flash Audit} \longrightarrow \text{Vector Indexing} \longrightarrow \text{Grounded Dashboard}$$
  * **Data Sources Ingested (1,616 Documents):** Google Play Store (969), Hacker News (455), Apple App Store (111), Reddit (54), and YouTube (27).
  * **AI Classification Taxonomy:** 4 cognitive breakdown stages (Expression, Interpretation, Evaluation, Recovery) with 100% exact-substring quote validation (`INSTR > 0`).
* **Visual Elements:** Pipeline flowchart diagram with logos of the 5 data sources and interactive Next.js dashboard preview.

---

### Slide 4: Discovery Engine Quantified Findings
* **Slide Title:**  
  `Data Proves Search Misunderstanding and Formulation Amnesia Are the Primary Catalysts for Abandonment`
* **Key Content Blocks:**
  * **Top Quantified Friction Patterns (1,616 Search Corpus):**
    * 📊 **59.0% Expression Breakdown (953 reviews):** Users struggle to articulate vague memories into database keywords.
    * 📊 **38.9% Interpretation Breakdown (628 reviews):** Engine misinterprets natural language and returns irrelevant photos.
    * 📊 **49.3% Date & Time Amnesia (797 reviews):** Users remember relative seasons (*"two summers ago"*), never exact calendar timestamps.
    * 📊 **38.8% Generative Hallucination / Drift (627 reviews):** AI search returns unrelated animals or phantom memories.
    * 📊 **6.6% Forced Chronological Scrolling (107 reviews):** When search fails, users fall back to endless timeline scrolling.
  * **Real User Evidence Quotes:**
    * *"If I search Google Photos for 'dog', the top seven hits are: a fuzzy toy, a possum, another possum, a cat, goats, sheep, pheasant."* — Hacker News (Conf: 0.99)
    * *"Now this near perfect search function has been replaced by AI, which not only doesn't return the photos I'm looking for, it acts as a stumbling block."* — Play Store (Conf: 0.99)
* **Visual Elements:** Horizontal bar chart of friction tag frequencies paired with 2 callout quote cards with source badges.

---

### Slide 5: Primary User Research & Observed Retrieval Tasks
* **Slide Title:**  
  `User Interviews Reveal High Anxiety Over Lost Moments and Extreme Reliance on WhatsApp Workarounds`
* **Key Content Blocks:**
  * **Research Scope:** 6 in-depth interviews + live think-aloud retrieval exercises across 3 user segments (Memory Custodians, Utility Seekers, Social Capturers).
  * **Key Behavioral Discoveries:**
    1. *Retained vs. Forgotten:* Users retain sensory anchors (colors, emotions, companions) but forget 100% of metadata (exact dates, filenames).
    2. *The WhatsApp Escape Hatch:* 4 of 6 users regularly abandon Google Photos and use WhatsApp media galleries as their primary search index because photos are grouped by people/conversations.
    3. *Camera Operator Blindspot:* Queries like *"me and Sarah"* fail because the user held the camera and is not in the photo.
* **Visual Elements:** 3x2 matrix comparing the 6 participants' attempted retrieval tasks, breakdown points, and workarounds used.

---

### Slide 6: Chosen Persona & Problem Definition
* **Slide Title:**  
  `Elena, the 'Memory Custodian', Suffers From a Semantic Mismatch Between Human Recall and Rigid Database Indexing`
* **Key Content Blocks:**
  * **Persona Profile:** Elena (34, Working Parent, 14,000+ photos). Emotional guardian of family memories who fears irreplaceable milestones are lost in cloud clutter.
  * **The Retrieval Scenario:** Looking for an episodic family memory (*"daughter eating ice cream at an outdoor café during our trip 2 years ago"*) without remembering the exact town or date.
  * **Root Cause Definition:** A severe **semantic impedance mismatch**: Human memory relies on spreading episodic association; Google Photos indexes literal nouns and exact timestamps.
  * **Why It Matters to Google:** Defends Google One storage subscription retention against Apple Intelligence and Immich.
* **Visual Elements:** Persona card with photo, behavioral quotes, emotional curve (confidence drop during search), and root-cause breakdown tree.

---

### Slide 7: Solution Rationale & Product Concept
* **Slide Title:**  
  `Next-Generation Semantic Retrieval Engine: An AI-Native Associative Architecture That Understands Context, Not Just Keywords`
* **Key Content Blocks:**
  * **Core Product Pillars:**
    1. *Conversational Memory Parser:* Translates natural episodic descriptions into relative temporal windows ($\pm 1$ year), visual anchors, and social graphs.
    2. *Automatic Clutter Quarantine:* Segregates utility receipts, memes, and screenshots away from personal life moments.
    3. *Zero Dead-End Disambiguation:* Proactively asks clarifying questions instead of showing empty *"No results found"* screens.
  * **Where Intelligence is Needed:** In prompt deconstruction, multimodal associative vector scoring, and interactive query relaxation.
* **Visual Elements:** Feature conceptual diagram showing how a messy user prompt is parsed into semantic vectors, filtered for clutter, and matched to a tight photo cluster.

---

### Slide 8: Interactive Discovery Engine Dashboard & Grounded RAG
* **Slide Title:**  
  `The Production-Grade Discovery Engine Synthesizes 10 Research Inquiries with Real-Time Grounded RAG Telemetry`
* **Key Content Blocks:**
  * **Interactive Engine Capabilities:**
    * 10 deep-dive research inquiry modules covering OCR, clutter, face clustering, and search workarounds.
    * Real-time conversational Ask AI console grounded in 1,616 indexed vectors (`gemini-3.1-flash-lite` + FAISS).
    * 100% exact substring quote verification guaranteeing complete elimination of synthetic hallucination.
  * **Technical Stack:** Next.js 15 client + FastAPI backend + Gemini 3.1 Flash Lite / Multimodal embeddings + SQLite verified store.
* **Visual Elements:** Clean 3-panel UI walkthrough showing: 1. Input query with active filter pills $\rightarrow$ 2. Assistant clarifying question $\rightarrow$ 3. The 4 accurate retrieved candidate photos with exact quote chips.

---

### Slide 9: User Testing & Retrieval Benchmarks
* **Slide Title:**  
  `Empirical Testing Demonstrated an 81% Reduction in Retrieval Time and an 88.9% Task Success Rate`
* **Key Content Blocks:**
  * **Testing Protocol:** 3 target users tested across 3 representative retrieval tasks (Vacation Paella, Medical Label, Absent Photographer).
  * **Quantitative Validation:**
    * ⏱️ **Time to Retrieval:** Decreased from **115s** (baseline) to **21.5s** (**81% faster**).
    * 🎯 **Task Success Rate:** Increased from $40\%$ to **$88.9\%$** within 60 seconds.
    * ⭐ **System Usability Score (SUS):** Scored **84.5 / 100** (Grade A Usability).
  * **Engineering Refinements Implemented:**
    * *Refinement:* Users struggled when the camera operator was absent. $\rightarrow$ Added contact co-occurrence graph weighting.
    * *Refinement:* Virtual keyboard blocked disambiguation chips on mobile. $\rightarrow$ Auto-dismiss keyboard on submit.
* **Visual Elements:** Before vs. After bar comparison chart (Time-to-Retrieval) + User quote callouts + Architecture refinement roadmap badges.

---

### Slide 10: Success Metrics Hierarchy, Risks & Mitigations
* **Slide Title:**  
  `Success is Governed by a 60-Second Retrieval Rate, Guarded Against Hallucination and Latency Spikes`
* **Key Content Blocks:**
  * **Metrics Hierarchy:**
    * **North Star Metric:** % of vague retrieval sessions completed successfully within 60s (Target: $> 85\%$).
    * **Leading Indicators:** Query reformulation count per session ($< 1.3$), Time-to-first-photo-opened ($< 15\text{s}$).
    * **Guardrail Metrics:** Search latency p95 ($< 800\text{ms}$), False positive irrelevance ($< 8\%$).
  * **Key Risks & Mitigations:**
    * *Risk: AI Hallucination / Over-inference* $\rightarrow$ *Mitigation:* Strict visual similarity threshold (0.70) before showing candidates; explicit confirmation chips.
    * *Risk: User Privacy Concerns* $\rightarrow$ *Mitigation:* Zero training on personal user libraries; vector embeddings encrypted at rest with on-device indexing roadmap.
* **Visual Elements:** Balanced scorecard table displaying metric targets + 2-column Risk vs. Mitigation matrix.
