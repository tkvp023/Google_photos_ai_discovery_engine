'use client';
import { useState } from 'react';
import Link from 'next/link';
import { QUESTION_META } from '@/lib/constants';

const Q_ICONS: Record<number, string> = {
  1: '📸', 2: '🧠', 3: '📅', 4: '🔎', 5: '❌',
  6: '📜', 7: '📱', 8: '👤', 9: '🧾', 10: '🚪',
};

const Q_SUBTITLES: Record<number, string> = {
  1: 'Episodic multi-cue memories account for 40.6% (592 of 1,457 tags) of photo retrieval struggles',
  2: 'Visual scenes & companions (69.4% of recall tags) retained far longer than dates',
  3: '36.4% (317 of 870 tags) cite date amnesia as the most commonly forgotten metadata',
  4: 'Literal keyword overfitting (31.8%) & Gemini misinterpretation (23.6%) across 110 query tags',
  5: 'Semantic gap failures account for 42.6% (72 of 169 result tags), returning no results',
  6: '68.9% (51 of 74 recovery tags) describe fallback to manual timeline scrolling',
  7: 'WhatsApp memes, receipts & screenshots: 147 clutter tags across feedback',
  8: 'Wrong face matches & missing camera operators dominate 55 face tags (52.7%)',
  9: 'Curved medicine labels & blurry receipts account for 39.1% (18 of 46 document tags)',
  10: 'Fallback to manual doom-scroll accounts for 68.9% (51 of 74 workaround tags)',
};

const Q_COLORS: Record<number, string> = {
  1: '#818cf8', 2: '#a78bfa', 3: '#c084fc',
  4: '#38bdf8', 5: '#22d3ee',
  6: '#f472b6', 7: '#fb923c', 8: '#4ade80', 9: '#fbbf24', 10: '#f87171',
};

const Q_CATEGORIES: Record<number, { stage: 'memory' | 'search' | 'library'; name: string; anchor: string }> = {
  1: { stage: 'memory', name: 'Human Memory Gap', anchor: 'Unposed & Utility Recall' },
  2: { stage: 'memory', name: 'Human Memory Gap', anchor: 'Sensory Visual Anchors' },
  3: { stage: 'memory', name: 'Human Memory Gap', anchor: 'Calendar Date Amnesia' },
  4: { stage: 'search', name: 'Search Breakdown', anchor: 'Abstract Query Translation' },
  5: { stage: 'search', name: 'Search Breakdown', anchor: 'False Misses & 0-Results' },
  6: { stage: 'library', name: 'Library Pathology', anchor: 'Timeline Scroll Fatigue' },
  7: { stage: 'library', name: 'Library Pathology', anchor: 'Screenshot Clutter Noise' },
  8: { stage: 'library', name: 'Library Pathology', anchor: 'Facial Grouping Blindspot' },
  9: { stage: 'library', name: 'Library Pathology', anchor: 'Document & OCR Breakdown' },
  10: { stage: 'library', name: 'Library Pathology', anchor: 'Workarounds & Switching' },
};

const STAGE_COLORS: Record<string, string> = {
  all: 'var(--brand-primary)',
  memory: '#a78bfa',
  search: '#38bdf8',
  library: '#fb923c',
};

