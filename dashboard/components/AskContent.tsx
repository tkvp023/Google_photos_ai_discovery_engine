'use client';
import { useState, useRef, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { SOURCE_COLORS } from '@/lib/constants';

const SUGGESTED = [
  'Why do users fail to retrieve photos when they have incomplete or vague memories?',
  'How do users search differently with Gemini Ask Photos vs traditional keyword search?',
  'What are the primary failure modes across Expression, Interpretation, and Recovery?',
  'Why does photo retrieval fail for partial temporal memories like "last summer" or "a few months ago"?',
  'How does screenshot and meme clutter ruin visual search in Google Photos?',
  'What unmet needs exist for conversational memory retrieval and refinement?',
];

interface Citation {
  source: string;
  confidence: number;
  color: string;
  count: number;
}

export interface RetrievedDoc {
  index: number;
  doc_id: string;
  source: string;
  raw_source: string;
  source_id: string;
  date: string;
  segment: string;
  similarity: number;
  tags: string[];
  content: string;
}

interface Message {
  role: 'user' | 'ai';
  content: string;
  citations?: Citation[];
  latencyMs?: number;
  docsRetrieved?: number;
  retrievedDocs?: RetrievedDoc[];
  suggestions?: string[];
  isOutOfScope?: boolean;
}

function SourceInspectorModal({
  doc,
  onClose,
}: {
  doc: RetrievedDoc | null;
  onClose: () => void;
}) {
  if (!doc) return null;

  const color = SOURCE_COLORS[doc.source] || '#6b7280';

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        backdropFilter: 'blur(8px)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 20,
        animation: 'fadeIn 0.2s ease-out',
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          maxWidth: 620,
          width: '100%',
          maxHeight: '85vh',
          overflowY: 'auto',
          background: 'var(--bg-card)',
          border: `1px solid ${color}80`,
          borderRadius: 16,
          padding: 24,
          position: 'relative',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
            <span
              style={{
                background: `${color}20`,
                border: `1px solid ${color}50`,
                color: color,
                padding: '4px 12px',
                borderRadius: 20,
                fontSize: 12,
                fontWeight: 700,
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: color }} />
              {doc.source}
            </span>
            <span
              style={{
                background: (doc.source.toLowerCase().includes('reddit') || doc.source.toLowerCase().includes('hacker')) ? 'rgba(99,102,241,0.12)' : 'rgba(26,115,232,0.12)',
                border: `1px solid ${(doc.source.toLowerCase().includes('reddit') || doc.source.toLowerCase().includes('hacker')) ? 'rgba(99,102,241,0.3)' : 'rgba(26,115,232,0.3)'}`,
                color: (doc.source.toLowerCase().includes('reddit') || doc.source.toLowerCase().includes('hacker')) ? '#6366f1' : 'var(--brand-primary)',
                padding: '4px 10px',
                borderRadius: 12,
                fontSize: 11,
                fontWeight: 700,
              }}
            >
              {(doc.source.toLowerCase().includes('reddit') || doc.source.toLowerCase().includes('hacker')) ? 'Community Discussion' : 'Verified App Store Review'}
            </span>

            <span
              style={{
                background: 'rgba(16,185,129,0.12)',
                border: '1px solid rgba(16,185,129,0.3)',
                color: 'var(--green)',
                padding: '4px 10px',
                borderRadius: 12,
                fontSize: 11,
                fontWeight: 600,
              }}
            >
              {(doc.similarity * 100).toFixed(0)}% Semantic Match
            </span>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'rgba(255,255,255,0.06)',
              border: '1px solid var(--border)',
              color: 'var(--text-muted)',
              width: 30,
              height: 30,
              borderRadius: '50%',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 14,
              transition: 'all 0.2s',
            }}
          >
            ✕
          </button>
        </div>
        <div
          style={{
            background: 'var(--glass-bg)',
            border: '1px solid var(--border)',
            borderRadius: 12,
            padding: 16,
            marginBottom: 16,
          }}
        >
          <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', marginBottom: 8, letterSpacing: '0.05em' }}>
            Authentic Customer Verbatim
          </div>
          <p style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--text-primary)', whiteSpace: 'pre-wrap', fontStyle: 'italic' }}>
            &ldquo;{doc.content}&rdquo;
          </p>
        </div>
        {doc.tags && doc.tags.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', marginBottom: 6, letterSpacing: '0.05em' }}>
              Extracted Hesitation Tags
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {doc.tags.map((t) => (
                <span
                  key={t}
                  style={{
                    background: 'var(--theme-accent-bg)',
                    border: '1px solid var(--theme-accent-border)',
                    color: 'var(--pink)',
                    borderRadius: 10,
                    padding: '2px 8px',
                    fontSize: 11,
                    fontWeight: 600,
                  }}
                >
                  #{t.replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </div>
        )}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontSize: 11,
            color: 'var(--text-muted)',
            borderTop: '1px solid var(--border)',
            paddingTop: 12,
          }}
        >
          <span>Evidence Doc ID: <code>{doc.doc_id.slice(0, 16)}...</code></span>
          <span>Indexed: {doc.date}</span>
        </div>
      </div>
    </div>
  );
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function MarkdownText({
  text,
  onInspectReview,
}: {
  text: string;
  onInspectReview?: (reviewNum: number) => void;
}) {
  const safeText = escapeHtml(text || '');
  const processed = safeText
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/^> (.+)$/gm, '<blockquote style="border-left:3px solid var(--brand-primary);padding-left:12px;margin:10px 0;color:var(--text-secondary);font-style:italic;background:var(--theme-accent-bg);padding:8px 12px;border-radius:0 8px 8px 0;">$1</blockquote>')
    .replace(/^(\d+)\. (.+)$/gm, '<div style="padding:3px 0"><span style="color:var(--brand-primary);font-weight:700;margin-right:6px;">$1.</span> $2</div>')
    .replace(/^- (.+)$/gm, '<div style="padding:2px 0;padding-left:12px;position:relative"><span style="position:absolute;left:0;color:var(--brand-secondary)">•</span> $1</div>')
    .replace(/\n\n/g, '<br/><br/>');

  return (
    <span
      dangerouslySetInnerHTML={{ __html: processed }}
      onClick={(e) => {
        const target = e.target as HTMLElement;
        const match = target.innerText?.match(/\[Review (\d+)\]/i);
        if (match && onInspectReview) {
          onInspectReview(parseInt(match[1], 10));
        }
      }}
    />
  );
}

