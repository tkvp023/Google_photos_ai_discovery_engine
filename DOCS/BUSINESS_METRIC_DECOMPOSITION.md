# Business Metric Decomposition — Google Photos Vague Memory Retrieval

## 1. Executive Context & Strategic Directive

As a Product Manager on the Core Experience team at Google Photos, your company’s strategic goal is to:
> **Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe when they start searching.**

The challenge is **not** to improve search in general (e.g., searching for "cats", "receipts from 2024", or "Mom"). Those are high-precision queries with explicit lexical or metadata anchors. The challenge lies in **episodic recall under partial cognitive decay**—where users retain rich sensory, emotional, or relative memories ("that small café during our Goa trip", "the yellow medicine bottle I took when I had fever"), but lack explicit dates, coordinates, or album tags.

---

## 2. Mathematical Metric Decomposition

We define the primary business metric as the **Vague Retrieval Success Rate ($\text{VRSR}$)**:

$$\text{VRSR} = \frac{\text{Sessions where user locates and interacts with target memory}}{\text{Total sessions initiated with vague memory recall intent}}$$

We mathematically decompose $\text{VRSR}$ into a 5-stage probabilistic behavioral funnel:

$$\text{VRSR} = P(\text{Formulate}) \times P(\text{Express} \mid \text{Formulate}) \times P(\text{Retrieve} \mid \text{Express}) \times P(\text{Recognize} \mid \text{Retrieve}) \times P(\text{Refine} \mid \text{Miss})$$

```
[1. Mental Recall Trigger]
       │  P(Formulate) — User recalls a memory exists and decides to search
       ▼
[2. Query Expression]
       │  P(Express) — Translates vague mental schema into input tokens
       ▼
[3. Semantic Retrieval & Matching]
       │  P(Retrieve) — Engine retrieves target photo in Candidate Pool (Top 50)
       ▼
[4. Evaluation & Visual Recognition]
       │  P(Recognize) — User spots target thumbnail amidst clutter without fatigue
       ▼
[5. Refinement / Recovery] (If initial attempt fails)
       │  P(Refine) — User modifies query/filters rather than abandoning app
       ▼
[Successful Retrieval Outcome]
```

---

## 3. Stage-by-Stage Behavioral & Product Decomposition

### Stage 1: Memory Formulation & Retrieval Intent
* **User Behavior:** A conversational trigger, nostalgia, or immediate utility need prompts the user to seek a specific past photo.
* **Cognitive State:** Incomplete episodic recall. User retains:
  * Temporal anchor: Relative (*"2 summers ago"*, *"during lockdown"*)
  * Visual anchor: Color, landmark, clothing (*"yellow awning"*, *"blue jacket"*)
  * Social context: Companions (*"with Sarah and Rahul"*)
  * Emotional state: Occasion (*"birthday dinner"*, *"when I fell sick"*)
* **Product Failure Risk:** User anticipates failure based on past bad experiences and decides not to even open Google Photos (Silent Churn).

---

### Stage 2: Query Expression Gap ($P(\text{Express})$)
* **The Core Problem:** Humans do not index memories in SQL or keyword tuples. They recall associative webs.
* **User Friction:**
  * **Vocabulary Mismatch:** User types literal keywords like *"beach shack seafood"* or *"sick medicine bottle"*.
  * **Over-Constrained Guessing:** User guesses a year (*"2022"*) that is off by 18 months, instantly returning zero results.
* **Product Outcome Needed:** Natural Language query flexibility that tolerates relative time, conceptual relationships, and vague descriptive adjectives without requiring exact boolean syntax.

---

### Stage 3: Semantic Comprehension & Index Matching ($P(\text{Retrieve})$)
* **The Core Problem:** The semantic gap between user's prompt tokens and Google Photos' computer vision/metadata tags.
* **Algorithmic Failure Points:**
  1. **Lexical Literalism:** Search treats *"paella beach shack"* as an exact intersection, missing the photo if vision models only tagged *"food"* and *"ocean"*.
  2. **Camera Operator Absence:** User searches *"me at the concert"*, but user was holding the camera, so their face tag is missing.
  3. **OCR Limitations:** Curved text on medicine bottles, stylized restaurant logos, or handwritten notes fail text detection.
* **Product Outcome Needed:** Multimodal dense vector retrieval (embeddings) connecting associative scenes, co-occurrence graph inference, and soft-filtered candidate generation.

---

