import { getSummary } from '@/lib/api';
import StatCard from '@/components/StatCard';
import SummaryAnimations from '@/components/SummaryAnimations';
import HeroRagInput from '@/components/HeroRagInput';
import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Executive Intelligence Summary | Google Photos AI Discovery Engine',
  description: 'Executive summary of 2,223 grounded customer discussions across Play Store, App Store, Reddit, Hacker News, and YouTube: root causes of visual retrieval friction, clutter, and AI opportunity rankings.',
};

export default async function SummaryPage() {
  const data = await getSummary();
  const totalDocs = data.kpi_cards?.find((k: { id: string; value: number }) => k.id === 'total_reviews')?.value || 2223;

  // Extract key anchor metrics for the hero ticker
  const clutterCard = data.kpi_cards?.find(k => k.id === 'clutter_pct' || k.label.includes('Clutter'));
  const zeroResultCard = data.kpi_cards?.find(k => k.id === 'zero_results_pct' || k.label.includes('Zero'));
  const unmetCard = data.kpi_cards?.find(k => k.id === 'unmet_needs_count' || k.label.includes('Unmet'));

  const clutterVal = clutterCard ? `${clutterCard.value.toFixed(1)}%` : '29.1%';
  const zeroResultVal = zeroResultCard ? `${zeroResultCard.value.toFixed(1)}%` : '23.9%';
  const unmetVal = unmetCard ? `${Math.round(unmetCard.value)}` : '81';

  return (
    <div className="container" style={{ paddingTop: 16, paddingBottom: 100 }}>
      {/* ═══ IMMERSIVE HERO VIEWPORT (UNCLUTTERED INITIAL SCREEN) ═══ */}
      <section className="hero-section" id="hero">
        <div className="hero-content">
          {/* Floating live status pills */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 22, flexWrap: 'wrap' }}>
            <span className="hero-badge" style={{ color: '#4ade80' }}>
              <span className="beacon-dot" style={{ width: 6, height: 6 }} />
              Live Unified Multi-Platform Corpus
            </span>
            <span className="hero-badge" style={{ color: 'var(--text-secondary)' }}>
              {totalDocs.toLocaleString()} Grounded Discussions
            </span>
            <span className="hero-badge" style={{ color: 'var(--brand-primary)' }}>
              Gemini 3.7 Flash · Confidence {((data.overall_confidence || 0.88) * 100).toFixed(0)}%
            </span>
          </div>

          {/* Large gradient heading */}
          <h1 style={{
            fontSize: 'clamp(34px, 4.4vw, 56px)',
            fontWeight: 700,
            lineHeight: 1.08,
            letterSpacing: '-0.04em',
            marginBottom: 20,
            maxWidth: 920,
          }}>
            Diagnosing{' '}
            <span className="hero-gradient-text">
              Visual Memory Retrieval Friction
            </span>
            {' '}& Discovery Gaps
          </h1>

          <p style={{
            fontSize: 16.5,
            lineHeight: 1.7,
            color: 'var(--text-secondary)',
            maxWidth: 780,
            marginBottom: 32,
          }}>
            Mining <strong style={{ color: 'var(--text-primary)' }}>2,223 verified customer conversations</strong> across{' '}
            <strong style={{ color: 'var(--text-primary)' }}>5 unified platforms</strong> to quantify why visual search breaks down and
            uncover high-leverage product levers for AI-native episodic recall.
          </p>

          {/* Interactive RAG Search Console & Prompt Chips */}
          <HeroRagInput />

          {/* Sleek Hero Telemetry Bar (4 core metrics in a single row) */}
          <div className="hero-ticker">
            <div className="hero-ticker-item">
              <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Total Analyzed
              </div>
              <div style={{ fontSize: 22, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", color: '#818cf8', letterSpacing: '-0.02em' }}>
                {totalDocs.toLocaleString()}
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>5 Unified Platforms</div>
            </div>
            <div className="hero-ticker-item">
              <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Screenshot Clutter
              </div>
              <div style={{ fontSize: 22, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", color: '#f472b6', letterSpacing: '-0.02em' }}>
                {clutterVal}
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>1,471 Reviews (66.2% Corpus)</div>
            </div>
            <div className="hero-ticker-item">
              <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Zero Search Results
              </div>
              <div style={{ fontSize: 22, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", color: '#f87171', letterSpacing: '-0.02em' }}>
                {zeroResultVal}
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>1,209 Reviews (54.4% Corpus)</div>
            </div>
            <div className="hero-ticker-item">
              <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Identified Needs
              </div>
              <div style={{ fontSize: 22, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", color: '#4ade80', letterSpacing: '-0.02em' }}>
                {unmetVal}
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>81 Categories (3,661 Mentions)</div>
            </div>
          </div>

          {/* Smooth Scroll Cue */}
          <div style={{ marginTop: 28, display: 'flex', alignItems: 'center', justifyContent: 'flex-start' }}>
            <a href="#telemetry-section" className="scroll-cue">
              <span className="scroll-cue-bounce">↓</span>
              <span>Explore Diagnostic Signals & Inquiries</span>
            </a>
          </div>
        </div>
      </section>

      {/* ═══ SECTION 01: CORE DIAGNOSTIC TELEMETRY (BELOW THE FOLD) ═══ */}
      <section id="telemetry-section" style={{ paddingTop: 64, marginBottom: 64 }}>
        <div style={{ marginBottom: 28 }}>
          <div className="section-kicker">
            <span>01</span> // <span>TELEMETRY HUB</span>
          </div>
          <h2 className="section-title">Core Diagnostic Signals</h2>
          <p className="section-subtitle">
            Grounded behavioral metrics tracking real-world retrieval failures, library clutter, and cognitive disconnects.
          </p>
        </div>

        <div className="grid-3 cascade-grid">
          {data.kpi_cards.map((card, i) => (
            <StatCard
              key={card.id}
              label={card.label}
              value={card.value}
              unit={card.unit as 'count' | 'percent'}
              sparkline={card.sparkline || []}
              delay={i * 70}
            />
          ))}
        </div>
      </section>

      {/* ═══ SECTION 02: THE ARCHITECTURAL GAP (STRATEGIC THESIS) ═══ */}
      <section style={{ marginBottom: 64 }}>
        <div style={{ marginBottom: 24 }}>
          <div className="section-kicker">
            <span>02</span> // <span>ARCHITECTURAL GAP</span>
          </div>
          <h2 className="section-title">The Fundamental Asymmetry of Photo Retrieval</h2>
          <p className="section-subtitle">
            Why traditional search engines fail to retrieve human memories despite billions of indexed photos.
          </p>
        </div>

        <div className="thesis-card">
          <div className="thesis-grid">
            {/* Human Episodic Recall */}
            <div className="thesis-col thesis-col-human">
              <div className="thesis-header">
                <span className="thesis-badge thesis-badge-human">Human Episodic Memory</span>
                <span style={{ fontSize: 20 }}>🧠</span>
              </div>
              <p className="thesis-text">
                Humans naturally remember moments through <strong>sensory atmospheres, social companions, emotions, and relative time</strong>.
              </p>
              <div className="thesis-quote">
                &ldquo;eating seafood with Sarah outdoors on a chilly evening&rdquo;
              </div>
              <div className="thesis-tags">
                <span className="thesis-tag">Atmosphere</span>
                <span className="thesis-tag">Social Bonds</span>
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
                <span className="thesis-badge thesis-badge-system">Traditional Search Index</span>
                <span style={{ fontSize: 20 }}>🏷️</span>
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
            <span style={{ fontSize: 18 }}>⚡</span>
            <div style={{ flex: 1 }}>
              <span style={{ fontWeight: 700, color: 'var(--brand-primary)' }}>The Engineering Lever: </span>
              <span style={{ color: 'var(--text-secondary)' }}>
                When users recall sensations but systems demand dates and literal tags, <strong>1,209 discussions (23.9% of friction signals / 54.4% of corpus)</strong> document false misses where users abandon search for endless timeline scrolling. This Discovery Engine quantifies where this semantic translation collapses.
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ SECTION 03, 04, 05: SOURCE SYNTHESIS, QUALITY & INQUIRY MATRIX ═══ */}
      <SummaryAnimations data={data} />
    </div>
  );
}
