'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface PromptChip {
  label: string;
  query: string;
}

const PROMPT_CHIPS: PromptChip[] = [
  {
    label: 'Receipts & doc loss',
    query: 'Why do users struggle to find receipts and utility documents in Google Photos?',
  },
  {
    label: 'Zero results for existing photos',
    query: 'Why do users get zero results for photos they know exist in their library?',
  },
  {
    label: 'Screenshot clutter (29.1%)',
    query: 'How does screenshot and meme clutter ruin visual search in Google Photos?',
  },
  {
    label: 'Calendar date amnesia',
    query: 'Why do users remember colors and feelings but forget exact calendar dates?',
  },
];

export default function HeroRagInput() {
  const [query, setQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    router.push(`/ask?q=${encodeURIComponent(query.trim())}`);
  };

  const handleChipClick = (q: string) => {
    router.push(`/ask?q=${encodeURIComponent(q)}`);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 36, width: '100%', maxWidth: 780 }}>
      {/* Subtle, Command-Style Search Bar */}
      <form
        onSubmit={handleSubmit}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          background: 'var(--input-bg)',
          border: isFocused ? '1px solid var(--brand-primary)' : '1px solid var(--border)',
          borderRadius: 'var(--radius-lg)',
          padding: '6px 8px 6px 14px',
          boxShadow: isFocused ? '0 0 0 3px rgba(129, 140, 248, 0.12)' : 'none',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
        }}
      >
        <svg
          width="15"
          height="15"
          viewBox="0 0 24 24"
          fill="none"
          stroke={isFocused ? 'var(--brand-primary)' : 'var(--text-muted)'}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{ flexShrink: 0, transition: 'stroke 0.2s ease' }}
          aria-hidden="true"
        >
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder="Search or ask grounded questions across 2,223 customer reviews..."
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: 'var(--text-primary)',
            fontSize: 14,
            fontWeight: 400,
            padding: '7px 2px',
            fontFamily: 'inherit',
          }}
          aria-label="Search or ask grounded questions across 2,223 customer reviews"
        />

        <button
          type="submit"
          disabled={!query.trim()}
          style={{
            padding: '6px 14px',
            fontSize: 12.5,
            fontWeight: 600,
            borderRadius: 'var(--radius-sm)',
            cursor: query.trim() ? 'pointer' : 'default',
            background: query.trim() ? 'var(--brand-primary)' : 'transparent',
            color: query.trim() ? '#fff' : 'var(--text-muted)',
            border: query.trim() ? '1px solid transparent' : '1px solid var(--border)',
            transition: 'all 0.18s ease',
            whiteSpace: 'nowrap',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 4,
          }}
        >
          <span>Ask</span>
          <span style={{ opacity: 0.6, fontSize: 11 }}>↵</span>
        </button>
      </form>

      {/* Understated Sparks row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
          <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 500 }}>
            Try:
          </span>
          {PROMPT_CHIPS.map((chip) => (
            <button
              key={chip.label}
              type="button"
              onClick={() => handleChipClick(chip.query)}
              style={{
                cursor: 'pointer',
                background: 'transparent',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-sm)',
                padding: '3px 9px',
                fontSize: 11.5,
                color: 'var(--text-secondary)',
                transition: 'all 0.15s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = 'var(--text-primary)';
                e.currentTarget.style.borderColor = 'var(--border-strong)';
                e.currentTarget.style.background = 'rgba(255,255,255,0.03)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = 'var(--text-secondary)';
                e.currentTarget.style.borderColor = 'var(--border)';
                e.currentTarget.style.background = 'transparent';
              }}
            >
              {chip.label}
            </button>
          ))}
        </div>

        <Link
          href="/gaps"
          style={{
            fontSize: 11.5,
            color: 'var(--text-muted)',
            textDecoration: 'none',
            display: 'inline-flex',
            alignItems: 'center',
            gap: 4,
            transition: 'color 0.15s ease',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--text-primary)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--text-muted)')}
        >
          <span>Systemic Gaps</span>
          <span>→</span>
        </Link>
      </div>
    </div>
  );
}
