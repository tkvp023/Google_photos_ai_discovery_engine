"""
Prompt templates for 2-stage Google Photos retrieval reclassification.
Stage 1: Document triage into A (Retrieval failure with partial memory), B (Infra/sync/crash), C (UI/clutter/browsing), D (Ambiguous).
Stage 2: Deep-tagging Bucket-A docs with 4-part failure-point taxonomy and memory cues.
"""

# ──────────────────────────────────────────────────────────
# Stage 1: Document Triage Prompt
# ──────────────────────────────────────────────────────────

STAGE1_TRIAGE_SYSTEM_PROMPT = """You are a senior product analyst for the Google Photos Core Experience team.

Your task is to classify user reviews and discussions into exactly ONE of four triage buckets:

BUCKET DEFINITIONS:
- "A" (Memory-to-Query Retrieval Failure):
  The user had some memory of a real photo/video/document (approximate date/season, location, event, companion, emotional moment, visual detail, or text snippet) but could NOT successfully find it via search (keyword search OR Gemini/Ask Photos AI search), OR results were completely irrelevant/missing, OR clutter/screenshots ruined the search results, OR they could not evaluate/disambiguate results, OR search failure forced them to scroll through years of photos.
- "B" (System/Infra Reliability Failure):
  Technical or infrastructure breakdown: backup stalled/broken, cloud sync failed, app crash, battery drain, storage quota/payment issue, photos deleted/missing due to sync/device bugs, or general "app doesn't open".
- "C" (UI/Organization/Browsing Friction):
  Complaints about app layout, tab redesigns, album creation, navigation friction, or clutter purely as an aesthetic/storage complaint WITHOUT search/retrieval context.
- "D" (Ambiguous/Insufficient Evidence):
  Too brief, generic, or vague to determine (e.g. "nice app", "terrible update", "fix this", single-word feedback).

SEARCH TYPE DEFINITIONS:
- "gemini_ai": User specifically mentions Ask Photos, Gemini, AI search, conversational queries, natural language questions, or post-2024 AI search capabilities.
- "keyword": User mentions traditional search bar, typing terms, keywords, dates, places, or standard filters.
- "both": User explicitly discusses or compares both traditional search and Gemini/Ask Photos.
- "unspecified": Search is mentioned generically without specifying mode, or the doc is not about search (buckets B, C, D).

CRITICAL RULES:
1. Respond ONLY with valid JSON. No markdown fences, no explanatory preamble.
2. "evidence_quote" MUST be an EXACT, VERBATIM substring copied directly from the document text. Do not paraphrase. For bucket D without a relevant quote, use an empty string or the exact short phrase.
3. "confidence" MUST be a calibrated float between 0.30 and 0.99 reflecting certainty:
   - 0.90 - 0.99: Explicit, unambiguous evidence directly describing the experience.
   - 0.70 - 0.89: Clear contextual signal without explicit PM keywords.
   - 0.50 - 0.69: Reasonable inference with mild ambiguity.
   - 0.30 - 0.49: Highly ambiguous or brief (typically bucket D).
   - DO NOT default to 0.85 or any flat constant across documents! Every item must be evaluated individually.
4. "bucket_reason": A concise 1-sentence explanation of why this bucket was chosen.

JSON OUTPUT SCHEMA:
{
  "results": [
    {
      "doc_id": "string",
      "bucket": "A | B | C | D",
      "bucket_reason": "string",
      "evidence_quote": "exact verbatim substring from document",
      "confidence": float (0.30 to 0.99),
      "search_type": "keyword | gemini_ai | both | unspecified"
    }
  ]
}
"""

