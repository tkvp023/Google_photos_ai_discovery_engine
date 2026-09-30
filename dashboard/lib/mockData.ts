// Mock / fallback data for Google Photos AI Discovery Engine
// Synchronized with 1,616 Search-Only Retrieval Corpus

export const MOCK_Q6_SANKEY = {
  nodes: [
    { id: 'Google Photos App' },
    { id: 'Hacker News Critiques' },
    { id: 'Reddit Discussions' },
    { id: 'Competitor / Local' },
    { id: 'Instagram / Social' },
    { id: 'Google Web Search' },
    { id: 'WhatsApp Media' },
    { id: 'Retrieved Photo ✓' },
    { id: 'Abandoned Search ✗' },
    { id: 'Switched to WhatsApp 🔄' },
  ],
  links: [
    { source: 'Google Photos App', target: 'Hacker News Critiques', value: 455 },
    { source: 'Google Photos App', target: 'Reddit Discussions', value: 54 },
    { source: 'Google Photos App', target: 'Competitor / Local', value: 80 },
    { source: 'Google Photos App', target: 'Instagram / Social', value: 40 },
    { source: 'Google Photos App', target: 'Google Web Search', value: 65 },
    { source: 'Google Photos App', target: 'WhatsApp Media', value: 101 },
    { source: 'Hacker News Critiques', target: 'Abandoned Search ✗', value: 310 },
    { source: 'Hacker News Critiques', target: 'Retrieved Photo ✓', value: 145 },
    { source: 'Reddit Discussions', target: 'Abandoned Search ✗', value: 35 },
    { source: 'Reddit Discussions', target: 'Retrieved Photo ✓', value: 19 },
    { source: 'Competitor / Local', target: 'Retrieved Photo ✓', value: 60 },
    { source: 'WhatsApp Media', target: 'Retrieved Photo ✓', value: 85 },
  ],
};

export const MOCK_Q9_GROUPED = [
  { factor: 'Forgot Exact Date', play_store: 479, hackernews: 224, app_store: 55, reddit: 26, youtube: 13 },
  { factor: 'Forgot Exact Location', play_store: 215, hackernews: 102, app_store: 25, reddit: 12, youtube: 6 },
  { factor: 'Forgot Filename Or Album', play_store: 125, hackernews: 59, app_store: 14, reddit: 7, youtube: 3 },
  { factor: 'Remembered Relative Time', play_store: 410, hackernews: 192, app_store: 47, reddit: 23, youtube: 11 },
  { factor: 'Remembered Visual Color Object', play_store: 380, hackernews: 178, app_store: 44, reddit: 21, youtube: 10 },
];

export const MOCK_SUMMARY = {
  generated_at: "2026-09-21T00:00:00Z",
  pipeline_version: "2.0.0",
  corpus_name: "Google Photos Search-Only Retrieval Corpus",
  total_in_scope_documents: 1616,
  quote_grounding_verified_pct: 100.0,
  primary_signal_docs: 1616,
  secondary_signal_docs: 0,
  no_signal_docs: 0,
  overall_confidence: 0.908,
  kpi_cards: [
    { id: "total_reviews", label: "Total Corpus (5 Channels)", value: 1616, unit: "count", sparkline: [800, 1000, 1200, 1400, 1616], trend: "up", trend_pct: 100.0 },
    { id: "on_brief_corpus", label: "Search Retrieval Signal (100% In-Scope)", value: 1616, unit: "count", sparkline: [800, 1000, 1200, 1400, 1616], trend: "up", trend_pct: 100.0 },
    { id: "interpretation_failure", label: "#1 Blocker: Interpretation / False Misses", value: 628, unit: "count", sparkline: [300, 380, 450, 520, 628], trend: "up", trend_pct: 38.9 },
    { id: "recovery_breakdown", label: "#2 Blocker: Forced Timeline Scrolling", value: 107, unit: "count", sparkline: [40, 55, 70, 85, 107], trend: "up", trend_pct: 6.6 },
  ],
  source_distribution: [
    { source: "Play Store", count: 969, pct: 60.0, color: "#ff3f6c" },
    { source: "Hacker News", count: 455, pct: 28.2, color: "#ea580c" },
    { source: "App Store", count: 111, pct: 6.9, color: "#2dd4bf" },
    { source: "Reddit", count: 54, pct: 3.3, color: "#ff7849" },
    { source: "YouTube", count: 27, pct: 1.7, color: "#a855f7" },
  ],
  top_opportunities: [
    { rank: 1, label: "Opportunity #1: Combining Multiple Details (Person + Place + Time)", question_id: 1, pct: 48.2, count: 779, avg_confidence: 0.91, impact_score: 9.8 },
    { rank: 2, label: "Opportunity #2: Natural-Language Questions Misread by Ask Photos", question_id: 5, pct: 41.5, count: 671, avg_confidence: 0.91, impact_score: 9.2 },
    { rank: 3, label: "Opportunity #3: Searching by Seasons & Milestones vs. Exact Dates", question_id: 3, pct: 36.7, count: 593, avg_confidence: 0.91, impact_score: 8.9 },
    { rank: 4, label: "Opportunity #4: Dead-End Screens When a Search Finds No Photos", question_id: 6, pct: 28.4, count: 459, avg_confidence: 0.91, impact_score: 8.1 },
    { rank: 5, label: "Opportunity #5: Telling Similar-Looking Photos Apart in Search Results", question_id: 5, pct: 6.6, count: 107, avg_confidence: 0.91, impact_score: 7.8 },
  ],
  total_signal_docs: 1616,
};

