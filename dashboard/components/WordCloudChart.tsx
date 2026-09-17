'use client';
import { formatLabel } from '@/lib/formatters';

interface WordItem { text: string; value: number; }

const COLORS = ['#1a73e8', '#0d9488', '#d97706', '#1e8e3e', '#7c3aed', '#0284c7', '#dc2626', '#b45309'];

export default function WordCloudChart({ words, color }: { words: WordItem[]; color?: string }) {
  if (!words || words.length === 0)
    return <div className="empty-state"><div className="empty-state-icon">☁️</div><div className="empty-state-text">No phrases found</div></div>;

  const maxVal = Math.max(...words.map((w) => w.value), 1);

  return (
    <div
      role="region"
      aria-label="Visual word cloud of recurring user search terms"
      style={{
        display: 'flex', flexWrap: 'wrap', gap: 10, alignItems: 'center',
        justifyContent: 'center', minHeight: 140, padding: '8px 0',
      }}
    >
      {words.map((word, i) => {
        const scale = 0.5 + (word.value / maxVal) * 0.5;
        const fontSize = Math.round(14 + scale * 28);
        const wordColor = color || COLORS[i % COLORS.length];
        return (
          <span
            key={word.text}
            title={`${word.text}: ${word.value} mentions`}
            style={{
              fontSize,
              fontFamily: "'Space Grotesk', sans-serif",
              fontWeight: fontSize > 30 ? 800 : 600,
              color: wordColor,
              opacity: 0.6 + scale * 0.4,
              cursor: 'default',
              transition: 'opacity 0.15s, transform 0.15s',
              padding: '2px 4px',
              borderRadius: 4,
              userSelect: 'none',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.opacity = '1';
              (e.currentTarget as HTMLElement).style.transform = 'scale(1.05)';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.opacity = String(0.6 + scale * 0.4);
              (e.currentTarget as HTMLElement).style.transform = 'scale(1)';
            }}
          >
            {formatLabel(word.text)}
          </span>
        );
      })}
    </div>
  );
}