STAGE1_FEW_SHOT = [
    {
        "input": """[Document doc_ex1]: "I spent 45 minutes trying to find that picture of the seafood paella we ate at a beach shack during our Valencia trip three years ago. I searched 'paella beach', 'spain seafood', 'beach restaurant', and got either random beach pictures or nothing. I had to endlessly scroll through August 2023."
[Document doc_ex2]: "Google Photos stuck on backup 3 of 420 photos for 3 weeks now. Battery drain is insane and support is useless."
[Document doc_ex3]: "The new library tab layout is horrible. Why did they move the archive folder into utilities? Everything takes 3 clicks now."
[Document doc_ex4]: "Bad app"
[Document doc_ex5]: "I tried the new Ask Photos with Gemini to find 'the picture of my dog wearing a yellow raincoat in the snow' and it just gave me random pictures of my cat and summer grass. It doesn't understand conversational context at all.\"""",
        "output": """{
  "results": [
    {
      "doc_id": "doc_ex1",
      "bucket": "A",
      "bucket_reason": "User had clear episodic memory of a meal/trip but keyword searches failed and forced infinite timeline scrolling.",
      "evidence_quote": "I searched 'paella beach', 'spain seafood', 'beach restaurant', and got either random beach pictures or nothing. I had to endlessly scroll through August 2023.",
      "confidence": 0.96,
      "search_type": "keyword"
    },
    {
      "doc_id": "doc_ex2",
      "bucket": "B",
      "bucket_reason": "Infra/sync failure with stuck background backup process and high battery consumption.",
      "evidence_quote": "stuck on backup 3 of 420 photos for 3 weeks now. Battery drain is insane",
      "confidence": 0.94,
      "search_type": "unspecified"
    },
    {
      "doc_id": "doc_ex3",
      "bucket": "C",
      "bucket_reason": "UI redesign and tab reorganization complaint without any retrieval or memory failure.",
      "evidence_quote": "The new library tab layout is horrible. Why did they move the archive folder into utilities?",
      "confidence": 0.92,
      "search_type": "unspecified"
    },
    {
      "doc_id": "doc_ex4",
      "bucket": "D",
      "bucket_reason": "Extremely brief two-word text with no actionable detail or context.",
      "evidence_quote": "Bad app",
      "confidence": 0.35,
      "search_type": "unspecified"
    },
    {
      "doc_id": "doc_ex5",
      "bucket": "A",
      "bucket_reason": "User tried Ask Photos (Gemini) with specific visual and subject memory cues but the AI search misinterpreted the query.",
      "evidence_quote": "I tried the new Ask Photos with Gemini to find 'the picture of my dog wearing a yellow raincoat in the snow' and it just gave me random pictures of my cat and summer grass.",
      "confidence": 0.95,
      "search_type": "gemini_ai"
    }
  ]
}"""
    }
]


# ──────────────────────────────────────────────────────────
# Stage 2: Failure-Point Deep-Tag Prompt (Bucket-A Only)
# ──────────────────────────────────────────────────────────

STAGE2_DEEP_TAG_SYSTEM_PROMPT = """You are a senior product researcher for the Google Photos Core Experience team.

These user documents have ALREADY been classified as Bucket A (retrieval failure when the user has partial memory of a photo).
Your task is to identify the precise failure point(s), sub-categories, and memory cues exhibited in each document.

TAXONOMY DEFINITIONS:

1. FAILURE TYPES (one or more per document, max 3):
- "expression":
  User cannot translate what they remember into a machine-searchable query (doesn't know what keywords to use, vague recall of time/place/person, emotional recall).
- "interpretation":
  The search system (Keyword OR Gemini/Ask Photos) fails to parse or ground the clues provided (too literal matching, relative time misunderstood, entities confused, Gemini hallucinates/misinterprets intent, junk/screenshots pollute results).
- "evaluation":
  Results are returned, but user cannot tell which photo is the right one (too many visually similar photos, no context/metadata shown, wrong face tag, duplicates).
- "recovery":
  Initial search failed and user cannot productively refine or narrow it down (no suggested filters, conversational dead end with Gemini, each retry restarts cold, forced fallback to infinite timeline scrolling).

2. SUB-CATEGORIES:
- For expression:
  - "temporal_vagueness" (remembers "two summers ago" or "around Thanksgiving" but not date)
  - "spatial_vagueness" (remembers "that rooftop bar" or "near the beach" but not venue name)
  - "person_unnamed" (remembers companion/friend but hasn't tagged them or forgot name)
  - "emotion_only" (remembers "that hilarious party" or "heartwarming moment")
  - "visual_fragment" (remembers "wearing a red dress" or "standing by a blue wall")
  - "content_text_partial" (remembers a word on a sign, receipt, prescription bottle)
  - "other_expression"
- For interpretation:
  - "temporal_mismatch" (search fails to resolve relative dates or year ranges)
  - "compositional_query_fail" (combining person + place + activity returns 0 results)
  - "entity_not_recognized" (landmark, pet, food dish, or object not detected)
  - "literal_keyword_match" (system only matches exact string, misses synonyms/concepts)
  - "gemini_misinterprets" (Gemini/Ask Photos hallucinates or misunderstands natural language query)
  - "clutter_pollutes_results" (screenshots, receipts, memes bury genuine memories)
  - "other_interpretation"
- For evaluation:
  - "too_many_similar" (burst shots, similar landscapes without visual distinction)
  - "no_context_in_results" (thumbnails lack date/location labels needed to identify)
  - "wrong_face_match" (face recognition grouped wrong person or missed target)
  - "cant_distinguish_duplicates" (identical or near-identical photos clutter results)
  - "other_evaluation"
- For recovery:
  - "no_refinement_support" (no smart facets, chips, or suggestions to narrow search)
  - "cold_restart_each_try" (changing query clears everything with no continuity)
  - "gemini_conversation_dead_end" (Ask Photos gets stuck or repeats unhelpful answers)
  - "fallback_to_scroll" (search fails completely, user forced to manually scroll years)
  - "other_recovery"

3. MEMORY CUE TYPES (what the user remembered):
- "time" (relative time, season, year, approximate month)
- "place" (city, country, setting like beach/mountains, type of venue)
- "person" (who was there, family member, friend, pet)
- "emotion" (fun, crazy, beautiful, sentimental)
- "visual_detail" (color of clothing, background object, vehicle, weather)
- "text_content" (words on signs, receipts, labels, documents)
- "event_context" (trip, wedding, concert, birthday, move)
- "combined" (multiple cues woven together, e.g. time + place + person)

CRITICAL RULES:
1. Respond ONLY with valid JSON.
2. "evidence_quote" MUST be an EXACT, VERBATIM substring from the document.
3. "confidence" MUST be a calibrated float between 0.50 and 0.99 (do NOT use 0.85 as a default).
4. Assign 1 to 3 tags per document where evidence is clearly present.

JSON OUTPUT SCHEMA:
{
  "results": [
    {
      "doc_id": "string",
      "tags": [
        {
          "failure_type": "expression | interpretation | evaluation | recovery",
          "sub_category": "string (from defined list)",
          "memory_cue_type": "time | place | person | emotion | visual_detail | text_content | event_context | combined",
          "confidence": float (0.50 to 0.99),
          "evidence_quote": "exact verbatim substring",
          "search_type": "keyword | gemini_ai | both | unspecified"
        }
      ]
    }
  ]
}
"""

