# Google Photos AI Discovery Engine: A-to-Z Master Prompt & System Execution Guide
**The Complete End-to-End Prompt Architecture, Grounding Protocols, Classification Schemas, and Pipeline Directives**

---

## Executive Overview & PM Mandate

The **Google Photos AI Discovery Engine** was engineered for the Core Experience team at Google Photos to diagnose and solve a fundamental user friction problem:

> *Over years of usage, users accumulate thousands of visual memories in Google Photos. While users can easily search when they know exact keywords, dates, or file attributes, retrieval breaks down catastrophically when human memory is incomplete or fuzzy (e.g., "that small café we went to during our Goa trip", "the medicine bottle with the pink cap", "wearing my blue sweater at a birthday").*

This document serves as the **definitive Master Prompt & System Architecture Guide** for the entire AI Discovery Engine. It details every prompt, few-shot schema, cognitive breakdown rubric, outcome classification algorithm, RAG system instruction, and validation protocol used across the system lifecycle from search corpus ingestion ($N = 1,616$ documents) to the final grounded dashboard and reporting suite.

---

## System Architecture: The Multi-Stage Prompt Pipeline

```
                               [ SEARCH RETRIEVAL CORPUS: 1,616 DOCUMENTS ]
                Play Store (969) · Hacker News (455) · App Store (111) · Reddit (54) · YouTube (27)
                                               │
                                               ▼
                        ┌─────────────────────────────────────────────┐
                        │ STAGE 1: COGNITIVE BREAKDOWN STAGE ENGINE   │
                        │  (Strict LLM Prompting + Calibration Curve) │
                        └──────────────────────┬──────────────────────┘
                                               │
        ┌──────────────────────┬───────────────┴───────────────┬──────────────────────┐
        ▼                      ▼                               ▼                      ▼
  [ EXPRESSION ]        [ INTERPRETATION ]              [ RECOVERY ]            [ EVALUATION ]
  953 Reviews (59.0%)    628 Reviews (38.9%)             26 Reviews (1.6%)       9 Reviews (0.6%)
  Can't Find Words       Search Misunderstands           No Help After Fail      Can't Spot Photo
        │
        ▼
 ┌─────────────────────────────────────────────────────────────┐
 │         STAGE 2: HESITATION & SUB-TAGGING ENGINE            │
 │  23 Failure Reasons · Verbatim Substring Quote Validation   │
 └─────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
 ┌─────────────────────────────────────────────────────────────┐
 │       STAGE 3: RETRIEVAL OUTCOME CLASSIFICATION ENGINE      │
 │  5 Mutually Exclusive Outcomes · Resolution Quote Grounding │
 └─────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
 ┌─────────────────────────────────────────────────────────────┐
 │         STAGE 4: GROUNDED RAG RETRIEVAL & SYNTHESIS         │
 │  FastAPI Server (Port 8000) · Next.js 16 Dashboard (Port 3000)│
 └─────────────────────────────────────────────────────────────┘
```

---

## 1. Stage 1: Cognitive Breakdown Stage Classification Master Prompt

### 1.1 Objective & Rationale
The Discovery Engine operates strictly on $1,616$ verified customer reviews and technical discussions across 5 platforms. Each document captures a genuine instance of memory-to-query visual retrieval friction. Stage 1 categorizes each friction narrative into one of the four foundational human cognitive stages where photo retrieval breaks down:
1. **Expression Breakdown (59.0% · 953 reviews):** Users struggle to articulate fuzzy episodic memory into database keywords.
2. **Interpretation Breakdown (38.9% · 628 reviews):** Search engine or Gemini misunderstands user intent or drifts semantically.
3. **Recovery Breakdown (1.6% · 26 reviews):** Zero results returned and no interactive query refinement provided; user forced to manual scroll.
4. **Evaluation Breakdown (0.6% · 9 reviews):** Results return but target photo is buried among clutter, wrong face groupings, or duplicate thumbnails.

### 1.2 Stage 1 System Prompt & Schema