export const MOCK_Q2 = {
  question_id: 2,
  question_text: "What information do people actually remember about a photo?",
  question_short: "Retained Memory Clues",
  total_relevant_docs: 1616,
  avg_confidence: 0.908,
  breakdown: [
    { label: "Remembered Visual Details & Objects", tag: "visual_details", count: 673, pct: 41.6, avg_confidence: 0.911, color: "#a855f7" },
    { label: "Remembered Specific People & Companions", tag: "specific_people", count: 615, pct: 38.1, avg_confidence: 0.909, color: "#10b981" },
    { label: "Remembered Relative Time & Seasons", tag: "relative_time", count: 424, pct: 26.2, avg_confidence: 0.914, color: "#f59e0b" },
    { label: "Remembered General Activity or Event", tag: "general_event", count: 592, pct: 36.6, avg_confidence: 0.934, color: "#6366f1" },
  ],
  source_attribution: [],
  key_quotes: [
    { text: "I remember looking for a photo of a dog in a blue bandana from two summers ago, but search showed random cats and documents.", source: "Play Store", source_id: "gp_001", date: "2026-01-15", confidence: 0.92, tags: ["remembered_visual_details"] },
  ],
  temporal_trend: [
    { month: "2025-01", count: 210, pct: 26.0 },
    { month: "2025-07", count: 320, pct: 32.5 },
    { month: "2026-01", count: 410, pct: 37.0 },
  ],
};

export const MOCK_SYSTEMIC_GAPS = {
  generated_at: "2026-09-21T07:49:35Z",
  total_documents: 1616,
  total_search_in_scope: 1616,
  platform_counts: {
    "Play Store": 969,
    "Hacker News": 455,
    "App Store": 111,
    "Reddit": 54,
    "YouTube": 27,
  },
  issue_breakdown: [
    { label: "Date Amnesia & Temporal Mismatch", tag: "temporal_amnesia", count: 797, pct: 49.3, avg_confidence: 0.91, color: "#f59e0b" },
    { label: "Gemini AI Generative Drift & Dead-Ends", tag: "gemini_drift", count: 627, pct: 38.8, avg_confidence: 0.911, color: "#3b82f6" },
    { label: "Facial Misidentification & Identity Clustering", tag: "face_clustering_gap", count: 446, pct: 27.6, avg_confidence: 0.909, color: "#06b6d4" },
    { label: "Literal Keyword Mismatch & Query Brittleness", tag: "literal_keyword", count: 174, pct: 10.8, avg_confidence: 0.936, color: "#f97316" },
    { label: "Forced Fallback to Endless Scrolling", tag: "fallback_to_scroll", count: 107, pct: 6.6, avg_confidence: 0.915, color: "#a855f7" },
    { label: "Search Abandonment & External Workarounds", tag: "search_abandonment", count: 101, pct: 6.2, avg_confidence: 0.901, color: "#22c55e" },
    { label: "Screenshot & Utility Clutter Intrusion", tag: "clutter_overflow", count: 95, pct: 5.9, avg_confidence: 0.914, color: "#ec4899" },
    { label: "Zero Recall / False Misses on Existing Photos", tag: "zero_recall", count: 29, pct: 1.8, avg_confidence: 0.942, color: "#ef4444" },
  ],
  correlation_with_hesitation: [],
  key_quotes: [
    { text: "Always demonstrating how easy it was to find a photo. Now AI search shows your photo briefly, then changes to 'Nothing found' or random garbage.", source: "Play Store", date: "2026-02-10", issue: "zero_recall" },
  ],
};

export const QUESTION_META: Record<number, { text: string; short: string }> = {
  1: { text: "What kinds of old photos do users struggle to retrieve?", short: "Struggled Photo Types" },
  2: { text: "What information do people actually remember about a photo?", short: "Retained Memory Clues" },
  3: { text: "What information have they forgotten?", short: "Forgotten Metadata" },
  4: { text: "How do users formulate searches when their memory is incomplete?", short: "Incomplete Query Formulation" },
  5: { text: "Why does search return completely irrelevant photos or say 'No results found' for photos users know are in their library?", short: "Irrelevant Results & False Misses" },
  6: { text: "Why do users complain about having to endlessly scroll through years of timeline photos when search fails them?", short: "Endless Timeline Scrolling" },
  7: { text: "How do screenshots, receipts, memes, and downloaded junk clutter and ruin search for personal memories?", short: "Screenshot & Junk Clutter" },
  8: { text: "What specific failures do users report with People & Pets / facial recognition search?", short: "Face Recognition Failures" },
  9: { text: "How well does text/OCR and document search perform on utility photos?", short: "Document & Utility Search" },
  10: { text: "What workarounds or alternative apps do users adopt when Google Photos search fails?", short: "Workarounds & Switching" },
};
