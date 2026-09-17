# Product Requirements Document (PRD): Google Photos "MemorySense" AI-Native MVP (Part 5)

## 1. Executive Summary & Product Vision

* **Product Name:** **Google Photos "MemorySense"** (AI-Native Associative Retrieval Assistant)
* **Status:** Prototype & Deployment Specification (Part 5 Deliverable)
* **Vision:** Transform Google Photos from an inert, chronological photo attic into an active **conversational episodic memory partner** that helps users retrieve any photo they remember, even when dates, locations, and exact keywords are forgotten.

---

## 2. Where Intelligence is Actually Needed in the User Journey

Our Discovery Engine and User Research revealed that intelligence is wasted if applied merely to generic captioning. Intelligence is strictly required at three specific friction points:

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

## 4. User Journey & Wireframe Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MemorySense Interface                           │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   [🔍 "Small café with blue chairs paella trip 2-3 years ago..."    ] │
│                                                                        │
│   ┌─────────────────────────── Active Filters ─────────────────────┐  │
│   │ 📅 ~2022-2023  │ 🥘 Paella/Seafood │ 🪑 Blue seating │ 🛡️ No Clutter│  │
│   └────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│   💬 Assistant: "Found 4 photos from your Valencia trip (Aug 2022).    │
│                 Was Sarah with you during this lunch?"                 │
│                 [ Yes, Sarah was there ]   [ No, different trip ]      │
│                                                                        │
│   ┌─────────────── Candidate Memories (Top Ranked) ────────────────┐  │
│   │  [📸 Hero Photo 1]   [📸 Photo 2]   [📸 Photo 3]   [📸 Photo 4]│  │
│   │   Beachfront Café     Paella Dish     Blue Chairs    Group Table│  │
│   │   Aug 14, 2022        Aug 14, 2022    Aug 14, 2022   Aug 14, 2022│  │
│   └────────────────────────────────────────────────────────────────┘  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Technical Architecture & Tech Stack

```
[Web Client (Next.js 15 / React / Tailwind)]
                    │  REST / JSON
                    ▼
[FastAPI Backend Engine (Python 3.11)]
    ├── Query Decomposer (Gemini 2.5 Flash / Groq LLM)
    ├── Multimodal Embedder (CLIP / Sentence-Transformers)
    ├── Vector Index (ChromaDB / Scikit-learn Cosine Similarity)
    └── Candidate Photo Store (Curated Test Library of 1,000 Representative Photos)
```

### Component Details:
* **Frontend:** Next.js App Router, responsive across mobile and desktop.
* **Backend:** FastAPI with sub-300ms latency.
* **Test Photo Corpus:** A realistic simulated user library of **1,000 photos** including:
  * Family vacations (Goa, Europe, road trips)
  * Everyday utility documents (prescriptions, receipts, whiteboard notes)
  * WhatsApp memes, screenshots, and burst shots.

---

## 6. API Endpoint Contracts

### Endpoint 1: `POST /api/memory/search`
* **Request:**
```json
{
  "query": "the medicine bottle for fever when I was sick last winter",
  "quarantine_clutter": true
}
```
* **Response:**
```json
{
  "parsed_context": {
    "intent": "utility_document_retrieval",
    "temporal_range": ["2023-11-01", "2024-03-31"],
    "visual_cues": ["medicine bottle", "pharmacy label", "pills"],
    "clutter_filtered": 42
  },
  "results": [
    {
      "photo_id": "img_0482",
      "url": "https://.../medicine_bottle.jpg",
      "timestamp": "2024-01-12T14:22:00Z",
      "similarity_score": 0.89,
      "matched_reasons": ["OCR text match: Paracetamol", "Temporal match: Jan 2024"]
    }
  ],
  "clarification_chips": [
    "Show only prescription labels",
    "Expand time window to 2023"
  ]
}
```

---

## 7. Public Deployment Plan

1. **Frontend Hosting:** Vercel (zero configuration, instant global CDN).
2. **Backend Hosting:** Railway / Render (containerized FastAPI service).
3. **Public Access:** Zero-login friction, pre-loaded with representative test scenarios so evaluators can test the prototype immediately via a public URL link.
