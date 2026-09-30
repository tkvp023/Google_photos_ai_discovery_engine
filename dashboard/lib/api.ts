// Data fetching utilities — reads from /public/data/*.json at build time via fs.
// Falls back to mock data if the JSON file doesn't exist yet.

import { MOCK_SUMMARY, MOCK_Q2, MOCK_SYSTEMIC_GAPS, MOCK_Q6_SANKEY, MOCK_Q9_GROUPED } from './mockData';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

function loadJSON<T>(filename: string, fallback: T): T {
  try {
    let filePath = join(process.cwd(), 'public', 'data', filename);
    if (!existsSync(filePath)) {
      filePath = join(process.cwd(), 'dashboard', 'public', 'data', filename);
    }
    if (!existsSync(filePath)) return fallback;
    const raw = readFileSync(filePath, 'utf-8');
    const data = JSON.parse(raw);
    // If pipeline hasn't run yet (0 docs), use mock
    if (data?.kpi_cards?.[0]?.value === 0 || data?.total_relevant_docs === 0) {
      return fallback as T;
    }
    return data as T;
  } catch {
    return fallback;
  }
}

export async function getSummary() {
  return loadJSON('summary.json', MOCK_SUMMARY);
}

export async function getQuestion(id: number) {
  const fallback = id === 2 ? MOCK_Q2 : generateMockQuestion(id);
  return loadJSON(`q${id}.json`, fallback);
}

export async function getSystemicGaps() {
  return loadJSON('systemic_gaps.json', MOCK_SYSTEMIC_GAPS);
}

export async function getCorpusMeta() {
  return loadJSON('corpus_meta.json', {});
}

export async function getTriageOverview() {
  return loadJSON('triage_overview.json', {
    total_documents: 1616,
    on_brief_count: 1616,
    on_brief_percentage: 100.0,
    buckets: {},
    methodology_note: '',
  });
}

export async function getBucketAFindings() {
  return loadJSON('bucket_a_findings.json', {
    failure_breakdown: { total_tags: 1616, total_bucket_a_docs: 1616, failure_points: {} },
    subcategories: [],
    memory_cues: { total_cues: 0, cues: [] },
  });
}

export async function getOpportunityRanking() {
  return loadJSON('opportunity_ranking.json', {
    ranking_table: [],
    opportunities: [],
  });
}

export async function getSampleAnswers() {
  return loadJSON('sample_answers.json', {
    questions: [],
  });
}

export async function getSearchTypeAnalysis() {
  return loadJSON('search_type_analysis.json', {
    counts: {},
    comparison: { keyword_failures: {}, gemini_ai_failures: {} },
    gemini_quotes: [],
    keyword_quotes: [],
    takeaway: '',
  });
}

export async function getConfidenceDistribution() {
  return loadJSON('confidence_distribution.json', {
    total_scored_tags: 0,
    average_confidence: 0.84,
    standard_deviation: 0.082,
    unique_score_values: 18,
    is_genuinely_varying: true,
    histogram: {},
    calibration_note: '',
  });
}

