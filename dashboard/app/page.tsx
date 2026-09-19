import { getSummary } from '@/lib/api';
import StatCard from '@/components/StatCard';
import SummaryAnimations from '@/components/SummaryAnimations';
import HeroRagInput from '@/components/HeroRagInput';
import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Overview | Google Photos AI Discovery Engine',
  description: 'Evidence-based analysis of 2,223 customer reviews across 5 platforms diagnosing why visual memory search breaks down and what users need instead.',
};

export default async function SummaryPage() {
  const data = await getSummary();
  const totalDocs = data.kpi_cards?.find((k: { id: string; value: number }) => k.id === 'total_reviews')?.value || 2223;

  return (
    <div className="container" style={{ paddingTop: 20, paddingBottom: 100 }}>
      {/* ═══ CLEAN HERO SECTION ═══ */}
      <section className="hero-section" id="hero" style={{ padding: '36px 0 28px 0' }}>
        <div className="hero-content">
          {/* Subtle status pills */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
            <span className="hero-badge" style={{ color: 'var(--semantic-green)' }}>
              <span className="beacon-dot" style={{ width: 6, height: 6, backgroundColor: 'var(--semantic-green)' }} />
              {totalDocs.toLocaleString()} customer reviews analyzed
            </span>
            <span className="hero-badge" style={{ color: 'var(--text-secondary)' }}>
              5 platforms (Play Store, App Store, Reddit, HN, YouTube)
            </span>
            <span className="hero-badge" style={{ color: 'var(--semantic-blue)' }}>
              Verified quotes & calibrated confidence
            </span>
          </div>

          {/* Clean, readable heading */}
          <h1 style={{
            fontSize: 'clamp(32px, 4vw, 50px)',
            fontWeight: 700,
            lineHeight: 1.15,
            letterSpacing: '-0.035em',
            marginBottom: 16,
            maxWidth: 860,
            color: 'var(--text-primary)',
          }}>
            Why users can&apos;t find the photo they&apos;re looking for
          </h1>

          <p style={{
            fontSize: 16,
            lineHeight: 1.65,
            color: 'var(--text-secondary)',
            maxWidth: 740,
            marginBottom: 28,
          }}>
            We analyzed 2,223 customer reviews across 5 platforms to understand why photo search fails — and what users need instead.
          </p>

          {/* Primary Action Buttons */}
          <div style={{ display: 'flex', gap: 12, marginBottom: 28, flexWrap: 'wrap' }}>
            <Link
              href="/findings"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
                padding: '11px 22px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--semantic-blue)',
                color: '#fff',
                fontWeight: 600,
                fontSize: 14,
                textDecoration: 'none',
                boxShadow: '0 2px 8px rgba(59, 130, 246, 0.25)',
                transition: 'background var(--t-base) ease',
              }}
            >
              <span>See detailed findings</span>
              <span>→</span>
            </Link>

            <Link
              href="/gaps"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 8,
                padding: '11px 18px',
                borderRadius: 'var(--radius-sm)',
                background: 'var(--bg-card)',
                border: '1px solid var(--border)',
                color: 'var(--text-primary)',
                fontWeight: 500,
                fontSize: 14,
                textDecoration: 'none',
              }}
            >
              <span>Gap analysis</span>
            </Link>
          </div>

          {/* Interactive RAG Search Console */}
          <HeroRagInput />

          {/* Quick link cue */}
          <div style={{ marginTop: 24, display: 'flex', alignItems: 'center', justifyContent: 'flex-start' }}>
            <a href="#scope-section" className="scroll-cue" style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              <span>Explore findings &amp; key numbers ↓</span>
            </a>
          </div>
        </div>
      </section>

      {/* ═══ "HOW WE MADE SURE THIS IS ACCURATE" EXPANDABLE CARD ═══ */}
      <section style={{ marginBottom: 36 }}>
        <div className="verification-card">
          <details className="verification-details">
            <summary>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span className="verification-badge">
                  ✓ Verified Methodology
                </span>
                <span style={{ fontSize: 13.5, fontWeight: 600, color: 'var(--text-primary)' }}>
                  How we made sure this data is accurate
                </span>
              </div>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Click to expand</span>
            </summary>
            <div className="verification-body">
              <div>
                <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: 3 }}>
                  Word-for-Word Quotes
                </strong>
                Every user quote cited in this report is verified character-for-character against the original raw review.
              </div>
              <div>
                <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: 3 }}>
                  Calibrated Confidence
                </strong>
                Confidence scores are based on evidence depth and multi-source corroboration (±0.18 σ variance), not arbitrary defaults.
              </div>
              <div>
                <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: 3 }}>
                  Clean Scope Separation
                </strong>
                Search friction is strictly isolated from app crashes, sync stalls, and UI complaints so search insights aren&apos;t polluted.
              </div>
              <div>
                <strong style={{ color: 'var(--text-primary)', display: 'block', marginBottom: 3 }}>
                  Transparent Totals
                </strong>
                Every statistic shows both the count and the exact total denominator (e.g. &ldquo;94 out of 278 mentions&rdquo;).
              </div>
            </div>
          </details>
        </div>
      </section>

      {/* ═══ SCOPE STORY: WHAT WE ANALYZED & WHAT WE FOCUSED ON ═══ */}
      <section id="scope-section" style={{ marginBottom: 54 }}>
        <div
          style={{
            background: 'var(--bg-surface)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius-lg)',
            padding: '28px 30px',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
            <div>
              <h2 style={{ fontSize: 21, fontWeight: 700, margin: 0, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
                What we analyzed — and what we focused on
              </h2>
              <p style={{ fontSize: 14, color: 'var(--text-secondary)', margin: '8px 0 0', maxWidth: 820, lineHeight: 1.55 }}>
                We analyzed 2,223 pieces of user feedback across 5 platforms. Most weren&apos;t about search — they were about app crashes, layout redesigns, or general praise. We separated those out to focus on the 251 reviews where people specifically described struggling to find a remembered photo.
              </p>
            </div>
            <Link
              href="/findings"
              style={{
                fontSize: 12.5,
                fontWeight: 600,
                color: 'var(--semantic-blue)',
                textDecoration: 'none',
                background: 'rgba(59, 130, 246, 0.08)',
                border: '1px solid rgba(59, 130, 246, 0.25)',
                padding: '6px 14px',
                borderRadius: 16,
                display: 'inline-flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              <span>Explore all findings</span>
              <span>→</span>
            </Link>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: 14 }}>
            {/* Primary: Search Friction */}
            <div style={{
              padding: '18px 20px',
              background: 'rgba(59, 130, 246, 0.07)',
              border: '1.5px solid rgba(59, 130, 246, 0.35)',
              borderRadius: 'var(--radius-md)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 11.5, fontWeight: 700, color: 'var(--semantic-blue)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Search Friction
                </span>
                <span style={{ fontSize: 11.5, fontWeight: 700, color: 'var(--semantic-blue)' }}>11.3%</span>
              </div>
              <div style={{ fontSize: 24, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", color: 'var(--semantic-blue)', marginBottom: 2 }}>
                251 Reviews
              </div>
              <div style={{ fontSize: 11.5, color: 'var(--semantic-blue)', opacity: 0.9, fontWeight: 500, marginBottom: 8 }}>
                Primary focus of this report
              </div>
              <div style={{ fontSize: 12.5, color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                People struggling to find a remembered photo through search (vague dates, lost receipts, forgotten moments).
              </div>
            </div>

            {/* Filtered: App & Backup Issues */}
            <div style={{
              padding: '18px 20px',
              background: 'rgba(100, 116, 139, 0.05)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 11.5, fontWeight: 600, color: 'var(--semantic-gray)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  App &amp; Backup Issues
                </span>
                <span style={{ fontSize: 11.5, fontWeight: 600, color: 'var(--text-muted)' }}>30.3%</span>
              </div>
              <div style={{ fontSize: 24, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", color: 'var(--text-secondary)', marginBottom: 2 }}>
                674 Reviews
              </div>
              <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginBottom: 8 }}>
                Filtered out for search analysis
              </div>
              <div style={{ fontSize: 12.5, color: 'var(--text-muted)', lineHeight: 1.45 }}>
                Cloud backup stalls, battery drain, syncing loops, and storage quota bugs.
              </div>
            </div>

            {/* Filtered: Layout & Menu Complaints */}
            <div style={{
              padding: '18px 20px',
              background: 'rgba(100, 116, 139, 0.05)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 11.5, fontWeight: 600, color: 'var(--semantic-gray)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Layout &amp; Menu Complaints
                </span>
                <span style={{ fontSize: 11.5, fontWeight: 600, color: 'var(--text-muted)' }}>29.6%</span>
              </div>
              <div style={{ fontSize: 24, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", color: 'var(--text-secondary)', marginBottom: 2 }}>
                659 Reviews
              </div>
              <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginBottom: 8 }}>
                Filtered out for search analysis
              </div>
              <div style={{ fontSize: 12.5, color: 'var(--text-muted)', lineHeight: 1.45 }}>
                Tab repositioning, bottom bar removal, and memories carousel redesign gripes.
              </div>
            </div>

            {/* Filtered: General Feedback */}
            <div style={{
              padding: '18px 20px',
              background: 'rgba(100, 116, 139, 0.05)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 11.5, fontWeight: 600, color: 'var(--semantic-gray)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  General Feedback
                </span>
                <span style={{ fontSize: 11.5, fontWeight: 600, color: 'var(--text-muted)' }}>28.7%</span>
              </div>
              <div style={{ fontSize: 24, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", color: 'var(--text-secondary)', marginBottom: 2 }}>
                639 Reviews
              </div>
              <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginBottom: 8 }}>
                Filtered out for search analysis
              </div>
              <div style={{ fontSize: 12.5, color: 'var(--text-muted)', lineHeight: 1.45 }}>
                General praise (&ldquo;great app&rdquo;), non-actionable chatter, and simple 5-star ratings.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ KEY NUMBERS ═══ */}
      <section id="key-numbers" style={{ marginBottom: 54 }}>
        <div style={{ marginBottom: 20 }}>
          <h2 className="section-title">Key numbers</h2>
          <p className="section-subtitle">
            Evidence-backed metrics tracking real-world search failures, library clutter, and memory disconnects.
          </p>
        </div>

        <div className="grid-3 cascade-grid">
          {data.kpi_cards.map((card, i) => (
            <StatCard
              key={card.id}
              id={card.id}
              label={card.label}
              value={card.value}
              unit={card.unit as 'count' | 'percent'}
              sparkline={card.sparkline || []}
              delay={i * 70}
            />
          ))}
        </div>
      </section>

      {/* ═══ WHY PHOTO SEARCH BREAKS DOWN (THESIS) ═══ */}
      <section style={{ marginBottom: 54 }}>
        <div style={{ marginBottom: 20 }}>
          <h2 className="section-title">Why photo search breaks down</h2>
          <p className="section-subtitle">
            Traditional search engines index literal metadata, but humans remember atmospheres, people, and emotions.
          </p>
        </div>

        <div className="thesis-card">
          <div className="thesis-grid">
            {/* Human Episodic Recall */}
            <div className="thesis-col thesis-col-human">
              <div className="thesis-header">
                <span className="thesis-badge thesis-badge-human">What users remember</span>
              </div>
              <p className="thesis-text">
                Humans naturally remember moments through <strong>sensory atmospheres, social companions, emotions, and relative time</strong>.
              </p>
              <div className="thesis-quote">
                &ldquo;eating seafood with Sarah outdoors on a chilly evening&rdquo;
              </div>
              <div className="thesis-tags">
                <span className="thesis-tag">Atmosphere</span>
                <span className="thesis-tag">Social Companions</span>
                <span className="thesis-tag">Relative Seasons</span>
                <span className="thesis-tag">Subjective Emotion</span>
              </div>
            </div>

            {/* VS Divider */}
            <div className="thesis-divider">
              <span className="thesis-vs">VS</span>
            </div>

            {/* Traditional Rigid Indexing */}
            <div className="thesis-col thesis-col-system">
              <div className="thesis-header">
                <span className="thesis-badge thesis-badge-system">What the system indexes</span>
              </div>
              <p className="thesis-text">
                Traditional engines index photos by <strong>rigid calendar timestamps, GPS coordinates, and literal object nouns</strong>.
              </p>
              <div className="thesis-quote">
                &ldquo;Date: 2023-11-04 · Lat: 37.7749° N · Label: plate, outdoor&rdquo;
              </div>
              <div className="thesis-tags">
                <span className="thesis-tag">Exact Calendar Date</span>
                <span className="thesis-tag">GPS Coordinates</span>
                <span className="thesis-tag">Literal Object Labels</span>
                <span className="thesis-tag">EXIF Metadata</span>
              </div>
            </div>
          </div>

          {/* Synthesis footer callout */}
          <div className="thesis-footer">
            <div style={{ flex: 1 }}>
              <span style={{ fontWeight: 700, color: 'var(--semantic-blue)' }}>Key Takeaway: </span>
              <span style={{ color: 'var(--text-secondary)' }}>
                When users search with sensory memories but systems require exact dates or keywords, search fails. Among the 251 search-related reviews, the data shows two primary roadblocks: in <strong>48.2% of issues, search misunderstands the query</strong>, and in <strong>26.6% of issues, the system offers no help after failing</strong>, leaving users stranded with endless scrolling.
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ DETAILED SECTIONS & INQUIRY MATRIX ═══ */}
      <SummaryAnimations data={data} />
    </div>
  );
}
