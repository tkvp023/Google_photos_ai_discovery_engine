# Evaluation Framework & Benchmarks (Evals) — Google Photos AI Discovery Engine & MVP

## 1. Executive Summary & Evaluation Architecture

This document establishes the formal **Evaluation Framework (Evals)** for the project, spanning two interconnected evaluation tracks:

```
                                  EVALUATION SUITE
                                         │
        ┌────────────────────────────────┴────────────────────────────────┐
        ▼                                                                 ▼
[Track 1: AI Discovery Engine Evals]             [Track 2: AI-Native Retrieval MVP Evals]
- Scraper Data Quality & Completeness            - Retrieval Precision & Recall (Recall@K, MRR)
- Relevance Filter Accuracy (Precision/Recall)   - Episodic Golden Benchmark (50 Queries)
- LLM Classification Taxonomy F1 Score           - Latency, Cost & Hallucination Guardrails
- Exact Evidence Quote Verification              - Human Usability Testing Rubric (TSR, TTR, SUS)
- RAG Answer Faithfulness & Groundedness
```

---

## 2. Track 1: AI Discovery Engine Pipeline Evals

The Discovery Engine must provide clean, truthful, quantitative proof to power product decisions. We evaluate each pipeline stage with concrete automated acceptance criteria:

### A. Data Ingestion & Scraper Health
| Metric | Definition | Target Threshold | Test Method |
| :--- | :--- | :--- | :--- |
| **Field Completeness** | % of records containing non-null `content`, `created_at`, `source`, and `doc_id`. | **$\ge 99.5\%$** | Automated check in `pipeline/db/connection.py` on ingest. |
| **Deduplication Rate** | % of exact/near-duplicate records filtered across cross-subreddit posts. | **$100\%$ exact, $\ge 90\%$ fuzzy** | Hash checking against `raw_documents.content_hash`. |
| **Checkpointed Continuity** | Zero data loss if crawler terminates mid-scrape. | **$100\%$ recovery** | Verified via checkpoint files in `data/checkpoints/`. |

---

### B. Cleaning & Relevance Filter Accuracy
Evaluated against a curated evaluation sample of **200 reviews** (100 retrieval complaints, 50 out-of-scope storage/billing complaints, 50 spam/bot comments).

$$\text{Precision} = \frac{\text{True Relevant Kept}}{\text{Total Kept}}, \quad \text{Recall} = \frac{\text{True Relevant Kept}}{\text{Total True Relevant}}$$

| Filter Metric | Target | Failure Consequence | Verification Command |
| :--- | :--- | :--- | :--- |
| **Relevance Precision** | **$\ge 92\%$** | Unrelated billing/quota reviews slip into retrieval analysis. | `python -m pytest tests/test_relevance.py -k "test_precision"` |
| **Relevance Recall** | **$\ge 95\%$** | Legitimate subtle photo retrieval complaints are dropped. | `python -m pytest tests/test_relevance.py -k "test_recall"` |
| **Noise Rejection** | **$\ge 98\%$** | Non-informative single-word reviews pollute analytics. | Tested against regex noise suite in `relevance_filter.py`. |

---

### C. LLM Classification Accuracy (Gold-Standard Benchmark)
A benchmark of **100 human-annotated reviews** labeled by PM evaluators with ground-truth hesitation tags, intent, and factors.

| Classification Dimension | Metric | Minimum Target | Target Excellence |
| :--- | :--- | :--- | :--- |
| **Hesitation Tag Identification** | Macro F1-Score | $\ge 0.82$ | $\ge 0.90$ |
| **Tag Precision** | Precision across 21 tags | $\ge 0.85$ | $\ge 0.92$ |
| **Tag Recall** | Recall across 21 tags | $\ge 0.80$ | $\ge 0.88$ |
| **Evidence Quote Validity** | Exact Substring Match | **$100\%$** (Strict) | **$100\%$** |
| **User Intent Classification** | Multi-class Accuracy | $\ge 85\%$ | $\ge 92\%$ |
| **Confidence Calibration** | Expected Calibration Error (ECE) | $< 0.12$ | $< 0.08$ |

> **Automated Gate:** [validator.py](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/pipeline/classification/validator.py) enforces that if `evidence_quote` is not an exact substring in the input text, the classification is rejected and routed to fallback regex tagging.

---

### D. RAG Semantic Server Evals (RAGAS Framework)
Evaluates the FastAPI query server when answering PM questions backed by real quotes.

1. **Faithfulness / Groundedness ($\ge 0.90$):** Are all claims made in the synthesized answer directly verifiable from the retrieved review quotes? (Zero ungrounded hallucination).
2. **Context Relevance ($\ge 0.85$):** Are the top 5 review quotes returned actually relevant to the PM's question?
3. **Answer Relevance ($\ge 0.88$):** Does the generated response directly answer the specific question asked?

---

## 3. Track 2: AI-Native Retrieval MVP Evals

The AI-Native MVP is designed to solve the vague-memory retrieval breakdown. We evaluate its performance against the **Golden Episodic Retrieval Benchmark**.

### A. Core Information Retrieval (IR) Metrics

$$\text{Recall}@K = \frac{\text{Number of relevant photos in top } K \text{ results}}{\text{Total relevant photos for that target memory}}$$

$$\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$