export default function QuestionGrid() {
  const [stageFilter, setStageFilter] = useState<'all' | 'memory' | 'search' | 'library'>('all');

  const questions = Object.entries(QUESTION_META).map(([idStr, meta]) => {
    const id = parseInt(idStr);
    const cat = Q_CATEGORIES[id] || { stage: 'memory', name: 'Strategic Memory', anchor: 'Retrieval' };
    return {
      id,
      ...meta,
      icon: Q_ICONS[id] || '📸',
      subtitle: Q_SUBTITLES[id] || meta.text,
      color: Q_COLORS[id] || '#818cf8',
      stage: cat.stage,
      stageName: cat.name,
      anchorTag: cat.anchor,
    };
  });

  const filteredQuestions = questions.filter((q) => stageFilter === 'all' || q.stage === stageFilter);

  const filterButtons = [
    { key: 'all' as const, label: 'All 10 Inquiries', count: 10 },
    { key: 'memory' as const, label: '🧠 Memory Gap', count: 3 },
    { key: 'search' as const, label: '🔎 Search', count: 2 },
    { key: 'library' as const, label: '📱 Library', count: 5 },
  ];

  return (
    <div>
      {/* Filter tabs */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        flexWrap: 'wrap', gap: 10, marginBottom: 20,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
          {filterButtons.map(({ key, label, count }) => {
            const isActive = stageFilter === key;
            const color = STAGE_COLORS[key];
            return (
              <button
                key={key}
                onClick={() => setStageFilter(key)}
                style={{
                  padding: '5px 14px',
                  borderRadius: 20,
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: 'pointer',
                  border: `1px solid ${isActive ? color : 'var(--border)'}`,
                  background: isActive ? `${typeof color === 'string' && color.startsWith('#') ? color : ''}14` : 'transparent',
                  color: isActive ? color : 'var(--text-secondary)',
                  transition: 'all 0.2s ease',
                  backdropFilter: 'blur(8px)',
                }}
              >
                {label} ({count})
              </button>
            );
          })}
        </div>
        <span style={{ fontSize: 11.5, color: 'var(--text-muted)' }}>
          {filteredQuestions.length} of 10
        </span>
      </div>

      {/* Denominator / Tags explanation note */}
      <div style={{
        marginBottom: 16,
        padding: '8px 14px',
        background: 'rgba(255, 255, 255, 0.025)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-sm)',
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        fontSize: 12,
        color: 'var(--text-muted)',
      }}>
        <span style={{ fontSize: 13 }}>🏷️</span>
        <span>
          <strong style={{ color: 'var(--text-secondary)' }}>Note on Denominators:</strong> Figures like <strong>(51 of 74 recovery tags)</strong> indicate verified failure instances cataloged for that topic. Reviews often contain multiple tags when a user encounters several friction points.
        </span>
      </div>

      {/* Grid with cascade animation */}
      <div
        className="cascade-grid"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(290px, 1fr))',
          gap: 14,
        }}
      >
        {filteredQuestions.map((q) => (
          <Link
            key={q.id}
            href={`/questions/${q.id}`}
            style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              padding: '20px 22px',
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-lg)',
              textDecoration: 'none',
              transition: 'all 0.25s cubic-bezier(0.16, 1, 0.3, 1)',
              position: 'relative',
              overflow: 'hidden',
              minHeight: 170,
              boxShadow: 'var(--shadow-card)',
            }}
            onMouseEnter={(e) => {
              const el = e.currentTarget;
              el.style.background = 'var(--bg-card-hover)';
              el.style.borderColor = `${q.color}50`;
              el.style.transform = 'translateY(-3px) scale(1.01)';
              el.style.boxShadow = `var(--shadow-elevated), 0 0 30px ${q.color}15`;
            }}
            onMouseLeave={(e) => {
              const el = e.currentTarget;
              el.style.background = 'var(--bg-card)';
              el.style.borderColor = 'var(--border)';
              el.style.transform = 'translateY(0) scale(1)';
              el.style.boxShadow = 'var(--shadow-card)';
            }}
          >
            <div>
              {/* Header */}
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 10, marginBottom: 10 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{
                    width: 30, height: 30,
                    borderRadius: 'var(--radius-sm)',
                    background: `${q.color}14`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 11.5, fontWeight: 700,
                    color: q.color,
                    fontFamily: "'Space Grotesk', sans-serif",
                    flexShrink: 0,
                    border: `1px solid ${q.color}30`,
                  }}>
                    Q{q.id}
                  </span>
                  {q.id <= 4 ? (
                    <span style={{
                      fontSize: 10, fontWeight: 700,
                      color: 'var(--semantic-blue)',
                      background: 'rgba(59, 130, 246, 0.12)',
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      padding: '1px 7px', borderRadius: 10,
                      textTransform: 'uppercase', letterSpacing: '0.04em',
                    }}>
                      Core Brief
                    </span>
                  ) : (
                    <span style={{
                      fontSize: 10, fontWeight: 600,
                      color: 'var(--text-muted)',
                      background: 'rgba(255, 255, 255, 0.04)',
                      border: '1px solid var(--border)',
                      padding: '1px 7px', borderRadius: 10,
                    }}>
                      Deep Dive
                    </span>
                  )}
                </div>
                <span style={{ fontSize: 16, opacity: 0.85, flexShrink: 0 }}>{q.icon}</span>
              </div>

              {/* Full Question Text as Primary Title */}
              <h4 style={{
                fontSize: 13.5,
                fontWeight: 700,
                color: 'var(--text-primary)',
                lineHeight: 1.4,
                margin: '0 0 10px 0',
                letterSpacing: '-0.01em',
              }}>
                {q.text}
              </h4>

              {/* Anchor badge */}
              <div style={{ marginBottom: 8 }}>
                <span style={{
                  fontSize: 10.5, fontWeight: 600,
                  color: q.color,
                  background: `${q.color}10`,
                  border: `1px solid ${q.color}25`,
                  padding: '2px 9px', borderRadius: 12,
                }}>
                  {q.anchorTag}
                </span>
              </div>

              {/* Key finding subtitle */}
              <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0, marginBottom: 12 }}>
                {q.subtitle}
              </p>
            </div>

            {/* Footer */}
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              paddingTop: 10, borderTop: '1px solid var(--border)',
            }}>
              <span style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', display: 'inline-flex', alignItems: 'center', gap: 5 }}>
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: q.color }} />
                {q.stageName}
              </span>
              <span style={{ fontSize: 12.5, color: q.color, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif" }}>
                Explore →
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
