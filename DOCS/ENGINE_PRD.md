# Product Requirements Document (PRD): Google Photos AI Discovery Engine & Semantic Retrieval Architecture

## 1. Executive Summary & Product Vision

* **Product Name:** **Google Photos AI Discovery Engine & Associative Retrieval System**
* **Status:** Product Requirements & Architecture Specification
* **Vision:** Transform Google Photos from an inert, chronological photo attic into an intelligent **associative visual memory partner** that empowers users to retrieve any remembered photo even when exact dates, locations, and filenames are forgotten.

---

## 2. Where Intelligence is Required in the Retrieval Journey

The Discovery Engine's analysis of 1,616 authentic customer discussions proves that search breaks down primarily at three moments:

```
[1. Intelligent Query Decomposition] ──► [2. Multimodal Associative Matching] ──► [3. Interactive Disambiguation]
Deconstructs vague memories into        Dense vector retrieval over visual,       Proactively clarifies fuzzy
relative temporal, visual & social      social & contextual embeddings            memories to avoid dead ends
sub-hypotheses.                         while quarantining clutter.               instead of "0 results".
```

---

## 3. Core Feature Requirements

### Feature 1: Conversational Episodic Query Parser
* **User Input:** Free-form natural language describing an incomplete memory.  
  * *Example:* *"That small café with blue chairs where we had seafood paella during our Spain trip a few years ago."*
* **AI Extraction Engine:**
  * Extracts **Relative Time Anchor:** `2022 - 2023` (expands by $\pm 1$ year buffer).
  * Extracts **Visual / Sensory Anchors:** `blue chairs`, `outdoor dining`, `seafood / paella`, `sunlight`.
  * Extracts **Location Context:** `Spain / coastal area`.
  * Injects **Clutter Quarantine:** Suppresses screenshots, memes, and receipts automatically.

---

### Feature 2: Multimodal Associative Retrieval & Clutter Segregation
* **Dense Embedding Scoring:** Compares the multi-attribute query representation against photo embeddings (CLIP / Gemini Multimodal).
* **Clutter Filter Engine:** Categorizes photos into two primary pools:
  1. `Life Memories` (Candid photos, family moments, trips, celebrations).
  2. `Utility & Junk Artifacts` (Screenshots, payment slips, medical labels, WhatsApp memes).
* **Smart Burst Collapse:** Identifies near-duplicate burst captures and collapses them into a single representative hero thumbnail to prevent scroll fatigue.

---

### Feature 3: Interactive Disambiguation (Zero Dead-Ends)
* **Trigger:** When candidate confidence is below 0.70 or spans multiple distinct candidate events.
* **Agent Behavior:** Proactively suggests smart conversational refinement chips:
  * *"Did you mean your trip to Valencia (Aug 2022) or Barcelona (May 2023)?"*
  * *"Was Sarah tagged in this photo?"*
  * *"Filter by: Daytime outdoor seating / Indoor dining"*
* **Rule:** The system **never** displays an empty *"No results found"* dead-end screen.

---

## 4. Technical Architecture & Data Models

### Query Processing Pipeline
1. **User Query** $\to$ Gemini NLP Parser $\to$ Structured Query Object (`relative_time`, `visual_cues`, `persons`, `exclude_clutter`).
2. **Embedding & Candidate Retrieval:** Cosine similarity against media vector index.
3. **Clutter Quarantine Filter:** Drops media tagged as receipts, memes, or screenshots unless specifically queried.
4. **Ranking & Grouping:** Groups burst shots and ranks by semantic proximity.
5. **Dynamic Clarification:** Generates disambiguation chips if candidate set is dispersed.
