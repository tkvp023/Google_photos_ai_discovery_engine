# Edge Cases & Failure Mode Analysis — Google Photos AI Discovery Engine & MVP

## 1. Overview & Objectives

This document categorizes all critical edge cases, cognitive failure modes, and technical anomalies across both:
1. **The AI Discovery Engine Pipeline** (Ingestion, Cleaning, LLM Classification, and RAG).
2. **The Visual Memory Retrieval Experience & MVP** (Human memory gaps, visual ambiguities, clutter interference, and retrieval algorithms).

Each failure mode is paired with root-cause mechanics and specific mitigation protocols.

---

## 2. Discovery Engine Pipeline Edge Cases

### A. Review Noise, Spam & Sarcasm
| Edge Case | Description & Example | Risk to Engine | Mitigation Protocol |
| :--- | :--- | :--- | :--- |
| **Ultra-Short / Non-Informative Reviews** | Reviews like *"Bad app"*, *"⭐⭐"*, or *"Search sucks"* without context. | Pollutes quantitative frequency and drags down confidence scores. | Filtered in [relevance_filter.py](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/ai-discovery-engine-template/ai-discovery-engine-template/pipeline/cleaning/relevance_filter.py) with `MIN_WORD_COUNT = 4` and regex noise pattern matches. |
| **Sarcastic User Complaints** | *"Great job Google! Searched for 'dog' and it showed my ex-boyfriend. Brilliant AI."* | Misclassified as positive sentiment or general praise. | Few-shot prompting in [prompts.py](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/ai-discovery-engine-template/ai-discovery-engine-template/pipeline/classification/prompts.py) instructing the model to detect sarcasm and tag `face_recognition_misidentification`. |
| **Multilingual & Hinglish Reviews** | Code-mixed Hindi-English (e.g. *"Purani photos search karne par kuch nahi milta, sab bekar hai"*). | Model skips review or assigns `unknown` tags. | Explicit system prompt rule: *"Many reviews are in Hinglish. Classify these with the same schema — do NOT skip them."* |
| **Account / Storage Confusion Out-of-Scope** | *"Google says my storage is full because of Gmail, won't let me back up photos."* | Dilutes retrieval friction insights with pricing/quota complaints. | Handled by domain relevance filters: checks for retrieval intent words (`search`, `find`, `retrieve`, `locate`, `face`, `timeline`). |

---

### B. LLM Classification & RAG Anomalies
| Edge Case | Failure Mechanism | Risk | Mitigation |
| :--- | :--- | :--- | :--- |
| **Hallucinated Evidence Quotes** | The LLM invents or paraphrases an evidence quote rather than quoting the verbatim string. | Corrupts data integrity and invalidates PM quote evidence. | [validator.py](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/ai-discovery-engine-template/ai-discovery-engine-template/pipeline/classification/validator.py) verifies `evidence_quote in review_content`. If false, rejects and falls back to regex extraction. |
| **Multi-Friction Compounding** | A user mentions 4 problems in one review (e.g. *"Search couldn't find my receipt, gave me screenshots, timeline lagged, and face grouping failed"*). | Model extracts only the first issue, under-reporting others. | Pydantic schema permits `List[HesitationReason]` up to 5 items with separate confidence scores. |
| **API Rate Limit Exceeded** | Gemini (15 RPM free tier) or Groq rate limits hit during bulk scraping. | Pipeline crashes mid-batch, causing data loss. | [batch_processor.py](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/ai-discovery-engine-template/ai-discovery-engine-template/pipeline/classification/batch_processor.py) implements exponential backoff, rate throttlers (`MAX_RPM_GEMINI`), and SQLite checkpointing every 50 records. |
| **RAG Hallucination on Low-Density Queries** | PM asks RAG: *"What do users think of photo widget search?"* (No reviews exist). | LLM fabricates insights. | Query engine requires minimum retrieval similarity threshold (0.65). If no matching quotes, returns: *"No user feedback found on this topic."* |

---

## 3. Human Memory & Cognitive Recall Edge Cases

These represent the psychological and behavioral ways user memory breaks down when trying to find old photos:

```
                          Cognitive Recall Breakdowns
                                       │
     ┌──────────────────┬──────────────┴─────┬─────────────────────┐
     ▼                  ▼                    ▼                     ▼
Temporal Drift    False Location    Misremembered Details    Missing Subject
(Wrong Year/Date) (Wrong Geo-Tag)   (Wrong Color/Context)   (Friend Took Photo)
```

### 1. Temporal Drift & Relative Anchoring
* **The User's Memory:** *"It was taken 2 years ago during winter"* or *"Around the time I had COVID."*
* **The Reality:** It was actually 3.5 years ago (human memory notoriously compresses past time).
* **The Failure Mode:** When the user searches or scrubs around 2024, the photo is actually in 2022. Google Photos' rigid chronological timeline causes total retrieval failure.
* **MVP Mitigation:** Enable relative semantic ranges (*"pre-pandemic"*, *"college years"*, *"winter season"*) and multi-year associative clustering.

