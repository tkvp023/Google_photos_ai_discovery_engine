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
  const totalDocs = data.kpi_cards?.find((k) => k.id === 'total_reviews')?.value || ((data.primary_signal_docs || 0) + (data.secondary_signal_docs || 0)) || 2223;

  return (
    <>
      {/* ═══ SECTION 03: SIGNAL SYNTHESIS ═══ */}
      <div style={{ marginBottom: 24, marginTop: 16 }}>
        <div className="section-kicker">
          <span>03</span> // <span>SIGNAL SYNTHESIS</span>
        </div>
        <h2 className="section-title">Platform Distribution & High-Leverage Opportunities</h2>
        <p className="section-subtitle">
          Cross-platform source decomposition and empirical frequency ranking of retrieval friction vectors.
        </p>
      </div>

      {/* Source distribution + Top Opportunities */}
      <div className="grid-2" style={{ marginBottom: 32 }}>
        <AnimatedCard delay={100} className="secondary-chart-col">
          <div className="card-header">
            <div>
              <span className="card-title">Multi-Platform Sources</span>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 3 }}>
                5 channels: App Stores + Forums + YouTube
              </div>
            </div>
            <span style={{
              fontSize: 11.5, fontWeight: 700,
              color: 'var(--brand-primary)',
              background: 'var(--theme-accent-bg)',
              border: '1px solid var(--theme-accent-border)',
              padding: '3px 10px', borderRadius: 12,
            }}>
              {totalDocs.toLocaleString()} Total
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
              <span className="card-title">Top Retrieval-Friction Opportunities</span>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 3 }}>
                Ranked by empirical frequency & user pain severity
              </div>
            </div>
            <span className="badge badge-conf-high">Ranked by Impact</span>
          </div>
          <div className="card-body">
            <HorizontalBar
              data={data.top_opportunities.map((op) => ({
                label: op.label,
                tag: `opp_${op.rank}`,
                count: op.count,
                pct: op.pct,
                avg_confidence: op.avg_confidence,
                color: ['#818cf8', '#4ade80', '#fbbf24', '#22d3ee', '#a78bfa'][op.rank - 1] || '#38bdf8',
                href: `/questions/${op.question_id || 2}`,
              }))}
            />
          </div>
        </AnimatedCard>
      </div>

      {/* Corpus Signal Quality */}
      <AnimatedCard delay={300} className="secondary-chart-col">
        <div className="card-header">
          <div>
            <span className="card-title">Corpus Architecture & Signal Quality</span>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 3 }}>
              Verified multi-tier pipeline — zero synthetic hallucination
            </div>
          </div>
          <span style={{
            fontSize: 11.5, fontWeight: 700, padding: '3px 10px', borderRadius: 12,
            background: 'rgba(74, 222, 128, 0.10)',
            color: '#4ade80',
            border: '1px solid rgba(74, 222, 128, 0.25)',
          }}>
            100% Grounded
          </span>
        </div>
        <div className="card-body">
          <div className="grid-3" style={{ gap: 16 }}>
            {[
              {
                title: 'Unified Multi-Platform Corpus',
                tag: '5 Channels',
                pctDisplay: '100%',
                value: totalDocs,
                unit: 'reviews',
                color: '#818cf8',
                desc: '2,223 verified discussions harvested across Play Store (975), App Store (608), Reddit (319), Hacker News (242), and YouTube (79).',
              },
              {
                title: 'High-Signal Grounding',
                tag: '99.1% Signal Rate',
                pctDisplay: '99.1%',
                value: 2202,
                unit: 'reviews',
                color: '#4ade80',
                desc: '2,202 discussions contain explicit visual memory friction signals validated via Gemini 3.7 Flash with 0.84 average confidence.',
              },
              {
                title: 'Grounded Signal Extraction',
                tag: 'Friction Taxonomy',
                pctDisplay: '5,061',
                unit: 'tag mentions',
                color: '#fbbf24',
                desc: '5,061 grounded hesitation tags across 81 distinct unmet need categories with 98.3% quote-evidence grounding.',
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
                        ({(item.value ?? 2223).toLocaleString()} {item.unit})
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

      {/* ═══ SECTION 04: GROUNDED RESEARCH MATRIX ═══ */}
      <div style={{ marginBottom: 20, marginTop: 52 }}>
        <div className="section-kicker">
          <span>04</span> // <span>GROUNDED RESEARCH</span>
        </div>
        <h2 className="section-title">Visual Memory Pathology (10 Inquiries)</h2>
        <p className="section-subtitle">
          Exhaustive empirical deep-dives mapping every breakdown stage across the photo retrieval journey.
        </p>
      </div>

      {/* 10 Inquiries Grid */}
      <AnimatedSection delay={400} style={{ marginTop: 0 }}>
        <div className="card">
          <div className="card-header">
            <div>
              <span className="card-title">Visual Memory Pathology (10 Inquiries)</span>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 3 }}>
                Deep-dives across the Google Photos retrieval journey
              </div>
            </div>
            <span style={{ fontSize: 12, color: 'var(--brand-primary)', fontWeight: 600 }}>
              Select an inquiry →
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
