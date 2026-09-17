import { getSystemicGaps } from '@/lib/api';
import GapsContent from '@/components/GapsContent';
import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Systemic Retrieval Gaps | Google Photos AI Discovery Engine',
  description: 'Deep-dive intelligence across 640 in-depth technical discussions (Reddit, Hacker News, YouTube teardowns) alongside app store feedback, capturing systemic architectural failure modes in visual memory retrieval.',
};

export default async function GapsPage() {
  const data = await getSystemicGaps();

  return (
    <div className="container" style={{ paddingTop: 32, paddingBottom: 64 }}>
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16, marginBottom: 12 }}>
          <div style={{ flex: 1, minWidth: 320 }}>
            <h1>
              <span style={{ background: 'var(--gradient-brand)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Systemic
              </span>{' '}
              Retrieval Gaps & Architecture Bottlenecks
            </h1>
            <p>
              Deep-dive technical intelligence from 640 in-depth engineering and community discussions (<strong>Reddit, Hacker News, YouTube Teardowns</strong>) synthesized alongside app store consumer feedback across the unified 2,223-document corpus — identifying systemic architectural failure modes (OCR indexing lag, face grouping blindspots, meme clutter pollution, and timeline scroll breakdown) that degrade the visual discovery experience.
            </p>
          </div>
          <Link
            href="/ask?q=What+are+the+core+systemic+architectural+gaps+and+failure+modes+in+Google+Photos%3F"
            style={{
              padding: '5px 12px',
              fontSize: 12,
              fontWeight: 500,
              color: 'var(--text-secondary)',
              textDecoration: 'none',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border)',
              background: 'rgba(255, 255, 255, 0.02)',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 5,
              whiteSpace: 'nowrap',
              marginTop: 8,
              transition: 'all 0.15s ease',
            }}
            title="Ask AI about systemic gaps"
          >
            <span style={{ fontSize: 11, color: 'var(--brand-primary)' }}>✦</span>
            <span>Ask AI about Gaps ↗</span>
          </Link>
        </div>
      </div>

      <GapsContent data={data} />
    </div>
  );
}