| IR Metric | Definition | Baseline (Current Keyword Search) | Target (AI-Native MVP) |
| :--- | :--- | :--- | :--- |
| **Recall@1** | Target photo is the very first result | $12\%$ | **$\ge 45\%$** |
| **Recall@5** | Target photo appears within top 5 results | $28\%$ | **$\ge 75\%$** |
| **Recall@10** | Target photo appears within top 10 results (without scrolling) | $39\%$ | **$\ge 88\%$** |
| **MRR (Mean Reciprocal Rank)** | Reciprocal rank of the target photo | $0.24$ | **$\ge 0.65$** |
| **NDCG@10** | Quality of ranking for multi-photo events | $0.35$ | **$\ge 0.78$** |
| **Clutter Intrusion Rate** | % of top 10 results that are memes, receipts, or screenshots | $42\%$ | **$\le 5\%$** |

---

### B. Golden Episodic Benchmark Test Suite (50 Scenarios)
A test dataset of 50 vague retrieval scenarios representing the core recall categories uncovered by the Discovery Engine:

| Category | Sample Benchmark Prompt | Target Clues | Expected Retrieval |
| :--- | :--- | :--- | :--- |
| **1. Relative Temporal Drift** | *"That small seaside shack we had paella at two or three summers ago"* | Paella, outdoor dining, beach, relative season 2022–2023 | Surfaces Valencia beach paella photos without requiring exact date. |
| **2. Utility / Label Search** | *"The yellow medicine bottle I took when I had the cough last winter"* | Yellow bottle, syrup/pills, medicine text, winter seasonal window | Surfaces medicine bottle photo, filtering out memes & insurance screenshots. |
| **3. Sensory / Visual Clue** | *"Me in front of a blue graffiti wall holding an iced coffee"* | Blue street art, iced coffee cup, outdoor sunlight | Matches visual composition even if user misremembers exact street or date. |
| **4. Social / Operator Bias** | *"Sarah laughing with a cocktail at the rooftop birthday"* | Sarah face tag, cocktail glass, nighttime terrace | Retains Sarah's photo even if user (photographer) is not in frame. |
| **5. OCR & Document Search** | *"The parking receipt from the underground airport garage"* | Parking receipt, slip, airport keyword, barcode | Surfaces specific receipt image and extracts license plate text. |

---

### C. Technical Latency & Operational Guardrails
| Parameter | Threshold | Failure Action |
| :--- | :--- | :--- |
| **Query Latency (p50)** | $< 400 \text{ ms}$ | Cache multimodal embeddings for user library. |
| **Query Latency (p95)** | $< 900 \text{ ms}$ | Degrade to lightweight vector similarity before full re-ranking. |
| **False Positive Cluster Rate** | $< 8\%$ | Surface disambiguation chip: *"Did you mean your trip to Goa or Pondicherry?"* |
| **Zero-Results Dead End Rate** | $< 2\%$ | Always provide relaxed semantic suggestions rather than blank screen. |

---

## 4. Track 3: Human User Testing Usability Rubric (Part 6)

During Part 6 validation, 3+ real users execute 3 standardized retrieval tasks on both the baseline experience and our AI-Native MVP:

### User Testing Metrics Sheet:
| Usability Metric | Measurement Method | Baseline Expectation | MVP Success Criteria |
| :--- | :--- | :--- | :--- |
| **Task Success Rate (TSR)** | % of retrieval tasks completed successfully within 60 seconds. | $\le 40\%$ | **$\ge 85\%$** |
| **Time to Retrieval (TTR)** | Clock seconds from entering query to tapping the target photo. | $> 95 \text{ seconds}$ | **$\le 25 \text{ seconds}$** |
| **Timeline Scroll Depth** | Number of screen heights scrolled to find the photo. | $> 12 \text{ screens}$ | **$\le 2 \text{ screens}$** |
| **Query Reformulation Count** | Number of times user changes search words due to failure. | $3.4 \text{ queries}$ | **$\le 1.2 \text{ queries}$** |
| **Subjective Frustration (1-5)** | Likert scale (1 = effortless, 5 = infuriating). | $4.2 / 5$ | **$\le 1.8 / 5$** |
| **System Usability Scale (SUS)** | Standardized 10-question SUS questionnaire. | $54 / 100$ | **$\ge 82 / 100$** |

---

## 5. Automated Evaluation Execution Scripts

### Running Discovery Engine Evals:
```bash
# Run schema and quote validation tests
python -m pytest tests/test_schema_validation.py

# Run classification F1 and confusion matrix against gold dataset
python pipeline/classification/validator.py --mode eval --gold-dataset data/gold_reviews.json

# Run RAG faithfulness check
python pipeline/rag/server.py --mode eval
```

### Running Retrieval MVP Benchmark Evals:
```bash
# Run 50 golden queries against retrieval MVP engine
python tests/evaluate_retrieval_benchmark.py --queries tests/golden_50_queries.json --top-k 10
```

---

## 6. Continuous Verification Summary Table

| Milestone | Eval Gate | Pass Requirement | Blocking? |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Scraper & Classification Eval | 100% Quote substring match, F1 > 0.82 | **YES** (Blocks Phase 2 export) |
| **Phase 2** | Aggregation & RAG Eval | Faithfulness > 0.90, 0 broken question tabs | **YES** (Blocks Phase 3) |
| **Phase 4** | Retrieval MVP Benchmark | Recall@10 $\ge 85\%$, p95 latency $< 900\text{ms}$ | **YES** (Blocks User Testing) |
| **Phase 5** | Human Usability Eval | Task Success Rate $\ge 85\%$, SUS $\ge 80$ | **YES** (Required for Slide 9) |
| **Phase 6** | Slide Deck Compliance | 10 slides max, font sizes adhered to, < 40MB | **YES** (Strict submission rule) |
