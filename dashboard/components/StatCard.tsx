'use client';
import { useEffect, useRef, useState, useId } from 'react';
import { useInView } from 'react-intersection-observer';
import { AreaChart, Area, ResponsiveContainer, Tooltip } from 'recharts';
import { formatLabel } from '@/lib/formatters';

interface StatCardProps {
  label: string;
  value: number;
  unit: 'count' | 'percent';
  sparkline: number[];
  trend?: 'up' | 'down' | 'stable';
  trend_pct?: number;
  delay?: number;
}

const KPI_CONFIG: Record<string, { color: string; icon: string; desc: string }> = {
  'Reviews Analyzed':              { color: '#818cf8', icon: '📚', desc: '2,223 unified multi-platform discussions' },
  'Screenshot & Meme Clutter':     { color: '#f472b6', icon: '📱', desc: '1,471 reviews (66.2% of corpus) · 29.1% signal share' },
  'Zero Results for Existing Photos': { color: '#f87171', icon: '🔍', desc: '1,209 reviews (54.4% of corpus) · 23.9% signal share' },
  'Irrelevant Search Results':     { color: '#22d3ee', icon: '⚡', desc: '393 reviews (17.7% of corpus) · Semantic ranking gap' },
  'Forgot Exact Date':             { color: '#fbbf24', icon: '📅', desc: '316 reviews (14.2% of corpus) · Calendar amnesia' },
  'Remembered Relative Time':      { color: '#a78bfa', icon: '⏳', desc: '288 reviews (13.0% of corpus) · Episodic temporal clues' },
  'Unmet Needs Identified':        { color: '#4ade80', icon: '💡', desc: '81 distinct categories (from 3,661 user statements)' },
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
  label,
  value,
  unit,
  sparkline,
  delay = 0,
}: StatCardProps) {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });
  const rawId = useId();
  const gradId = `spark-${rawId.replace(/:/g, '')}`;
  const cleanLabel = formatLabel(label);
  const config = KPI_CONFIG[cleanLabel] || KPI_CONFIG[label] || { color: '#818cf8', icon: '📸', desc: '' };
  const sparkData = (sparkline && sparkline.length > 0 ? sparkline : [value * 0.6, value * 0.8, value]).map((v, i) => ({ v, i }));

  return (
    <div
      ref={ref}
      className="card stat-card animate-enter"
      style={{
        animationDelay: `${delay}ms`,
        opacity: inView ? 1 : 0,
        minHeight: 156,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '22px 24px',
      }}
    >
      <div>
        {/* Header row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
          <span style={{ fontSize: 12.5, color: 'var(--text-secondary)', fontWeight: 600, letterSpacing: '-0.01em' }}>
            {cleanLabel}
          </span>
          <span
            style={{
              fontSize: 15,
              width: 32, height: 32,
              borderRadius: 'var(--radius-sm)',
              background: `${config.color}14`,
              border: `1px solid ${config.color}28`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {config.icon}
          </span>
        </div>

        {/* Large number */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
          <div className="stat-value tabular-nums" style={{ color: config.color }}>
            {inView ? <AnimatedNumber target={value} unit={unit} /> : formatValue(value, unit)}
          </div>
        </div>

        {config.desc && (
          <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginTop: 5, lineHeight: 1.35 }}>
            {config.desc}
          </div>
        )}
      </div>

      {/* Sparkline */}
      <div style={{ height: 36, marginTop: 12 }}>
        <ResponsiveContainer width="100%" height={36} minWidth={0} minHeight={0}>
          <AreaChart data={sparkData} margin={{ top: 2, right: 0, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={config.color} stopOpacity={0.30} />
                <stop offset="100%" stopColor={config.color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="v"
              stroke={config.color}
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
              formatter={(val: unknown) => [formatValue(Number(val), unit), cleanLabel]}
              labelFormatter={() => ''}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