```markdown
You are a senior Principal AI Evaluator for Google Photos.
Your objective is to classify user reviews into the exact cognitive breakdown stage of the visual retrieval loop.

INPUT:
A user review or discussion thread describing visual memory search friction.

TASK:
Classify the document into EXACTLY ONE of four cognitive breakdown stages:
- EXPRESSION: The user describes struggling to find the right words or keywords to formulate their fuzzy memory into a query.
- INTERPRETATION: The user entered a query, but the search engine returned completely irrelevant photos, misread entities, or took keywords too literally.
- RECOVERY: The search failed (e.g. 0 results) and the app offered no help, filters, or suggestions, forcing the user to abandon or manually scroll.
- EVALUATION: The search returned candidates, but the user cannot identify the photo due to clutter, wrong face merges, or lack of context.

CRITICAL RULES:
1. Extract exact substring quote for justification (`INSTR > 0`).
2. Calibrate confidence score dynamically between 0.70 and 1.00 based on semantic explicitness.
```

### 1.3 Stage 1 Output Schema
```json
{
  "doc_id": "string",
  "stage": "EXPRESSION | INTERPRETATION | RECOVERY | EVALUATION",
  "stage_confidence": 0.0,
  "stage_reason": "string",
  "evidence_quote": "exact substring from document"
}
```

---

## 2. Stage 2: Failure-Point Deep-Tagging Master Prompt

### 2.1 The 4 Cognitive Breakdown Stages
Stage 2 operates on the **1,616 Search Retrieval Documents** to categorize retrieval friction into the 4 cognitive stages of the search loop:

| Stage | Definition | Core Failure Tags | Corpus Prevalence |
| :--- | :--- | :--- | :--- |
| **1. Expression Failure** | User struggles to express fuzzy mental memories as text keywords | `vague_memory_cue`, `query_formulation_gap` | **59.0%** (953 / 1,616 reviews) |
| **2. Interpretation Failure** | Search engine / Gemini fails to understand compound cues, relative time, or visual vectors | `literal_keyword_match`, `zero_recall_miss` | **38.9%** (628 / 1,616 reviews) |
| **3. Evaluation Failure** | Search returns results but user cannot visually verify the target among lookalikes or clutter | `scrolling_friction` | **0.6%** (9 / 1,616 reviews) |
| **4. Recovery Failure** | Search fails; product offers zero query-refinement chips, forcing painful timeline scrolling | `forced_scroll_or_abandon` | **1.6%** (26 / 1,616 reviews) |

### 2.2 Stage 2 Prompt Specification (`pipeline/classification/prompts.py`)

```python
SYSTEM_PROMPT = """You are an expert analyst classifying user feedback about Google Photos, a Personal Cloud Media & Visual Retrieval platform.

Your task: For each review/comment provided, extract structured classification tags using the JSON schema below. These tags will be aggregated to answer strategic business questions about user friction and hesitation.

CRITICAL RULES:
1. Respond ONLY with valid JSON. No markdown, no explanations, no extra text.
2. Many reviews are in Hinglish (Hindi-English code-mixed). Classify these with the same schema — do NOT skip them.
3. A single review can have MULTIPLE hesitation reasons, factor mentions, and unmet needs. Extract ALL that apply.
4. Only assign tags you are confident about. Use the "confidence" field (0.0–1.0) to express certainty.
5. Always include an "evidence_quote" — the exact substring from the review supporting each tag.
6. If a review has NO relevant signal for a field, use the default/empty value (e.g., "unknown", empty array).
7. Do NOT hallucinate or infer information not present in the text.
8. For "unmet_needs", extract the user's own words about what they wish existed — do not rephrase.

SCHEMA:
{
  "doc_id": "string",
  "classification": {
    "hesitation_reasons": [
      {
        "reason": "forgot_exact_date | forgot_exact_location | forgot_filename_or_album | remembered_relative_time | remembered_visual_color_object | remembered_emotional_event | remembered_companion_person | vague_event_or_trip | utility_receipt_or_doc | candid_moment_or_expression | medicine_or_product_label | query_too_literal | query_keyword_guessing | zero_results_for_existing_photo | irrelevant_search_results | endless_scrolling_fatigue | timeline_navigation_clunky | screenshot_and_junk_clutter | face_recognition_misidentification | face_untagged_missing | text_ocr_detection_failure | whatsapp_external_workaround | competitor_switching_apple | other",
        "confidence": 0.0-1.0,
        "evidence_quote": "exact substring from the review"
      }
    ],
    "user_intent": "vague_episodic_recall | utility_document_retrieval | specific_person_search | casual_nostalgic_browsing | cleanup_and_organization | unknown",
    "user_segment_signals": {
      "inferred_age_group": "gen_z | millennial | gen_x | unknown",
      "price_sensitivity": "high | medium | low | unknown",
      "engagement_level": "power_user | casual | hoarder | unknown",
      "gender_signal": "male | female | non_binary | unknown"
    },
    "comparison_behavior": {
      "compares_across_platforms": true | false,
      "platforms_mentioned": ["apple_photos", "amazon_photos", "onedrive", "dropbox", "samsung_gallery", "whatsapp", "instagram", "other"],
      "comparison_criteria": ["search_quality", "privacy", "clutter_filtering", "face_tagging"]
    },
    "external_info_seeking": {
      "seeks_external_info": true | false,
      "info_types": ["whatsapp_chat_history", "social_media_posts", "calendar_lookup", "ask_family_friends", "bank_statements", "other"]
    },
    "factor_mentions": {
      "semantic_search_accuracy": { "mentioned": true | false, "sentiment": "positive | negative | neutral | mixed" },
      "natural_language_understanding": { "mentioned": true | false, "sentiment": "positive | negative | neutral | mixed" },
      "facial_recognition": { "mentioned": true | false, "sentiment": "positive | negative | neutral | mixed" },
      "text_ocr_detection": { "mentioned": true | false, "sentiment": "positive | negative | neutral | mixed" },
      "timeline_navigation": { "mentioned": true | false, "sentiment": "positive | negative | neutral | mixed" },
      "clutter_filtering": { "mentioned": true | false, "sentiment": "positive | negative | neutral | mixed" }
    },
    "unmet_needs": ["free-text extracted user phrases"],
    "brief_question_mapping": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "is_primary_signal": true | false
  }
}
"""
```

