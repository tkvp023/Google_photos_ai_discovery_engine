import { Metadata } from 'next';
import {
  getTriageOverview,
  getBucketAFindings,
  getOpportunityRanking,
  getSampleAnswers,
  getSearchTypeAnalysis,
  getConfidenceDistribution,
} from '@/lib/api';
import FindingsContent from '@/components/FindingsContent';

export const metadata: Metadata = {
  title: 'Brief-Relevant Findings | Google Photos AI Discovery Engine',
  description: 'Evidence-grounded discovery findings on why photo retrieval fails when memory is incomplete, triaged into Expression, Interpretation, Evaluation, and Recovery.',
};

export default async function FindingsPage() {
  const [
    corpusOverview,
    bucketA,
    opportunities,
    sampleAnswers,
    searchType,
    confidenceDist,
  ] = await Promise.all([
    getTriageOverview(),
    getBucketAFindings(),
    getOpportunityRanking(),
    getSampleAnswers(),
    getSearchTypeAnalysis(),
    getConfidenceDistribution(),
  ]);

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 100 }}>
      <FindingsContent
        corpus={corpusOverview}
        bucketA={bucketA}
        opportunities={opportunities}
        sampleAnswers={sampleAnswers}
        searchType={searchType}
        confidenceDist={confidenceDist}
      />
    </div>
  );
}
