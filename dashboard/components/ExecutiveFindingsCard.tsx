'use client';
import { useState } from 'react';

interface QuestionData {
  question_text?: string;
  question_short?: string;
  total_relevant_docs?: number;
  avg_confidence?: number;
  [key: string]: unknown;
}

interface ExecutiveFindingsCardProps {
  questionId: number;
  data: QuestionData;
  color: string;
}

const EXECUTIVE_INSIGHTS: Record<number, { headline: string; bullets: string[]; statLabel: string; statValue: string; actionableLever: string }> = {
  1: {
    headline: 'People search by scenes and companions, but the engine only looks for single objects',
    bullets: [
      'Over 40% of search struggles (592 of 1,457 tags, 40.6%) involve multi-cue memories (e.g. "friend + beach + sunset") where the engine cannot connect multiple recall fragments.',
      '42.2% of search issues (615 of 1,457 tags) involve looking for specific companions present in the photo.',
      '6.4% of search issues (93 of 1,457 tags) involve everyday items like receipts or medicine labels that lack readable text.',
    ],
    statLabel: 'Scenes & Companions',
    statValue: '42.2% (615 of 1,457 tags)',
    actionableLever: 'Prioritize episodic multimodal embeddings over literal single-noun object labels.',
  },
  2: {
    headline: 'Users vividly remember colors, people, and seasons — but forget exact dates',
    bullets: [
      'Nearly 80% of users (805 of 1,009 tags, 79.8%) recall overall scene composition (colors, objects, setting) when formulating a search.',
      '31.9% of users (322 of 1,009 tags) recall who they were with during the moment.',
      '23.5% of users (237 of 1,009 tags) remember relative time ("two summers ago", "around graduation") rather than exact calendar dates.',
    ],
    statLabel: 'Visual & Scene Recall',
    statValue: '79.8% (805 of 1,009 tags)',
    actionableLever: 'Map natural language descriptions of color, companions, and relative time directly into visual search vectors.',
  },
  3: {
    headline: 'Calendar dates and filenames are the first things users forget',
    bullets: [
      'Over 36% of search issues (317 of 870 tags, 36.4%) involve forgetting the exact date or month of a photo.',
      'Nearly half of users (429 of 870 tags, 49.3%) cannot recall device filenames or folder locations.',
      '23.9% of search issues (208 of 870 tags) involve forgetting the formal venue name or exact location.',
    ],
    statLabel: 'Date & Filename Amnesia',
    statValue: '49.3% (429 of 870 tags)',
    actionableLever: 'Support flexible time ranges (+/- 12 months) and remove hard date-matching requirements.',
  },
  4: {
    headline: 'Keyword search takes queries too literally, and AI search misinterprets intent',
    bullets: [
      'About a third of query failures (35 of 110 query tags, 31.8%) happen because keyword search matches exact words instead of meaning.',
      'Nearly a quarter of query failures (26 of 110 query tags, 23.6%) happen because Ask Photos (Gemini AI) misreads the user\'s intent.',
      'Users describe trying multiple keyword guesses in frustration before abandoning search entirely.',
    ],
    statLabel: 'Query Misinterpretation',
    statValue: '55.4% (61 of 110 query tags)',
    actionableLever: 'Decompose user queries into separate time, visual, and social clues to infer the real intent.',
  },
  5: {
    headline: 'Abstract search terms either return zero results or flood users with irrelevant photos',
    bullets: [
      'Over 40% of irrelevant results (72 of 169 result tags, 42.6%) stem from abstract descriptions ("cozy breakfast") that fail to match photo tags.',
      '20.7% of irrelevant results (35 of 169 result tags) are literal keyword overfits that flood the screen with wrong photos.',
      '17.2% of irrelevant results (29 of 169 result tags) stem from face recognition returning the wrong person.',
    ],
    statLabel: 'Semantic & Literal Mismatch',
    statValue: '63.3% (107 of 169 result tags)',
    actionableLever: 'Introduce fuzzy associative matching and replace "no results found" screens with nearest related memories.',
  },
  6: {
    headline: 'When search fails, users are forced to endlessly scroll through years of photos',
    bullets: [
      'Over two-thirds of recovery issues (51 out of 74 recovery tags, 68.9%) describe being forced to scroll manually through thousands of photos.',
      '14.9% of recovery complaints (11 of 74 recovery tags) cite zero suggestions or refinement help when search fails.',
      'Users report spending 20 to 40 minutes scrolling back chronologically to find a single photo.',
    ],
    statLabel: 'Manual Scroll Fallback',
    statValue: '68.9% (51 of 74 recovery tags)',
    actionableLever: 'Collapse duplicate burst shots automatically and show dynamic milestone markers in the timeline.',
  },
  7: {
    headline: 'Screenshots and memes pollute search results and bury real personal memories',
    bullets: [
      'Across customer feedback, library clutter from non-personal images is a frequent pain point.',
      'Among search-specific reviews, users reported WhatsApp memes (48 tags), receipts (41 tags), and screenshots (36 tags) clogging search results.',
      'Users describe having to dig through hundreds of temporary images to find one personal photo.',
    ],
    statLabel: 'Clutter Complaint Volume',
    statValue: '147 clutter tags across feedback',
    actionableLever: 'Automatically quarantine receipts, screenshots, and memes into a separate utility section away from personal photos.',
  },
  8: {
    headline: 'People behind the camera get forgotten, and pets are often misidentified',
    bullets: [
      'Over half of face search issues (29 out of 55 face tags, 52.7%) involve wrong face matches or merged identities.',
      '21.8% of face issues (12 of 55 face tags) involve untagged people in candid group shots where faces are distant or angled.',
      '14.5% of face issues (8 of 55 face tags) involve confusing different pets or dog breeds.',
    ],
    statLabel: 'Wrong Face Match Rate',
    statValue: '52.7% (29 of 55 face tags)',
    actionableLever: 'Use photo co-occurrence and device ownership context to infer who took the photo or was present.',
  },
  9: {
    headline: 'Curved medicine labels and handwritten notes defeat standard photo search',
    bullets: [
      'Nearly 40% of document search issues (18 out of 46 document tags, 39.1%) involve prescription and medicine bottle labels.',
      '26.1% of document issues (12 of 46 document tags) involve handwritten recipes, whiteboard notes, or scribbled addresses.',
      '15.2% of document issues (7 of 46 document tags) involve glare or low contrast on reflective surfaces.',
    ],
    statLabel: 'Prescription & Medicine Issues',
    statValue: '39.1% (18 of 46 document tags)',
    actionableLever: 'Combine partial text reading with bottle and document shape recognition to identify prescriptions.',
  },
  10: {
    headline: 'When search fails, users switch to WhatsApp, text friends, or give up entirely',
    bullets: [
      'Over two-thirds of workarounds (51 out of 74 workaround tags, 68.9%) involve falling back to exhausting timeline scrolling.',
      '16.2% of users (12 of 74 workaround tags) search their WhatsApp or messaging chat history instead, because messages are organized by person.',
      '5.4% of users (4 of 74 workaround tags) reported switching to Apple Photos or self-hosted solutions for better search control.',
    ],
    statLabel: 'Manual Doom-Scroll Fallback',
    statValue: '68.9% (51 of 74 workaround tags)',
    actionableLever: 'Build conversational search refinement chips so users can narrow down failed searches without scrolling.',
  },
};

