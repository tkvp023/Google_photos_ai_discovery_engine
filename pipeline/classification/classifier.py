"""
Multi-tier LLM classifier.
Tiered failover: Gemini 3.7 Flash → Groq Llama 3.3 → Ollama → Keyword tagger.
"""

import os
import json
import time
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

from pipeline.classification.prompts import SYSTEM_PROMPT, format_batch_prompt, build_few_shot_messages
from pipeline.classification.keyword_tagger import classify_with_keywords
from pipeline.classification.schema import empty_classification


# ──────────────────────────────────────────────────────────
# Tier 1: Gemini 3.7 Flash
# ──────────────────────────────────────────────────────────

class GeminiClassifier:
    """Google Gemini Flash classifier with JSON mode and multi-model fallback."""

    CANDIDATE_MODELS = [
        "gemini-3.6-flash",
        "gemini-3.8-flash",
        "gemini-3.7-flash",
    ]

    def __init__(self):
        pref = os.getenv("GEMINI_MODEL")
        if pref and pref not in self.CANDIDATE_MODELS:
            self.models_to_try = [pref] + self.CANDIDATE_MODELS
        elif pref:
            self.models_to_try = [pref] + [m for m in self.CANDIDATE_MODELS if m != pref]
        else:
            self.models_to_try = list(self.CANDIDATE_MODELS)
        self._clients = {}

    @property
    def api_key(self) -> Optional[str]:
        return os.getenv("GEMINI_API_KEY")

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def _get_client(self, model_name: str):
        if model_name not in self._clients:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._clients[model_name] = genai.GenerativeModel(
                model_name,
                system_instruction=SYSTEM_PROMPT,
                generation_config={
                    "temperature": 0.1,
                    "top_p": 0.95,
                    "max_output_tokens": 12000,
                    "response_mime_type": "application/json",
                },
            )
        return self._clients[model_name]

    def classify(self, documents: List[dict]) -> Tuple[List[dict], str]:
        """
        Classify a batch of documents using Gemini, trying 3.7-flash first with failover to 3.6-flash.
        
        Returns:
            (classifications, error_or_empty_string)
        """
        prompt = format_batch_prompt(documents)
        last_error = ""

        for model_name in self.models_to_try:
            try:
                model = self._get_client(model_name)
                response = model.generate_content(prompt, request_options={"timeout": 25})
                text = response.text.strip()
                parsed = json.loads(text)

                if isinstance(parsed, dict):
                    if "results" in parsed:
                        parsed = parsed["results"]
                    elif "classifications" in parsed:
                        parsed = parsed["classifications"]
                    else:
                        parsed = [parsed]

                return parsed, ""

            except json.JSONDecodeError as e:
                last_error = f"JSON parse error from {model_name}: {e}"
                continue
            except Exception as e:
                error_str = str(e)
                last_error = f"{model_name} error: {error_str[:150]}"
                continue

        if "429" in last_error or "quota" in last_error.lower() or "resource" in last_error.lower():
            return [], f"QUOTA_EXHAUSTED: {last_error}"
        return [], last_error or "All Gemini models failed"


# ──────────────────────────────────────────────────────────
# Tier 2: Groq (Llama 3.3 70B)
# ──────────────────────────────────────────────────────────

class GroqClassifier:
    """Groq Llama 3.3 70B classifier with JSON mode."""

    def __init__(self):
        self.model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self._client = None

    @property
    def api_key(self) -> Optional[str]:
        return os.getenv("GROQ_API_KEY")

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def _get_client(self):
        if self._client is None:
            from groq import Groq
            self._client = Groq(api_key=self.api_key)
        return self._client

    def classify(self, documents: List[dict]) -> Tuple[List[dict], str]:
        """Classify a batch of documents using Groq."""
        client = self._get_client()
        prompt = format_batch_prompt(documents)

        for attempt in range(3):
            try:
                # Build messages with few-shot
                messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                few_shot = build_few_shot_messages()
                for msg in few_shot:
                    role = "assistant" if msg["role"] == "model" else msg["role"]
                    messages.append({"role": role, "content": msg["content"]})
                messages.append({"role": "user", "content": prompt})

                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=8000,
                    response_format={"type": "json_object"},
                )

                text = response.choices[0].message.content.strip()
                parsed = json.loads(text)

                if isinstance(parsed, dict):
                    # Groq may wrap in a top-level key
                    if "results" in parsed:
                        parsed = parsed["results"]
                    elif "classifications" in parsed:
                        parsed = parsed["classifications"]
                    else:
                        parsed = [parsed]

                return parsed, ""

            except json.JSONDecodeError as e:
                return [], f"JSON parse error: {e}"
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "rate" in error_str.lower():
                    if attempt < 2:
                        time.sleep(4 * (attempt + 1))
                        continue
                    return [], f"QUOTA_EXHAUSTED: {error_str[:100]}"
                return [], f"Groq error: {error_str[:200]}"


# ──────────────────────────────────────────────────────────
# Tier 3: Ollama (Local Llama 3.1 8B)
# ──────────────────────────────────────────────────────────

