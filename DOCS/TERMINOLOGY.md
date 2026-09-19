# Terminology Reference — Google Photos AI Discovery Engine Dashboard

This document maps every internal/engineering label used in the discovery engine's code and data to the plain-language label shown to dashboard viewers. It also documents the semantic color system.

Any code that reads from JSON data files retains the original internal keys — only the **user-facing display text** changes.

---

## Label Mapping: Internal → Plain Language

### Corpus Categories (Triage Buckets)

| Internal Code | Internal Label | Dashboard Label | Meaning |
|:---|:---|:---|:---|
| `A` | Bucket A · On-Brief | **Search Friction** | Reviews where users describe struggling to find a remembered photo through search |
| `B` | Bucket B · Reliability | **App & Backup Issues** | Sync failures, crashes, storage quota, battery drain complaints |
| `C` | Bucket C · UI Backlash | **Layout & Menu Complaints** | Tab repositioning, bottom bar removal, navigation redesign gripes |
| `D` | Bucket D · Chatter | **General Feedback** | Short praise, generic ratings, unrelated feature requests |

### Cognitive Failure Stages

| Internal Code | Internal Label | Dashboard Label | Plain Description |
|:---|:---|:---|:---|
| `expression` | Formulation Failure / Cognitive Stage 1 | **Can't find the right words** | Users struggle to translate fuzzy memories into search terms |
| `interpretation` | Interpretation Failure / Cognitive Stage 2 | **Search misunderstands them** | Google Photos misreads the query intent and returns wrong results |
| `evaluation` | Evaluation Failure / Cognitive Stage 3 | **Can't spot the right photo** | Results are returned but the target photo is buried in clutter |
| `recovery` | Recovery Failure / Cognitive Stage 4 | **No help when search fails** | No refinement suggestions offered; user forced to scroll manually |

### Stat Card Labels

| Internal Label | Dashboard Label |
|:---|:---|
| Total Corpus (5 Channels) | **Reviews analyzed** |
| On-Brief Retrieval Signal (Bucket A) | **Search-related reviews** |
| #1 Blocker: Interpretation Failure | **Biggest gap: Search misunderstands the query** |
| #2 Blocker: Recovery Breakdown | **Second gap: No help after failure** |
| Zero Results for Existing Photos | **"No results" for photos that exist** |
| Screenshot & Meme Clutter | **Junk photos polluting search** |
| Calibrated Confidence (±0.18 σ) | **Data confidence level** |

### Section Headings

| Internal Heading | Dashboard Heading |
|:---|:---|
| Corpus Triage Architecture & Noise Segregation | **What we focused on** |
| 2-STAGE TRIAGE FUNNEL | *(removed — no numbered section kickers)* |
| TELEMETRY HUB | *(removed)* |
| Core Diagnostic Signals | **Key numbers** |
| The Fundamental Asymmetry of Photo Retrieval | **Why photo search breaks down** |
| The 4 Retrieval Breakdown Stages (Bucket A) | **Where search goes wrong** |
| Sub-Category Evidence Ranking | **Detailed breakdown** |
| Verbatim Grounded Substrings | **Real user quotes** |
| Cognitive Recall Analysis | *(removed)* |
| The Memory Cue Spectrum: What Humans Remember | **What users actually remember** |
| Retrieval Engine Showdown | **Classic search vs. AI search** |
| Prioritized Roadmap | *(removed)* |
| Case Study Alignment | *(removed)* |
| Direct Quote-Grounded Answers to Core Questions | **Answers to the core questions** |
| Visual Memory Pathology (10 Inquiries) | **Deep-dive research questions** |
| SIGNAL SYNTHESIS | *(removed)* |
| GROUNDED RESEARCH | *(removed)* |

### Data Units

| Internal Term | Dashboard Term |
|:---|:---|
| tag / failure tag | **mention** (e.g., "mentioned 94 times") |
| doc / docs | **review** or **reviews** |
| on-brief | **search-related** |
| Conf: 0.89 | **High confidence** (see tiers below) |

### Confidence Tiers

| Score Range | Dashboard Display |
|:---|:---|
| ≥ 0.85 | **High confidence** — directly stated by multiple users |
| 0.70 – 0.84 | **Moderate confidence** — supported by clear evidence |
| < 0.70 | **Lower confidence** — limited or indirect evidence |

---

## Semantic Color System

Colors on the dashboard are not decorative — each maps to a specific category of meaning.

| Color | Hex | Meaning | Used For |
|:---|:---|:---|:---|
| **Blue** | `#3b82f6` | Search friction findings | Search-related review counts, primary findings, "where search goes wrong" stages, CTAs |
| **Gray** | `#64748b` | Filtered-out / context | Non-search categories (App & Backup, Layout, General), supporting detail, secondary text |
| **Amber** | `#f59e0b` | Warnings & caveats | Data limitations, uncertainty notices, "this is an estimate" labels |
| **Green** | `#22c55e` | Verified / confidence | Verification badges, "how we made sure this is accurate", high-confidence indicators |

### Color Usage Rules

1. **Primary findings and interactive elements** use Blue.
2. **Categories that were filtered out** (Buckets B, C, D) use Gray — they are context, not findings.
3. **Anywhere we flag uncertainty** (e.g., "Outcome Not Stated: 91%", legacy data provenance, estimates) uses Amber.
4. **Verification and trust signals** (e.g., "every quote verified word-for-word") use Green.
5. No other accent colors are used for semantic meaning. Charts may use lighter/darker variants of these four.

---

## RAG System Prompt — Plain Language Directive

The RAG query engine (`pipeline/rag/query_engine.py`) system prompt has been updated to use the same plain-language terminology documented above when generating conversational responses. Specifically:

- Uses "search-related reviews" instead of "Bucket A docs"
- Uses "mentioned X times" instead of "X failure tags"
- Uses stage names like "search misunderstands them" instead of "interpretation failure"
- Cites confidence as plain tiers ("High confidence") rather than bare decimals
- Still grounds every finding in real numbers and verbatim quotes

This ensures the one dynamically-generated part of the dashboard (the Ask feature) speaks the same language as the static UI.

---

*This reference document is maintained alongside the dashboard codebase. Internal code keys and JSON field names remain unchanged — only user-facing display text is affected.*
