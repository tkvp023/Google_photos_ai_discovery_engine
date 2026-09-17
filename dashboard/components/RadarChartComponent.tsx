'use client';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, Tooltip, ResponsiveContainer, PolarRadiusAxis } from 'recharts';
import { formatLabel } from '@/lib/formatters';

interface RadarDataPoint {
  factor: string;
  importance: number;
  negative_pct: number;
  [key: string]: unknown;
}

export default function RadarChartComponent({ data }: { data: RadarDataPoint[] }) {
  const formattedData = (data || []).map((d) => ({
    ...d,
    factor: formatLabel(d.factor),
  }));

  return (
    <div role="img" aria-label="Radar chart displaying importance and negative sentiment across memory friction factors" style={{ width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 20, marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
          <span style={{ width: 14, height: 4, background: '#2563eb', borderRadius: 2, display: 'inline-block' }} />
          <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>Importance Share (%)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
          <span style={{ width: 14, height: 0, borderTop: '2px dashed #d97706', display: 'inline-block' }} />
          <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>Negative Sentiment (%)</span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={300} minWidth={0} minHeight={0}>
        <RadarChart data={formattedData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
          <PolarGrid stroke="var(--border)" opacity={0.7} />
          <PolarAngleAxis
            dataKey="factor"
            tick={{ fill: 'var(--text-secondary)', fontSize: 12, fontWeight: 500 }}
          />
        <PolarRadiusAxis
          angle={90}
          domain={[0, 40]}
          tick={{ fill: 'var(--text-muted)', fontSize: 10 }}
          axisLine={false}
        />
        <Radar
          name="Importance %"
          dataKey="importance"
          stroke="#2563eb"
          fill="#2563eb"
          fillOpacity={0.22}
          strokeWidth={2}
          dot={{ r: 4, fill: '#2563eb', strokeWidth: 0 }}
        />
        <Radar
          name="Negative %"
          dataKey="negative_pct"
          stroke="#d97706"
          fill="#d97706"
          fillOpacity={0.14}
          strokeWidth={1.5}
          strokeDasharray="4 2"
          dot={false}
        />
        <Tooltip
          contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 10, fontSize: 12, color: 'var(--text-primary)' }}
          itemStyle={{ color: 'var(--text-primary)', fontWeight: 600 }}
          formatter={(val: unknown, name: unknown) => [`${Number(val)}%`, String(name ?? '')]}
        />
      </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
