'use client';
import { useState } from 'react';
import { formatLabel } from '@/lib/formatters';

interface TriageBucketInfo {
  bucket: string;
  label: string;
  description: string;
  color: string;
  count: number;
  percentage: number;
  avg_confidence: number;
  platform_counts: Record<string, number>;
  sample_quotes: Array<{ quote: string; reason: string; source: string; confidence: number }>;
}

interface TriageOverviewData {
  total_documents: number;
  on_brief_count: number;
  on_brief_percentage: number;
  buckets: Record<string, TriageBucketInfo>;
  methodology_note: string;
}

interface FailurePointInfo {
  failure_type: string;
  label: string;
  description: string;
  color: string;
  tag_count: number;
  tag_percentage: number;
  doc_count: number;
  doc_percentage: number;
  avg_confidence: number;
  top_subcategories: Array<{ sub_category: string; label: string; count: number; percentage: number }>;
  sample_quotes: Array<{ quote: string; confidence: number; search_type: string; source: string }>;
}

interface BucketAFindingsData {
  failure_breakdown: {
    total_tags: number;
    total_bucket_a_docs: number;
    failure_points: Record<string, FailurePointInfo>;
  };
  subcategories: Array<{
    sub_category: string;
    label: string;
    failure_type: string;
    count: number;
    percentage: number;
    avg_confidence: number;
    sample_quote: string;
    search_type: string;
  }>;
  memory_cues: {
    total_cues: number;
    cues: Array<{
      cue_type: string;
      label: string;
      count: number;
      percentage: number;
      avg_confidence: number;
      sample_quote: string;
    }>;
  };
}

interface OpportunityItem {
  rank: number;
  title: string;
  failure_type: string;
  sub_category: string;
  problem_description: string;
  solution_direction: string;
  severity: string;
  score: number;
}

interface RankingShiftItem {
  rank_new: number;
  title: string;
  old_volume_rank: number;
  old_metric: string;
  new_metric: string;
  shift: string;
  pm_rationale: string;
}

interface OpportunityRankingData {
  opportunities: OpportunityItem[];
  ranking_comparison: RankingShiftItem[];
}

interface SampleQuestionItem {
  question_id: number;
  question: string;
  key_finding: string;
  evidence_quotes: string[];
  pm_implication: string;
}

interface SearchTypeAnalysisData {
  counts: Record<string, number>;
  comparison: {
    keyword_failures: Record<string, number>;
    gemini_ai_failures: Record<string, number>;
  };
  gemini_quotes: Array<{ quote: string; confidence: number; sub_category: string }>;
  keyword_quotes: Array<{ quote: string; confidence: number; sub_category: string }>;
  takeaway: string;
}

interface ConfidenceDistributionData {
  total_scored_tags: number;
  average_confidence: number;
  standard_deviation: number;
  unique_score_values: number;
  is_genuinely_varying: boolean;
  histogram: Record<string, number>;
  calibration_note: string;
}

interface FindingsContentProps {
  triage: TriageOverviewData;
  bucketA: BucketAFindingsData;
  opportunities: OpportunityRankingData;
  sampleAnswers: { questions: SampleQuestionItem[] };
  searchType: SearchTypeAnalysisData;
  confidenceDist: ConfidenceDistributionData;
}

const STAGE_LABELS: Record<string, { title: string; tab: string }> = {
  expression: { title: "Can't find the right words", tab: "Finding words" },
  interpretation: { title: "Search misunderstands query", tab: "Understanding" },
  evaluation: { title: "Can't spot the right photo", tab: "Identifying" },
  recovery: { title: "No help when search fails", tab: "Getting help" },
};

const BUCKET_LABELS: Record<string, { title: string; filterLabel: string }> = {
  A: { title: "Search Friction", filterLabel: "Primary focus" },
  B: { title: "App & Backup Issues", filterLabel: "Filtered out" },
  C: { title: "Layout & Menu Complaints", filterLabel: "Filtered out" },
  D: { title: "General Feedback", filterLabel: "Filtered out" },
};