function CitationBadges({
  citations,
  latencyMs,
  docsRetrieved,
  retrievedDocs,
  onInspectDoc,
}: {
  citations: Citation[];
  latencyMs?: number;
  docsRetrieved?: number;
  retrievedDocs?: RetrievedDoc[];
  onInspectDoc?: (doc: RetrievedDoc) => void;
}) {
  return (
    <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Grounding Citations ({docsRetrieved || citations.reduce((acc, c) => acc + (c.count || 1), 0)} evidence reviews)
        </span>
        {latencyMs !== undefined && (
          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
            ⚡ {latencyMs}ms
          </span>
        )}
      </div>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
        {citations.map((c, i) => (
          <button
            key={`${c.source}-${i}`}
            onClick={() => {
              if (onInspectDoc && retrievedDocs) {
                const found = retrievedDocs.find((d) => d.source.toLowerCase() === c.source.toLowerCase()) || retrievedDocs[0];
                if (found) onInspectDoc(found);
              }
            }}
            title="Click to inspect raw customer reviews from this platform"
            style={{
              background: `${c.color}15`,
              border: `1px solid ${c.color}40`,
              color: c.color,
              borderRadius: 16,
              padding: '4px 12px',
              fontSize: 11,
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              cursor: onInspectDoc ? 'pointer' : 'default',
              transition: 'all 0.18s ease',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.transform = 'translateY(-1px)')}
            onMouseLeave={(e) => (e.currentTarget.style.transform = 'translateY(0)')}
          >
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: c.color }} />
            {c.source}
            {c.count > 0 && <span style={{ opacity: 0.7, fontSize: 10 }}>({c.count})</span>}
            <span style={{ opacity: 0.85, fontSize: 10, background: 'rgba(0,0,0,0.2)', padding: '1px 6px', borderRadius: 6 }}>
              {(c.confidence * 100).toFixed(0)}% relevance 🔍
            </span>
          </button>
        ))}

        {retrievedDocs && retrievedDocs.length > 0 && onInspectDoc && (
          <button
            onClick={() => onInspectDoc(retrievedDocs[0])}
            style={{
              background: 'var(--theme-accent-bg)',
              border: '1px solid var(--theme-accent-border)',
              color: 'var(--pink)',
              borderRadius: 16,
              padding: '4px 12px',
              fontSize: 11,
              fontWeight: 600,
              cursor: 'pointer',
              marginLeft: 'auto',
            }}
          >
            Inspect Raw Evidence ({retrievedDocs.length}) ↗
          </button>
        )}
      </div>
    </div>
  );
}

