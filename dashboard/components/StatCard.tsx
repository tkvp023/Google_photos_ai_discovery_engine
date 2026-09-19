'use client';
import { useEffect, useRef, useState, useId } from 'react';
import { useInView } from 'react-intersection-observer';
import { AreaChart, Area, ResponsiveContainer, Tooltip } from 'recharts';
import { formatLabel } from '@/lib/formatters';

interface StatCardProps {
  id?: string;
  label: string;
  value: number;
  unit: 'count' | 'percent';
  sparkline: number[];
  trend?: 'up' | 'down' | 'stable';
  trend_pct?: number;
  delay?: number;
}

interface CardMeta {
  displayLabel: string;
  color: string;
  tag?: string;
  desc: string;
}

const KPI_META: Record<string, CardMeta> = {
  // By ID
  'total_reviews': {
    displayLabel: 'Reviews analyzed',
    color: '#3b82f6',
    desc: '2,223 verified discussions across 5 platforms',
  },
  'on_brief_bucket_a': {
    displayLabel: 'Search-related reviews',
    color: '#3b82f6',
    desc: '251 out of 2,223 reviews where people struggled with search',
  },
  'interpretation_failure': {
    displayLabel: 'Search misunderstands query',
    color: '#3b82f6',
    tag: '#1 Gap',
    desc: '134 out of 278 mentions (48.2% of search issues)',
  },
  'recovery_breakdown': {
    displayLabel: 'No help when search fails',
    color: '#f59e0b',
    tag: '#2 Gap',
    desc: '74 out of 278 mentions (26.6% forced scroll or dead-ends)',
  },
  'zero_results_for_existing_photo': {
    displayLabel: '"No results" for existing photos',
    color: '#f59e0b',
    desc: '531 out of 2,223 reviews describe zero results for photos they have',
  },
  'calibrated_confidence': {
    displayLabel: 'Data confidence level',
    color: '#22c55e',
    tag: 'High confidence',
    desc: 'Supported by direct user quotes with dynamic variance (±0.18 σ)',
  },
  // By Label fallback
  'Total Corpus (5 Channels)': {
    displayLabel: 'Reviews analyzed',
    color: '#3b82f6',
    desc: '2,223 verified discussions across 5 platforms',
  },
  'On-Brief Retrieval Signal (Bucket A)': {
    displayLabel: 'Search-related reviews',
    color: '#3b82f6',
    desc: '251 out of 2,223 reviews where people struggled with search',
  },
  '#1 Blocker: Interpretation Failure': {
    displayLabel: 'Search misunderstands query',
    color: '#3b82f6',
    tag: '#1 Gap',
    desc: '134 out of 278 mentions (48.2% of search issues)',
  },
  '#2 Blocker: Recovery Breakdown': {
    displayLabel: 'No help when search fails',
    color: '#f59e0b',
    tag: '#2 Gap',
    desc: '74 out of 278 mentions (26.6% forced scroll or dead-ends)',
  },
  'Zero Results for Existing Photos': {
    displayLabel: '"No results" for existing photos',
    color: '#f59e0b',
    desc: '531 out of 2,223 reviews describe zero results for photos they have',
  },
  'Calibrated Confidence (±0.18 σ)': {
    displayLabel: 'Data confidence level',
    color: '#22c55e',
    tag: 'High confidence',
    desc: 'Supported by direct user quotes with dynamic variance (±0.18 σ)',
  },
  'Screenshot & Meme Clutter': {
    displayLabel: 'Junk photos polluting search',
    color: '#64748b',
    desc: 'Screenshots and downloaded media burying personal memories',
  },
};

function formatValue(value: number, unit: string) {
  if (unit === 'percent') return `${value.toFixed(1)}%`;
  if (value >= 1000) return Math.round(value).toLocaleString();
  return Math.round(value).toString();
}

function AnimatedNumber({ target, unit, duration = 1200 }: { target: number; unit: string; duration?: number }) {
  const [current, setCurrent] = useState(0);
  const startTime = useRef<number | null>(null);

  useEffect(() => {
    startTime.current = null;
    const step = (timestamp: number) => {
      if (!startTime.current) startTime.current = timestamp;
      const progress = Math.min((timestamp - startTime.current) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 4); // quartic ease-out
      setCurrent(eased * target);
      if (progress < 1) requestAnimationFrame(step);
    };
    const id = requestAnimationFrame(step);
    return () => cancelAnimationFrame(id);
  }, [target, duration]);

  return <>{formatValue(current, unit)}</>;
}

export default function StatCard({
  id,
  label,
  value,
  unit,
  sparkline,
  delay = 0,
}: StatCardProps) {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });
  const rawId = useId();
  const gradId = `spark-${rawId.replace(/:/g, '')}`;
  
  const meta = (id && KPI_META[id]) || KPI_META[label] || {
    displayLabel: formatLabel(label),
    color: '#3b82f6',
    desc: '',
  };

  const sparkData = (sparkline && sparkline.length > 0 ? sparkline : [value * 0.6, value * 0.8, value]).map((v, i) => ({ v, i }));

  return (
    <div
      ref={ref}
      className="card stat-card animate-enter"
      style={{
        animationDelay: `${delay}ms`,
        opacity: inView ? 1 : 0,
        minHeight: 154,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '20px 22px',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-md)',
        background: 'var(--bg-card)',
      }}
    >
      <div>
        {/* Header row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
          <span style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 600, letterSpacing: '-0.01em' }}>
            {meta.displayLabel}
          </span>
          {meta.tag ? (
            <span
              style={{
                fontSize: 10.5,
                fontWeight: 600,
                padding: '2px 8px',
                borderRadius: 12,
                color: meta.color,
                background: `${meta.color}14`,
                border: `1px solid ${meta.color}30`,
              }}
            >
              {meta.tag}
            </span>
          ) : (
            <span
              style={{
                width: 7,
                height: 7,
                borderRadius: '50%',
                background: meta.color,
                opacity: 0.7,
              }}
            />
          )}
        </div>

        {/* Large number */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
          <div className="stat-value tabular-nums" style={{ color: meta.color, fontSize: 30, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif" }}>
            {inView ? <AnimatedNumber target={value} unit={unit} /> : formatValue(value, unit)}
          </div>
        </div>

        {meta.desc && (
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 6, lineHeight: 1.4 }}>
            {meta.desc}
          </div>
        )}
      </div>

      {/* Sparkline */}
      <div style={{ height: 36, marginTop: 12 }}>
        <ResponsiveContainer width="100%" height={36} minWidth={0} minHeight={0}>
          <AreaChart data={sparkData} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={meta.color} stopOpacity={0.30} />
                <stop offset="100%" stopColor={meta.color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="v"
              stroke={meta.color}
              strokeWidth={2}
              fill={`url(#${gradId})`}
              dot={false}
              isAnimationActive={inView}
              animationDuration={1000}
              animationEasing="ease-out"
            />
            <Tooltip
              contentStyle={{
                background: 'var(--bg-elevated)',
                border: '1px solid var(--border)',
                borderRadius: 10,
                fontSize: 11,
                padding: '4px 10px',
                boxShadow: 'var(--shadow-card)',
                backdropFilter: 'blur(12px)',
              }}
              itemStyle={{ color: 'var(--text-primary)', fontWeight: 600 }}
              formatter={(val: unknown) => [formatValue(Number(val), unit), meta.displayLabel]}
              labelFormatter={() => ''}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
