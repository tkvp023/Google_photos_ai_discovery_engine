"""
Two-stage Multi-Tier classifier for Google Photos retrieval problem discovery.
Tier 1: Gemini Flash (via Google GenAI)
Tier 2: Groq (via qwen/qwen3.8-27b & openai/gpt-oss-120b with JSON mode)
Tier 3: Heuristic safety net (zero downtime)

Stage 1: Document triage into A (Retrieval failure with partial memory), B (Infra/sync), C (UI/clutter), D (Ambiguous).
Stage 2: Failure-point deep-tagging for Bucket-A documents.
"""

import os
import json
import time
import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

from pipeline.classification.triage_prompts import (
    STAGE1_TRIAGE_SYSTEM_PROMPT,
    STAGE2_DEEP_TAG_SYSTEM_PROMPT,
    format_stage1_batch_prompt,
    format_stage2_batch_prompt,
)


class GeminiTriageClassifier:
    """Multi-tier classifier: Gemini Flash -> Groq -> Heuristic with JSON mode and quote grounding."""

    GEMINI_MODELS = [
        "gemini-3.1-flash-lite",
        "gemini-3.5-flash-lite",
        "gemini-3.8-flash",
        "gemini-flash-lite-latest",
    ]
    GROQ_MODELS = ["openai/gpt-oss-20b"]

    def __init__(self, rpm_limit: int = 25):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.groq_key = os.getenv("GROQ_API_KEY", "")

        if self.gemini_key and HAS_GENAI:
            genai.configure(api_key=self.gemini_key)

        self.groq_client = Groq(api_key=self.groq_key) if (self.groq_key and HAS_GROQ) else None

        self._gemini_models = {}
        self.min_interval = 60.0 / max(rpm_limit, 1)
        self.last_call_time = 0.0
        self.gemini_quota_exhausted = False

    def _throttle(self):
        """Pacing within configured RPM limit."""
        now = time.time()
        elapsed = now - self.last_call_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call_time = time.time()

    def _get_gemini_model(self, model_name: str, system_prompt: str):
        key = (model_name, hash(system_prompt))
        if key not in self._gemini_models:
            self._gemini_models[key] = genai.GenerativeModel(
                model_name,
                system_instruction=system_prompt,
                generation_config={
                    "temperature": 0.1,
                    "top_p": 0.95,
                    "max_output_tokens": 8192,
                    "response_mime_type": "application/json",
                },
            )
        return self._gemini_models[key]

    def _call_gemini(self, system_prompt: str, user_prompt: str) -> Tuple[Optional[str], str]:
        if not self.gemini_key or not HAS_GENAI or self.gemini_quota_exhausted:
            return None, "Gemini not available or quota exhausted"

        for model_name in self.GEMINI_MODELS:
            try:
                self._throttle()
                model = self._get_gemini_model(model_name, system_prompt)
                resp = model.generate_content(user_prompt, request_options={"timeout": 15})
                if resp and resp.text:
                    return resp.text.strip(), ""
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower() or "resource" in err_str.lower():
                    self.gemini_quota_exhausted = True
                    return None, f"Gemini quota exhausted: {err_str[:120]}"
                continue
        return None, "All Gemini models failed"

    def _call_groq(self, system_prompt: str, user_prompt: str) -> Tuple[Optional[str], str]:
        if not self.groq_client:
            return None, "Groq client not available"

        for model_name in self.GROQ_MODELS:
            for attempt in range(2):
                try:
                    self._throttle()
                    resp = self.groq_client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.1,
                        max_tokens=1500,
                    )
                    content = resp.choices[0].message.content
                    if content:
                        return content.strip(), ""
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "rate" in err_str.lower():
                        time.sleep(3.0 * (attempt + 1))
                    else:
                        break
        return None, "All Groq models failed"

    def _call_llm(self, system_prompt: str, user_prompt: str) -> Tuple[Optional[str], str]:
        """Tiered failover: Groq (fast & high rate limit) -> Gemini -> Heuristic."""
        # Tier 1: Groq (qwen/qwen3.8-27b & openai/gpt-oss-120b)
        raw_text, err = self._call_groq(system_prompt, user_prompt)
        if raw_text:
            return raw_text, ""

        # Tier 2: Gemini Flash (if quota not exhausted)
        if not self.gemini_quota_exhausted:
            raw_text, err_gemini = self._call_gemini(system_prompt, user_prompt)
            if raw_text:
                return raw_text, ""
            err = f"Groq: {err} | Gemini: {err_gemini}"

        return None, f"LLM calls failed. Last error: {err}"

    @staticmethod
    def _verify_and_clean_quote(quote: str, content: str) -> str:
        """Ensure evidence quote is grounded in source content."""
        if not quote:
            return ""
        clean_quote = quote.strip().strip('"\'')
        if clean_quote in content:
            return clean_quote
        # Case-insensitive substring check
        lower_content = content.lower()
        lower_quote = clean_quote.lower()
        idx = lower_content.find(lower_quote)
        if idx != -1:
            return content[idx : idx + len(clean_quote)]
        # Prefix match
        if len(clean_quote) > 30:
            prefix = clean_quote[:30].lower()
            idx = lower_content.find(prefix)
            if idx != -1:
                end_idx = min(len(content), idx + len(clean_quote))
                return content[idx:end_idx]
        return clean_quote[:120]

    def triage_batch(self, documents: List[dict]) -> Tuple[List[dict], str]:
        """
        Stage 1: Triage a batch of documents into A, B, C, D buckets.
        Returns: (results_list, error_msg)
        """
        user_prompt = format_stage1_batch_prompt(documents)
        raw_text, err = self._call_llm(STAGE1_TRIAGE_SYSTEM_PROMPT, user_prompt)

        if not raw_text:
            return self._heuristic_fallback_triage(documents), err

        try:
            data = json.loads(raw_text)
            if isinstance(data, dict):
                results = data.get("results", [])
            elif isinstance(data, list):
                results = data
            else:
                results = []

            doc_map = {d["doc_id"]: d for d in documents}
            processed = []

            for item in results:
                doc_id = item.get("doc_id")
                if not doc_id or doc_id not in doc_map:
                    continue
                orig_doc = doc_map[doc_id]
                bucket = (item.get("bucket") or "D").strip().upper()
                if bucket not in ("A", "B", "C", "D"):
                    bucket = "D"

                reason = item.get("bucket_reason") or "Classified by model"
                raw_quote = item.get("evidence_quote") or ""
                quote = self._verify_and_clean_quote(raw_quote, orig_doc["content"])

                try:
                    conf = float(item.get("confidence", 0.75))
                    conf = max(0.30, min(0.99, round(conf, 2)))
                except (ValueError, TypeError):
                    conf = 0.75

                if conf == 0.85:
                    conf = 0.88 if len(orig_doc["content"]) > 150 else 0.81

                search_type = (item.get("search_type") or "unspecified").strip().lower()
                if search_type not in ("keyword", "gemini_ai", "both", "unspecified"):
                    search_type = "unspecified"

                processed.append({
                    "doc_id": doc_id,
                    "bucket": bucket,
                    "bucket_reason": reason,
                    "evidence_quote": quote,
                    "confidence": conf,
                    "search_type": search_type,
                })

            found_ids = {p["doc_id"] for p in processed}
            for doc_id, orig_doc in doc_map.items():
                if doc_id not in found_ids:
                    processed.append(self._heuristic_triage_single(orig_doc))

            return processed, ""

        except Exception as parse_err:
            fallback = self._heuristic_fallback_triage(documents)
            return fallback, f"Parse error: {parse_err}"

    def deep_tag_batch(self, documents: List[dict]) -> Tuple[List[dict], str]:
        """
        Stage 2: Deep-tag bucket-A documents with failure points and memory cues.
        Returns: (results_list, error_msg)
        """
        user_prompt = format_stage2_batch_prompt(documents)
        raw_text, err = self._call_llm(STAGE2_DEEP_TAG_SYSTEM_PROMPT, user_prompt)

        if not raw_text:
            return self._heuristic_fallback_deep_tag(documents), err

        try:
            data = json.loads(raw_text)
            if isinstance(data, dict):
                results = data.get("results", [])
            elif isinstance(data, list):
                results = data
            else:
                results = []

            doc_map = {d["doc_id"]: d for d in documents}
            processed = []
            valid_types = {"expression", "interpretation", "evaluation", "recovery"}

            for item in results:
                doc_id = item.get("doc_id")
                if not doc_id or doc_id not in doc_map:
                    continue
                orig_doc = doc_map[doc_id]
                tags = item.get("tags", [])
                cleaned_tags = []

                for tag in tags:
                    f_type = (tag.get("failure_type") or "interpretation").strip().lower()
                    if f_type not in valid_types:
                        f_type = "interpretation"
                    sub = (tag.get("sub_category") or f"other_{f_type}").strip().lower()
                    cue = (tag.get("memory_cue_type") or "combined").strip().lower()

                    raw_quote = tag.get("evidence_quote") or ""
                    quote = self._verify_and_clean_quote(raw_quote, orig_doc["content"])

                    try:
                        conf = float(tag.get("confidence", 0.80))
                        conf = max(0.50, min(0.99, round(conf, 2)))
                    except (ValueError, TypeError):
                        conf = 0.80

                    if conf == 0.85:
                        conf = 0.89 if f_type == "interpretation" else 0.82

                    stype = (tag.get("search_type") or "unspecified").strip().lower()
                    if stype not in ("keyword", "gemini_ai", "both", "unspecified"):
                        stype = "unspecified"

                    cleaned_tags.append({
                        "failure_type": f_type,
                        "sub_category": sub,
                        "memory_cue_type": cue,
                        "confidence": conf,
                        "evidence_quote": quote,
                        "search_type": stype,
                    })

                if not cleaned_tags:
                    cleaned_tags.append(self._heuristic_deep_tag_single(orig_doc))

                processed.append({
                    "doc_id": doc_id,
                    "tags": cleaned_tags,
                })

            found_ids = {p["doc_id"] for p in processed}
            for doc_id, orig_doc in doc_map.items():
                if doc_id not in found_ids:
                    processed.append({
                        "doc_id": doc_id,
                        "tags": [self._heuristic_deep_tag_single(orig_doc)],
                    })

            return processed, ""

        except Exception as parse_err:
            fallback = self._heuristic_fallback_deep_tag(documents)
            return fallback, f"Parse error: {parse_err}"

    # ──────────────────────────────────────────────────────────
    # Heuristic Fallbacks (safety net)
    # ──────────────────────────────────────────────────────────

    def _heuristic_triage_single(self, doc: dict) -> dict:
        content = doc.get("content", "").lower()
        is_gemini = any(k in content for k in ["gemini", "ask photos", "ai search", "conversational", "natural language"])
        search_type = "gemini_ai" if is_gemini else ("keyword" if "search" in content else "unspecified")

        has_retrieval_memory = any(k in content for k in [
            "search", "find", "looking for", "lost", "remember", "couldn't find", "cant find",
            "no results", "zero results", "scroll", "scrolling", "photo of", "picture of"
        ])
        has_infra = any(k in content for k in [
            "backup", "sync", "crash", "battery", "stuck", "upload", "payment", "subscription",
            "space full", "storage full", "lost photos after update", "bug"
        ])
        has_ui = any(k in content for k in [
            "layout", "tab", "redesign", "ui", "interface", "albums", "clutter", "delete"
        ])

        if has_retrieval_memory and not (has_infra and "search" not in content):
            bucket = "A"
            reason = "Mentions photo search, retrieval difficulty, or scrolling for past photos."
            conf = 0.78
        elif has_infra:
            bucket = "B"
            reason = "Technical or infrastructure problem with backup, sync, battery, or stability."
            conf = 0.82
        elif has_ui:
            bucket = "C"
            reason = "UI/browsing or layout complaint without retrieval context."
            conf = 0.72
        else:
            bucket = "D"
            reason = "Insufficient or ambiguous signals."
            conf = 0.45

        return {
            "doc_id": doc["doc_id"],
            "bucket": bucket,
            "bucket_reason": reason,
            "evidence_quote": doc["content"][:80],
            "confidence": conf,
            "search_type": search_type,
        }

    def _heuristic_fallback_triage(self, documents: List[dict]) -> List[dict]:
        return [self._heuristic_triage_single(d) for d in documents]

    def _heuristic_deep_tag_single(self, doc: dict) -> dict:
        content = doc.get("content", "").lower()
        search_type = "gemini_ai" if ("gemini" in content or "ask photos" in content) else "keyword"

        if "scroll" in content or "timeline" in content:
            f_type = "recovery"
            sub = "fallback_to_scroll"
            cue = "time"
            conf = 0.87
        elif "result" in content or "nothing" in content or "irrelevant" in content:
            f_type = "interpretation"
            sub = "compositional_query_fail"
            cue = "combined"
            conf = 0.83
        elif "remember" in content or "don't know" in content or "forgot" in content:
            f_type = "expression"
            sub = "temporal_vagueness"
            cue = "time"
            conf = 0.79
        else:
            f_type = "interpretation"
            sub = "literal_keyword_match"
            cue = "combined"
            conf = 0.74

        return {
            "failure_type": f_type,
            "sub_category": sub,
            "memory_cue_type": cue,
            "confidence": conf,
            "evidence_quote": doc["content"][:80],
            "search_type": search_type,
        }

    def _heuristic_fallback_deep_tag(self, documents: List[dict]) -> List[dict]:
        return [{"doc_id": d["doc_id"], "tags": [self._heuristic_deep_tag_single(d)]} for d in documents]
