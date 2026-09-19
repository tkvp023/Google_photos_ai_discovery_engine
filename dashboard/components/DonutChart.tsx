'use client';
import { useState, useMemo } from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { useInView } from 'react-intersection-observer';
import { formatLabel } from '@/lib/formatters';

interface DonutChartProps {
  data: { label?: string; source?: string; tag?: string; count: number; pct: number; color: string }[];
  title?: string;
  centerLabel?: string;
  maxSlices?: number;
}

const RADIAN = Math.PI / 180;
interface CustomLabelProps {
  cx?: number;
  cy?: number;
  midAngle?: number;
  innerRadius?: number;
  outerRadius?: number;
  pct?: number;
}
function CustomLabel({ cx = 0, cy = 0, midAngle = 0, innerRadius = 0, outerRadius = 0, pct = 0 }: CustomLabelProps) {
  if (pct < 8) return null; // Only show on large slices to prevent label collisions
  const radius = innerRadius + (outerRadius - innerRadius) * 0.52;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  return (
    <text
      x={x}
      y={y}
      fill="#ffffff"
      textAnchor="middle"
      dominantBaseline="central"
      fontSize={11}
      fontWeight={700}
      style={{ pointerEvents: 'none', textShadow: '0 1px 3px rgba(0,0,0,0.85)' }}
    >
      {pct.toFixed(0)}%
    </text>
  );
}

