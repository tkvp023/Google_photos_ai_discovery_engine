'use client';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { useInView } from 'react-intersection-observer';

interface TemporalPoint { month: string; count: number; pct: number; }

export default function AreaTimeline({ data, title }: { data: TemporalPoint[]; title?: string }) {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });

  return (
    <div ref={ref}>
      {title && (
        <p style={{ fontSize: 13, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 16 }}>
          {title}
        </p>
      )}
      <ResponsiveContainer width="100%" height={220} minWidth={0} minHeight={0}>
        <AreaChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
          <defs>
            <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--brand-primary)" stopOpacity={0.35} />
              <stop offset="100%" stopColor="var(--brand-primary)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.6} />
          <XAxis
            dataKey="month"
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            tickLine={false}
            axisLine={{ stroke: 'var(--border)', opacity: 0.5 }}
            tickFormatter={(v) => v.slice(2)}
          />
          <YAxis
            tick={{ fill: 'var(--text-muted)', fontSize: 11 }}
            tickLine={false}
            axisLine={{ stroke: 'var(--border)', opacity: 0.5 }}
          />
          <Tooltip
            contentStyle={{
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              borderRadius: 10,
              fontSize: 12,
              color: 'var(--text-primary)',
            }}
            itemStyle={{ color: 'var(--text-primary)', fontWeight: 600 }}
            labelStyle={{ color: 'var(--text-primary)', fontWeight: 700 }}
            formatter={(val: unknown, name: unknown) => [name === 'pct' ? `${Number(val)}%` : Number(val).toLocaleString(), name === 'pct' ? 'Signal %' : 'Count']}
          />
          <Area
            type="monotone"
            dataKey="pct"
            stroke="var(--brand-primary)"
            strokeWidth={2.5}
            fill="url(#areaGrad)"
            dot={{ r: 3, fill: 'var(--brand-primary)', strokeWidth: 0 }}
            activeDot={{ r: 5, fill: 'var(--brand-primary)' }}
            animationBegin={inView ? 0 : 99999}
            animationDuration={900}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
