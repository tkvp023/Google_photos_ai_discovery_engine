# Google Photos Search-Only Retrieval Corpus — Collection Funnel Report

**Scope:** Strict Search-Based Retrieval (Collection-Level Scoping)  
**Classifier Suite:** Google Gemini Suite (gemini-3.1-flash-lite, gemini-3.1-flash-lite-preview)  
**Timestamp:** 2026-09-21 06:45:30 UTC  
**Quote Grounding Rate:** 100.0% Verifiable Substrings  

---

## 1. The Collection Funnel

| Stage | Document Count | Percentage of Raw Pool | Definition & Scope Boundary |
|:---|---:|---:|:---|
| **1. Total Raw Documents Reviewed** | **25,551** | **100.0%** | Multi-source collection across HN, Play Store, App Store, YouTube, Reddit |
| **2. Excluded (Out of Scope)** | **23,815** | **93.2%** | Manual timeline scroll without search, backup/sync errors, UI gripes, ratings |
| **3. Logged as Ambiguous** | **120** | **0.5%** | Unclear whether search was attempted; strictly excluded to protect data purity |
| **4. Retained Search-Only Corpus** | **1,616** | **6.3%** | **100% Verified Search-Based Retrieval Attempts** (Classic Keyword or Gemini/Ask Photos) |

---

## 2. Retrieval Flow Stage Tagging

Every retained document evidences one or more chronological stages of the retrieval journey:

$$\text{Intent} \rightarrow \text{Articulation} \rightarrow \text{Search} \rightarrow \text{Initial Results} \rightarrow \text{Scrolling Results} \rightarrow \text{Iterative Refinement} \rightarrow \text{Outcome}$$

| Flow Stage | Description | Documents Evidencing Stage | Share of Search Corpus |
|:---|:---|---:|---:|
| **Intent** | User remembers a specific photo/moment and intends to retrieve it | **877** | **54.3%** |
| **Articulation** | User phrases the memory into words, keywords, or conversational prompt | **339** | **21.0%** |
| **Search** | User executes search via search bar or Ask Photos AI | **1348** | **83.4%** |
| **Initial Results** | First results returned (irrelevant photos, zero results, accurate hit) | **593** | **36.7%** |
| **Scrolling Results** | Looking/skimming through returned search results to locate target photo | **92** | **5.7%** |
| **Iterative Refinement** | Trying another query, rephrasing, adding terms, or asking follow-ups | **33** | **2.0%** |
| **Outcome** | Finding the photo, giving up, abandoning search, or forced scroll fallback | **477** | **29.5%** |

---

## 3. Retained Search-Only Corpus by Source Platform

| Platform | Channel Nature | Retained Search Documents | Percentage of Search Corpus |
|:---|:---|---:|---:|
| **playstore** | Playstore | **969** | **60.0%** |
| **hackernews** | Hackernews | **455** | **28.2%** |
| **appstore** | Appstore | **111** | **6.9%** |
| **reddit** | Reddit | **54** | **3.3%** |
| **youtube** | Youtube | **27** | **1.7%** |
| **Total Retained** | **All 5 Channels** | **1,616** | **100.0%** |

---

## 4. Grounding & Storage Artifacts

- **Dedicated SQLite Database:** `data/search_only_corpus/search_only_corpus.sqlite`
- **Clean JSON Dataset:** `data/search_only_corpus/search_only_corpus.json`
- **Ambiguous Cases Log:** `data/search_only_corpus/ambiguous_excluded.json`
- **Verification:** 100.0% of quotes character-for-character verified against raw review text (`INSTR > 0`).