export default function DonutChart({
  data,
  title,
  centerLabel,
  maxSlices = 5,
}: DonutChartProps) {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });
  const [showAll, setShowAll] = useState(false);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  const total = data?.reduce((s, d) => s + (d.count || 0), 0) || 0;
  const safeTotal = total || 1;

  // Consolidate data: when not showAll and item count > maxSlices, group long tail into "Other"
  const displayData = useMemo(() => {
    if (!data || data.length === 0) return [];
    if (showAll || data.length <= maxSlices + 1) {
      return data;
    }
    const sorted = [...data].sort((a, b) => (b.count || 0) - (a.count || 0));
    const top = sorted.slice(0, maxSlices);
    const rest = sorted.slice(maxSlices);

    const restCount = rest.reduce((acc, d) => acc + (d.count || 0), 0);
    const restPct = Number(((restCount / safeTotal) * 100).toFixed(1));

    return [
      ...top,
      {
        label: `Other (${rest.length} categories)`,
        source: `Other (${rest.length})`,
        count: restCount,
        pct: restPct,
        color: '#64748b',
      },
    ];
  }, [data, showAll, maxSlices, safeTotal]);

  const hasManyItems = (data?.length || 0) > maxSlices + 1;

  return (
    <div ref={ref} style={{ position: 'relative', width: '100%' }}>
      {/* Title & View Toggle Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12, minHeight: 24 }}>
        {title ? (
          <p style={{ fontSize: 13, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.07em', margin: 0 }}>
            {title}
          </p>
        ) : <div />}

        {hasManyItems && (
          <div style={{ display: 'inline-flex', background: 'var(--card-bg-subtle, rgba(255,255,255,0.04))', borderRadius: 14, padding: '2px', border: '1px solid var(--border)' }}>
            <button
              onClick={() => setShowAll(false)}
              aria-label="Show top 5 categories"
              style={{
                background: !showAll ? 'var(--brand-primary)' : 'transparent',
                color: !showAll ? '#fff' : 'var(--text-muted)',
                border: 'none',
                borderRadius: 12,
                padding: '2px 8px',
                fontSize: 11,
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              Top {maxSlices}
            </button>
            <button
              onClick={() => setShowAll(true)}
              aria-label="Show all categories"
              style={{
                background: showAll ? 'var(--brand-primary)' : 'transparent',
                color: showAll ? '#fff' : 'var(--text-muted)',
                border: 'none',
                borderRadius: 12,
                padding: '2px 8px',
                fontSize: 11,
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              All ({data.length})
            </button>
          </div>
        )}
      </div>

      {/* Main Content: Donut + Accessible Custom Legend Side-by-Side */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 16,
          minHeight: 250,
        }}
      >
        {/* Left: Donut Chart with Center Callout */}
        <div style={{ position: 'relative', width: '210px', height: '230px', flexShrink: 0, margin: '0 auto' }}>
          <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
            <PieChart>
              <Pie
                data={displayData}
                dataKey="count"
                nameKey={displayData[0]?.source !== undefined ? 'source' : 'label'}
                cx="50%"
                cy="50%"
                innerRadius={62}
                outerRadius={95}
                paddingAngle={2}
                animationBegin={inView ? 0 : 99999}
                animationDuration={800}
                labelLine={false}
                label={CustomLabel}
                onMouseEnter={(_, idx) => setHoveredIndex(idx)}
                onMouseLeave={() => setHoveredIndex(null)}
              >
                {displayData.map((entry, i) => (
                  <Cell
                    key={i}
                    fill={entry.color}
                    stroke={hoveredIndex === i ? '#ffffff' : 'transparent'}
                    strokeWidth={hoveredIndex === i ? 2 : 0}
                    opacity={hoveredIndex === null || hoveredIndex === i ? 1 : 0.45}
                    style={{ transition: 'opacity 0.2s, stroke 0.2s', cursor: 'pointer' }}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-elevated)',
                  border: '1px solid var(--border)',
                  borderRadius: 10,
                  fontSize: 12.5,
                  boxShadow: '0 4px 20px rgba(0,0,0,0.4)',
                }}
                itemStyle={{ color: 'var(--text-primary)' }}
                formatter={(val: unknown, name: unknown) => [
                  `${Number(val).toLocaleString()} / ${safeTotal.toLocaleString()} (${((Number(val) / safeTotal) * 100).toFixed(1)}%)`,
                  formatLabel(String(name ?? '')),
                ]}
              />
            </PieChart>
          </ResponsiveContainer>

          {/* Center Hole Statistics */}
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              textAlign: 'center',
              pointerEvents: 'none',
              width: '100px',
            }}
          >
            <div style={{ fontSize: 20, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", color: 'var(--text-primary)', lineHeight: 1.1 }}>
              {total.toLocaleString()}
            </div>
            <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)', fontWeight: 600, marginTop: 2 }}>
              {centerLabel || 'Total Reviews'}
            </div>
          </div>
        </div>

        {/* Right: Clean, Height-Constrained, Scrollable Legend */}
        <div
          style={{
            flex: '1 1 200px',
            minWidth: '200px',
            maxHeight: '240px',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: 6,
            paddingRight: 4,
          }}
          className="inquiry-stepper-container"
        >
          {displayData.map((item, i) => {
            const rawName = item.label || item.source || item.tag || `Item ${i + 1}`;
            const isHovered = hoveredIndex === i;
            const pctVal = item.pct !== undefined ? item.pct : (item.count / safeTotal) * 100;

            return (
              <div
                key={`${rawName}-${i}`}
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 10,
                  padding: '5px 8px',
                  borderRadius: 6,
                  background: isHovered ? 'var(--theme-accent-bg, rgba(255,255,255,0.06))' : 'transparent',
                  transition: 'background 0.15s ease',
                  cursor: 'pointer',
                  fontSize: 12,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, minWidth: 0, flex: 1 }}>
                  <span
                    style={{
                      width: 9,
                      height: 9,
                      borderRadius: 2.5,
                      background: item.color,
                      flexShrink: 0,
                      boxShadow: isHovered ? `0 0 8px ${item.color}` : 'none',
                    }}
                  />
                  <span
                    title={formatLabel(rawName)}
                    style={{
                      color: isHovered ? 'var(--text-primary)' : 'var(--text-secondary)',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      fontWeight: isHovered ? 600 : 500,
                    }}
                  >
                    {formatLabel(rawName)}
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0 }}>
                  <span style={{ fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", color: 'var(--text-primary)', fontSize: 12 }}>
                    {pctVal.toFixed(1)}%
                  </span>
                  <span style={{ fontSize: 10.5, color: 'var(--text-muted)' }}>
                    ({item.count.toLocaleString()} / {safeTotal.toLocaleString()})
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