// Generate a skeleton mock for questions without a specific mock
function generateMockQuestion(id: number) {
  const metas: Record<number, [string, string]> = {
    1:  ["What types of photos or events do users struggle most to retrieve?", "Struggled Photo Types"],
    2:  ["What clues do users retain when searching for visual memories?", "Retained Memory Clues"],
    3:  ["What metadata is systematically forgotten by users?", "Forgotten Metadata"],
    4:  ["How do users formulate incomplete or vague queries?", "Incomplete Query Formulation"],
    5:  ["Where does retrieval break down and return irrelevant results or false misses?", "Irrelevant Results & False Misses"],
    6:  ["How does endless scrolling behavior manifest when search fails?", "Endless Timeline Scrolling"],
    7:  ["How does media clutter (memes, screenshots, receipts) impact recall?", "Screenshot & Junk Clutter"],
    8:  ["Where do face recognition, pet tagging, and people search fail?", "Face Recognition Failures"],
    9:  ["How do text and document search capabilities perform on receipts and prescriptions?", "Text & Document Search Failures"],
    10: ["What workarounds or platform switching do users adopt?", "Workarounds & Switching"],
  };
  const [text, short] = metas[id] || [`Question ${id}`, `Q${id}`];
  return {
    question_id: id,
    question_text: text,
    question_short: short,
    total_relevant_docs: 1616,
    avg_confidence: 0.91,
    breakdown: [
      { label: "Date Amnesia & Temporal Mismatch", tag: "temporal_amnesia", count: 797, pct: 49.3, avg_confidence: 0.91, color: "#f59e0b" },
      { label: "Gemini AI Generative Drift", tag: "gemini_drift", count: 627, pct: 38.8, avg_confidence: 0.91, color: "#3b82f6" },
      { label: "Facial Misidentification", tag: "face_clustering_gap", count: 446, pct: 27.6, avg_confidence: 0.91, color: "#06b6d4" },
      { label: "Literal Keyword Mismatch", tag: "literal_keyword", count: 174, pct: 10.8, avg_confidence: 0.94, color: "#f97316" },
      { label: "Forced Fallback to Timeline Scrolling", tag: "fallback_to_scroll", count: 107, pct: 6.6, avg_confidence: 0.92, color: "#a855f7" },
      { label: "Screenshot & Junk Clutter Intrusion", tag: "clutter_overflow", count: 95, pct: 5.9, avg_confidence: 0.91, color: "#ec4899" },
    ],
    source_attribution: [],
    key_quotes: [
      { text: "I spent 40 minutes scrolling back through 2022 because search showed nothing for 'paella cafe beach'. I knew the photo was there, but the app gave me zero results.", source: "Play Store", source_id: "gp_001", date: "2026-03-15", confidence: 0.92, tags: ["zero_results_for_existing", "remembered_visual_details"] },
      { text: "Whenever I search for my kid's medicine bottle or fever prescription, Google Photos dumps 50 forwarded WhatsApp memes and payment screenshots. The clutter completely destroys search.", source: "Reddit", source_id: "reddit_001", date: "2026-05-22", confidence: 0.91, tags: ["screenshot_clutter", "document_text_search"] },
    ],
    temporal_trend: [
      { month: "2025-01", count: 110, pct: 22.0 },
      { month: "2025-04", count: 145, pct: 25.0 },
      { month: "2025-07", count: 180, pct: 28.5 },
      { month: "2025-10", count: 210, pct: 31.0 },
      { month: "2026-01", count: 240, pct: 33.5 },
      { month: "2026-04", count: 290, pct: 35.0 },
    ],
    // Q5 extra
    platform_matrix: id === 5 ? {
      rows: ["vague_episodic", "ocr_prescription", "candid_facial", "relative_time", "scenic_landscape"],
      columns: ["Google Photos", "Apple Photos", "Immich", "WhatsApp Media", "Local Storage"],
      values: [[25, 40, 30, 85, 20], [35, 60, 25, 75, 40], [45, 50, 65, 30, 20], [30, 20, 15, 90, 10], [80, 75, 70, 40, 60]],
    } : undefined,
    // Q7 extras
    radar_data: id === 7 ? [
      { factor: "Clutter Quarantine", importance: 34, positive_pct: 12, negative_pct: 88 },
      { factor: "Sensory Anchors", importance: 28, positive_pct: 25, negative_pct: 75 },
      { factor: "Temporal Buffers", importance: 22, positive_pct: 18, negative_pct: 82 },
      { factor: "Face Continuity", importance: 18, positive_pct: 45, negative_pct: 55 },
      { factor: "Prescription OCR", importance: 12, positive_pct: 20, negative_pct: 80 },
      { factor: "Sub-Second Latency", importance: 15, positive_pct: 65, negative_pct: 35 },
    ] : undefined,
    // Q8 extras
    word_cloud_data: id === 8 ? {
      episodic_retrieval_queries: [
        { text: "paella beach", value: 120 }, { text: "strawberry gelato", value: 95 },
        { text: "siena trip", value: 80 }, { text: "blue chairs", value: 65 },
        { text: "two summers ago", value: 55 }, { text: "daughter laughing", value: 44 },
      ],
      clutter_friction_queries: [
        { text: "zero results", value: 110 }, { text: "whatsapp memes", value: 88 },
        { text: "payment receipts", value: 72 }, { text: "wrong face tag", value: 60 },
        { text: "date amnesia", value: 45 }, { text: "lost photo", value: 38 },
      ],
    } : undefined,
    // Q6 extras
    sankey_data: id === 6 ? MOCK_Q6_SANKEY : undefined,
    // Q9 extras
    segment_grouped_data: id === 9 ? MOCK_Q9_GROUPED : undefined,
    // Q10 extras
    treemap_data: id === 10 ? [
      { theme: "Episodic Search Tools", children: [
        { name: "Vague query decomposer", value: 1240 },
        { name: "Relative time buffers", value: 680 },
        { name: "Clarification chips", value: 450 },
      ]},
      { theme: "Clutter Quarantine", children: [
        { name: "Auto-isolate memes", value: 890 },
        { name: "Receipt separation", value: 520 },
        { name: "Burst shot collapse", value: 310 },
      ]},
      { theme: "Document & OCR Search", children: [
        { name: "Curved bottle OCR", value: 760 },
        { name: "Prescription tagger", value: 430 },
      ]},
      { theme: "Privacy & Control", children: [
        { name: "On-device parsing", value: 640 },
        { name: "Zero training guarantee", value: 380 },
      ]},
    ] : undefined,
  };
}
