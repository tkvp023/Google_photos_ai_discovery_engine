'use client';
import { useState } from 'react';
import { useInView } from 'react-intersection-observer';
import HorizontalBar from './HorizontalBar';
import { QuoteCard } from './QuoteCarousel';
import { formatLabel } from '@/lib/formatters';

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
  date?: string;
  issue?: string;
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

const BUCKET_A_STAGES = [
  { label: 'Search misunderstands query (#1 Gap)', tag: 'interpretation', count: 134, pct: 48.2, avg_confidence: 0.887, color: '#3b82f6' },
  { label: 'No help when search fails (#2 Gap)', tag: 'recovery', count: 74, pct: 26.6, avg_confidence: 0.849, color: '#f59e0b' },
  { label: 'Can\'t spot the right photo in clutter', tag: 'evaluation', count: 51, pct: 18.3, avg_confidence: 0.885, color: '#64748b' },
  { label: 'Can\'t find the right words to describe photo', tag: 'expression', count: 19, pct: 6.8, avg_confidence: 0.844, color: '#64748b' },
];

export default function GapsContent({ data }: GapsContentProps) {
  const [cohortView, setCohortView] = useState<'all' | 'bucket_a'>('bucket_a');

  const formattedBreakdown = cohortView === 'bucket_a'
    ? BUCKET_A_STAGES
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
              2,223 total reviews = 1,583 app store reviews + 640 tech forum discussions
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
              <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--semantic-blue)' }}>1,583 reviews (71.2%)</span>
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginBottom: 6 }}>
              1,583 out of 2,223 total reviews
            </div>
            <p style={{ fontSize: 12.5, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.45 }}>
              Google Play Store (975) &amp; Apple App Store (608). Captures high-volume customer sentiment, ratings, and immediate everyday retrieval breakdowns.
            </p>
          </div>

          {/* Technical Community Discussions */}
          <div style={{ padding: 16, background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
              <span style={{ fontSize: 13.5, fontWeight: 600, color: 'var(--text-primary)' }}>Technical Discussions</span>
              <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--semantic-blue)' }}>640 discussions (28.8%)</span>
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginBottom: 6 }}>
              640 out of 2,223 total reviews
            </div>
            <p style={{ fontSize: 12.5, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.45 }}>
              Reddit (319), Hacker News (242), and YouTube teardowns (79). Captures detailed technical complaints: OCR indexing lag, face clustering inaccuracies, and self-hosted migrations.
            </p>
          </div>
        </div>

        <div style={{ padding: '10px 14px', background: 'var(--bg-elevated)', borderRadius: 8, border: '1px solid var(--border)', fontSize: 12.5, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          <strong style={{ color: 'var(--text-primary)' }}>Note on cohorts: </strong>
          Use the toggle buttons below to switch between the <strong>Search-related only (251 reviews)</strong> focus cohort and <strong>All feedback (2,223 reviews)</strong>.
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Issue breakdown */}
        <AnimatedCard delay={0}>
          <div className="card-header" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 6, paddingBottom: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
              <span className="card-title">
                {cohortView === 'all' ? 'All Feedback: Issue Breakdown' : 'Search Breakdown: Four Failure Stages'}
              </span>
              <div style={{ display: 'flex', gap: 6 }}>
                <button
                  onClick={() => setCohortView('bucket_a')}
                  style={{
                    padding: '4px 12px',
                    borderRadius: 14,
                    fontSize: 11.5,
                    fontWeight: cohortView === 'bucket_a' ? 700 : 500,
                    background: cohortView === 'bucket_a' ? 'var(--semantic-blue)' : 'var(--bg-elevated)',
                    color: cohortView === 'bucket_a' ? '#fff' : 'var(--text-secondary)',
                    border: '1px solid var(--border)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                >
                  Search-related only (251)
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
                  All feedback (2,223)
                </button>
              </div>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.45, fontWeight: 400, marginTop: 2 }}>
              {cohortView === 'all'
                ? 'Shows overall problem distribution across all 2,223 reviews before filtering out non-search feedback.'
                : 'Shows the 4 breakdown stages across the 251 search-related reviews (278 specific mentions).'}
            </div>
          </div>
          <div className="card-body">
            <HorizontalBar
              data={formattedBreakdown}
              showConfidence={cohortView === 'bucket_a'}
              denominator={cohortView === 'bucket_a' ? 278 : 5061}
            />
          </div>
        </AnimatedCard>

        {/* Impact on hesitation */}
        <AnimatedCard delay={100}>
          <div className="card-header" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4, paddingBottom: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
              <span className="card-title">Correlation with Search Abandonment</span>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.45, fontWeight: 400, marginTop: 2 }}>
              Correlation coefficient (r) linking search friction points to users giving up on search.
            </div>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              {(data.correlation_with_hesitation || []).map((item) => (
                <div key={item.systemic_issue} style={{
                  padding: '13px 15px',
                  background: 'var(--bg-elevated)',
                  borderRadius: 'var(--radius-md)',
                  borderLeft: '3px solid var(--semantic-blue)',
                  border: '1px solid var(--border)',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{formatLabel(item.systemic_issue)}</span>
                    <span style={{
                      fontSize: 13, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif",
                      color: item.correlation_hint > 0.6 ? 'var(--semantic-amber)' : 'var(--semantic-blue)',
                    }}>
                      r = {item.correlation_hint.toFixed(2)}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: 14, fontSize: 12, color: 'var(--text-muted)' }}>
                    <span>Frequency: {item.systemic_frequency.toLocaleString()}</span>
                    <span>Hesitation: {item.hesitation_frequency.toLocaleString()}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>→ {formatLabel(item.related_hesitation)}</span>
                  </div>
                </div>
              ))}
              {(!data.correlation_with_hesitation || data.correlation_with_hesitation.length === 0) && (
                <div className="empty-state">
                  <div className="empty-state-text">No correlation data available</div>
                </div>
              )}
            </div>
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
                  tags: [q.issue || ''],
                  source_id: '',
                  confidence: 0.85,
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
