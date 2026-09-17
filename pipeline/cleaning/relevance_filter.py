"""
Relevance filter — keeps documents that contain domain-relevant visual retrieval signals.
Strictly eliminates bogus, low-signal, spam, and non-retrieval data.
"""

import re
from typing import List, Tuple, Set

# Noise patterns (ultra-short, pure praise/complaints, or non-informative)
NOISE_PATTERNS = [
    r"^\s*(good|nice|bad|worst|best|ok|okay|fine|great|excellent|awesome|terrible|horrible|amazing|super|cool|useful|helpful|wow|love it|hate it)\s*[.!]*\s*$",
    r"^[⭐★☆✩✪\s\d.,!?-]+$",
    r"^\s*\d+\s*$",
    r"(whatsapp\s+number|call\s+me|telegram\s+@|crypto|loan|invest)",
]

NOISE_REGEXES = [re.compile(p, re.IGNORECASE) for p in NOISE_PATTERNS]

MIN_WORD_COUNT = 8

# Core retrieval action & friction keywords
RETRIEVAL_ACTION_KEYWORDS: Set[str] = {
    "search", "searching", "find", "finding", "retrieve", "retrieval", "locate", "locating",
    "look for", "looking for", "cant find", "can't find", "cannot find", "lost", "missing",
    "query", "queries", "ask photos", "gemini", "ai search", "semantic search", "natural language",
    "remember", "remembering", "memory", "memories", "forgot", "forget", "recall",
    "timeline", "scroll", "scrolling", "grid", "feed", "clutter", "cluttered", "organize",
    "organization", "organized", "album", "albums", "folder", "folders", "archive",
    "face", "faces", "facial recognition", "face recognition", "person", "people",
    "tag", "tags", "tagging", "tagged", "name", "naming", "cluster", "clustering", "group", "grouping",
    "date", "dates", "year", "years", "month", "timestamp", "metadata", "exif", "location", "map", "places",
    "screenshot", "screenshots", "receipt", "receipts", "document", "documents",
    "duplicate", "duplicates", "blurry", "quality", "compressed", "disappeared", "deleted",
    "vanished", "buried", "hard to find", "browse", "browsing", "backup", "sync",
    "filter", "filtering", "sort", "sorting"
}

# Media and application context keywords
MEDIA_CONTEXT_KEYWORDS: Set[str] = {
    "photo", "photos", "picture", "pictures", "image", "images", "video", "videos",
    "pic", "pics", "shot", "shots", "camera", "gallery", "library", "cloud",
    "google photos", "apple photos", "photos app", "device", "storage",
    "screenshot", "screenshots", "receipt", "receipts", "document", "documents"
}

# High-signal multi-word phrases that immediately confirm retrieval relevance
STRONG_SIGNAL_PHRASES = [
    "can't find",
    "cannot find",
    "cant find",
    "looking for a photo",
    "find old photos",
    "search is broken",
    "search doesn't work",
    "search does not work",
    "face grouping",
    "facial recognition",
    "face recognition",
    "timeline scroll",
    "infinite scroll",
    "ask photos",
    "screenshot clutter",
    "lost my photos",
    "missing photos",
    "wrong date",
    "wrong person",
    "tag people",
    "album organization",
    "semantic search",
    "photo search",
    "video search",
    "search query",
    "search results"
]


def is_relevant(text: str) -> bool:
    """
    Check if a text is strictly relevant to Google Photos visual retrieval.
    Rejects short noise, spam, and non-retrieval complaints.
    """
    if not text or not isinstance(text, str):
        return False

    clean_text = text.strip()
    words = clean_text.split()
    
    # Minimum substantive length requirement
    if len(words) < MIN_WORD_COUNT:
        return False

    # Check against pure noise regexes
    for pattern in NOISE_REGEXES:
        if pattern.search(clean_text):
            return False

    lower_text = clean_text.lower()

    # Instant pass for explicit high-signal retrieval phrases
    for phrase in STRONG_SIGNAL_PHRASES:
        if phrase in lower_text:
            return True

    # Check for domain keywords presence
    has_retrieval_action = any(
        re.search(rf"\b{re.escape(kw)}\b", lower_text) for kw in RETRIEVAL_ACTION_KEYWORDS
    )
    has_media_context = any(
        re.search(rf"\b{re.escape(kw)}\b", lower_text) for kw in MEDIA_CONTEXT_KEYWORDS
    )

    # Must contain both a retrieval/friction action AND media context
    return has_retrieval_action and has_media_context


def is_relevant_with_source(text: str, source: str) -> bool:
    """
    Check relevance with source context — strictly enforces domain keywords across ALL sources.
    No automatic pass for app stores or any other source.
    """
    return is_relevant(text)


def filter_documents(docs: List[dict]) -> Tuple[List[dict], int]:
    """Filter documents for relevance. Returns (relevant_docs, dropped_count)."""
    kept = []
    dropped = 0
    for doc in docs:
        content = doc.get("content", "")
        source = doc.get("source", "")
        if is_relevant_with_source(content, source):
            kept.append(doc)
        else:
            dropped += 1
    return kept, dropped