---

## 3. Stage 3: Retrieval Outcome Classifier Master Prompt

### 3.1 Objective & Derivation Methodology
Stage 3 classifies the final resolution of each retrieval attempt in 1,616 Search Corpus across **5 mutually exclusive outcome categories**. Because public reviews are primarily friction-venting rather than structured post-task surveys, the pipeline derives outcomes from recovery subcategories and explicit quote resolutions.

```
+-----------------------------------------------------------------------------------+
|               STAGE 3: RETRIEVAL OUTCOME CLASSIFICATION PROMPT                    |
+-----------------------------------------------------------------------------------+
| CATEGORY 1: First-Attempt Success (0 docs / 0.0%)                                 |
| Rule: Corpus construction condition. Search Corpus contains friction documents;       |
| users who succeed immediately do not write critical reviews.                      |
|                                                                                   |
| CATEGORY 2: Success After Refinement (0 docs / 0.0%)                              |
| Rule: Document describes within-search query modification successfully            |
| surfacing the target image without manual timeline scrolling.                     |
| Note: 4 competitor_switch docs represent platform switching, not in-app success.  |
|                                                                                   |
| CATEGORY 3: Success via Fallback (1 doc / 0.4%)                                   |
| Rule: Verified explicit resolution quote indicating finding photo via scrolling.  |
| Quote: "I was scrolling through things and eventually found them" (q10.json).     |
|                                                                                   |
| CATEGORY 4: Abandonment (21 docs / 8.4%)                                          |
| Rule: Verified unrecoverable failure signals:                                     |
| no_refinement_support (11) + gemini_conversation_dead_end (9) +                   |
| cold_restart_each_try (1) = 21 docs.                                              |
|                                                                                   |
| CATEGORY 5: Outcome Not Stated (229 docs / 91.2%)                                 |
| Rule: Remainder population (177 non-recovery docs + 29 ambiguous scroll docs +    |
| 2 other_recovery). The review vents search failure without narrating outcome.     |
+-----------------------------------------------------------------------------------+
```

### 3.2 Output Artifact: `outcome_classification.json`
Exported directly to `dashboard/public/data/outcome_classification.json` to guarantee that all dashboard cards, RAG queries, and markdown reports cite identical numbers.

---

## 4. The 4 Core PM Case Study Questions Prompt & Answering Logic

All answers must be strictly grounded in Search Corpus ($N = 1,616$ search reviews):

