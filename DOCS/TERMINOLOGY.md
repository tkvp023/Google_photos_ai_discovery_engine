# Terminology Reference — Google Photos AI Discovery Engine

This document maps internal pipeline terminology to the executive, plain-language labels shown across the Google Photos AI Discovery Engine dashboard and reports. It also documents the semantic color system and quote grounding standards.

---

## 1. Multi-Platform Channels (1,616 In-Scope Search Reviews)

The Discovery Engine analyzes genuine user discussions and customer reviews describing visual memory search failures across 5 platform channels:

| Platform Code | Platform Channel | Review Count | Pct of Corpus | Nature of Channel |
|:---|:---|---:|---:|:---|
| `playstore` | **Google Play Store** | 969 | 60.0% | Consumer Android app store reviews detailing search failures |
| `hackernews` | **Hacker News** | 455 | 28.2% | Deep technical engineering discussions on vector indexing & CLIP limits |
| `appstore` | **Apple App Store** | 111 | 6.9% | Consumer iOS reviews detailing search regressions & layout shifts |
| `reddit` | **Reddit** | 54 | 3.3% | Community troubleshooting threads across r/googlephotos and r/android |
| `youtube` | **YouTube** | 27 | 1.7% | User comments on Ask Photos demo videos and search tutorials |

---

## 2. Cognitive Failure Stages

When users attempt to retrieve a remembered photo with incomplete memory, breakdowns occur across four distinct cognitive stages:

| Stage Key | Pipeline Label | Dashboard Label | Plain Description | Corpus Count |
|:---|:---|:---|:---|---:|
| `expression` | Formulation Failure / Stage 1 | **Can't find the right words** | Users struggle to translate fuzzy, abstract memories into rigid search terms | 953 reviews (59.0%) |
| `interpretation` | Interpretation Failure / Stage 2 | **Search misunderstands query** | Google Photos takes terms too literally or hallucinates semantic associations | 628 reviews (38.9%) |
| `recovery` | Recovery Failure / Stage 3 | **No help when search fails** | System shows zero results and offers no interactive refinement or suggestions | 26 reviews (1.6%) |
| `evaluation` | Evaluation Failure / Stage 4 | **Can't spot the right photo** | Results are returned but the target photo is lost among clutter or burst shots | 9 reviews (0.6%) |

---

## 3. Executive Label Mappings

| Technical / Internal Key | Executive Dashboard Label |
|:---|:---|
| Total Search Corpus | **Reviews analyzed (1,616)** |
| In-Scope Problem Signal | **Search-related reviews (1,616)** |
| Stage 1: Expression Failure | **#1 Gap: Can't find the right words (953)** |
| Stage 2: Interpretation Failure | **#2 Gap: Search misunderstands query (628)** |
| Stage 3: Recovery Failure | **#3 Gap: No help when search fails (26)** |
| Stage 4: Evaluation Failure | **#4 Gap: Can't spot the right photo (9)** |
| Zero Results for Existing Photos | **"No results" for photos that exist** |
| Timeline Scroll Fallback | **Forced to endless chronological grid scroll** |
| Calibrated Confidence (±0.18 σ) | **Data confidence score** |

---

## 4. Semantic Color System

Colors across the engine and dashboard follow a strict, semantic design grammar:

| Color | Hex | Meaning | Used For |
|:---|:---|:---|:---|
| **Blue** | `#3b82f6` | Core Search Findings | Primary search friction counts, stage navigation, interactive CTAs |
| **Teal / Cyan** | `#06b6d4` | Platform Channels | Source channel badges, technical community metrics, API telemetry |
| **Amber** | `#f59e0b` | Friction & Limitations | Cognitive failure patterns, recovery dead-ends, confidence tier alerts |
| **Green** | `#22c55e` | Verified Grounding | 100% exact substring quote badges, certified zero-hallucination audits |
| **Slate Gray** | `#64748b` | Structural Context | Secondary labels, timestamps, metadata borders |

---

## 5. Confidence Tiers

Every document and insight carries an evidence-calibrated confidence score calculated from verbatim substring density and sentiment calibration:

| Score Range | Dashboard Display | Definition |
|:---|:---|:---|
| **≥ 0.85** | **High confidence** | Directly articulated by multiple users with explicit failure quotes |
| **0.70 – 0.84** | **Moderate confidence** | Supported by strong multi-sentence descriptive evidence |
| **< 0.70** | **Lower confidence** | Short commentary or indirect contextual signals |

---

## 6. Grounded RAG Query Directive

The RAG query engine (`pipeline/rag/query_engine.py`) generates executive conversational responses adhering to these terminology rules:
- Cites exact review numbers from the verified **1,616 Search Corpus**.
- Cites cognitive breakdown stages using clear executive titles (*"Can't find the right words"*, *"Search misunderstands query"*).
- Displays quote snippets verbatim with platform attribution and confidence score.
- Eliminates any obsolete classification codes, legacy abbreviations, or ungrounded claims.
