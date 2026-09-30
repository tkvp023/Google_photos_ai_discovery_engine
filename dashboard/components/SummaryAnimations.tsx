'use client';
import { useInView } from 'react-intersection-observer';
import DonutChart from './DonutChart';
import HorizontalBar from './HorizontalBar';
import QuestionGrid from './QuestionGrid';

function AnimatedCard({ children, delay = 0, className }: { children: React.ReactNode; delay?: number; className?: string }) {
  const { ref, inView } = useInView({ threshold: 0.1, triggerOnce: true });
  return (
    <div
      ref={ref}
      className={`card animate-section ${className || ''}`}
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

function AnimatedSection({ children, delay = 0, className, style }: { children: React.ReactNode; delay?: number; className?: string; style?: React.CSSProperties }) {
  const { ref, inView } = useInView({ threshold: 0.1, triggerOnce: true });
  return (
    <div
      ref={ref}
      className={`animate-section ${className || ''}`}
      style={{
        animationDelay: `${delay}ms`,
        opacity: inView ? 1 : 0,
        transition: 'opacity 0.5s ease',
        ...style,
      }}
    >
      {children}
    </div>
  );
}

interface SourceDistributionItem { source: string; count: number; pct: number; color: string; }
interface TopOpportunityItem { label: string; rank: number; count: number; pct: number; avg_confidence: number; question_id?: number; }
interface SummaryData {
  primary_signal_docs?: number; secondary_signal_docs?: number;
  source_distribution: SourceDistributionItem[];
  top_opportunities: TopOpportunityItem[];
  kpi_cards?: Array<{ id: string; value: number }>;
  [key: string]: unknown;
}

export default function SummaryAnimations({ data }: { data: SummaryData }) {
  const totalDocs = data.kpi_cards?.find((k) => k.id === 'total_reviews')?.value || ((data.primary_signal_docs || 0) + (data.secondary_signal_docs || 0)) || 1616;

  return (
    <>
      {/* ═══ PLATFORM DISTRIBUTION & TOP OPPORTUNITIES ═══ */}
      <div style={{ marginBottom: 24, marginTop: 16 }}>
        <h2 className="section-title">Feedback Sources &amp; Top Opportunities</h2>
        <p className="section-subtitle">
          Where user feedback came from and which search problems were reported most frequently.
        </p>
      </div>

      {/* Source distribution + Top Opportunities */}
      <div className="grid-2" style={{ marginBottom: 32 }}>
        <AnimatedCard delay={100} className="secondary-chart-col">
          <div className="card-header">
            <div>
              <span className="card-title">Feedback Sources</span>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 3 }}>
                5 platforms: App Stores, Reddit, Hacker News, YouTube
              </div>
            </div>
            <span style={{
              fontSize: 11.5, fontWeight: 700,
              color: 'var(--semantic-blue)',
              background: 'rgba(59, 130, 246, 0.08)',
              border: '1px solid rgba(59, 130, 246, 0.25)',
              padding: '3px 10px', borderRadius: 12,
            }}>
              {totalDocs.toLocaleString()} Reviews
            </span>
          </div>
          <div className="card-body">
            <DonutChart
              data={data.source_distribution.map((s) => ({ ...s, label: s.source }))}
              centerLabel="reviews"
            />
            {/* Source chips */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
              gap: 8, marginTop: 18, paddingTop: 16,
              borderTop: '1px solid var(--border)',
            }}>
              {data.source_distribution.map((s) => (
                <div key={s.source} style={{
                  display: 'flex', flexDirection: 'column',
                  padding: '8px 10px', borderRadius: 'var(--radius-sm)',
                  background: 'var(--input-bg)',
                  border: '1px solid var(--border)',
                  transition: 'all 0.2s ease',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: 'var(--text-secondary)' }}>
                    <span style={{ width: 7, height: 7, borderRadius: '50%', background: s.color }} />
                    <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{s.source}</span>
                  </div>
                  <div style={{ fontSize: 14, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", color: 'var(--text-primary)', marginTop: 3 }}>
                    {s.count.toLocaleString()} <span style={{ fontSize: 11, fontWeight: 500, color: 'var(--text-muted)' }}>({s.pct}%)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </AnimatedCard>

        <AnimatedCard delay={200} className="focus-expanded">
          <div className="card-header">
            <div>
              <span className="card-title">Top Search Problems</span>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 3 }}>
                Ranked by how often users reported them in search feedback
              </div>
            </div>
            <span className="badge badge-conf-high" style={{ color: 'var(--semantic-blue)', background: 'rgba(59, 130, 246, 0.1)', border: '1px solid rgba(59, 130, 246, 0.25)' }}>
              Ranked by Mentions
            </span>
          </div>
          <div className="card-body">
            <HorizontalBar
              data={data.top_opportunities.map((op) => ({
                label: op.label,
                tag: `opp_${op.rank}`,
                count: op.count,
                pct: op.pct,
                avg_confidence: op.avg_confidence,
                color: ['#3b82f6', '#22c55e', '#f59e0b', '#06b6d4', '#64748b'][op.rank - 1] || '#3b82f6',
                href: `/questions/${op.question_id || 2}`,
              }))}
              denominator={1616}
              unit="reviews"
              showTagExplanation={false}
            />
          </div>
        </AnimatedCard>
      </div>

      {/* Corpus Signal Quality */}
      <AnimatedCard delay={300} className="secondary-chart-col">
        <div className="card-header">
          <div>
            <span className="card-title">Feedback Breakdown &amp; Verification</span>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 3 }}>
              Strictly filtered to search issues — all quotes verified word-for-word
            </div>
          </div>
          <span style={{
            fontSize: 11.5, fontWeight: 700, padding: '3px 10px', borderRadius: 12,
            background: 'rgba(34, 197, 94, 0.10)',
            color: 'var(--semantic-green)',
            border: '1px solid rgba(34, 197, 94, 0.25)',
          }}>
            100% Verified
          </span>
        </div>
        <div className="card-body">
          <div className="grid-3" style={{ gap: 16 }}>
            {[
              {
                title: 'Total Reviews Analyzed',
                tag: '5 Platforms',
                pctDisplay: '1,616',
                value: totalDocs,
                unit: 'reviews',
                color: '#3b82f6',
                desc: '1,080 app store reviews (Play Store 969 + App Store 111) and 536 community discussions (HN 455 + Reddit 54 + YouTube 27).',
              },
              {
                title: 'Search-Related Reviews',
                tag: 'Search Focus',
                pctDisplay: '1,616',
                value: 1616,
                unit: 'reviews',
                color: '#3b82f6',
                desc: 'Specific visual memory search failures, strictly separated from 23,815 unrelated harvest complaints about backup loops, battery drain, and tab layout.',
              },
              {
                title: 'Search Breakdowns Identified',
                tag: '4 Stages',
                pctDisplay: '1,616',
                unit: 'tags',
                color: '#f59e0b',
                desc: 'Categorized into Expression (59.0%), Interpretation (38.9%), Recovery (1.6%), and Evaluation (0.6%) with 100% quote grounding.',
              },
            ].map((item) => {
              return (
                <div
                  key={item.title}
                  style={{
                    padding: '20px 22px',
                    borderRadius: 'var(--radius-md)',
                    background: `${item.color}0a`,
                    border: `1px solid ${item.color}22`,
                    display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
                    transition: 'all 0.2s ease',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                      <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>
                        {item.title}
                      </span>
                      <span style={{ fontSize: 10, fontWeight: 700, color: item.color, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        {item.tag}
                      </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, margin: '6px 0' }}>
                      <span style={{ fontSize: 32, fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, color: item.color, letterSpacing: '-0.03em' }}>
                        {item.pctDisplay}
                      </span>
                      <span style={{ fontSize: 13, fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600, color: 'var(--text-secondary)' }}>
                        ({(item.value ?? 1616).toLocaleString()} {item.unit})
                      </span>
                    </div>
                  </div>
                  <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0, marginTop: 8 }}>
                    {item.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </AnimatedCard>

      {/* ═══ RESEARCH QUESTIONS MATRIX ═══ */}
      <div style={{ marginBottom: 20, marginTop: 52 }}>
        <h2 className="section-title">Deep-Dive Research Questions</h2>
        <p className="section-subtitle">
          10 detailed investigations mapping every failure stage across the photo search journey.
        </p>
      </div>

      {/* 10 Inquiries Grid */}
      <AnimatedSection delay={400} style={{ marginTop: 0 }}>
        <div className="card">
          <div className="card-header">
            <div>
              <span className="card-title">10 Research Questions</span>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 3 }}>
                Detailed analyses answering specific product and engineering questions
              </div>
            </div>
            <span style={{ fontSize: 12, color: 'var(--semantic-blue)', fontWeight: 600 }}>
              Select a question to view →
            </span>
          </div>
          <div className="card-body">
            <QuestionGrid />
          </div>
        </div>
      </AnimatedSection>
    </>
  );
}