export default function AskContent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [source, setSource] = useState('all');
  const [scope, setScope] = useState<'brief' | 'all'>('brief');
  const [copied, setCopied] = useState<number | null>(null);
  const [isLive, setIsLive] = useState(true);
  const [inspectDoc, setInspectDoc] = useState<RetrievedDoc | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const searchParams = useSearchParams();
  const autoRunRef = useRef(false);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return;
    const q = text.trim();
    setInput('');
    setMessages((m) => [...m, { role: 'user', content: q }]);
    setLoading(true);

    try {
      const directUrl = process.env.NEXT_PUBLIC_RAG_API_URL || 'http://localhost:8000';
      let res = await fetch(`${directUrl}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: q,
          filters: { source },
          scope,
        }),
      }).catch(() => null);

      if (!res || !res.ok) {
        res = await fetch('/api/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: q,
            filters: { source },
            scope,
          }),
        }).catch(() => null);
      }

      if (res && res.ok) {
        const data = await res.json();
        setIsLive(true);
        setMessages((m) => [
          ...m,
          {
            role: 'ai',
            content: data.answer,
            citations: data.citations,
            latencyMs: data.latency_ms,
            docsRetrieved: data.docs_retrieved,
            retrievedDocs: data.retrieved_docs,
            suggestions: data.suggestions,
            isOutOfScope: data.is_out_of_scope,
          },
        ]);
      } else {
        throw new Error('RAG backend not responding');
      }
    } catch {
      setIsLive(false);
      setMessages((m) => [
        ...m,
        {
          role: 'ai',
          content: `⚠️ **RAG Server Notice**: The Python intelligence backend (FastAPI on port 8000) is currently initializing or offline. To start it, run \`python -m pipeline.rag.server\` in the terminal.`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Auto-run query if passed via URL ?q=...
  useEffect(() => {
    const urlQuery = searchParams.get('q');
    if (urlQuery && !autoRunRef.current) {
      autoRunRef.current = true;
      sendMessage(urlQuery);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const clearChat = () => {
    setMessages([]);
  };

  const copyResponse = (idx: number, text: string) => {
    navigator.clipboard.writeText(text.replace(/\*\*/g, '').replace(/\*/g, ''));
    setCopied(idx);
    setTimeout(() => setCopied(null), 1500);
  };

  return (
    <div className="container" style={{ paddingTop: 32, paddingBottom: 64 }}>
      <SourceInspectorModal doc={inspectDoc} onClose={() => setInspectDoc(null)} />

      <div className="page-header">
        <h1>
          <span className="hero-gradient-text">
            Ask
          </span>{' '}
          the Data
        </h1>
        <p style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', color: 'var(--text-secondary)', fontSize: 14 }}>
          <span>Conversational RAG retrieval over verified customer reviews across 5 platforms.</span>
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              fontSize: 12,
              color: isLive ? '#10b981' : 'var(--text-muted)',
            }}
          >
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: isLive ? '#10b981' : 'var(--text-muted)' }} />
            {isLive ? `${scope === 'brief' ? '251 Core Brief Documents' : '2,223 Documents Indexed'}` : 'Standby'}
          </span>
        </p>
      </div>

      {/* Scope Selector Bar */}
      <div
        style={{
          maxWidth: 940,
          margin: '0 auto 16px',
          padding: '12px 18px',
          background: 'var(--glass-bg)',
          border: '1px solid var(--border)',
          borderRadius: 14,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 12,
          backdropFilter: 'blur(12px)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            RAG Evidence Scope:
          </span>
          <div style={{ display: 'inline-flex', background: 'rgba(0,0,0,0.25)', padding: 3, borderRadius: 10, border: '1px solid var(--border)' }}>
            <button
              type="button"
              onClick={() => setScope('brief')}
              style={{
                background: scope === 'brief' ? 'var(--brand-primary)' : 'transparent',
                color: scope === 'brief' ? '#fff' : 'var(--text-muted)',
                border: 'none',
                borderRadius: 7,
                padding: '6px 14px',
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              <span>🎯</span> Core Retrieval Brief (251 reviews)
            </button>
            <button
              type="button"
              onClick={() => setScope('all')}
              style={{
                background: scope === 'all' ? 'var(--brand-primary)' : 'transparent',
                color: scope === 'all' ? '#fff' : 'var(--text-muted)',
                border: 'none',
                borderRadius: 7,
                padding: '6px 14px',
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              <span>🌐</span> Full Corpus (2,223 reviews)
            </button>
          </div>
        </div>

        <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
          {scope === 'brief' ? (
            <span style={{ color: '#34d399', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#34d399' }} />
              <strong>Strict Grounding:</strong> Filtered to Bucket A (episodic search & retrieval friction).
            </span>
          ) : (
            <span style={{ color: 'var(--text-muted)', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--text-muted)' }} />
              <strong>Unfiltered:</strong> Includes sync stalls, backup bugs, and tab redesign complaints.
            </span>
          )}
        </div>
      </div>

      <div className="card" style={{ maxWidth: 940, margin: '0 auto', backdropFilter: 'blur(16px)' }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
            <p style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              Suggested executive queries
            </p>
            {messages.length > 0 && (
              <button
                onClick={clearChat}
                style={{
                  background: 'none',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--text-muted)',
                  fontSize: 11,
                  padding: '3px 10px',
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                }}
              >
                Clear chat
              </button>
            )}
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {SUGGESTED.map((q) => (
              <button
                key={q}
                onClick={() => sendMessage(q)}
                disabled={loading}
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border)',
                  borderRadius: 20,
                  padding: '6px 14px',
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s ease',
                  opacity: loading ? 0.5 : 1,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  backdropFilter: 'blur(8px)',
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.currentTarget.style.borderColor = 'var(--brand-primary)';
                    e.currentTarget.style.background = 'var(--theme-accent-bg)';
                    e.currentTarget.style.color = 'var(--brand-primary)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border)';
                  e.currentTarget.style.background = 'var(--bg-card)';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }}
              >
                <span>💡</span> {q}
              </button>
            ))}
          </div>
        </div>

        <div
          role="log"
          aria-live="polite"
          aria-label="AI conversation history"
          style={{ minHeight: 380, maxHeight: 600, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: 20 }}
        >
          {messages.length === 0 && (
            <div className="empty-state" style={{ opacity: 0.7, padding: '40px 20px' }}>
              <div className="empty-state-icon" style={{ fontSize: 44 }}>🧠</div>
              <div className="empty-state-text" style={{ fontSize: 16, fontWeight: 600 }}>Query the Google Photos Knowledge Graph</div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)', maxWidth: 480, marginTop: 6, lineHeight: 1.5 }}>
                Ask questions about visual memory recall, screenshot clutter, date amnesia, face recognition failures, or episodic search unmet needs. Grounded across <strong>5 Multi-Platform Discovery Sources</strong> (Play Store, App Store, Reddit, Hacker News, YouTube).
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
              {msg.role === 'user' ? (
                <div className="chat-bubble-user" style={{ maxWidth: '80%', padding: '10px 16px', fontSize: 14 }}>
                  {msg.content}
                </div>
              ) : (
                <div
                  className="chat-bubble-ai"
                  style={{
                    maxWidth: '94%',
                    padding: '18px 22px',
                    fontSize: 13.5,
                    lineHeight: 1.6,
                    background: msg.isOutOfScope ? 'rgba(239, 68, 68, 0.05)' : 'rgba(255,255,255,0.03)',
                    border: msg.isOutOfScope ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid var(--border)',
                    borderRadius: 'var(--radius-md)',
                  }}
                >
                  {msg.isOutOfScope && (
                    <div
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 6,
                        background: 'rgba(239, 68, 68, 0.15)',
                        border: '1px solid rgba(239, 68, 68, 0.4)',
                        color: '#f87171',
                        padding: '3px 10px',
                        borderRadius: 12,
                        fontSize: 11,
                        fontWeight: 700,
                        marginBottom: 12,
                      }}
                    >
                      🛡️ OUT OF SCOPE QUERY
                    </div>
                  )}

                  <MarkdownText
                    text={msg.content}
                    onInspectReview={(revIdx) => {
                      if (msg.retrievedDocs && msg.retrievedDocs[revIdx - 1]) {
                        setInspectDoc(msg.retrievedDocs[revIdx - 1]);
                      }
                    }}
                  />

                  {msg.citations && msg.citations.length > 0 && (
                    <CitationBadges
                      citations={msg.citations}
                      latencyMs={msg.latencyMs}
                      docsRetrieved={msg.docsRetrieved}
                      retrievedDocs={msg.retrievedDocs}
                      onInspectDoc={(doc) => setInspectDoc(doc)}
                    />
                  )}

                  {msg.suggestions && msg.suggestions.length > 0 && (
                    <div style={{ marginTop: 14, paddingTop: 10, borderTop: '1px dashed var(--border)' }}>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', marginBottom: 8, letterSpacing: '0.05em' }}>
                        Suggested Follow-Up Inquiries
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                        {msg.suggestions.map((sug, sIdx) => (
                          <button
                            key={sIdx}
                            onClick={() => sendMessage(sug)}
                            disabled={loading}
                            style={{
                              background: 'var(--glass-bg)',
                              border: '1px solid var(--border)',
                              borderRadius: 16,
                              padding: '5px 12px',
                              fontSize: 12,
                              color: 'var(--pink)',
                              cursor: loading ? 'not-allowed' : 'pointer',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: 6,
                              transition: 'all 0.15s ease',
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.borderColor = 'var(--pink)';
                              e.currentTarget.style.background = 'var(--theme-accent-bg)';
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.borderColor = 'var(--border)';
                              e.currentTarget.style.background = 'var(--glass-bg)';
                            }}
                          >
                            <span>💬</span> {sug}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  <div style={{ marginTop: 12, display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
                    <button
                      className="copy-btn"
                      onClick={() => copyResponse(i, msg.content)}
                      style={{
                        background: 'rgba(255,255,255,0.04)',
                        border: '1px solid var(--border)',
                        borderRadius: 6,
                        color: 'var(--text-muted)',
                        padding: '4px 10px',
                        fontSize: 11,
                        cursor: 'pointer',
                      }}
                    >
                      {copied === i ? '✓ Copied' : '📋 Copy Analysis'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
              <div
                className="chat-bubble-ai"
                style={{
                  display: 'flex',
                  gap: 8,
                  alignItems: 'center',
                  padding: '14px 20px',
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius-md)',
                }}
              >
                <div style={{ display: 'flex', gap: 4 }}>
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                </div>
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  {scope === 'brief'
                    ? 'Searching 251 verified Bucket A on-brief retrieval friction reviews & synthesizing insights...'
                    : 'Searching 2,223 vector embeddings across 5 discovery sources & synthesizing insights...'}
                </span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border)', background: 'rgba(0,0,0,0.1)' }}>
          <div style={{ display: 'flex', gap: 10 }}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage(input);
                }
              }}
              aria-label="Ask the Discovery Engine a question about visual retrieval"
              placeholder="Ask anything about episodic memory retrieval, screenshot clutter, date amnesia, face recognition..."
              style={{
                flex: 1,
                background: 'var(--glass-bg)',
                border: '1px solid var(--border)',
                borderRadius: 'var(--radius-md)',
                padding: '12px 16px',
                color: 'var(--text-primary)',
                fontSize: 14,
                outline: 'none',
                transition: 'border-color 0.15s',
              }}
              onFocus={(e) => {
                (e.target as HTMLInputElement).style.borderColor = 'var(--brand-primary)';
                (e.target as HTMLInputElement).style.boxShadow = '0 0 20px var(--card-glow-color)';
              }}
              onBlur={(e) => {
                (e.target as HTMLInputElement).style.borderColor = 'var(--border)';
                (e.target as HTMLInputElement).style.boxShadow = 'none';
              }}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || loading}
              aria-label="Submit question"
              style={{
                backgroundColor: loading ? 'var(--bg-card)' : 'transparent',
                backgroundImage: loading ? 'none' : 'var(--gradient-brand)',
                backgroundSize: '200% 200%',
                animation: loading ? 'none' : 'gradientShift 4s ease infinite',
                border: 'none',
                borderRadius: 'var(--radius-xl)',
                color: loading ? 'var(--text-muted)' : '#fff',
                padding: '12px 24px',
                fontSize: 14,
                fontWeight: 700,
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: !input.trim() ? 0.5 : 1,
                transition: 'all 0.2s ease',
                minWidth: 90,
                boxShadow: !loading && input.trim() ? '0 4px 20px var(--card-glow-color)' : 'none',
              }}
            >
              {loading ? '···' : 'Ask →'}
            </button>
          </div>

          <div style={{ display: 'flex', gap: 12, marginTop: 12, alignItems: 'center', flexWrap: 'wrap' }}>
            <span style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Platform Filter:
            </span>
            <select
              className="chat-filter-select"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              aria-label="Filter by review source"
              style={{
                background: 'var(--glass-bg)',
                border: '1px solid var(--border)',
                color: 'var(--text-secondary)',
                borderRadius: 8,
                padding: '4px 10px',
                fontSize: 12,
              }}
            >
              <option value="all">All Platforms (2,223 Discussions)</option>
              <option value="Play Store">Google Play Store (975)</option>
              <option value="App Store">Apple App Store (608)</option>
              <option value="Reddit">Reddit (319)</option>
              <option value="Hacker News">Hacker News (242)</option>
              <option value="YouTube">YouTube (79)</option>
            </select>
            <span
              style={{
                marginLeft: 'auto',
                fontSize: 11,
                color: 'var(--text-muted)',
                display: 'flex',
                alignItems: 'center',
                gap: 4,
              }}
            >
              Grounding: {scope === 'brief' ? '251 On-Brief Retrieval Discussions' : '2,223 Multi-Platform Discussions'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
