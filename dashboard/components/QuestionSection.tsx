'use client';
import { useState } from 'react';
import HorizontalBar, { BreakdownItem } from './HorizontalBar';
import DonutChart from './DonutChart';
import AreaTimeline from './AreaTimeline';
import QuoteCarousel from './QuoteCarousel';
import RadarChartComponent from './RadarChartComponent';
import HeatmapChart from './HeatmapChart';
import WordCloudChart from './WordCloudChart';
import TreemapChart from './TreemapChart';
import SankeyDiagram from './SankeyDiagram';
import { useInView } from 'react-intersection-observer';
import { formatLabel } from '@/lib/formatters';
import { SOURCE_COLORS } from '@/lib/constants';

interface SourceMatch {
  source: string;
  count: number;
  pct?: number;
}

interface AttributionItem {
  label: string;
  tag?: string;
  avg_confidence?: number;
  color?: string;
  sources?: SourceMatch[];
}

interface QuoteItem {
  text?: string;
  quote?: string;
  content?: string;
  source: string;
  source_id?: string;
  confidence?: number;
  tags?: string[];
  [key: string]: unknown;
}

interface QuestionSectionData {
  breakdown?: Array<{
    label: string;
    tag?: string;
    count: number;
    pct: number;
    avg_confidence?: number;
    color?: string;
  }>;
  total_relevant_docs?: number;
  key_quotes?: QuoteItem[];
  source_attribution?: AttributionItem[];
  avg_confidence?: number;
  temporal_distribution?: Array<{ month: string; count: number; pct: number }>;
  factor_correlation?: Array<{ factor: string; importance: number; negative_pct: number; [key: string]: unknown }>;
  retrieval_heatmap?: { rows: string[]; columns: string[]; values: number[][] };
  query_terms?: Array<{ text: string; value: number }>;
  retrieval_treemap?: Array<{ theme: string; children: Array<{ name: string; value: number }> }>;
  failure_sankey?: { nodes?: Array<{ id: string; name?: string }>; links?: Array<{ source: string; target: string; value: number }> };
  [key: string]: unknown;
}

interface QuestionSectionProps {
  data: QuestionSectionData;
  questionId: number;
}

function ChartCard({
  title,
  subtitle,
  children,
  delay = 0,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  delay?: number;
}) {
  const { ref, inView } = useInView({ threshold: 0.1, triggerOnce: true });
  return (
    <div
      ref={ref}
      className="card animate-enter"
      style={{
        animationDelay: `${delay}ms`,
        opacity: inView ? 1 : 0,
        transition: 'opacity 0.4s ease',
      }}
    >
      <div className="card-header" style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: 4, paddingBottom: 14 }}>
        <span className="card-title">{title}</span>
        {subtitle && (
          <span style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.45, fontWeight: 400 }}>
            {subtitle}
          </span>
        )}
      </div>
      <div className="card-body">{children}</div>
    </div>
  );
}

const DEFAULT_COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#06b6d4', '#64748b', '#8b5cf6', '#ec4899'];