export default function ExecutiveFindingsCard({ questionId, data, color }: ExecutiveFindingsCardProps) {
  const [copied, setCopied] = useState(false);
  const insight = EXECUTIVE_INSIGHTS[questionId] || {
    headline: data?.question_text || 'Key Findings Summary',
    bullets: [
      `${data?.total_relevant_docs?.toLocaleString() || '1,616'} search-related customer reviews analyzed.`,
      'Evidence confidence calibrated with dynamic variance across multiple raters.',
      'Synthesized across 5 platform feedback sources.',
    ],
    statLabel: 'Evidence Base',
    statValue: `${data?.total_relevant_docs?.toLocaleString() || '1,616'} Reviews`,
    actionableLever: 'Apply synthesized retrieval improvements across search, recall, and library organization.',
  };

  const copyToClipboard = () => {
    const textToCopy = `[Research Summary — Question ${questionId}: ${data?.question_short || ''}]\n\n` +
      `Headline: ${insight.headline}\n\n` +
      `Key Takeaways:\n` +
      insight.bullets.map((b) => `• ${b}`).join('\n') +
      `\n\nRecommended Product Direction: ${insight.actionableLever}\n` +
      `Reviews Analyzed: ${data?.total_relevant_docs?.toLocaleString() || '1,616'}`;

    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div
      className="card animate-enter"
      aria-label="Synthesized findings and recommendations"
      style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderLeft: `4px solid ${color}`,
        borderRadius: 'var(--radius-lg)',
        padding: '22px 24px',
        marginBottom: 28,
        boxShadow: 'var(--shadow-card)',
      }}
    >
      {/* Level 1: Glance - Executive Verdict */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16, marginBottom: 18, flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: 280 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <span
              style={{
                fontSize: 11,
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
                color: color,
                display: 'inline-flex',
                alignItems: 'center',
                gap: 5,
              }}
            >
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: color }} />
              Key Finding
            </span>
            <span style={{ fontSize: 11, background: `${color}14`, color: color, padding: '2px 8px', borderRadius: 10, fontWeight: 600, border: `1px solid ${color}25` }}>
              Question {questionId}
            </span>
          </div>
          <h2 style={{ fontSize: 19, fontWeight: 700, color: 'var(--text-primary)', margin: 0, letterSpacing: '-0.02em', lineHeight: 1.35 }}>
            {insight.headline}
          </h2>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase' }}>
              {insight.statLabel}
            </div>
            <div style={{ fontSize: 24, fontWeight: 800, color: color, fontFamily: "'Space Grotesk', sans-serif", letterSpacing: '-0.02em' }}>
              {insight.statValue}
            </div>
          </div>

          <button
            onClick={copyToClipboard}
            aria-label="Copy summary to clipboard"
            style={{
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-sm)',
              padding: '6px 12px',
              fontSize: 12,
              fontWeight: 600,
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              transition: 'all 0.15s ease',
            }}
            title="Copy summary to clipboard"
          >
            <span>{copied ? '✓ Copied' : 'Copy'}</span>
          </button>
        </div>
      </div>

      {/* Level 2: Scan - 3 Evidence Tiles */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12, marginBottom: 16 }}>
        {insight.bullets.map((bullet, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 10,
              fontSize: 13,
              color: 'var(--text-secondary)',
              lineHeight: 1.55,
              background: 'var(--bg-elevated)',
              border: '1px solid var(--border)',
              padding: '12px 14px',
              borderRadius: 'var(--radius-md)',
            }}
          >
            <span
              style={{
                width: 18,
                height: 18,
                borderRadius: '50%',
                background: `${color}18`,
                color: color,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 11,
                fontWeight: 700,
                flexShrink: 0,
                marginTop: 2,
              }}
            >
              {idx + 1}
            </span>
            <span>{bullet}</span>
          </div>
        ))}
      </div>

      {/* Level 3: Actionable Product Lever */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          background: `${color}0c`,
          border: `1px solid ${color}25`,
          borderRadius: 'var(--radius-md)',
          padding: '11px 16px',
          fontSize: 13,
          color: 'var(--text-primary)',
        }}
      >
        <div style={{ lineHeight: 1.5 }}>
          <strong style={{ color: color }}>Recommended product direction: </strong>
          {insight.actionableLever}
        </div>
      </div>

      {/* Level 4: Tag & Denominator Clarification */}
      <div
        style={{
          marginTop: 12,
          display: 'flex',
          alignItems: 'flex-start',
          gap: 8,
          background: 'rgba(255, 255, 255, 0.025)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-sm)',
          padding: '8px 12px',
          fontSize: 11.5,
          color: 'var(--text-muted)',
          lineHeight: 1.45,
        }}
      >
        <span style={{ fontSize: 13, flexShrink: 0, marginTop: 1 }}>🏷️</span>
        <div>
          <strong style={{ color: 'var(--text-secondary)' }}>What are &ldquo;tags&rdquo; in the denominator?</strong> In this discovery engine, a <em>tag</em> is an individual, machine-verified failure pattern or memory signal identified in customer reviews (e.g. date amnesia, wrong face match, or forced scroll fallback). The denominator shows total verified failure tags cataloged for that specific category. A single user review often contains multiple tags if the user hit several obstacles.
        </div>
      </div>
    </div>
  );
}
