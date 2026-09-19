'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

interface DataDictionaryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function DataDictionaryModal({ isOpen, onClose }: DataDictionaryModalProps) {
  const [activeTab, setActiveTab] = useState<'cohorts' | 'funnel' | 'stages' | 'questions'>('cohorts');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.78)',
        backdropFilter: 'blur(10px)',
        zIndex: 99999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
        animation: 'fadeIn 0.2s ease-out',
      }}
      onClick={onClose}
    >
      <div
        className="card"
        style={{
          maxWidth: 920,
          width: '100%',
          maxHeight: '88vh',
          overflowY: 'auto',
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: 20,
          padding: 28,
          position: 'relative',
          boxShadow: '0 20px 50px rgba(0, 0, 0, 0.5)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20 }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
              <span style={{ fontSize: 22 }}>📖</span>
              <h2 style={{ fontSize: 20, fontWeight: 800, margin: 0, letterSpacing: '-0.02em' }}>
                Discovery Engine Data Dictionary & Cohort Guide
              </h2>
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0 }}>
              Complete transparency on sample sizes (N), cohort definitions, confusing terms, and question mappings.
            </p>
          </div>

          <button
            onClick={onClose}
            aria-label="Close modal"
            style={{
              background: 'rgba(255, 255, 255, 0.08)',
              border: '1px solid var(--border)',
              color: 'var(--text-muted)',
              width: 32,
              height: 32,
              borderRadius: '50%',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 16,
              transition: 'all 0.15s',
            }}
          >
            ✕
          </button>
        </div>

        {/* Tab Switcher */}
        <div
          style={{
            display: 'flex',
            gap: 6,
            marginBottom: 24,
            padding: 4,
            background: 'rgba(0, 0, 0, 0.25)',
            borderRadius: 12,
            border: '1px solid var(--border)',
            flexWrap: 'wrap',
          }}
        >
          <button
            onClick={() => setActiveTab('cohorts')}
            style={{
              flex: 1,
              padding: '8px 12px',
              borderRadius: 8,
              border: 'none',
              background: activeTab === 'cohorts' ? 'var(--brand-primary)' : 'transparent',
              color: activeTab === 'cohorts' ? '#fff' : 'var(--text-muted)',
              fontSize: 12,
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >
            1. Data Cohorts (2,223 vs 640 vs 251)
          </button>
          <button
            onClick={() => setActiveTab('funnel')}
            style={{
              flex: 1,
              padding: '8px 12px',
              borderRadius: 8,
              border: 'none',
              background: activeTab === 'funnel' ? 'var(--brand-primary)' : 'transparent',
              color: activeTab === 'funnel' ? '#fff' : 'var(--text-muted)',
              fontSize: 12,
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >
            2. Triage & Noise Segregation
          </button>
          <button
            onClick={() => setActiveTab('stages')}
            style={{
              flex: 1,
              padding: '8px 12px',
              borderRadius: 8,
              border: 'none',
              background: activeTab === 'stages' ? 'var(--brand-primary)' : 'transparent',
              color: activeTab === 'stages' ? '#fff' : 'var(--text-muted)',
              fontSize: 12,
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >
            3. The 4 Failure Stages (Recovery Breakdown Explained)
          </button>
          <button
            onClick={() => setActiveTab('questions')}
            style={{
              flex: 1,
              padding: '8px 12px',
              borderRadius: 8,
              border: 'none',
              background: activeTab === 'questions' ? 'var(--brand-primary)' : 'transparent',
              color: activeTab === 'questions' ? '#fff' : 'var(--text-muted)',
              fontSize: 12,
              fontWeight: 700,
              cursor: 'pointer',
              transition: 'all 0.15s',
            }}
          >
            4. PM Brief Mapping
          </button>
        </div>

        {/* TAB 1: THE 3 DATA COHORTS */}
        {activeTab === 'cohorts' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div
              style={{
                padding: 16,
                background: 'rgba(37, 99, 235, 0.08)',
                border: '1px solid rgba(37, 99, 235, 0.25)',
                borderRadius: 14,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 14, fontWeight: 800, color: '#60a5fa' }}>
                  🎯 Bucket A Focus Cohort (N = 251 documents · 11.3%)
                </span>
                <span style={{ fontSize: 11, background: '#2563eb', color: '#fff', padding: '2px 8px', borderRadius: 10, fontWeight: 700 }}>
                  Case Study Core Brief
                </span>
              </div>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                <strong>What it is:</strong> Every review where a user attempted to retrieve a specific visual memory (meal, pet, trip, document, receipt) with partial memory cues. Contains <strong>278 deep-dive failure point tags</strong> (Interpretation 48.2%, Recovery 26.6%, Evaluation 18.3%, Expression 6.8%).
                <br />
                <strong>Where used:</strong> <a href="/findings" style={{ color: '#60a5fa' }}>Findings Page</a>, <a href="/ask?scope=brief" style={{ color: '#60a5fa' }}>Strict RAG Mode</a>, and the Strategic Opportunity Rankings.
              </p>
            </div>

            <div
              style={{
                padding: 16,
                background: 'rgba(168, 85, 247, 0.08)',
                border: '1px solid rgba(168, 85, 247, 0.25)',
                borderRadius: 14,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 14, fontWeight: 800, color: '#c084fc' }}>
                  🔬 In-Depth Technical Community Discussions (N = 640 documents · 28.8%)
                </span>
                <span style={{ fontSize: 11, background: '#7e22ce', color: '#fff', padding: '2px 8px', borderRadius: 10, fontWeight: 700 }}>
                  Architecture & Gaps
                </span>
              </div>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                <strong>What it is:</strong> The subset of technical discussions from <strong>Reddit (319)</strong>, <strong>Hacker News (242)</strong>, and <strong>YouTube teardowns (79)</strong>. These contain deep technical breakdowns of OCR pipeline indexing lag, face clustering inaccuracies, local vector embeddings, and Immich self-hosting migrations.
                <br />
                <strong>Where used:</strong> <a href="/gaps" style={{ color: '#c084fc' }}>Systemic Gaps Page</a> alongside the 1,583 app store reviews.
              </p>
            </div>

            <div
              style={{
                padding: 16,
                background: 'rgba(34, 197, 94, 0.08)',
                border: '1px solid rgba(34, 197, 94, 0.25)',
                borderRadius: 14,
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 14, fontWeight: 800, color: '#4ade80' }}>
                  🌐 Total Unified Multi-Platform Corpus (N = 2,223 documents · 100%)
                </span>
                <span style={{ fontSize: 11, background: '#15803d', color: '#fff', padding: '2px 8px', borderRadius: 10, fontWeight: 700 }}>
                  Total Raw Corpus
                </span>
              </div>
              <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                <strong>What it is:</strong> The complete raw customer dataset across all 5 platforms: Google Play Store (975), Apple App Store (608), Reddit (319), Hacker News (242), and YouTube (79).
                <br />
                <strong>Where used:</strong> Homepage platform distribution, overall corpus scale telemetry.
              </p>
            </div>

            <div style={{ padding: '12px 16px', background: 'rgba(255,255,255,0.03)', borderRadius: 10, border: '1px solid var(--border)' }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>
                💡 Critical Note on Tag Frequencies vs Document Counts
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                When you see &ldquo;Screenshot Clutter: 1,471 (29.1%)&rdquo;, <strong>1,471</strong> is the number of discussions mentioning clutter (66.2% of all 2,223 reviews). <strong>29.1%</strong> is its share of the <em>5,057 total extracted tag mentions</em> across the library. In contrast, <strong>48.2% Interpretation Failure</strong> on Findings represents 134 out of 278 failure tags specifically within the on-brief Bucket A cohort.
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: THE 4 TRIAGE BUCKETS */}
        {activeTab === 'funnel' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
              59.9% of user reviews in app stores complain about backup sync errors, battery drain, or tab redesign backlash. Including them would drown out retrieval friction. The 2-stage rebuild segregated this noise:
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 12 }}>
              <div style={{ padding: 14, background: 'rgba(37, 99, 235, 0.08)', border: '1px solid rgba(37, 99, 235, 0.3)', borderRadius: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <strong style={{ color: '#60a5fa' }}>Bucket A: Retrieval Friction</strong>
                  <span style={{ fontWeight: 700, color: '#60a5fa' }}>251 docs (11.3%)</span>
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                  <strong>ON-BRIEF.</strong> Users attempting visual memory search (meal, trip, receipt) who face zero results, conversational dead-ends, or timeline scrolling.
                </div>
              </div>

              <div style={{ padding: 14, background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <strong style={{ color: '#fbbf24' }}>Bucket B: Sync & Backup Bugs</strong>
                  <span style={{ fontWeight: 700, color: '#fbbf24' }}>674 docs (30.3%)</span>
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                  <strong>SEGREGATED.</strong> Infrastructure complaints: stuck backups, battery drain, storage quota confusion, cloud upload loops.
                </div>
              </div>

              <div style={{ padding: 14, background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <strong style={{ color: '#f87171' }}>Bucket C: UI Redesign Backlash</strong>
                  <span style={{ fontWeight: 700, color: '#f87171' }}>659 docs (29.6%)</span>
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                  <strong>SEGREGATED.</strong> Anger over moving the search bar, bottom tab reorganization, and Memories carousel changes.
                </div>
              </div>

              <div style={{ padding: 14, background: 'rgba(156, 163, 175, 0.08)', border: '1px solid rgba(156, 163, 175, 0.3)', borderRadius: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <strong style={{ color: 'var(--text-muted)' }}>Bucket D: Praise & Chatter</strong>
                  <span style={{ fontWeight: 700, color: 'var(--text-muted)' }}>639 docs (28.7%)</span>
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                  <strong>SEGREGATED.</strong> 5-star generic reviews (&ldquo;great app&rdquo;), ungrounded questions, or non-actionable chatter.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: THE 4 FAILURE STAGES (RECOVERY BREAKDOWN EXPLAINED) */}
        {activeTab === 'stages' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div style={{ padding: '12px 16px', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.25)', borderRadius: 12 }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: '#f87171', marginBottom: 4 }}>
                ❓ What does &ldquo;#2 Blocker: Recovery Breakdown&rdquo; mean in plain English?
              </div>
              <p style={{ fontSize: 12.5, color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
                When a search query yields <strong>0 results</strong> or irrelevant items, Google Photos offers <strong>zero dynamic recovery options</strong>: no related query suggestions, no date relaxation sliders, and no conversational clarification chips.
                <br /><br />
                The search loop &ldquo;breaks down&rdquo; because the user is stranded at a dead end. Faced with no way to repair or refine their query, users either <strong>abandon the app entirely</strong> or fall back to spending <strong>15–30 minutes doom-scrolling</strong> through thousands of chronological photos.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: 12 }}>
              {/* Stage 1: Expression */}
              <div style={{ padding: 14, background: 'rgba(99, 102, 241, 0.08)', border: '1px solid rgba(99, 102, 241, 0.3)', borderRadius: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <strong style={{ color: '#818cf8' }}>Stage 1: Expression Failure</strong>
                  <span style={{ fontWeight: 700, color: '#818cf8', fontSize: 11.5 }}>
                    19 tags (6.8% of 278) · 19 docs (7.6% of 251)
                  </span>
                </div>
                <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                  <strong>The User&apos;s Memory Bottleneck:</strong> The user remembers a feeling, color, or person, but cannot find the right words or keywords to type. They don&apos;t know what Google&apos;s AI can or cannot understand.
                </p>
              </div>

              {/* Stage 2: Interpretation */}
              <div style={{ padding: 14, background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <strong style={{ color: '#f87171' }}>Stage 2: Interpretation Failure (#1 Blocker)</strong>
                  <span style={{ fontWeight: 700, color: '#f87171', fontSize: 11.5 }}>
                    134 tags (48.2% of 278) · 127 docs (50.6% of 251)
                  </span>
                </div>
                <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                  <strong>The AI Engine&apos;s Semantic Bottleneck:</strong> The user typed a reasonable natural language query, but Google Photos or Ask Photos took it too literally, missed visual synonyms, or misparsed relative temporal clues.
                </p>
              </div>

              {/* Stage 3: Evaluation */}
              <div style={{ padding: 14, background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <strong style={{ color: '#fbbf24' }}>Stage 3: Evaluation Failure</strong>
                  <span style={{ fontWeight: 700, color: '#fbbf24', fontSize: 11.5 }}>
                    51 tags (18.3% of 278) · 48 docs (19.1% of 251)
                  </span>
                </div>
                <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                  <strong>The Results Grid Bottleneck:</strong> Results were returned, but the user cannot evaluate them because the true memory is buried under 50 memes, payment screenshots, or WhatsApp receipts.
                </p>
              </div>

              {/* Stage 4: Recovery */}
              <div style={{ padding: 14, background: 'rgba(234, 88, 12, 0.08)', border: '1px solid rgba(234, 88, 12, 0.3)', borderRadius: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <strong style={{ color: '#fb923c' }}>Stage 4: Recovery Breakdown (#2 Blocker)</strong>
                  <span style={{ fontWeight: 700, color: '#fb923c', fontSize: 11.5 }}>
                    74 tags (26.6% of 278) · 70 docs (27.9% of 251)
                  </span>
                </div>
                <p style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>
                  <strong>The Systemic Dead-End Bottleneck:</strong> The search failed, and the engine gave zero corrective guidance, forcing users into 20+ minutes of chronological timeline doom-scrolling or complete abandonment.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: PM BRIEF MAPPING */}
        {activeTab === 'questions' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.55, margin: 0 }}>
              The 10 Inquiries map directly to the 4 Core Questions of the Google Photos PM Case Study Brief:
            </p>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12.5 }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border)', textAlign: 'left', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '8px 10px' }}>PM Brief Case Study Question</th>
                    <th style={{ padding: '8px 10px' }}>Discovery Engine Inquiries</th>
                    <th style={{ padding: '8px 10px' }}>Data Cohort</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '10px', fontWeight: 600, color: 'var(--text-primary)' }}>
                      <strong>Brief Q1:</strong> What specific photos do users struggle to retrieve when memory is incomplete?
                    </td>
                    <td style={{ padding: '10px' }}>
                      <Link href="/questions/1" style={{ color: '#60a5fa', fontWeight: 600 }}>Q1: Struggled Photo Types</Link><br />
                      <Link href="/questions/7" style={{ color: 'var(--text-secondary)', fontSize: 11.5 }}>Q7: Screenshot & Clutter Intrusion</Link>
                    </td>
                    <td style={{ padding: '10px', color: '#4ade80' }}>Bucket A (N=251)</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '10px', fontWeight: 600, color: 'var(--text-primary)' }}>
                      <strong>Brief Q2:</strong> What clues do users retain vs what have they forgotten?
                    </td>
                    <td style={{ padding: '10px' }}>
                      <Link href="/questions/2" style={{ color: '#60a5fa', fontWeight: 600 }}>Q2: Retained Memory Clues</Link><br />
                      <Link href="/questions/3" style={{ color: '#60a5fa', fontWeight: 600 }}>Q3: Forgotten Metadata</Link>
                    </td>
                    <td style={{ padding: '10px', color: '#4ade80' }}>Bucket A (N=251)</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '10px', fontWeight: 600, color: 'var(--text-primary)' }}>
                      <strong>Brief Q3:</strong> Where does retrieval break down across Classic Keyword vs Ask Photos?
                    </td>
                    <td style={{ padding: '10px' }}>
                      <Link href="/questions/4" style={{ color: '#60a5fa', fontWeight: 600 }}>Q4: Incomplete Query Formulation</Link><br />
                      <Link href="/questions/5" style={{ color: 'var(--text-secondary)', fontSize: 11.5 }}>Q5: Irrelevant Results & False Misses</Link>
                    </td>
                    <td style={{ padding: '10px', color: '#4ade80' }}>Bucket A (N=251)</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '10px', fontWeight: 600, color: 'var(--text-primary)' }}>
                      <strong>Brief Q4:</strong> What workarounds and recovery behaviors do users resort to?
                    </td>
                    <td style={{ padding: '10px' }}>
                      <Link href="/questions/6" style={{ color: '#60a5fa', fontWeight: 600 }}>Q6: Endless Timeline Scrolling</Link><br />
                      <Link href="/questions/10" style={{ color: '#60a5fa', fontWeight: 600 }}>Q10: Workarounds & WhatsApp Switching</Link>
                    </td>
                    <td style={{ padding: '10px', color: '#4ade80' }}>Bucket A (N=251)</td>
                  </tr>
                  <tr>
                    <td style={{ padding: '10px', fontWeight: 600, color: 'var(--text-muted)' }}>
                      <strong>Extended Vectors:</strong> Algorithmic blindspots & friction
                    </td>
                    <td style={{ padding: '10px' }}>
                      <Link href="/questions/8" style={{ color: 'var(--text-secondary)', fontSize: 11.5 }}>Q8: Face Recognition Failures</Link><br />
                      <Link href="/questions/9" style={{ color: 'var(--text-secondary)', fontSize: 11.5 }}>Q9: Document & Text OCR Failures</Link>
                    </td>
                    <td style={{ padding: '10px', color: 'var(--text-muted)' }}>Total Corpus (N=2,223)</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        <div style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            style={{
              padding: '8px 20px',
              borderRadius: 'var(--radius-sm)',
              background: 'var(--brand-primary)',
              color: '#fff',
              border: 'none',
              fontWeight: 700,
              fontSize: 13,
              cursor: 'pointer',
            }}
          >
            Got it, close guide
          </button>
        </div>
      </div>
    </div>
  );
}