export default function QuestionSection({ data, questionId }: QuestionSectionProps) {
  const [source, setSource] = useState<string>('all');

  // Compute active filtered data
  const baseBreakdown: BreakdownItem[] = (data.breakdown || []).map((it, idx) => ({
    label: it.label,
    tag: it.tag || `seg_${idx}`,
    count: it.count,
    pct: it.pct,
    avg_confidence: it.avg_confidence,
    color: it.color || DEFAULT_COLORS[idx % DEFAULT_COLORS.length],
  }));

  let activeBreakdown: BreakdownItem[] = baseBreakdown;
  let activeDocsCount = data.total_relevant_docs || 0;
  let activeQuotes: QuoteItem[] = data.key_quotes || [];

  if (source !== 'all' && data.source_attribution && data.source_attribution.length > 0) {
    const computedItems: BreakdownItem[] = [];
    data.source_attribution.forEach((attr, i: number) => {
      const match = attr.sources?.find((s) => s.source.toLowerCase() === source.toLowerCase());
      if (match && match.count > 0) {
        computedItems.push({
          label: attr.label,
          tag: attr.tag || `attr_${i}`,
          count: match.count,
          pct: match.pct || 0,
          avg_confidence: attr.avg_confidence || data.avg_confidence,
          color: attr.color || DEFAULT_COLORS[i % DEFAULT_COLORS.length],
        });
      }
    });

    if (computedItems.length > 0) {
      const totalCount = computedItems.reduce((acc, it) => acc + it.count, 0) || 1;
      activeBreakdown = computedItems
        .map((it) => ({
          ...it,
          pct: Number(((it.count / totalCount) * 100).toFixed(1)),
        }))
        .sort((a, b) => b.count - a.count);
      activeDocsCount = totalCount;
    }
  }

  // Filter quotes by source if selected
  if (source !== 'all' && data.key_quotes && data.key_quotes.length > 0) {
    const filtered = data.key_quotes.filter(
      (q) => q.source && q.source.toLowerCase().includes(source.toLowerCase())
    );
    if (filtered.length > 0) activeQuotes = filtered;
  }

  const sourcesList = [
    { id: 'all', label: 'All Platforms' },
    { id: 'play store', label: 'Play Store' },
    { id: 'app store', label: 'App Store' },
    { id: 'reddit', label: 'Reddit' },
    { id: 'hacker news', label: 'Hacker News' },
    { id: 'youtube', label: 'YouTube' },
  ];

  const formattedQuotes = activeQuotes.map((q) => ({
    text: q.text || q.quote || q.content || '',
    source: q.source || 'Discovery Source',
    source_id: q.source_id || '',
    confidence: q.confidence || 0.85,
    tags: q.tags || [],
    date: (q as { date?: string }).date || '',
  }));

  return (
    <div>
      {/* Channel Segment Filter Bar */}
      <div
        className="card filter-bar-card"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: 12,
          padding: '12px 18px',
          marginBottom: 24,
          background: 'var(--bg-surface)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-md)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-secondary)', marginRight: 4, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Filter by platform:
          </span>
          {sourcesList.map((s) => {
            const isSelected = source === s.id;
            return (
              <button
                key={s.id}
                onClick={() => setSource(s.id)}
                style={{
                  background: isSelected ? 'var(--semantic-blue)' : 'var(--bg-elevated)',
                  color: isSelected ? '#fff' : 'var(--text-secondary)',
                  border: `1px solid ${isSelected ? 'var(--semantic-blue)' : 'var(--border)'}`,
                  borderRadius: 16,
                  padding: '4px 12px',
                  fontSize: 12,
                  fontWeight: isSelected ? 600 : 500,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                {s.label}
              </button>
            );
          })}
        </div>

        <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
          Showing <strong style={{ color: 'var(--text-primary)' }}>{activeDocsCount.toLocaleString()}</strong> reviews
        </div>
      </div>

      {/* Row 1: Distribution Breakdown + Key Segments */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        <ChartCard
          title="Frequency Breakdown"
          subtitle="How often users reported each specific search problem within this question."
          delay={0}
        >
          <HorizontalBar data={activeBreakdown} />
        </ChartCard>

        <ChartCard
          title="Relative Share"
          subtitle="Proportional share of each issue within this research topic."
          delay={100}
        >
          <DonutChart data={activeBreakdown} />
        </ChartCard>
      </div>

      {/* Row 2: Specialized Analytics based on Inquiry ID */}
      <div style={{ marginBottom: 24 }}>
        {questionId === 1 && data.temporal_distribution && (
          <ChartCard
            title="Temporal Drift of Search Struggles"
            subtitle="Shows how struggled retrieval patterns evolve across photo age (recent vs archival memories)."
            delay={150}
          >
            <AreaTimeline data={data.temporal_distribution} />
          </ChartCard>
        )}

        {questionId === 2 && data.factor_correlation && (
          <ChartCard
            title="Memory Anchor Retention Multi-Factor Radar"
            subtitle="Compares user retention importance vs negative sentiment across visual, temporal, emotional, and social recall clues."
            delay={150}
          >
            <RadarChartComponent data={data.factor_correlation} />
          </ChartCard>
        )}

        {questionId === 3 && data.retrieval_heatmap && (
          <ChartCard
            title="Forgotten Metadata Co-Occurrence Matrix"
            subtitle="Heatmap indicating which metadata types (dates, filenames, folder locations) are simultaneously forgotten."
            delay={150}
          >
            <HeatmapChart matrix={data.retrieval_heatmap} />
          </ChartCard>
        )}

        {questionId === 4 && data.query_terms && (
          <ChartCard
            title="Query Keyword Reformulation Density"
            subtitle="Word cloud of high-frequency vague query terms used by consumers when memory is incomplete."
            delay={150}
          >
            <WordCloudChart words={data.query_terms} />
          </ChartCard>
        )}

        {questionId === 5 && data.retrieval_treemap && (
          <ChartCard
            title="False-Miss & Irrelevant Result Root Causes"
            subtitle="Hierarchical treemap clustering false-miss failure modes by semantic gap, thumbnail misclassification, and sync amnesia."
            delay={150}
          >
            <TreemapChart data={data.retrieval_treemap} />
          </ChartCard>
        )}

        {questionId === 6 && data.failure_sankey && (
          <ChartCard
            title="Search Breakdown to Doom-Scrolling Escalation Flow"
            subtitle="Sankey diagram tracing user journey from initial search query formulation to endless chronological scroll fallback and abandonment."
            delay={150}
          >
            <SankeyDiagram
              nodes={data.failure_sankey.nodes || []}
              links={data.failure_sankey.links || []}
            />
          </ChartCard>
        )}
      </div>

      {/* Cross-Platform Attribution */}
      {data.source_attribution && data.source_attribution.length > 0 && (
        <ChartCard
          title="Cross-Platform Attribution"
          subtitle="Multi-channel comparison displaying how prominently this friction topic surfaces across Google Play Store, App Store, Reddit, Hacker News, and YouTube."
          delay={250}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {data.source_attribution.slice(0, 4).map((item, i: number) => (
              <div key={`${item.tag || item.label || 'attr'}-${i}`}>
                <p style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 8 }}>{formatLabel(item.label)}</p>
                <HorizontalBar
                  data={(item.sources || []).map((s, si: number) => ({
                    label: s.source,
                    tag: `${s.source}-${si}`,
                    count: s.count,
                    pct: s.pct || 0,
                    color: SOURCE_COLORS[s.source] || '#6b7280',
                  }))}
                  showCount={true}
                />
              </div>
            ))}
          </div>
        </ChartCard>
      )}

      {/* Grounded Verbatim Quotes */}
      {formattedQuotes && formattedQuotes.length > 0 && (
        <div style={{ marginTop: 24 }}>
          <QuoteCarousel quotes={formattedQuotes} />
        </div>
      )}
    </div>
  );
}
