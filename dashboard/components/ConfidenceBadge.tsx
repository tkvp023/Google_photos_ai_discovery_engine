'use client';

interface ConfidenceBadgeProps {
  confidence: number;
  showLabel?: boolean;
  compact?: boolean;
}

/**
 * ConfidenceBadge — shows calibrated evidence confidence as plain-language tiers:
 * - High confidence (≥ 85%): Directly stated by multiple users (Green)
 * - Moderate confidence (70-84%): Supported by clear evidence (Blue)
 * - Lower confidence (< 70%): Limited or indirect evidence (Amber)
 */
export default function ConfidenceBadge({
  confidence,
  showLabel = true,
  compact = false,
}: ConfidenceBadgeProps) {
  // Normalize score between 0 and 1 if passed as percentage (e.g. 84.6 -> 0.846)
  const score = confidence > 1 ? confidence / 100 : confidence;
  const pct = Math.round(score * 100);

  let tierLabel = 'High confidence';
  let color = 'var(--semantic-green, #22c55e)';
  let bg = 'rgba(34, 197, 94, 0.12)';
  let border = 'rgba(34, 197, 94, 0.28)';

  if (score < 0.70) {
    tierLabel = 'Lower confidence';
    color = 'var(--semantic-amber, #f59e0b)';
    bg = 'rgba(245, 158, 11, 0.12)';
    border = 'rgba(245, 158, 11, 0.28)';
  } else if (score < 0.85) {
    tierLabel = 'Moderate confidence';
    color = 'var(--semantic-blue, #3b82f6)';
    bg = 'rgba(59, 130, 246, 0.12)';
    border = 'rgba(59, 130, 246, 0.28)';
  }

  return (
    <span
      className="badge-confidence"
      title={`Calibrated score: ${pct}% (Dynamic multi-rater variance)`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 5,
        fontSize: compact ? 11 : 11.5,
        fontWeight: 600,
        color,
        background: bg,
        border: `1px solid ${border}`,
        padding: compact ? '2px 7px' : '3px 9px',
        borderRadius: 12,
        whiteSpace: 'nowrap',
      }}
    >
      <span
        style={{
          width: 5,
          height: 5,
          borderRadius: '50%',
          backgroundColor: color,
        }}
      />
      <span>{showLabel ? tierLabel : `${pct}%`}</span>
    </span>
  );
}