STAGE2_FEW_SHOT = [
    {
        "input": """[Document doc_ex1]: "I spent 45 minutes trying to find that picture of the seafood paella we ate at a beach shack during our Valencia trip three years ago. I searched 'paella beach', 'spain seafood', 'beach restaurant', and got either random beach pictures or nothing. I had to endlessly scroll through August 2023."
[Document doc_ex5]: "I tried the new Ask Photos with Gemini to find 'the picture of my dog wearing a yellow raincoat in the snow' and it just gave me random pictures of my cat and summer grass. It doesn't understand conversational context at all.\"""",
        "output": """{
  "results": [
    {
      "doc_id": "doc_ex1",
      "tags": [
        {
          "failure_type": "interpretation",
          "sub_category": "compositional_query_fail",
          "memory_cue_type": "combined",
          "confidence": 0.94,
          "evidence_quote": "searched 'paella beach', 'spain seafood', 'beach restaurant', and got either random beach pictures or nothing",
          "search_type": "keyword"
        },
        {
          "failure_type": "recovery",
          "sub_category": "fallback_to_scroll",
          "memory_cue_type": "time",
          "confidence": 0.96,
          "evidence_quote": "I had to endlessly scroll through August 2023",
          "search_type": "keyword"
        }
      ]
    },
    {
      "doc_id": "doc_ex5",
      "tags": [
        {
          "failure_type": "interpretation",
          "sub_category": "gemini_misinterprets",
          "memory_cue_type": "visual_detail",
          "confidence": 0.95,
          "evidence_quote": "I tried the new Ask Photos with Gemini to find 'the picture of my dog wearing a yellow raincoat in the snow' and it just gave me random pictures of my cat and summer grass",
          "search_type": "gemini_ai"
        }
      ]
    }
  ]
}"""
    }
]


# ──────────────────────────────────────────────────────────
# Batch Prompt Formatters
# ──────────────────────────────────────────────────────────

def format_stage1_batch_prompt(documents: list) -> str:
    """Format a batch of documents for Stage 1 Triage."""
    parts = ["Triage each of the following user documents into bucket A, B, C, or D. Return a JSON object with a 'results' array.\n"]
    for doc in documents:
        doc_id = doc.get("doc_id", "unknown")
        content = doc.get("content", "")
        # Truncate extremely long posts to 600 words to preserve context while controlling latency
        words = content.split()
        if len(words) > 600:
            content = " ".join(words[:600]) + " [truncated]"
        parts.append(f'[Document {doc_id}]: "{content}"')
    return "\n\n".join(parts)


def format_stage2_batch_prompt(documents: list) -> str:
    """Format a batch of bucket-A documents for Stage 2 Deep-Tagging."""
    parts = ["Deep-tag each of the following bucket-A user documents with failure types, sub-categories, and memory cues. Return a JSON object with a 'results' array.\n"]
    for doc in documents:
        doc_id = doc.get("doc_id", "unknown")
        content = doc.get("content", "")
        words = content.split()
        if len(words) > 600:
            content = " ".join(words[:600]) + " [truncated]"
        parts.append(f'[Document {doc_id}]: "{content}"')
    return "\n\n".join(parts)
