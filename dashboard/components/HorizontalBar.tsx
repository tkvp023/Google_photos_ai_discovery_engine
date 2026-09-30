'use client';
import { useInView } from 'react-intersection-observer';
import Link from 'next/link';
import { formatLabel } from '@/lib/formatters';

export interface BreakdownItem {
  label: string;
  tag: string;
  count: number;
  pct: number;
  avg_confidence?: number;
  color: string;
  href?: string;
  onClick?: () => void;
}

interface HorizontalBarProps {
  data: BreakdownItem[];
  title?: string;
  maxBars?: number;
  showCount?: boolean;
  showConfidence?: boolean;
  denominator?: number;
  unit?: string;
  showTagExplanation?: boolean;
  onItemClick?: (item: BreakdownItem) => void;
}

function ConfidenceDot({ conf }: { conf?: number }) {
  if (conf === undefined) return null;
  const color = conf >= 0.8 ? '#84cc16' : conf >= 0.6 ? '#fbbf24' : '#ef4444';
  return (
    <span
      title={`Confidence: ${(conf * 100).toFixed(0)}%`}
      style={{
        display: 'inline-block',
        width: 8, height: 8,
        borderRadius: '50%',
        background: color,
        marginLeft: 6,
        verticalAlign: 'middle',
        flexShrink: 0,
      }}
    />
  );
}

export default function HorizontalBar({
  data,
  title,
  maxBars = 8,
  showCount = true,
  denominator,
  unit,
  showTagExplanation = true,
  onItemClick,
}: HorizontalBarProps) {
  const { ref, inView } = useInView({ threshold: 0.2, triggerOnce: true });
  const visible = data.slice(0, maxBars);
  const totalCount = denominator || data.reduce((acc, it) => acc + (it.count || 0), 0) || 1;

  // 1,616 is the total number of customer reviews in the corpus.
  // Subsets (e.g. 74, 110, 169) represent failure point tags.
  const resolvedUnit = unit !== undefined
    ? unit
    : (totalCount === 1616 ? 'reviews' : 'tags');

  return (
    <div ref={ref}>
      {title && (
        <p style={{ fontSize: 13, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 16 }}>
          {title}
        </p>
      )}
      <div className="bar-row">
        {visible.map((item, i) => {
          const isClickable = Boolean(item.href || item.onClick || onItemClick);

          const content = (
            <div
              className={`bar-item ${isClickable ? 'bar-item-clickable' : ''}`}
              role={isClickable && !item.href ? 'button' : undefined}
              tabIndex={isClickable && !item.href ? 0 : undefined}
              aria-label={`${formatLabel(item.label)}: ${item.pct.toFixed(1)}%, ${item.count.toLocaleString()} of ${totalCount.toLocaleString()}`}
              style={{
                animationDelay: `${i * 60}ms`,
                cursor: isClickable ? 'pointer' : 'default',
                padding: isClickable ? '4px 6px' : '0',
                borderRadius: isClickable ? 8 : 0,
                transition: 'all 0.15s ease',
              }}
              onClick={() => {
                if (item.onClick) item.onClick();
                else if (onItemClick) onItemClick(item);
              }}
              onKeyDown={(e) => {
                if (isClickable && !item.href && (e.key === 'Enter' || e.key === ' ')) {
                  e.preventDefault();
                  if (item.onClick) item.onClick();
                  else if (onItemClick) onItemClick(item);
                }
              }}
            >
              <div className="bar-meta">
                <span className="bar-label" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  {formatLabel(item.label)}
                  <ConfidenceDot conf={item.avg_confidence} />
                  {isClickable && <span style={{ fontSize: 11, opacity: 0.6 }}>↗</span>}
                </span>
                <span className="bar-value" style={{ display: 'inline-flex', alignItems: 'baseline', gap: 4 }}>
                  <strong style={{ fontWeight: 700 }}>{item.pct.toFixed(1)}%</strong>
                  {showCount && (
                    <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 500 }}>
                      ({item.count.toLocaleString()} / {totalCount.toLocaleString()} {resolvedUnit})
                    </span>
                  )}
                </span>
              </div>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{
                    width: inView ? `${item.pct}%` : '0%',
                    background: `linear-gradient(90deg, ${item.color}90, ${item.color}dd, ${item.color})`,
                    transition: `width ${500 + i * 80}ms ${i * 60}ms ease-out`,
                  }}
                />
              </div>
            </div>
          );

          if (item.href) {
            return (
              <Link key={`${item.tag || item.label || 'bar'}-${i}`} href={item.href} style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
                {content}
              </Link>
            );
          }

          return <div key={`${item.tag || item.label || 'bar'}-${i}`}>{content}</div>;
        })}
      </div>

      {showTagExplanation && resolvedUnit.toLowerCase().includes('tag') && (
        <div style={{
          marginTop: 14,
          padding: '8px 12px',
          background: 'rgba(255, 255, 255, 0.02)',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'flex-start',
          gap: 7,
          fontSize: 11.5,
          color: 'var(--text-muted)',
          lineHeight: 1.45,
        }}>
          <span style={{ fontSize: 13, flexShrink: 0, marginTop: 1 }}>🏷️</span>
          <span>
            <strong style={{ color: 'var(--text-primary)' }}>What are &ldquo;tags&rdquo;?</strong> In this discovery engine, a <em>tag</em> is a specific, machine-verified failure pattern or memory signal identified in user feedback (e.g. <em>date amnesia</em>, <em>wrong face match</em>, or <em>forced scroll fallback</em>). The denominator represents total verified tags cataloged for this topic. A single user review can contain multiple tags if the user hit several obstacles.
          </span>
        </div>
      )}
    </div>
  );
}