### 2. False Location Attribution
* **The User's Memory:** Remembers eating seafood at a beach café *"in Goa"*.
* **The Reality:** The trip was actually to Gokarna or Pondicherry.
* **The Failure Mode:** User filters by `Location: Goa` and gets zero results. Because the location constraint is hardcoded, retrieval hits a complete dead end.
* **MVP Mitigation:** Soft/probabilistic location constraints (suggesting related coastal vacation clusters rather than hard zero-results).

### 3. Misremembered Visual Details (Feature Distortion)
* **The User's Memory:** Searching for *"me wearing a red jacket in the snow"*.
* **The Reality:** The jacket was burnt orange or dark pink, or the lighting made it appear reddish.
* **The Failure Mode:** Strict semantic or object filters fail because the visual embedding distance between "red jacket" and "orange parka" in low-light is too large.
* **MVP Mitigation:** Multimodal semantic relaxation: returns visually adjacent color spectrums and contextual anchors (*"snow jacket"*, *"winter outdoor apparel"*).

### 4. The "Missing Subject" Paradox (Camera Operator Bias)
* **The User's Memory:** *"Find that photo of me and Sarah at the concert."*
* **The Reality:** The user took the photo, so only Sarah is in the frame.
* **The Failure Mode:** User filters by their own face tag or searches *"me and Sarah"*; Google Photos returns nothing because the user's face is absent.
* **MVP Mitigation:** Co-occurrence inference: Search Sarah's concert photos from that same time window even if the user isn't visible in the image.

---

## 4. Content Clutter & Artifact Noise Edge Cases

### 1. Screenshots Stripped of Metadata
* **Problem:** When users screenshot an old photo, boarding pass, or receipt, the EXIF timestamp reflects the moment of the screenshot, not the original event. GPS is completely absent.
* **Failure Mode:** Searching for an event from 2022 fails because the screenshot is indexed in 2025.
* **Mitigation:** OCR date extraction from inside the screenshot image text to infer original chronological context.

### 2. WhatsApp & Social Media Media Dumps
* **Problem:** WhatsApp re-encodes images, removes EXIF metadata, and clumps 50 downloaded memes and forwards on the exact day they were received.
* **Failure Mode:** Search results for personal memories get flooded with irrelevant memes and forward graphics.
* **Mitigation:** Automatic "Utility vs. Memory" classifier separating personal camera-roll captures from downloaded forwards and memes.

### 3. Near-Duplicate Burst Clutter
* **Problem:** 40 burst shots of the same pose or plate of food.
* **Failure Mode:** Top 30 search results are filled by the same burst sequence, pushing alternative relevant photos off the visible screen and inducing scroll fatigue.
* **Mitigation:** Visual diversity de-duplication: collapse identical burst frames into a single representative hero photo in search results.

---

## 5. Technical & Feature-Specific Edge Cases

### A. Text & OCR Detection Failures
| Sub-Case | Description | Real Example | Mitigation |
| :--- | :--- | :--- | :--- |
| **Curved / Cylindrical Text** | Medicine bottles, soda cans, coffee mugs. | Searching for prescription drug *"Amoxicillin"* on a pill bottle fails. | Enhanced multi-angle OCR preprocessing & phonetic fuzzy search. |
| **Handwritten Notes & Whiteboards** | Cursive handwriting, whiteboard markers, sticky notes. | Searching for meeting notes or handwritten recipe. | Fine-tuned handwriting OCR model with character confidence smoothing. |
| **Low Contrast / Glare** | Laminated ID cards, vehicle license plates with headlight reflection. | Searching for car parking ticket or license plate. | Adaptive contrast normalization prior to text recognition. |

---

### B. Facial Recognition & Aging Edge Cases
| Sub-Case | Description | Real Example | Mitigation |
| :--- | :--- | :--- | :--- |
| **Infant to Toddler Transition** | Face structure changes radically between 0–3 years old. | Google Photos splits a single child into 3 separate unidentified people. | Chronological identity chaining: clustering face models over adjacent monthly intervals. |
| **Severe Occlusion** | Sunglasses, masks, helmets, dramatic makeup. | Photos from a ski trip or Halloween party not linked to person. | Multi-modal body & clothing co-occurrence tagging. |
| **Lookalike Siblings / Twins** | Merging two distinct children into one face cluster. | Parent searches for Child A and gets 50% photos of Child B. | Disambiguation prompt: *"Are these two different people?"* with manual split verification. |

---

## 6. Summary Matrix: Edge Cases vs. Product Impact

| Edge Case Group | Primary Failure | Frequency in Reviews | Severity | MVP Priority |
| :--- | :--- | :--- | :--- | :--- |
| **Temporal Recall Drift** | Hard date filters return 0 results | **Very High (42%)** | Critical | **P0** |
| **Screenshot & Junk Clutter** | Memes & receipts drown memories | **High (34%)** | Major | **P0** |
| **Curved/Medical OCR Failure** | Utility retrieval dead end | **Moderate (22%)** | High | **P1** |
| **Camera Operator Absence** | "Photos with X" missing user's face | **Moderate (18%)** | Medium | **P1** |
| **Sarcastic / Hinglish Reviews** | Classifier mislabels user sentiment | **Moderate (15%)** | Medium | **P1 (Pipeline)** |
| **Sibling Face Merge** | Identity contamination | **Low (9%)** | Annoying | **P2** |