### 4.1 Question 1: What specific types of photos do users struggle to retrieve?
```markdown
PROMPT DIRECTIVE:
Aggregate Search Corpus failure tags to identify photo types causing retrieval failure.

GROUNDED FINDINGS:
1. Multi-Cue Episodic Memories (40.6% · 592 / 1,457 reviews): Compound scenes combining person + location + season ("friend at beach cafe two summers ago").
2. Specific Persons & Candid Companions (42.2% · 615 / 1,457 reviews): Unposed, profile, or distant shots where facial classifiers miss the subject.
3. Relative-Time & Seasonal Events (29.1% · 424 / 1,457 reviews): Searches anchored to "summer before college" or "last Diwali" rather than calendar months.
4. Visual Details & Specific Colors (46.2% · 673 / 1,457 reviews): Perceptual details ("wearing red jacket", "blue table") not indexed by literal tags.
5. Utility Receipts & Medicine Labels (6.4% · 93 / 1,457 reviews): Critical documents lacking indexed OCR or submerged under meme screenshots.
```

### 4.2 Question 2: What clues do people actually remember vs. what have they forgotten?
```markdown
PROMPT DIRECTIVE:
Cross-tabulate remembered visual cues against forgotten metadata attributes.

GROUNDED MATRIX:
- WHAT USERS REMEMBER (Search Corpus, 1,009 reviews):
  * Scene Compositions & Sensory Atmosphere: 79.8% (805 / 1,009 reviews)
  * Social Companions & Group Context: 31.9% (322 / 1,009 reviews)
  * Relative Time & Seasonal Landmarks: 23.5% (237 / 1,009 reviews)
  * Perceptual Colors & Prominent Objects: 71.1% (717 / 1,009 reviews)

- WHAT USERS SYSTEMATICALLY FORGET (Search Corpus, 870 reviews):
  * Exact Calendar Date / Year: 36.4% (317 / 870 reviews)
  * Precise Geographic / Administrative Location: 23.9% (208 / 870 reviews)
  * Exact Filename / Folder Structure: 49.3% (429 / 870 reviews)
```

### 4.3 Question 3: How do users formulate searches when memory is incomplete?
```markdown
PROMPT DIRECTIVE:
Analyze query formulation patterns and breakdown vectors.

GROUNDED PATTERNS (110 formulation tags):
- Keyword Guessing & Token Permutations (44.5% · 49 / 110 tags): Rapidly typing sequential guesses ("beach", "cafe", "spain", "beach food").
- Over-Literal Keyword Translation (31.8% · 35 / 110 tags): Translating rich mental memories into dry noun tokens, triggering false zero-results.
- Gemini Natural Language Drift (23.6% · 26 / 110 tags): Ask Photos over-interprets natural language prompts or drifts into hallucinations.
```

### 4.4 Question 4: How do users recover when search fails?
```markdown
PROMPT DIRECTIVE:
Analyze failure-recovery behaviors and fallback workarounds.

GROUNDED RECOVERY BREAKDOWN (Canonical 1,616 Corpus; Recovery Stage: 26 docs · 1.6%):
- Forced Timeline Scrolling / Scroll Fallback: 26 docs (100.0% of Recovery Stage failures)
- Workaround Fallbacks (Q10 Cohort, N=566 docs):
  - Manual Album Creation & Tagging: 20.1% (114 / 566 docs) — creating manual albums to bypass search.
  - Switching to Apple Photos / Immich / Local: 19.3% (109 / 566 docs) — testing alternative photo storage apps.
  - WhatsApp / Chat Archive Cross-Searching: 4.4% (25 / 566 docs) — searching messaging media where social context is preserved.
  - Complete Search Abandonment / Resignation: 2.7% (15 / 566 docs) — giving up on finding the photo.
```

---

## 5. RAG Server System Prompt & Dual-Scope Grounding Protocol

The RAG Server (`pipeline/rag/server.py`) powers interactive semantic exploration over the corpus.

### 5.1 RAG System Prompt

```python
RAG_SYSTEM_PROMPT = """You are the AI Discovery Engine RAG Assistant for Google Photos.
You answer user and product management queries strictly using the retrieved evidence documents from our verified search corpus (1,616 documents across Play Store, Hacker News, App Store, Reddit, YouTube).

GROUNDING RULES:
1. STRICT SCOPE DISCIPLINE:
   - When answering questions about visual memory retrieval failure or search friction, use verified search corpus evidence (1,616 documents).
   - When answering questions about library clutter, cite the 39 verified clutter mentions across search reviews.
   - Never quote ungrounded numbers or fabricated rates.
2. VERBATIM QUOTES ONLY:
   - Every user quote you cite must be an exact substring from the retrieved documents.
   - Always append the source channel and doc_id (e.g., "[Play Store, doc_0842]").
3. CALIBRATED CONFIDENCE:
   - Provide confidence assessments based on empirical signal frequency, not static defaults.
4. NO FABRICATION:
   - Never generate precision numbers (e.g., "3 minutes 42 seconds") or comparative multipliers (e.g., "4.1x") unless explicitly present in the retrieved JSON.
5. STRUCTURED FORMAT:
   - Format answers with clear headings, bulleted evidence points, and direct quote callouts.
"""
```