class OllamaClassifier:
    """Ollama local Llama 3.1 8B classifier."""

    def __init__(self):
        self.model_name = "llama3.1:8b"
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self._available = None

    @property
    def available(self) -> bool:
        if self._available is None:
            try:
                import requests
                r = requests.get(f"{self.base_url}/api/tags", timeout=3)
                if r.status_code == 200:
                    models = [m["name"] for m in r.json().get("models", [])]
                    self._available = any("llama3" in m for m in models)
                else:
                    self._available = False
            except Exception:
                self._available = False
        return self._available

    def classify(self, documents: List[dict]) -> Tuple[List[dict], str]:
        """Classify using local Ollama."""
        import requests

        prompt = format_batch_prompt(documents)
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "format": "json",
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 12000,
                    },
                },
                timeout=120,
            )
            response.raise_for_status()

            text = response.json().get("response", "").strip()
            parsed = json.loads(text)

            if isinstance(parsed, dict):
                parsed = [parsed]

            return parsed, ""

        except json.JSONDecodeError as e:
            return [], f"JSON parse error from Ollama: {e}"
        except Exception as e:
            return [], f"Ollama error: {str(e)[:200]}"


# ──────────────────────────────────────────────────────────
# Tier 4: Keyword Tagger (No LLM)
# ──────────────────────────────────────────────────────────

class KeywordClassifier:
    """Rule-based keyword tagger — always available."""

    @property
    def available(self) -> bool:
        return True

    def classify(self, documents: List[dict]) -> Tuple[List[dict], str]:
        results = []
        for doc in documents:
            result = classify_with_keywords(
                doc.get("doc_id", ""),
                doc.get("content", ""),
            )
            results.append(result)
        return results, ""


# ──────────────────────────────────────────────────────────
# Multi-Tier Classifier with Failover
# ──────────────────────────────────────────────────────────

class TieredClassifier:
    """
    Multi-tier classifier with automatic failover.
    
    Order: Gemini 3.7 Flash → Groq Llama 3.3 → Ollama → Keywords
    """

    TIER_NAMES = ["gemini", "groq", "ollama", "keyword"]

    def __init__(self):
        self.tiers = {
            "gemini": GeminiClassifier(),
            "groq": GroqClassifier(),
            "ollama": OllamaClassifier(),
            "keyword": KeywordClassifier(),
        }
        self.stats = {
            "gemini_calls": 0, "groq_calls": 0, "ollama_calls": 0, "keyword_calls": 0,
            "gemini_errors": 0, "groq_errors": 0, "ollama_errors": 0,
            "failovers": 0, "total_docs": 0,
        }
        # Track exhausted tiers (don't retry until reset)
        self._exhausted_tiers = set()

    def get_available_tiers(self) -> List[str]:
        """Return list of available tier names in order."""
        available = []
        for name in self.TIER_NAMES:
            if name not in self._exhausted_tiers and self.tiers[name].available:
                available.append(name)
        return available

    def classify_batch(
        self,
        documents: List[dict],
        preferred_tier: Optional[str] = None,
    ) -> Tuple[List[dict], str, str]:
        """
        Classify a batch of documents, with automatic failover.
        
        Args:
            documents: List of dicts with 'doc_id' and 'content'.
            preferred_tier: Optional tier to try first.
        
        Returns:
            (classifications, tier_used, error_or_empty)
        """
        tiers_to_try = self.get_available_tiers()

        # If preferred tier is specified and available, put it first
        if preferred_tier and preferred_tier in tiers_to_try:
            tiers_to_try.remove(preferred_tier)
            tiers_to_try.insert(0, preferred_tier)

        for tier_name in tiers_to_try:
            classifier = self.tiers[tier_name]

            try:
                results, error = classifier.classify(documents)

                if error:
                    self.stats[f"{tier_name}_errors"] = self.stats.get(f"{tier_name}_errors", 0) + 1

                    # Mark as exhausted if quota error
                    if "QUOTA_EXHAUSTED" in error:
                        self._exhausted_tiers.add(tier_name)
                        self.stats["failovers"] += 1
                        continue

                    # Retry on other errors only if not keyword tier
                    if tier_name != "keyword":
                        self.stats["failovers"] += 1
                        continue

                if results:
                    self.stats[f"{tier_name}_calls"] = self.stats.get(f"{tier_name}_calls", 0) + 1
                    self.stats["total_docs"] += len(documents)
                    return results, tier_name, ""

            except Exception as e:
                self.stats[f"{tier_name}_errors"] = self.stats.get(f"{tier_name}_errors", 0) + 1
                self.stats["failovers"] += 1
                continue

        # All tiers failed — return empty classifications
        empty = [empty_classification(d.get("doc_id", "")).model_dump() for d in documents]
        return empty, "none", "All classification tiers failed"

    def reset_exhausted(self):
        """Reset exhausted tiers (e.g., after quota resets)."""
        self._exhausted_tiers.clear()

    def get_stats(self) -> dict:
        """Return classification statistics."""
        return self.stats.copy()
