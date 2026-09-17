import { Suspense } from 'react';
import AskContent from '@/components/AskContent';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'AI RAG Chatbot | Episodic Memory Discovery Engine',
  description: 'Natural-language RAG intelligence grounded across 2,223 verified customer conversations (Google Play Store, Apple App Store, Reddit, Hacker News, YouTube) with quote-level evidence and multi-source citations.',
};

export default function AskPage() {
  return (
    <Suspense
      fallback={
        <div className="container" style={{ paddingTop: 64, textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 10, color: 'var(--brand-primary)', fontWeight: 600 }}>
            <span style={{ fontSize: 18 }}>✦</span>
            <span>Initializing Grounded AI RAG Chatbot...</span>
          </div>
        </div>
      }
    >
      <AskContent />
    </Suspense>
  );
}
