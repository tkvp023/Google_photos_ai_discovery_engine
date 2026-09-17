/**
 * Formats tags, codes, and identifiers into clean, polished human labels.
 * Strips underscores, handles acronyms (OCR, AI, UI, GPS, ML),
 * and standardizes conjunctions and prepositions.
 */
export function formatLabel(str?: string | null): string {
  if (!str) return '';
  if (!str.includes('_')) return str;

  const ACRONYMS: Record<string, string> = {
    ocr: 'OCR',
    ai: 'AI',
    ui: 'UI',
    ml: 'ML',
    gps: 'GPS',
    id: 'ID',
    kpi: 'KPI',
  };

  const LOWER_WORDS = new Set(['and', 'or', 'for', 'in', 'of', 'to', 'by', 'with', 'a', 'an', 'the']);

  return str
    .split('_')
    .filter(Boolean)
    .map((word, idx) => {
      const lower = word.toLowerCase();
      if (ACRONYMS[lower]) return ACRONYMS[lower];
      if (lower === 'and') return '&';
      if (idx > 0 && LOWER_WORDS.has(lower)) return lower;
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    })
    .join(' ');
}