function getConfidenceTierText(score: number): string {
  if (score >= 0.85) return 'High confidence';
  if (score >= 0.70) return 'Moderate confidence';
  return 'Lower confidence';
}

export default function FindingsContent({
  triage,
  bucketA,
  opportunities,
  sampleAnswers,
  searchType,
  confidenceDist,
}: FindingsContentProps) {
  const [activeStageTab, setActiveStageTab] = useState<'all' | 'expression' | 'interpretation' | 'evaluation' | 'recovery'>('all');
  const [expandedQuestion, setExpandedQuestion] = useState<number | null>(1);

  const failurePoints = bucketA.failure_breakdown.failure_points || {};
  const totalBucketADocs = triage.on_brief_count || bucketA.failure_breakdown.total_bucket_a_docs || 251;
  const totalCorpusDocs = triage.total_documents || 2223;

  // Filter subcategories for the active tab
  const filteredSubcategories = activeStageTab === 'all'
    ? bucketA.subcategories
    : bucketA.subcategories.filter(s => s.failure_type === activeStageTab);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 36 }}>
      {/* ═══ 1. HERO BANNER & SCOPE CLARITY ═══ */}
      <section style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '32px 30px',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
          <span style={{
            fontSize: 11.5, fontWeight: 700,
            padding: '3px 9px', borderRadius: 12,
            background: 'rgba(59, 130, 246, 0.10)',
            color: 'var(--semantic-blue)',
            border: '1px solid rgba(59, 130, 246, 0.25)',
          }}>
            Search Friction Analysis
          </span>
          <span style={{
            fontSize: 11.5, fontWeight: 600, color: 'var(--semantic-green)',
            display: 'flex', alignItems: 'center', gap: 6,
            background: 'rgba(34, 197, 94, 0.08)',
            padding: '3px 9px', borderRadius: 12,
            border: '1px solid rgba(34, 197, 94, 0.20)',
          }}>
            ✓ Word-for-Word Quotes Verified
          </span>
          <span style={{
            fontSize: 11.5, fontWeight: 600, color: 'var(--semantic-blue)',
            background: 'rgba(59, 130, 246, 0.08)',
            padding: '3px 9px', borderRadius: 12,
            border: '1px solid rgba(59, 130, 246, 0.20)',
          }}>
            Calibrated Confidence (±{confidenceDist.standard_deviation.toFixed(2)} σ)
          </span>
        </div>

        <h1 style={{
          fontSize: 'clamp(26px, 3.2vw, 40px)',
          fontWeight: 700,
          lineHeight: 1.2,
          letterSpacing: '-0.03em',
          marginBottom: 14,
          maxWidth: 920,
          color: 'var(--text-primary)',
        }}>
          Why photo search fails when memories are incomplete
        </h1>

        <p style={{
          fontSize: 15.5, lineHeight: 1.65, color: 'var(--text-secondary)',
          maxWidth: 860, marginBottom: 26,
        }}>
          Rather than analyzing general app store complaints, we isolated the 251 reviews where users specifically struggled to find a photo they remembered. We mapped these failures across four distinct stages: finding the right words, search misunderstanding, spotting the photo in clutter, and lack of recovery help.
        </p>

        {/* 4 Anchor Stat Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
          gap: 14,
        }}>
          {/* Total Corpus */}
          <div style={{
            background: 'var(--bg-elevated)', border: '1px solid var(--border)',
            padding: '16px 18px', borderRadius: 'var(--radius-md)',
          }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>
              Total Reviews Analyzed
            </div>
            <div style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-primary)', fontFamily: "'Space Grotesk', sans-serif" }}>
              {totalCorpusDocs.toLocaleString()}
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginTop: 4 }}>
              1,583 store reviews + 640 forum discussions
            </div>
          </div>

          {/* Search-Related */}
          <div style={{
            background: 'rgba(59, 130, 246, 0.08)', border: '1.5px solid rgba(59, 130, 246, 0.35)',
            padding: '16px 18px', borderRadius: 'var(--radius-md)',
          }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--semantic-blue)', textTransform: 'uppercase', marginBottom: 4 }}>
              Search-Related Reviews
            </div>
            <div style={{ fontSize: 26, fontWeight: 800, color: 'var(--semantic-blue)', fontFamily: "'Space Grotesk', sans-serif" }}>
              {totalBucketADocs.toLocaleString()}
              <span style={{ fontSize: 13.5, fontWeight: 600, marginLeft: 8, opacity: 0.9 }}>
                ({((totalBucketADocs / totalCorpusDocs) * 100).toFixed(1)}%)
              </span>
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--semantic-blue)', opacity: 0.9, marginTop: 4 }}>
              Core focus of this report
            </div>
          </div>

          {/* Filtered Out: Reliability */}
          <div style={{
            background: 'var(--bg-elevated)', border: '1px solid var(--border)',
            padding: '16px 18px', borderRadius: 'var(--radius-md)',
          }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>
              App &amp; Backup Issues (Filtered Out)
            </div>
            <div style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-secondary)', fontFamily: "'Space Grotesk', sans-serif" }}>
              {triage.buckets?.B?.count || 674}
              <span style={{ fontSize: 13.5, fontWeight: 600, marginLeft: 8, color: 'var(--text-muted)' }}>
                ({(triage.buckets?.B?.percentage || 30.3).toFixed(1)}%)
              </span>
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginTop: 4 }}>
              Backup stalls, crashes, sync bugs
            </div>
          </div>

          {/* Filtered Out: UI */}
          <div style={{
            background: 'var(--bg-elevated)', border: '1px solid var(--border)',
            padding: '16px 18px', borderRadius: 'var(--radius-md)',
          }}>
            <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>
              Layout Complaints (Filtered Out)
            </div>
            <div style={{ fontSize: 26, fontWeight: 700, color: 'var(--text-secondary)', fontFamily: "'Space Grotesk', sans-serif" }}>
              {triage.buckets?.C?.count || 659}
              <span style={{ fontSize: 13.5, fontWeight: 600, marginLeft: 8, color: 'var(--text-muted)' }}>
                ({(triage.buckets?.C?.percentage || 29.6).toFixed(1)}%)
              </span>
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginTop: 4 }}>
              Tab moves, navigation redesign gripes
            </div>
          </div>
        </div>
      </section>

      {/* ═══ 2. TRIAGE FILTER: HOW WE SEPARATED SEARCH PROBLEMS ═══ */}
      <section style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '28px',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', margin: 0, letterSpacing: '-0.02em' }}>
              How we separated search problems from everything else
            </h2>
            <p style={{ fontSize: 14, color: 'var(--text-secondary)', margin: '6px 0 0', maxWidth: 840, lineHeight: 1.55 }}>
              All 2,223 raw user reviews were triaged into 4 mutually exclusive categories. Only search-related reviews (people struggling to find a photo with partial memory) are included in the search analysis. App crashes, sync loops, and UI redesign feedback are separated out so they don&apos;t pollute search findings.
            </p>
          </div>
        </div>

        {/* 4 Bucket Distribution Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14 }}>
          {(['A', 'B', 'C', 'D'] as const).map((bKey) => {
            const b = triage.buckets?.[bKey] || {
              bucket: bKey,
              label: `Bucket ${bKey}`,
              description: '',
              color: '#3b82f6',
              count: 0,
              percentage: 0,
              avg_confidence: 0.85,
              sample_quotes: [],
            };
            const isPrimary = bKey === 'A';
            const meta = BUCKET_LABELS[bKey] || { title: `Bucket ${bKey}`, filterLabel: '' };

            return (
              <div
                key={bKey}
                style={{
                  padding: 18,
                  borderRadius: 'var(--radius-md)',
                  background: isPrimary ? 'rgba(59, 130, 246, 0.05)' : 'var(--bg-elevated)',
                  border: isPrimary ? '1.5px solid rgba(59, 130, 246, 0.35)' : '1px solid var(--border)',
                  position: 'relative',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span style={{
                    fontSize: 12.5, fontWeight: 700, color: isPrimary ? 'var(--semantic-blue)' : 'var(--text-secondary)',
                    display: 'flex', alignItems: 'center', gap: 6,
                  }}>
                    <span style={{ width: 7, height: 7, borderRadius: '50%', background: isPrimary ? 'var(--semantic-blue)' : 'var(--semantic-gray)' }} />
                    {meta.title}
                  </span>
                  <span style={{ fontSize: 12, fontWeight: 700, color: isPrimary ? 'var(--semantic-blue)' : 'var(--text-muted)' }}>
                    {b.percentage}%
                  </span>
                </div>

                <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4, fontFamily: "'Space Grotesk', sans-serif" }}>
                  {b.count.toLocaleString()}
                  <span style={{ fontSize: 12, fontWeight: 400, color: 'var(--text-muted)', marginLeft: 6 }}>reviews</span>
                </div>

                <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.45, marginBottom: 12, minHeight: 34 }}>
                  {b.description}
                </div>

                {/* Sample Grounded Quote */}
                {b.sample_quotes?.[0] && (
                  <div style={{
                    fontSize: 11.5, fontStyle: 'italic', color: 'var(--text-muted)',
                    borderLeft: `2px solid ${isPrimary ? 'var(--semantic-blue)' : 'var(--border-strong)'}`, paddingLeft: 8, marginTop: 8,
                  }}>
                    &ldquo;{b.sample_quotes[0].quote.slice(0, 105)}...&rdquo;
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* ═══ 3. THE 4-STAGE FAILURE TAXONOMY ═══ */}
      <section style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '28px',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', margin: 0, letterSpacing: '-0.02em' }}>
              Where search goes wrong: four stages
            </h2>
            <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', margin: '6px 0 0' }}>
              Every search breakdown happens at one of four distinct cognitive moments in the user journey.
            </p>
          </div>

          {/* Stage Filter Tabs */}
          <div style={{ display: 'flex', gap: 4, background: 'var(--bg-elevated)', padding: 3, borderRadius: 8, border: '1px solid var(--border)' }}>
            {(['all', 'expression', 'interpretation', 'evaluation', 'recovery'] as const).map((tab) => {
              const tabLabel = tab === 'all' ? 'All stages' : STAGE_LABELS[tab]?.tab || tab;
              return (
                <button
                  key={tab}
                  onClick={() => setActiveStageTab(tab)}
                  style={{
                    background: activeStageTab === tab ? 'var(--bg-card)' : 'transparent',
                    color: activeStageTab === tab ? 'var(--text-primary)' : 'var(--text-muted)',
                    border: activeStageTab === tab ? '1px solid var(--border)' : '1px solid transparent',
                    padding: '5px 11px',
                    borderRadius: 6,
                    fontSize: 12,
                    fontWeight: activeStageTab === tab ? 600 : 500,
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  {tabLabel}
                </button>
              );
            })}
          </div>
        </div>

        {/* 4 Stage Cards Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16, marginBottom: 24 }}>
          {(['expression', 'interpretation', 'evaluation', 'recovery'] as const).map((stage) => {
            const info = failurePoints[stage] || {
              failure_type: stage,
              label: formatLabel(stage),
              description: '',
              color: '#3b82f6',
              tag_count: 0,
              tag_percentage: 0,
              doc_count: 0,
              doc_percentage: 0,
              avg_confidence: 0.85,
              top_subcategories: [],
              sample_quotes: [],
            };

            const isSelected = activeStageTab === 'all' || activeStageTab === stage;
            const stageMeta = STAGE_LABELS[stage] || { title: info.label, tab: stage };

            return (
              <div
                key={stage}
                onClick={() => setActiveStageTab(stage)}
                style={{
                  padding: '18px 20px',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--bg-elevated)',
                  border: `1.5px solid ${isSelected ? 'var(--semantic-blue)' : 'var(--border)'}`,
                  opacity: isSelected ? 1 : 0.45,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span style={{
                    fontSize: 11, fontWeight: 700, color: 'var(--semantic-blue)', textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}>
                    Stage {stage === 'expression' ? '1' : stage === 'interpretation' ? '2' : stage === 'evaluation' ? '3' : '4'}
                  </span>
                  <span style={{
                    fontSize: 11, fontWeight: 700, padding: '2px 7px', borderRadius: 4,
                    background: 'rgba(59, 130, 246, 0.10)', color: 'var(--semantic-blue)', border: '1px solid rgba(59, 130, 246, 0.25)',
                  }}>
                    {info.tag_count} mentions ({info.tag_percentage}%)
                  </span>
                </div>

                <div style={{ fontSize: 15.5, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>
                  {stageMeta.title}
                </div>
                <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginBottom: 8 }}>
                  Found in {info.doc_count} of {totalBucketADocs} search-related reviews
                </div>

                <div style={{ fontSize: 12.5, color: 'var(--text-secondary)', lineHeight: 1.45, marginBottom: 12 }}>
                  {info.description}
                </div>

                {/* Top Subcategories Pills */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5, marginBottom: 12 }}>
                  {info.top_subcategories?.slice(0, 3).map((sub) => (
                    <span
                      key={sub.sub_category}
                      style={{
                        fontSize: 11, fontWeight: 500, padding: '2px 7px', borderRadius: 4,
                        background: 'var(--bg-card)', border: '1px solid var(--border)',
                        color: 'var(--text-secondary)',
                      }}
                    >
                      {sub.label} ({sub.count})
                    </span>
                  ))}
                </div>

                {/* Grounded Quote Snippet */}
                {info.sample_quotes?.[0] && (
                  <div style={{
                    fontSize: 11.5, fontStyle: 'italic', color: 'var(--text-muted)',
                    borderLeft: '2px solid var(--semantic-blue)', paddingLeft: 8, marginTop: 8,
                  }}>
                    &ldquo;{info.sample_quotes[0].quote.slice(0, 95)}...&rdquo;
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Detailed Subcategory Table for Selected Stage */}
        <div style={{
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-md)',
          overflow: 'hidden',
          background: 'var(--bg-card)',
        }}>
          <div style={{
            padding: '12px 18px', background: 'var(--bg-elevated)', borderBottom: '1px solid var(--border)',
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }}>
            <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>
              Detailed breakdown ({filteredSubcategories.length} failure types)
            </span>
            <span style={{ fontSize: 11.5, color: 'var(--text-muted)' }}>
              Real user quotes verified word-for-word
            </span>
          </div>

          <div style={{ maxHeight: 380, overflowY: 'auto' }}>
            {filteredSubcategories.map((sub, idx) => (
              <div
                key={sub.sub_category}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '2fr 1fr 3fr',
                  gap: 16,
                  padding: '12px 18px',
                  borderBottom: idx === filteredSubcategories.length - 1 ? 'none' : '1px solid var(--border)',
                  alignItems: 'center',
                  fontSize: 13,
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{sub.label}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                    {STAGE_LABELS[sub.failure_type]?.title || sub.failure_type}
                  </div>
                </div>

                <div>
                  <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{sub.count} mentions</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{sub.percentage}% of search issues</div>
                </div>

                <div style={{ fontSize: 12, color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                  {sub.sample_quote ? `“${sub.sample_quote}”` : 'No quote available'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ 4. WHAT HUMANS REMEMBER ═══ */}
      <section style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '28px',
      }}>
        <div style={{ marginBottom: 18 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', margin: 0, letterSpacing: '-0.02em' }}>
            What users actually remember
          </h2>
          <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', margin: '6px 0 0', maxWidth: 840, lineHeight: 1.55 }}>
            When users try to retrieve memories, they remember sensory atmospheres, seasons, social companions, and emotions — while search engines historically demand calendar dates and exact keywords.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: 14 }}>
          {bucketA.memory_cues.cues?.map((cue) => (
            <div
              key={cue.cue_type}
              style={{
                padding: '15px 16px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
                  {cue.label}
                </span>
                <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--semantic-blue)' }}>
                  {cue.percentage}%
                </span>
              </div>

              <div style={{
                height: 5, background: 'var(--border)', borderRadius: 3, overflow: 'hidden', marginBottom: 8,
              }}>
                <div style={{
                  height: '100%', width: `${cue.percentage}%`, background: 'var(--semantic-blue)', borderRadius: 3,
                }} />
              </div>

              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                Mentioned by {cue.count} users · {getConfidenceTierText(cue.avg_confidence)}
              </div>

              {cue.sample_quote && (
                <div style={{
                  fontSize: 11.5, fontStyle: 'italic', color: 'var(--text-secondary)',
                  marginTop: 8, borderTop: '1px dashed var(--border)', paddingTop: 6,
                }}>
                  &ldquo;{cue.sample_quote.slice(0, 80)}...&rdquo;
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* ═══ 5. CLASSIC SEARCH VS AI SEARCH ═══ */}
      <section style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '28px',
      }}>
        <div style={{ marginBottom: 18 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', margin: 0, letterSpacing: '-0.02em' }}>
            Classic search vs. AI search (Ask Photos)
          </h2>
          <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', margin: '6px 0 0', maxWidth: 840, lineHeight: 1.55 }}>
            {searchType.takeaway || (
              "Classic keyword search fails when users describe relative time or sensory moments instead of exact keywords. Ask Photos (AI) understands broader questions better, but misinterprets queries and offers no suggestions when it fails."
            )}
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 18 }}>
          {/* Keyword Search Card */}
          <div style={{
            padding: 20, borderRadius: 'var(--radius-md)',
            background: 'var(--bg-elevated)', border: '1px solid var(--border)',
          }}>
            <h3 style={{ fontSize: 15.5, fontWeight: 700, margin: '0 0 4px 0', color: 'var(--text-primary)' }}>
              Classic Keyword Search
            </h3>
            <div style={{ fontSize: 12, color: 'var(--semantic-amber)', marginBottom: 14 }}>
              Main problem: searches for exact words, misses the meaning
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {searchType.keyword_quotes?.map((q, i) => (
                <div key={i} style={{
                  padding: 10, borderRadius: 6, background: 'var(--bg-card)', border: '1px solid var(--border)',
                  fontSize: 12, color: 'var(--text-secondary)', fontStyle: 'italic',
                }}>
                  &ldquo;{q.quote}&rdquo;
                  <div style={{ fontSize: 10.5, color: 'var(--text-muted)', fontStyle: 'normal', marginTop: 4 }}>
                    — User review · {getConfidenceTierText(q.confidence)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Gemini AI / Ask Photos Card */}
          <div style={{
            padding: 20, borderRadius: 'var(--radius-md)',
            background: 'var(--bg-elevated)', border: '1.5px solid rgba(59, 130, 246, 0.3)',
          }}>
            <h3 style={{ fontSize: 15.5, fontWeight: 700, margin: '0 0 4px 0', color: 'var(--semantic-blue)' }}>
              Ask Photos (AI Search)
            </h3>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 14 }}>
              Main problem: misinterprets questions, then offers no way forward
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {searchType.gemini_quotes?.map((q, i) => (
                <div key={i} style={{
                  padding: 10, borderRadius: 6, background: 'var(--bg-card)', border: '1px solid var(--border)',
                  fontSize: 12, color: 'var(--text-secondary)', fontStyle: 'italic',
                }}>
                  &ldquo;{q.quote}&rdquo;
                  <div style={{ fontSize: 10.5, color: 'var(--text-muted)', fontStyle: 'normal', marginTop: 4 }}>
                    — User review · {getConfidenceTierText(q.confidence)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ 6. WHAT TO FIX FIRST (OPPORTUNITY RANKING) ═══ */}
      <section style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '28px',
      }}>
        <div style={{ marginBottom: 18 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', margin: 0, letterSpacing: '-0.02em' }}>
            What to fix first: Strategic Opportunities
          </h2>
          <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', margin: '6px 0 0' }}>
            When we filter out generic complaints and look specifically at search failures, the priority ranking changes.
          </p>
        </div>

        {/* Comparison Table */}
        <div style={{
          border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', overflow: 'hidden',
          marginBottom: 24, background: 'var(--bg-elevated)',
        }}>
          <div style={{
            padding: '11px 16px', background: 'var(--bg-card)', borderBottom: '1px solid var(--border)',
            fontWeight: 600, fontSize: 12.5, color: 'var(--text-primary)',
          }}>
            Raw complaint count vs. Search-focused priority
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12.5 }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)', fontSize: 11, textTransform: 'uppercase' }}>
                  <th style={{ padding: '10px 14px', textAlign: 'left' }}>New Rank</th>
                  <th style={{ padding: '10px 14px', textAlign: 'left' }}>Opportunity</th>
                  <th style={{ padding: '10px 14px', textAlign: 'left' }}>Shift</th>
                  <th style={{ padding: '10px 14px', textAlign: 'left' }}>Old Raw Rank</th>
                  <th style={{ padding: '10px 14px', textAlign: 'left' }}>Why the priority changed</th>
                </tr>
              </thead>
              <tbody>
                {opportunities.ranking_comparison?.map((item) => (
                  <tr key={item.rank_new} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '10px 14px', fontWeight: 700, color: 'var(--semantic-blue)' }}>
                      #{item.rank_new}
                    </td>
                    <td style={{ padding: '10px 14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                      {item.title}
                    </td>
                    <td style={{ padding: '10px 14px' }}>
                      <span style={{
                        fontSize: 11, fontWeight: 700, padding: '2px 7px', borderRadius: 4,
                        background: item.shift.includes('UP') ? 'rgba(34, 197, 94, 0.12)' : 'rgba(245, 158, 11, 0.12)',
                        color: item.shift.includes('UP') ? 'var(--semantic-green)' : 'var(--semantic-amber)',
                      }}>
                        {item.shift}
                      </span>
                    </td>
                    <td style={{ padding: '10px 14px', color: 'var(--text-muted)' }}>
                      #{item.old_volume_rank} ({item.old_metric})
                    </td>
                    <td style={{ padding: '10px 14px', color: 'var(--text-secondary)', fontSize: 12, lineHeight: 1.45 }}>
                      {item.pm_rationale}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 6 Ranked Opportunities Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))', gap: 14 }}>
          {opportunities.opportunities?.map((opp) => (
            <div
              key={opp.rank}
              style={{
                padding: '18px 20px',
                borderRadius: 'var(--radius-md)',
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
                display: 'flex',
                flexDirection: 'column',
                gap: 8,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{
                  fontSize: 11.5, fontWeight: 700, color: 'var(--semantic-blue)',
                  background: 'rgba(59, 130, 246, 0.10)', padding: '2px 7px', borderRadius: 4,
                }}>
                  Rank #{opp.rank}
                </span>
                <span style={{
                  fontSize: 10.5, fontWeight: 600, padding: '2px 6px', borderRadius: 4,
                  background: opp.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.12)' : 'rgba(245, 158, 11, 0.12)',
                  color: opp.severity === 'CRITICAL' ? '#ef4444' : 'var(--semantic-amber)',
                }}>
                  {opp.severity}
                </span>
              </div>

              <div style={{ fontSize: 14.5, fontWeight: 700, color: 'var(--text-primary)' }}>
                {opp.title}
              </div>

              <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                <strong style={{ color: 'var(--text-primary)' }}>Problem: </strong>
                {opp.problem_description}
              </div>

              <div style={{
                fontSize: 12, color: 'var(--text-primary)', lineHeight: 1.45,
                background: 'var(--bg-card)', padding: '8px 10px', borderRadius: 6,
                border: '1px solid var(--border)', marginTop: 'auto',
              }}>
                <strong style={{ color: 'var(--semantic-blue)' }}>Recommended fix: </strong>
                {opp.solution_direction}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ═══ 7. ANSWERS TO CORE QUESTIONS ═══ */}
      <section style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '28px',
      }}>
        <div style={{ marginBottom: 18 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', margin: 0, letterSpacing: '-0.02em' }}>
            Answers to the core questions
          </h2>
          <p style={{ fontSize: 13.5, color: 'var(--text-secondary)', margin: '6px 0 0' }}>
            Direct answers to the key research questions, grounded in verbatim customer feedback.
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {sampleAnswers.questions?.map((item) => {
            const isOpen = expandedQuestion === item.question_id;

            return (
              <div
                key={item.question_id}
                style={{
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius-md)',
                  background: 'var(--bg-elevated)',
                  overflow: 'hidden',
                }}
              >
                <button
                  onClick={() => setExpandedQuestion(isOpen ? null : item.question_id)}
                  style={{
                    width: '100%',
                    padding: '14px 18px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    background: 'transparent',
                    border: 'none',
                    textAlign: 'left',
                    cursor: 'pointer',
                    color: 'var(--text-primary)',
                    fontWeight: 600,
                    fontSize: 13.5,
                  }}
                >
                  <span style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{
                      width: 22, height: 22, borderRadius: '50%', background: 'rgba(59, 130, 246, 0.12)',
                      color: 'var(--semantic-blue)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: 11, fontWeight: 700,
                    }}>
                      Q{item.question_id}
                    </span>
                    {item.question}
                  </span>
                  <span style={{ fontSize: 14, transform: isOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s ease', color: 'var(--text-muted)' }}>
                    ▼
                  </span>
                </button>

                {isOpen && (
                  <div style={{
                    padding: '0 18px 18px 18px',
                    borderTop: '1px solid var(--border)',
                    background: 'var(--bg-card)',
                  }}>
                    <div style={{ marginTop: 12, marginBottom: 10, fontSize: 13, lineHeight: 1.55, color: 'var(--text-primary)' }}>
                      <strong style={{ color: 'var(--semantic-blue)' }}>Finding: </strong>
                      {item.key_finding}
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 10 }}>
                      {item.evidence_quotes?.map((q, idx) => (
                        <div
                          key={idx}
                          style={{
                            fontSize: 11.5, fontStyle: 'italic', color: 'var(--text-secondary)',
                            background: 'var(--bg-elevated)', padding: '8px 10px', borderRadius: 6,
                            borderLeft: '2px solid var(--semantic-blue)',
                          }}
                        >
                          &ldquo;{q}&rdquo;
                        </div>
                      ))}
                    </div>

                    <div style={{
                      fontSize: 12, color: 'var(--text-secondary)',
                      background: 'rgba(59, 130, 246, 0.05)', padding: '8px 12px', borderRadius: 6,
                      border: '1px solid rgba(59, 130, 246, 0.18)',
                    }}>
                      <strong style={{ color: 'var(--semantic-blue)' }}>What this means: </strong>
                      {item.pm_implication}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