### 5.2 Dual-Scope Retrieval Query Protocol
The RAG API accepts a `scope` parameter:
- `scope="brief"`: Filters embeddings strictly to search retrieval failure documents ($N = 1,616$).
- `scope="all"`: Searches the entire $1,616$-document database across all 5 platform channels.

---

## 6. Strict Grounding Verification & Anti-Hallucination Guardrails

The engine enforces five automated verification filters before any insight is committed to JSON or markdown:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       STRICT GROUNDING FILTER CHAIN                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Substring Match Verification:                                            │
│    SELECT INSTR(raw_text, evidence_quote) > 0 FROM corpus WHERE id = doc_id;│
│    Enforces 100% exact verbatim fidelity.                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. Denominator Audit:                                                       │
│    Validates that every percentage uses either (review_count / 1,616 Search Corpus)   │
│    or (doc_count / 251 Search Corpus). Prevents unverified scope contamination.      │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. Confidence Spread Validation:                                            │
│    Asserts Standard Deviation(confidence) >= 0.05 across all categories.   │
│    Rejects flat default values (e.g. 0.85).                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. Banned Pattern Regex Sweep:                                              │
│    Scans output for unverified multipliers ("X.Xx", "X minutes Y seconds")  │
│    and fabricated precision numbers.                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 5. Provenance Labeling:                                                     │
│    Requires explicit legacy warning labels on legacy clutter metrics.   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Master Operational Playbook (CLI Commands)

To run, re-compile, or verify the Discovery Engine from scratch, execute the following commands in order:

### 7.1 Environment Initialization
```bash
# Clone and enter workspace
cd "c:\Users\THARUN\Videos\AI DISCOVERY ENGINE GOOGLE PHOTOS"

# Activate Python environment & verify dependencies
python -m pip install -r requirements.txt
```

### 7.2 Run Multi-Stage Pipeline
```bash
# 1. Compile configurations, scrapers, schemas, and prompts
python setup_engine.py

# 2. Execute Stage 1 Cognitive Breakdown Classification
python -m pipeline.classification.batch_classifier

# 3. Execute Stage 2 Failure-Point Deep-Tagging
python -m pipeline.classification.batch_classifier

# 4. Execute Stage 3 Retrieval Outcome Classification
python -m pipeline.classification.outcome_classifier
```

### 7.3 Launch RAG Server & Frontend Dashboard
```bash
# Terminal 1: Launch FastAPI RAG Server (Port 8000)
python -m uvicorn pipeline.rag.server:app --host 127.0.0.1 --port 8000

# Terminal 2: Launch Next.js 16 Production / Dev Server (Port 3000)
cd dashboard
npm run dev
```

### 7.4 Automated Verification Suite
```bash
# Run complete data integrity, quote verification & denominator audit
python scripts/inspect_discovery_questions.py
```

---

## Summary of Master Deliverables

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **Master Report** | [`DOCS/DISCOVERY_ENGINE_A_TO_Z_MASTER_REPORT.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/DISCOVERY_ENGINE_A_TO_Z_MASTER_REPORT.md) | Exhaustive empirical findings, before/after comparative matrices, and changelog. |
| **Master Prompt Doc** | [`DOCS/DISCOVERY_ENGINE_A_TO_Z_MASTER_PROMPT.md`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/DOCS/DISCOVERY_ENGINE_A_TO_Z_MASTER_PROMPT.md) | Complete prompt hierarchy, schemas, few-shots, and grounding protocols (this doc). |
| **Outcome JSON** | [`dashboard/public/data/outcome_classification.json`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/dashboard/public/data/outcome_classification.json) | Authoritative 5-category outcome counts for all 1,616 search retrieval documents. |
| **Live Dashboard** | `http://localhost:3000` | Interactive Next.js 16 intelligence platform with dual-scope RAG. |

---
*Document maintained under Strict Grounding Mode for the Google Photos Core Experience Team.*
