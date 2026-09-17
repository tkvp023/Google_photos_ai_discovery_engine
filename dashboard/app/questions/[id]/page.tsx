import { getQuestion } from '@/lib/api';
import QuestionSection from '@/components/QuestionSection';
import InquiryStepper from '@/components/InquiryStepper';
import ExecutiveFindingsCard from '@/components/ExecutiveFindingsCard';
import QuestionNavFooter from '@/components/QuestionNavFooter';
import { QUESTION_META } from '@/lib/constants';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import type { Metadata } from 'next';

export async function generateStaticParams() {
  return Array.from({ length: 10 }, (_, i) => ({ id: String(i + 1) }));
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const qid = parseInt(id);
  const data = await getQuestion(qid);
  return {
    title: `Q${qid}: ${data.question_short} | Google Photos AI Discovery Engine`,
    description: data.question_text,
  };
}

export default async function QuestionPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const qid = parseInt(id);
  if (isNaN(qid) || qid < 1 || qid > 10) notFound();

  const data = await getQuestion(qid);
  const meta = QUESTION_META[qid];
  const isBoth = meta?.sourceType === 'both';

  return (
    <div className="container" style={{ paddingTop: 28, paddingBottom: 64 }}>
      {/* Breadcrumb Bar */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          fontSize: 12.5,
          color: 'var(--text-muted)',
          marginBottom: 16,
        }}
      >
        <Link href="/" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontWeight: 500 }}>
          Executive Summary
        </Link>
        <span>/</span>
        <span style={{ color: 'var(--text-secondary)' }}>10 Strategic Inquiries</span>
        <span>/</span>
        <span style={{ color: meta?.color || 'var(--brand-primary)', fontWeight: 700 }}>
          Q{qid}: {meta?.short || `Question ${qid}`}
        </span>
      </div>

      {/* 10 Inquiry Stepper Ribbon */}
      <InquiryStepper activeId={qid} />

      {/* Question Header */}
      <div className="page-header" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12, flexWrap: 'wrap' }}>
          <span
            style={{
              background: meta?.color || 'var(--brand-primary)',
              color: '#fff',
              fontFamily: "'Space Grotesk', sans-serif",
              fontWeight: 800,
              fontSize: 13,
              padding: '3px 12px',
              borderRadius: 20,
              letterSpacing: '0.02em',
            }}
          >
            Inquiry {qid} of 10
          </span>

          <span
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 20,
              padding: '3px 12px',
              fontSize: 12,
              color: 'var(--text-secondary)',
              fontWeight: 600,
            }}
          >
            {data.total_relevant_docs.toLocaleString()} Grounded Documents
          </span>

          {/* Source Derivation Badge */}
          <span
            style={{
              fontSize: 12,
              fontWeight: 700,
              padding: '3px 12px',
              borderRadius: 16,
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              background: 'rgba(56, 189, 248, 0.12)',
              border: '1px solid rgba(56, 189, 248, 0.35)',
              color: 'var(--brand-primary)',
            }}
          >
            <span>🌐</span>
            Derivation: Unified Multi-Platform Corpus (5 Channels)
          </span>

          {/* Subtle Ask AI Link */}
          <Link
            href={`/ask?q=${encodeURIComponent(data.question_text)}`}
            style={{
              marginLeft: 'auto',
              fontSize: 12,
              fontWeight: 500,
              color: 'var(--text-secondary)',
              textDecoration: 'none',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 5,
              padding: '3px 10px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border)',
              background: 'rgba(255, 255, 255, 0.02)',
              transition: 'all 0.15s ease',
              whiteSpace: 'nowrap',
            }}
            title="Ask AI about this inquiry"
          >
            <span style={{ fontSize: 11, color: 'var(--brand-primary)' }}>✦</span>
            <span>Ask AI about this ↗</span>
          </Link>
        </div>

        <h1 style={{ fontSize: 'clamp(24px, 2.8vw, 34px)', fontWeight: 800, letterSpacing: '-0.025em', lineHeight: 1.25, marginBottom: 12 }}>
          {data.question_text}
        </h1>

        {/* Source Derivation Transparency Note */}
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderLeft: '3px solid var(--brand-primary)',
            borderRadius: 'var(--radius-sm)',
            padding: '10px 16px',
            fontSize: 12.5,
            lineHeight: 1.5,
            color: 'var(--text-secondary)',
          }}
        >
          <strong style={{ color: 'var(--text-primary)' }}>Corpus Derivation: </strong>
          Grounded across 2,223 verified customer discussions from Google Play Store, Apple App Store, Reddit, Hacker News, and YouTube teardowns.
        </div>
      </div>

      {/* Executive Key Findings Summary Card */}
      <ExecutiveFindingsCard questionId={qid} data={data} color={meta?.color || '#ff2d55'} />

      {/* Deep-Dive Interactive Visualizations & Analytics */}
      <QuestionSection data={data} questionId={qid} />

      {/* Prev / Next Inquiry Navigation and AI Assistant Deep-Link */}
      <QuestionNavFooter currentId={qid} />
    </div>
  );
}