### Stage 4: Result Scanning & Evaluation Fatigue ($P(\text{Recognize})$)
* **The Core Problem:** Search returns a candidate pool of 200+ photos, but evaluating them imposes unbearable cognitive load.
* **Friction Points:**
  1. **Near-Duplicate Burst Flooding:** 40 shots of the same plate of food occupy the first 3 viewport screens.
  2. **Non-Personal Clutter Interference:** Screenshots, WhatsApp memes, and documents crowd out genuine life memories.
  3. **Thumbnail Discrimination:** Small grid thumbnails make it impossible to identify the target photo without tapping into each one individually.
* **User Drop-off Behavior:** User abandons search and resorts to manually scrolling the infinite chronological timeline backwards.
* **Product Outcome Needed:** Clutter segregation (quarantining utility/memes), burst deduplication, and contextual visual clustering.

---

### Stage 5: Query Refinement & Recovery ($P(\text{Refine})$)
* **The Core Problem:** When the initial search returns 0 results or irrelevant results, the system gives the user no guidance.
* **Friction Points:**
  * **Dead-End Experience:** Screen displays *"No results found"* with an empty graphic.
  * **Trial-and-Error Exhaustion:** User frantically tries 3 slightly different synonyms (*"Goa trip"*, *"Goa beach"*, *"Goa café"*), gets frustrated, and quits.
* **User Coping Mechanism (Workarounds):**
  * Opens WhatsApp media gallery to find where they originally shared it.
  * Checks Instagram archived stories or Google Calendar to locate the date.
  * Asks friends/family: *"Hey, do you have that photo from our trip?"*
* **Product Outcome Needed:** Dynamic semantic disambiguation chips (*"Did you mean near Baga Beach?"*, *"Include photos from 2022–2024?"*, *"Filter by photos with Sarah"*).

---

## 4. Metric Decomposition Matrix: Behaviors, Outcomes & Discovery Tags

| Funnel Stage | Underlying User Behavior | Product Outcome Intended | Related Discovery Engine Tags |
| :--- | :--- | :--- | :--- |
| **1. Expression** | User attempts to translate a vague mental image into text. | Tolerant NLU that accepts relative time, sensory clues, and subjective descriptions. | `query_too_literal`<br>`query_keyword_guessing`<br>`forgot_exact_date`<br>`forgot_exact_location` |
| **2. Comprehension** | User provides indirect or relational clues. | Associative retrieval understanding context, OCR, and subject co-occurrence. | `zero_results_for_existing_photo`<br>`text_ocr_detection_failure`<br>`face_recognition_misidentification` |
| **3. Evaluation** | User scans candidate photos to locate the specific memory. | Clutter-free, high-relevance visual ranking with hero-photo clustering. | `irrelevant_search_results`<br>`screenshot_and_junk_clutter`<br>`endless_scrolling_fatigue` |
| **4. Refinement** | Initial search misses; user attempts to adjust search. | Interactive suggestions, facet relaxation, and zero dead-end screens. | `timeline_navigation_clunky`<br>`whatsapp_external_workaround`<br>`competitor_switching_apple` |

---

## 5. Leading, Diagnostic & Guardrail Metrics Hierarchy

To measure and optimize this decomposition in production, Google Photos should monitor the following telemetry:

```
                                 NORTH STAR METRIC
                 Vague Retrieval Success Rate (VRSR) within 60 Seconds
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        ▼                                                                 ▼
[Leading / Diagnostic Metrics]                                    [Guardrail Metrics]
- Expression: Reformulation Count per Session (< 1.5)             - Search Latency p95 (< 800ms)
- Comprehension: Zero-Result Rate on Long Queries (< 3%)          - False Positive Irrelevance (< 8%)
- Evaluation: Time-to-First-Photo-Opened (< 12s)                  - Cloud Inference Cost per Query
- Evaluation: Timeline Scroll Depth post-search (< 2 screens)     - Privacy / On-device Compliance
- Refinement: Query Abandonment Rate (< 10%)
```

---

## 6. Strategic Conclusion for Google Photos

Improving search by adding more exact metadata filters (e.g. *"Filter by ISO speed or camera model"*) does **not** solve the human memory problem. Users forget dates, filenames, and exact locations. 

The greatest leverage point in this metric funnel is:
> **Bridging the Semantic Gap between Incomplete Memory Expression and Associative Visual Matching (Stages 2 & 3), while eliminating Non-Memory Clutter in Evaluation (Stage 4).**

This decomposition directly defines the architecture of our **AI-Native Retrieval MVP**.
