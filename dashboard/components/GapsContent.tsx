'use client';
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
    total_community_docs?: number;
    total_secondary_docs?: number;
    issue_breakdown: IssueBreakdownItem[];
    correlation_with_hesitation: CorrelationItem[];
    key_quotes: KeyQuoteItem[];
  };
}

const ISSUE_COLORS = ['#818cf8', '#4ade80', '#fbbf24', '#22d3ee', '#f87171', '#fb923c', '#f472b6'];

export default function GapsContent({ data }: GapsContentProps) {
  const formattedBreakdown = (data.issue_breakdown || []).map((item, idx) => ({
    label: item.label,
    tag: item.tag || `issue_${idx}`,
    count: item.count,
    pct: item.pct,
    color: item.color || ISSUE_COLORS[idx % ISSUE_COLORS.length],
  }));

  return (
    <>
      <div
        className="insight-banner"
        style={{ marginBottom: 24 }}
      >
        <span className="insight-icon">💡</span>
        <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.55 }}>
          <strong style={{ color: 'var(--brand-primary)' }}>Unified Multi-Platform Methodology:</strong> Synthesizing real-world consumer reviews across all 5 channels (Google Play, Apple App Store, Reddit, Hacker News, and YouTube teardowns) to reveal root architectural bottlenecks — such as OCR indexing lag, face clustering inaccuracies, screenshot clutter overflow, and timeline scrolling fatigue.
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* Issue breakdown */}
        <AnimatedCard delay={0}>
          <div className="card-header" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4, paddingBottom: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
              <span className="card-title">Systemic Architecture Breakdown</span>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{(data.total_community_docs || data.total_secondary_docs || 640).toLocaleString()} In-Depth Discussions</span>
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--text-muted)', lineHeight: 1.45, fontWeight: 400, marginTop: 2 }}>
              💡 <strong style={{ color: 'var(--text-secondary)' }}>How to read:</strong> Quantifies root architectural and system-level bottlenecks surfaced across in-depth community engineering discussions (Reddit, Hacker News, YouTube teardowns).
            </div>
          </div>
          <div className="card-body">
            <HorizontalBar data={formattedBreakdown} />
          </div>
        </AnimatedCard>

        {/* Impact on hesitation */}
        <AnimatedCard delay={100}>
          <div className="card-header" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4, paddingBottom: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
              <span className="card-title">Correlation with Search Abandonment</span>
            </div>
            <div style={{ fontSize: 11.5, color: 'var(--text-muted)', lineHeight: 1.45, fontWeight: 400, marginTop: 2 }}>
              💡 <strong style={{ color: 'var(--text-secondary)' }}>How to read:</strong> Pearson correlation coefficient (r) linking technical platform bottlenecks to end-user search abandonment and retrieval fatigue.
            </div>
          </div>
          <div className="card-body">
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {(data.correlation_with_hesitation || []).map((item) => (
                <div key={item.systemic_issue} style={{
                  padding: '14px 16px',
                  background: 'var(--card-bg-subtle, rgba(255,255,255,0.02))',
                  borderRadius: 'var(--radius-md)',
                  borderLeft: '3px solid var(--brand-primary)',
                  border: '1px solid var(--border)',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                    <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>{formatLabel(item.systemic_issue)}</span>
                    <span style={{
                      fontSize: 13, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif",
                      color: item.correlation_hint > 0.6 ? '#f87171' : '#fbbf24',
                    }}>
                      r = {item.correlation_hint.toFixed(2)}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: 16, fontSize: 12, color: 'var(--text-muted)' }}>
                    <span>Systemic: {item.systemic_frequency.toLocaleString()}</span>
                    <span>Hesitation: {item.hesitation_frequency.toLocaleString()}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>→ {formatLabel(item.related_hesitation)}</span>
                  </div>
                </div>
              ))}
              {(!data.correlation_with_hesitation || data.correlation_with_hesitation.length === 0) && (
                <div className="empty-state">
                  <div className="empty-state-icon">🔗</div>
                  <div className="empty-state-text">Run pipeline to see correlations</div>
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
            <div style={{ fontSize: 11.5, color: 'var(--text-muted)', lineHeight: 1.45, fontWeight: 400, marginTop: 2 }}>
              💡 <strong style={{ color: 'var(--text-secondary)' }}>How to read:</strong> In-depth customer complaint excerpts detailing specific retrieval crashes, indexing lags, and sync bottlenecks.
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
                accent="var(--brand-primary)"
              />
            ))}
          </div>
        </AnimatedCard>
      )}
    </>
  );
}
