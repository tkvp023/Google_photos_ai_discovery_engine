'use client';
import { useState } from 'react';
import { SOURCE_COLORS } from '@/lib/constants';

export interface Quote {
  text: string;
  source: string;
  source_id?: string;
  date?: string;
  confidence: number;
  tags: string[];
  segment?: string;
}


function ConfBadge({ conf }: { conf: number }) {
  const cls = conf >= 0.8 ? 'badge-conf-high' : conf >= 0.6 ? 'badge-conf-mid' : 'badge-conf-low';
  return <span className={`badge ${cls}`}>{(conf * 100).toFixed(0)}%</span>;
}

function QuoteCard({ quote, accent }: { quote: Quote; accent?: string }) {
  const [expanded, setExpanded] = useState(false);
  const text = (quote.text || '').trim();
  const isLong = text.length > 220;

  // Find clean word boundary for snippet
  let snippet = text;
  if (isLong && !expanded) {
    const cutoff = text.lastIndexOf(' ', 220);
    snippet = (cutoff > 160 ? text.slice(0, cutoff) : text.slice(0, 220)) + '…';
  }

  return (
    <div
      className="quote-card"
      style={{
        borderLeftColor: accent || SOURCE_COLORS[quote.source] || 'var(--brand-primary)',
        transition: 'all 0.2s ease',
      }}
    >
      <p
        className="quote-text"
        style={{
          whiteSpace: 'pre-wrap',
          lineHeight: 1.6,
          fontSize: 13.5,
          color: 'var(--text-primary)',
          margin: '0 0 10px 0',
        }}
      >
        &ldquo;{snippet}&rdquo;
      </p>

      {isLong && (
        <button
          onClick={() => setExpanded(!expanded)}
          style={{
            background: 'var(--theme-accent-bg)',
            border: '1px solid var(--theme-accent-border)',
            color: 'var(--brand-primary)',
            fontSize: 11.5,
            fontWeight: 500,
            cursor: 'pointer',
            marginBottom: 10,
            padding: '4px 10px',
            borderRadius: 6,
            display: 'inline-flex',
            alignItems: 'center',
            gap: 4,
            transition: 'all 0.15s ease',
          }}
        >
          {expanded ? (
            <>
              <span>Collapse quote</span>
              <span style={{ fontSize: 10 }}>▲</span>
            </>
          ) : (
            <>
              <span>Read full quote</span>
              <span style={{ fontSize: 10, opacity: 0.7 }}>({text.length} chars)</span>
              <span style={{ fontSize: 10 }}>▼</span>
            </>
          )}
        </button>
      )}

      <div className="quote-meta" style={{ display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center' }}>
        <span
          className="badge badge-source"
          style={{
            background: `${SOURCE_COLORS[quote.source] || '#6b7280'}22`,
            color: SOURCE_COLORS[quote.source] || 'var(--text-secondary)',
          }}
        >
          {quote.source}
        </span>
        {quote.tags && quote.tags.length > 0 && quote.tags[0] && (
          <span
            className="badge"
            style={{
              background: 'var(--theme-accent-bg)',
              color: 'var(--brand-primary)',
              border: '1px solid var(--theme-accent-border)',
              fontSize: 11,
            }}
          >
            #{quote.tags[0].replace(/_/g, ' ')}
          </span>
        )}

        <ConfBadge conf={quote.confidence} />
        {quote.source_id && (
          <span
            style={{
              fontSize: 10.5,
              color: 'var(--text-muted)',
              fontFamily: 'var(--font-mono, monospace)',
              background: 'var(--card-bg-subtle, rgba(255,255,255,0.03))',
              padding: '2px 6px',
              borderRadius: 4,
            }}
            title="Database Source Record ID"
          >
            {quote.source_id.length > 18 ? quote.source_id.slice(0, 18) + '…' : quote.source_id}
          </span>
        )}
        <span style={{ fontSize: 11, color: 'var(--text-muted)', marginLeft: 'auto' }}>{quote.date}</span>
      </div>
    </div>
  );
}

function EmptyQuoteCard({ note }: { note?: string }) {
  return (
    <div
      className="quote-card"
      style={{
        borderLeftColor: 'var(--text-muted, #64748b)',
        padding: '22px 24px',
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderLeft: '3px solid var(--text-muted, #64748b)',
        borderRadius: '0 var(--radius-md) var(--radius-md) 0',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
        <span style={{ fontSize: 20, color: 'var(--text-muted)', lineHeight: 1.3 }}>🔍</span>
        <div>
          <p
            style={{
              margin: '0 0 8px 0',
              fontSize: 13.5,
              lineHeight: 1.6,
              color: 'var(--text-secondary)',
              fontWeight: 400,
            }}
          >
            {note ||
              'No distinct verbatim quotes specific to this workaround pattern were found in the strictly-verified corpus subset. Aggregate mention counts above are based on tag-level classification of the full review text.'}
          </p>
          <span
            style={{
              fontSize: 12,
              color: 'var(--text-muted)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 4,
            }}
          >
            See the frequency breakdown and cross-platform attribution above for the full evidence basis.
          </span>
        </div>
      </div>
    </div>
  );
}

export default function QuoteCarousel({ quotes, emptyNote }: { quotes: Quote[]; emptyNote?: string }) {
  const [idx, setIdx] = useState(0);

  if (!quotes || quotes.length === 0) {
    return <EmptyQuoteCard note={emptyNote} />;
  }

  // If 1 or 2 quotes, show them directly in an adaptive responsive grid so no cards are hidden behind clicks
  if (quotes.length <= 2) {
    return (
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: quotes.length === 1 ? '1fr' : 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: 14,
        }}
      >
        {quotes.map((q, i) => (
          <QuoteCard key={i} quote={q} />
        ))}
      </div>
    );
  }

  // For 3+ quotes, render the cinema-style carousel with pagination
  return (
    <div>
      <QuoteCard quote={quotes[idx]} />
      <div style={{ display: 'flex', gap: 8, marginTop: 12, justifyContent: 'center', alignItems: 'center' }}>
        <button
          onClick={() => setIdx((i) => Math.max(0, i - 1))}
          disabled={idx === 0}
          aria-label="Previous quote"
          style={{ background: 'var(--glass-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-secondary)', width: 32, height: 32, cursor: 'pointer', fontSize: 14, opacity: idx === 0 ? 0.3 : 1 }}
        >←</button>
        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{idx + 1} / {quotes.length}</span>
        <button
          onClick={() => setIdx((i) => Math.min(quotes.length - 1, i + 1))}
          disabled={idx === quotes.length - 1}
          aria-label="Next quote"
          style={{ background: 'var(--glass-bg)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-secondary)', width: 32, height: 32, cursor: 'pointer', fontSize: 14, opacity: idx === quotes.length - 1 ? 0.3 : 1 }}
        >→</button>
      </div>
    </div>
  );
}

export { QuoteCard, EmptyQuoteCard };

