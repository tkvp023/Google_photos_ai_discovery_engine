'use client';
import { useState } from 'react';
import { useInView } from 'react-intersection-observer';
import HorizontalBar from './HorizontalBar';
import { QuoteCard } from './QuoteCarousel';

function AnimatedCard({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const { ref, inView } = useInView({ threshold: 0.1, triggerOnce: true });
  return (
    <div
      ref={ref}
      className="card animate-section"
      style={{
        animationDelay: `${delay}ms`,
        opacity: inView ? 1 : 0,
        transition: 'opacity 0.5s ease',
      }}
    >
      {children}
    </div>
  );
}

interface IssueBreakdownItem {
  label: string;
  count: number;
  pct: number;
  tag?: string;
  color?: string;
  [key: string]: unknown;
}

interface CorrelationItem {
  systemic_issue: string;
  correlation_hint: number;
  systemic_frequency: number;
  hesitation_frequency: number;
  related_hesitation: string;
}

interface KeyQuoteItem {
  quote?: string;
  text?: string;
  content?: string;
  author?: string;
  source?: string;
  source_id?: string;
  date?: string;
  issue?: string;
  tags?: string[];
  confidence?: number;
  [key: string]: unknown;
}

interface GapsContentProps {
  data: {
    total_documents?: number;
    total_community_docs?: number;
    total_secondary_docs?: number;
    total_store_reviews?: number;
    issue_breakdown: IssueBreakdownItem[];
    correlation_with_hesitation: CorrelationItem[];
    key_quotes: KeyQuoteItem[];
  };
}

const ISSUE_COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#06b6d4', '#64748b', '#8b5cf6', '#ec4899'];

const COGNITIVE_BREAKDOWN_STAGES = [
  { label: 'Query Articulation Gap (#1 Stage)', tag: 'expression', count: 953, pct: 59.0, avg_confidence: 0.911, color: '#f59e0b' },
  { label: 'Search Misunderstanding (#2 Stage)', tag: 'interpretation', count: 628, pct: 38.9, avg_confidence: 0.905, color: '#3b82f6' },
  { label: 'No Help When Search Fails (#3 Stage)', tag: 'recovery', count: 26, pct: 1.6, avg_confidence: 0.829, color: '#ec4899' },
  { label: 'Results Disambiguation Overload (#4 Stage)', tag: 'evaluation', count: 9, pct: 0.6, avg_confidence: 0.877, color: '#8b5cf6' },
];

export default function GapsContent({ data }: GapsContentProps) {
  const [cohortView, setCohortView] = useState<'all' | 'stages'>('stages');

  const formattedBreakdown = cohortView === 'stages'
    ? COGNITIVE_BREAKDOWN_STAGES
    : (data.issue_breakdown || []).map((item, idx) => ({
        label: item.label,
        tag: item.tag || `issue_${idx}`,
        count: item.count,
        pct: item.pct,
        color: item.color || ISSUE_COLORS[idx % ISSUE_COLORS.length],
      }));

  return (
    <>
      {/* Corpus Composition & Channel Breakdown Card */}
      <div
        style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-lg)',
          padding: '24px 26px',
          marginBottom: 24,
          boxShadow: 'var(--shadow-card)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14, flexWrap: 'wrap', gap: 10 }}>
          <div>
            <h3 style={{ fontSize: 17, fontWeight: 700, margin: 0, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
              Feedback Sources Breakdown
            </h3>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 3 }}>
              1,616 total search-specific reviews = 1,080 app store reviews + 536 tech forum discussions
            </div>
          </div>
          <span
            style={{
              fontSize: 11.5,
              fontWeight: 600,
              padding: '4px 12px',
              borderRadius: 14,
              background: 'rgba(59, 130, 246, 0.08)',
              color: 'var(--semantic-blue)',
              border: '1px solid rgba(59, 130, 246, 0.25)',
            }}
          >
            5 Platform Channels
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 14, marginBottom: 16 }}>
          {/* App Store Reviews */}
          <div style={{ padding: 16, background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
              <span style={{ fontSize: 13.5, fontWeight: 600, color: 'var(--text-primary)' }}>Consumer App Stores</span>
              <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--semantic-blue)' }}>1,080 reviews (66.8%)</span>
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginBottom: 6 }}>
              1,080 out of 1,616 search-specific reviews
            </div>
            <p style={{ fontSize: 12.5, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.45 }}>
              Google Play Store (969) &amp; Apple App Store (111). Captures everyday memory recall friction, natural language failures, and immediate retrieval breakdowns.
            </p>
          </div>

          {/* Technical Community Discussions */}
          <div style={{ padding: 16, background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
              <span style={{ fontSize: 13.5, fontWeight: 600, color: 'var(--text-primary)' }}>Technical Discussions</span>
              <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--semantic-blue)' }}>536 discussions (33.2%)</span>
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginBottom: 6 }}>
              536 out of 1,616 search-specific reviews
            </div>
            <p style={{ fontSize: 12.5, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.45 }}>
              Hacker News (455), Reddit (54), and YouTube teardowns (27). Captures in-depth technical analysis: OCR indexing lag, face clustering inaccuracies, and self-hosted migrations.
            </p>
          </div>
        </div>

        <div style={{ padding: '10px 14px', background: 'var(--bg-elevated)', borderRadius: 8, border: '1px solid var(--border)', fontSize: 12.5, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          <strong style={{ color: 'var(--text-primary)' }}>Corpus Scoping: </strong>
          All 1,616 analyzed discussions strictly represent verified personal visual memory search failures across 5 unified platforms with 100% exact substring quote grounding.
        </div>
      </div>

      <div style={{ marginBottom: 24 }}>
        {/* Issue breakdown */}
        <AnimatedCard delay={0}>
          <div className="card-header" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 6, paddingBottom: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
              <span className="card-title">
                {cohortView === 'all' ? 'Systemic Issue Breakdown' : 'Four Breakdown Stages'}
              </span>
              <div style={{ display: 'flex', gap: 6 }}>
                <button
                  onClick={() => setCohortView('stages')}
                  style={{
                    padding: '4px 12px',
                    borderRadius: 14,
                    fontSize: 11.5,
                    fontWeight: cohortView === 'stages' ? 700 : 500,
                    background: cohortView === 'stages' ? 'var(--semantic-blue)' : 'var(--bg-elevated)',
                    color: cohortView === 'stages' ? '#fff' : 'var(--text-secondary)',
                    border: '1px solid var(--border)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  Breakdown Stages (1,616)
                </button>
                <button
                  onClick={() => setCohortView('all')}
                  style={{
                    padding: '4px 12px',
                    borderRadius: 14,
                    fontSize: 11.5,
                    fontWeight: cohortView === 'all' ? 700 : 500,
                    background: cohortView === 'all' ? 'var(--semantic-blue)' : 'var(--bg-elevated)',
                    color: cohortView === 'all' ? '#fff' : 'var(--text-secondary)',
                    border: '1px solid var(--border)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  Systemic Vectors (1,616)
                </button>
              </div>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.45, fontWeight: 400, marginTop: 2 }}>
              {cohortView === 'all'
                ? 'Shows overall systemic failure vector distribution across the 1,616 in-scope search reviews.'
                : 'Shows the 4 breakdown stages across the 1,616 search-specific reviews (1,616 verified tags).'}
            </div>
          </div>
          <div className="card-body">
            <HorizontalBar
              data={formattedBreakdown}
              showConfidence={cohortView === 'stages'}
              denominator={1616}
              unit="reviews"
              showTagExplanation={false}
            />
          </div>
        </AnimatedCard>
      </div>

      {/* Key quotes */}
      {data.key_quotes && data.key_quotes.length > 0 && (
        <AnimatedCard delay={200}>
          <div className="card-header" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4, paddingBottom: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
              <span className="card-title">Representative User Problem Statements</span>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{data.key_quotes.length} quotes</span>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.45, fontWeight: 400, marginTop: 2 }}>
              Verbatim user feedback describing specific retrieval failures and search frustration.
            </div>
          </div>
          <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {data.key_quotes.map((q, i) => (
              <QuoteCard
                key={i}
                quote={{
                  text: q.text || q.quote || q.content || '',
                  source: q.source || 'Community Forum',
                  tags: q.tags && q.tags.length > 0 ? q.tags : [q.issue || ''],
                  source_id: q.source_id || '',
                  confidence: q.confidence || 0.85,
                  date: q.date || '',
                }}
                accent="var(--semantic-blue)"
              />
            ))}
          </div>
        </AnimatedCard>
      )}
    </>
  );
}
