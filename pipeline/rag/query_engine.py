"""
Query Engine — retrieves relevant documents from VectorStore and generates
structured answers using Gemini Flash with inline citations and Groq fallback.

Can be used as a library or run directly for CLI testing:
    python -m pipeline.rag.query_engine "Why do users hesitate to buy?"
"""

import sys
import os
import json
from pathlib import Path
from typing import Optional, Dict, List, Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import google.generativeai as genai
from pipeline.rag.vector_store import VectorStore

TOP_K = 12

SOURCE_DISPLAY = {
    "playstore": ("Play Store", "#ff3f6c"),
    "appstore": ("App Store", "#2dd4bf"),
    "reddit": ("Reddit", "#ff7849"),
    "youtube": ("YouTube", "#a855f7"),
    "hackernews": ("Hacker News", "#ea580c"),
    "pissedconsumer": ("PissedConsumer", "#fbbf24"),
}


class RAGQueryEngine:
    """Retrieval-Augmented Generation engine for the Google Photos corpus with Hybrid SQL + Vector intelligence."""

    def __init__(self):
        self.store = VectorStore()
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def retrieve(
        self,
        query: str,
        top_k: int = TOP_K,
        segment: Optional[str] = None,
        source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve top-k documents from VectorStore matching query and filters."""
        return self.store.query(
            query_text=query,
            top_k=top_k,
            segment=segment,
            source=source,
        )

    def _get_quantitative_context(self, query: str, segment: Optional[str] = None) -> str:
        """Fetch real-time quantitative metrics to supplement semantic retrieval."""
        try:
            from pipeline.db.connection import DB_PATH, get_session
            from pipeline.quantification.aggregator import Aggregator
            if DB_PATH.exists():
                session = get_session()
                agg = Aggregator(session)
                tag_freq = agg.hesitation_frequency(segment=segment if segment != "all" else None)[:6]
                lines = [
                    "QUANTITATIVE AGGREGATES FROM 2,223 CLASSIFIED REVIEWS:",
                    f"- Top Friction / Search Gaps: " + ", ".join([f"{t['label']} ({t['pct']}% of issues, {t['count']} docs)" for t in tag_freq]),
                ]
                return "\n".join(lines)
        except Exception:
            pass

        # Fallback to pre-exported summary JSON (always available in repo)
        try:
            summary_path = PROJECT_ROOT / "data" / "exports" / "summary.json"
            if summary_path.exists():
                with open(summary_path, "r", encoding="utf-8") as f:
                    summ = json.load(f)
                kpi_str = ", ".join([f"{k['label']} ({k['value']}{'%' if k['unit'] == 'percent' else ' reviews'})" for k in summ.get("kpi_cards", [])])
                return f"QUANTITATIVE AGGREGATES FROM 2,223 CLASSIFIED REVIEWS:\n- Key Indicators: {kpi_str}"
        except Exception:
            pass
        return ""

    def _is_greeting(self, query: str) -> bool:
        """Check if query is a simple greeting or identity question."""
        q = query.lower().strip().strip("!?.,:;")
        greetings = {
            "hi", "hello", "hey", "hey there", "good morning", "good afternoon", "good evening",
            "howdy", "namaste", "hola", "greetings", "hi there", "hello there", "what's up",
            "whats up", "how are you", "who are you", "what can you do", "help", "start"
        }
        return q in greetings or q.startswith(("hi ", "hello ", "hey "))

    def generate_answer(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]],
        segment: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a structured answer using Gemini Flash with retrieved context and strict guardrails."""

        # 1. Handle Greetings Directly without semantic retrieval hallucination
        if self._is_greeting(query):
            return {
                "answer": "Hello! 👋 I am the **Google Photos AI Discovery Engine**, specialized in visual retrieval and personal media intelligence. I can help you analyze photo retrieval friction, forgotten metadata (dates/locations), vague episodic recall, screenshot clutter, timeline fatigue, and competitor comparisons across our **classified voice-of-customer reviews** — spanning Google Play Store, Reddit, YouTube, and Apple App Store.\n\nWhat visual retrieval friction or user behavior would you like to explore today?",
                "citations": [],
                "filters_applied": {"segment": segment or "all", "source": source or "all"},
                "docs_retrieved": 0,
                "retrieved_docs": [],
                "suggestions": [
                    "What kinds of old photos do users struggle to retrieve?",
                    "What information do people actually remember about a photo?",
                    "How does clutter and screenshots impact retrieval success?"
                ],
                "is_out_of_scope": False,
            }

        if not retrieved_docs:
            return {
                "answer": "I couldn't find any relevant reviews or customer feedback matching your query with the current filters. Try relaxing the source filters or asking about forgotten dates/locations, vague visual memories, or screenshot clutter.",
                "citations": [],
                "filters_applied": {"source": source or "all"},
                "docs_retrieved": 0,
                "retrieved_docs": [],
                "suggestions": [
                    "What information do users forget most often?",
                    "Why do users experience timeline scrolling fatigue?",
                    "How do users formulate search queries with incomplete memory?"
                ],
                "is_out_of_scope": False,
            }

        # Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(retrieved_docs[:10]):
            src_display = SOURCE_DISPLAY.get(doc["source"], (doc["source"], "#6b7280"))[0]
            tags = doc.get("hesitation_tags", "")
            context_parts.append(
                f"[Review {i+1}] Source: {src_display} | "
                f"Tags: {tags or 'none'} | Relevance: {doc['similarity']:.0%}\n"
                f"\"{doc['content_preview'] or doc['content']}\""
            )

        context_block = "\n\n---\n\n".join(context_parts)
        quant_block = self._get_quantitative_context(query)

        # Build source summary for citations
        source_counts: Dict[str, int] = {}
        source_similarities: Dict[str, List[float]] = {}
        for doc in retrieved_docs:
            src = doc["source"]
            source_counts[src] = source_counts.get(src, 0) + 1
            source_similarities.setdefault(src, []).append(doc["similarity"])

        filter_context = ""
        if source and source != "all":
            filter_context += f"\nThe user has filtered for **{source}** reviews only."

        system_prompt = f"""You are an evidence-based discovery analyst for the Google Photos AI Discovery Engine.
Your role is to report and synthesize grounded findings from our corpus of real voice-of-customer reviews (Google Play Store, Apple App Store, Reddit, YouTube, Hacker News) and verified database metrics.

CORE DIRECTIVE — MINIMAL SPECULATIVE INFERENCE, MAXIMUM EVIDENCE GROUNDING:
1. MINIMIZE SPECULATIVE AI REASONING:
   - Do NOT invent or inject external academic theories, neurobiology jargon, or ungrounded cognitive speculations that are absent from user statements.
   - When explaining "WHY" a phenomenon occurs (e.g. why users remember colors/feelings but forget dates), explain it strictly through what users themselves explicitly report and experience:
     * What users explicitly state they recalled (e.g., clothing color, weather, companions, emotions).
     * What users explicitly complain they could NOT remember (e.g., exact calendar dates from 3 years ago, camera filenames).
     * What happened when they tried searching (e.g., search gave 0 results, search returned irrelevant memes, search required rigid dates).
     * What immediate workarounds users were forced into (e.g., timeline doom-scrolling, asking family on WhatsApp).

2. EVERY FINDING MUST BE ANCHORED IN CORPUS EVIDENCE:
   - Cite exact verified numbers and percentages from the corpus in **bold** (e.g., **71.4%**, **84.2%**, **2,223 reviews**).
   - ALWAYS quote authentic customer verbatims with markdown blockquotes: `> "quote" — [Review X] (Source)`.
   - Distinguish verified user facts from actionable product recommendations.

3. STRICT HONESTY & NO HALLUCINATION:
   - OUT-OF-SCOPE: If the question is not about Google Photos, photo retrieval, visual search, clutter, or library organization, output exactly: [OUT_OF_SCOPE].
   - NO EVIDENCE IN CORPUS: If the retrieved customer reviews do not contain sufficient evidence to answer the question, do NOT invent an answer. State clearly: "Our customer review corpus does not contain sufficient evidence to answer this specific question."

STRUCTURE YOUR RESPONSE:
1. **Direct Empirical Findings:** What the user data and reviews directly state about this issue.
2. **Authentic Voice-of-Customer Verbatims:** 2–3 exact quotes from the retrieved reviews proving the findings.
3. **Reported Product Breakdown:** The exact mechanism of failure described by users (e.g. 0-results shock, clutter pollution, rigid date filters).
4. **Targeted Product Recommendations:** 1–2 practical UX improvements directly addressing the user quotes above.
5. End with [FOLLOW_UP_SUGGESTIONS] with 2-3 relevant questions.

{filter_context}

{quant_block}

RETRIEVED VOICE-OF-CUSTOMER EVIDENCE ({len(retrieved_docs)} reviews):
{context_block}"""

        user_prompt = f"Question: {query}\n\nSynthesize an actionable analysis based strictly on the voice-of-customer reviews and quantitative evidence above:"

        # PRIMARY: Generate answer with Gemini 3.7 Flash (with fallback to 3.6-flash)
        answer_text = ""
        if self.api_key:
            candidate_gemini_models = [
                "gemini-3.7-flash",
                "gemini-3.6-flash",
                "gemini-flash-latest",
            ]
            for g_model_name in candidate_gemini_models:
                try:
                    model = genai.GenerativeModel(g_model_name)
                    response = model.generate_content(
                        [{"role": "user", "parts": [system_prompt + "\n\n" + user_prompt]}],
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.2,
                            max_output_tokens=1600,
                        ),
                    )
                    answer_text = response.text.strip()
                    if answer_text:
                        print(f"✅ Gemini primary succeeded with model: {g_model_name}", flush=True)
                        break
                except Exception as e:
                    print(f"⚠️ Gemini {g_model_name} error: {type(e).__name__}: {e}", flush=True)
                    continue

        # FALLBACK: Groq is strictly a fallback model if Gemini is unavailable
        if not answer_text and os.getenv("GROQ_API_KEY"):
            print("🔄 Falling back to Groq...", flush=True)
            answer_text = self._fallback_groq(system_prompt, user_prompt)

        # Parse OUT_OF_SCOPE and FOLLOW_UP_SUGGESTIONS
        is_out_of_scope = False
        suggestions = []

        if "[OUT_OF_SCOPE]" in answer_text:
            is_out_of_scope = True
            answer_text = answer_text.replace("[OUT_OF_SCOPE]", "").strip()
            suggestions = [
                "Why do users get zero results for photos they know exist?",
                "How does screenshot and meme clutter ruin visual search?",
                "Why do users remember colors and feelings but forget exact dates?"
            ]
        else:
            if "[FOLLOW_UP_SUGGESTIONS]" in answer_text:
                parts = answer_text.split("[FOLLOW_UP_SUGGESTIONS]")
                answer_text = parts[0].strip()
                suggestion_lines = parts[1].strip().split("\n")
                for s in suggestion_lines:
                    clean_s = s.strip().lstrip("-*•1234567890. ").strip()
                    if clean_s and len(clean_s) > 5:
                        suggestions.append(clean_s)

        if not suggestions:
            suggestions = [
                "How do users use WhatsApp as an escape hatch when search fails?",
                "What are the primary friction points in face recognition and pet tags?",
                "What unmet needs exist for conversational memory retrieval?"
            ]

        # Build citations
        citations = []
        for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
            display_name, color = SOURCE_DISPLAY.get(src, (src, "#6b7280"))
            avg_sim = sum(source_similarities[src]) / len(source_similarities[src])
            citations.append({
                "source": display_name,
                "confidence": round(avg_sim, 2),
                "color": color,
                "count": count,
            })

        # Format full retrieved docs payload for frontend inspector
        formatted_retrieved_docs = []
        for i, doc in enumerate(retrieved_docs):
            src_display = SOURCE_DISPLAY.get(doc["source"], (doc["source"], "#6b7280"))[0]
            formatted_retrieved_docs.append({
                "index": i + 1,
                "doc_id": doc.get("doc_id", ""),
                "source": src_display,
                "raw_source": doc.get("source", ""),
                "source_id": doc.get("source_id", ""),
                "date": doc.get("timestamp", "")[:10] if doc.get("timestamp") else "2026",
                "segment": doc.get("segment", "unknown"),
                "similarity": round(float(doc.get("similarity", 0.8)), 2),
                "tags": [t.strip() for t in doc.get("hesitation_tags", "").split(",") if t.strip()],
                "content": doc.get("content", doc.get("content_preview", "")),
            })

        return {
            "answer": answer_text,
            "citations": citations,
            "filters_applied": {"segment": segment or "all", "source": source or "all"},
            "docs_retrieved": len(retrieved_docs),
            "retrieved_docs": formatted_retrieved_docs,
            "suggestions": suggestions[:3],
            "is_out_of_scope": is_out_of_scope,
        }

    def _fallback_groq(self, system_prompt: str, user_prompt: str) -> str:
        """Attempt answer generation via Groq as fallback with model cascade."""
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not groq_key:
            print("⚠️ Groq fallback skipped — GROQ_API_KEY not set", flush=True)
            return ""

        candidate_groq_models = [
            os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b",
            "llama-3.3-70b-versatile",
        ]

        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            for m in candidate_groq_models:
                try:
                    response = client.chat.completions.create(
                        model=m,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.2,
                        max_tokens=1200,
                    )
                    text = response.choices[0].message.content.strip()
                    if text:
                        print(f"✅ Groq fallback succeeded with model: {m}", flush=True)
                        return text
                except Exception as model_err:
                    print(f"⚠️ Groq model '{m}' failed: {model_err}", flush=True)
            return ""
        except Exception as e:
            print(f"⚠️ Groq client initialization error: {type(e).__name__}: {e}", flush=True)
            return ""

    def ask(
        self,
        query: str,
        segment: Optional[str] = None,
        source: Optional[str] = None,
        top_k: int = TOP_K,
    ) -> Dict[str, Any]:
        """Full RAG pipeline: retrieve -> generate -> return structured answer."""
        retrieved = self.retrieve(query, top_k=top_k, segment=segment, source=source)
        return self.generate_answer(query, retrieved, segment=segment, source=source)


_engine: Optional[RAGQueryEngine] = None

def get_engine() -> RAGQueryEngine:
    global _engine
    if _engine is None:
        _engine = RAGQueryEngine()
        _engine.store.load()
    return _engine


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="RAG Query Engine CLI")
    parser.add_argument("query", type=str, help="Question to ask")
    parser.add_argument("--segment", type=str, default=None)
    parser.add_argument("--source", type=str, default=None)
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    engine = get_engine()
    result = engine.ask(args.query, segment=args.segment, source=args.source)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*60}")
        print(f"Query: {args.query}")
        print(f"Docs retrieved: {result['docs_retrieved']}")
        print(f"{'='*60}\n")
        print(result["answer"])
        print(f"\n{'─'*40}")
        print("Sources:")
        for c in result["citations"]:
            print(f"  • {c['source']} ({c['count']} docs, {c['confidence']:.0%} avg relevance)")
