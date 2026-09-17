'use client';
import { formatLabel } from '@/lib/formatters';

interface Matrix { rows: string[]; columns: string[]; values: number[][]; }

export default function HeatmapChart({ matrix }: { matrix: Matrix }) {
  if (!matrix?.values?.length) return <div className="empty-state"><div className="empty-state-icon">🔲</div><div className="empty-state-text">No comparison data yet</div></div>;

  const allVals = matrix.values.flat();
  const maxVal = Math.max(...allVals, 1);

  function getColor(val: number): string {
    if (val === 0) return 'var(--card-bg-subtle, rgba(0,0,0,0.03))';
    const intensity = Math.min(Math.max(val / maxVal, 0.1), 1);
    const alpha = (0.12 + intensity * 0.76).toFixed(2);
    return `color-mix(in srgb, var(--brand-primary) ${Math.round(intensity * 100)}%, var(--bg-elevated))`;
  }

  function getTextColor(val: number): string {
    const intensity = val / maxVal;
    return intensity > 0.55 ? '#ffffff' : 'var(--text-primary)';
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table
        aria-label="Platform and criteria co-occurrence matrix"
        style={{ borderCollapse: 'separate', borderSpacing: 3, minWidth: 480 }}
      >
        <thead>
          <tr>
            <th scope="col" style={{ width: 120 }}>
              <span className="sr-only">Criteria</span>
            </th>
            {matrix.columns.map((col) => (
              <th
                key={col}
                scope="col"
                style={{ padding: '6px 8px', fontSize: 12, color: 'var(--text-secondary)', fontWeight: 600, textAlign: 'center' }}
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.rows.map((row, ri) => (
            <tr key={row}>
              <th
                scope="row"
                style={{ fontSize: 12, color: 'var(--text-secondary)', paddingRight: 12, fontWeight: 500, whiteSpace: 'nowrap', textAlign: 'left' }}
              >
                {formatLabel(row)}
              </th>
              {matrix.values[ri].map((val, ci) => (
                <td
                  key={ci}
                  aria-label={`${formatLabel(row)} for ${matrix.columns[ci]}: ${val} co-occurrences`}
                  style={{
                    background: getColor(val),
                    color: getTextColor(val),
                    textAlign: 'center',
                    padding: '10px 16px',
                    borderRadius: 6,
                    fontSize: 13,
                    fontWeight: 700,
                    fontFamily: "'Space Grotesk', sans-serif",
                    minWidth: 48,
                    transition: 'transform 0.15s ease',
                    cursor: 'default',
                  }}
                  title={`${formatLabel(row)} × ${matrix.columns[ci]}: ${val}`}
                >
                  {val}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Color scale legend */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 16 }}>
        <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>Low Co-occurrence</span>
        <div style={{ flex: 1, height: 6, borderRadius: 3, background: 'linear-gradient(90deg, var(--bg-elevated), var(--brand-primary))' }} />
        <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600 }}>High Co-occurrence</span>
      </div>
    </div>
  );
}
