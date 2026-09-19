'use client';
import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import dynamic from 'next/dynamic';
import DataDictionaryModal from './DataDictionaryModal';

const ThemeControls = dynamic(() => import('@/components/ThemeControls'), {
  ssr: false,
  loading: () => (
    <div
      style={{ display: 'flex', alignItems: 'center', gap: 8, height: 34, minWidth: 180 }}
      suppressHydrationWarning
    />
  ),
});

const QUESTIONS = [
  { id: 1, phase: 'What users remember', short: 'Photos people struggle to find', color: '#3b82f6', isCoreBrief: true },
  { id: 2, phase: 'What users remember', short: 'What clues users remember', color: '#3b82f6', isCoreBrief: true },
  { id: 3, phase: 'What users remember', short: 'What users forget (dates, tags)', color: '#64748b', isCoreBrief: true },
  { id: 4, phase: 'Where search fails', short: 'Struggling to describe photos', color: '#3b82f6', isCoreBrief: true },
  { id: 5, phase: 'Where search fails', short: 'Wrong results & false misses', color: '#3b82f6', isCoreBrief: false },
  { id: 6, phase: 'Library problems', short: 'Endless timeline scrolling', color: '#64748b', isCoreBrief: true },
  { id: 7, phase: 'Library problems', short: 'Screenshots & meme clutter', color: '#64748b', isCoreBrief: false },
  { id: 8, phase: 'Library problems', short: 'Face & people search issues', color: '#64748b', isCoreBrief: false },
  { id: 9, phase: 'Library problems', short: 'Receipt & document search', color: '#64748b', isCoreBrief: false },
  { id: 10, phase: 'Library problems', short: 'Workarounds & app switching', color: '#64748b', isCoreBrief: true },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [questionsOpen, setQuestionsOpen] = useState(false);
  const [dictionaryOpen, setDictionaryOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const isActive = (href: string) => pathname === href || (href !== '/' && pathname.startsWith(href));

  // Scroll detection for morph effect
  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 30);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleMouseEnter = () => {
    if (timeoutRef.current) { clearTimeout(timeoutRef.current); timeoutRef.current = null; }
    setQuestionsOpen(true);
  };
  const handleMouseLeave = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => setQuestionsOpen(false), 220);
  };
  const closeMenus = () => { setMobileOpen(false); setQuestionsOpen(false); };

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setQuestionsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') setQuestionsOpen(false);
    else if (e.key === 'ArrowDown' && !questionsOpen) setQuestionsOpen(true);
  };

  // Group questions by phase for the mega menu
  const phases = ['What users remember', 'Where search fails', 'Library problems'];
  const phaseColors: Record<string, string> = {
    'What users remember': '#3b82f6',
    'Where search fails': '#3b82f6',
    'Library problems': '#64748b',
  };

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`} role="navigation" aria-label="Main navigation" suppressHydrationWarning>
      {/* Brand */}
      <Link href="/" className="navbar-logo" onClick={closeMenus}>
        <span
          className="navbar-logo-badge"
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            boxShadow: 'var(--shadow-card)',
          }}
          aria-hidden="true"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path d="M12 3C9.24 3 7 5.24 7 8V12H12C14.76 12 17 9.76 17 8C17 5.24 14.76 3 12 3Z" fill="#EA4335" />
            <path d="M21 12C21 9.24 18.76 7 16 7H12V12C12 14.76 14.76 17 17.5 17C20.26 17 21 14.76 21 12Z" fill="#4285F4" />
            <path d="M12 21C14.76 21 17 18.76 17 16V12H12C9.24 12 7 14.24 7 16C7 18.76 9.24 21 12 21Z" fill="#34A853" />
            <path d="M3 12C3 14.76 5.24 17 8 17H12V12C12 9.24 9.24 7 6.5 7C3.74 7 3 9.24 3 12Z" fill="#FBBC05" />
          </svg>
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>Discovery</span>
          <span style={{ color: 'var(--text-muted)', fontWeight: 400, fontSize: 13 }}>Engine</span>
        </span>
      </Link>

      {/* Mobile Hamburger */}
      <button
        className="navbar-hamburger"
        onClick={() => setMobileOpen(!mobileOpen)}
        aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
        aria-expanded={mobileOpen}
      >
        {mobileOpen ? '✕' : '☰'}
      </button>

      {/* Nav Links */}
      <div className={`navbar-nav ${mobileOpen ? 'mobile-open' : ''}`} suppressHydrationWarning>
        <Link href="/" className={`nav-link ${pathname === '/' ? 'active' : ''}`} onClick={closeMenus}>
          Overview
        </Link>

        <Link
          href="/findings"
          className={`nav-link ${isActive('/findings') ? 'active' : ''}`}
          onClick={closeMenus}
          style={{
            fontWeight: 600,
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          <span>Findings</span>
        </Link>

        {/* Inquiry Mega-Menu */}
        <div
          className="nav-dropdown"
          ref={dropdownRef}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          onKeyDown={handleKeyDown}
          suppressHydrationWarning
        >
          <button
            className={`nav-link ${isActive('/questions') ? 'active' : ''}`}
            onClick={(e) => { e.preventDefault(); setQuestionsOpen(prev => !prev); }}
            style={{ cursor: 'pointer' }}
            aria-expanded={questionsOpen}
            aria-haspopup="true"
            id="questions-menu-button"
          >
            <span>Research Questions</span>
            <svg width="9" height="5" viewBox="0 0 9 5" fill="none" style={{
              transition: 'transform 0.2s ease',
              transform: questionsOpen ? 'rotate(180deg)' : 'rotate(0)',
              stroke: 'currentColor', strokeWidth: 1.5, strokeLinecap: 'round', strokeLinejoin: 'round',
            }}>
              <path d="M1 1L4.5 4L8 1" />
            </svg>
          </button>

          {questionsOpen && (
            <div
              id="questions-mega-menu"
              className="nav-dropdown-menu"
              style={{
                display: 'block',
                width: '580px',
                maxWidth: 'calc(100vw - 32px)',
                padding: '12px',
                background: 'var(--dropdown-bg)',
                border: '1px solid var(--border-strong)',
                borderRadius: 'var(--radius-lg)',
                backdropFilter: 'var(--glass-blur)',
                WebkitBackdropFilter: 'var(--glass-blur)',
                position: 'absolute',
                top: '100%',
                left: 0,
                marginTop: '10px',
                zIndex: 300,
                boxShadow: 'var(--shadow-elevated)',
                animation: 'fadeSlideUp 0.18s cubic-bezier(0.16, 1, 0.3, 1)',
              }}
              role="menu"
            >
              {phases.map((phase) => (
                <div key={phase} style={{ marginBottom: 8 }}>
                  <div style={{
                    fontSize: 10, fontWeight: 700, textTransform: 'uppercase',
                    letterSpacing: '0.1em', color: phaseColors[phase],
                    padding: '4px 8px 6px',
                  }}>
                    {phase}
                  </div>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                    gap: 3,
                  }}>
                    {QUESTIONS.filter(q => q.phase === phase).map((q) => {
                      const isCurrent = pathname === `/questions/${q.id}`;
                      return (
                        <Link
                          key={q.id}
                          href={`/questions/${q.id}`}
                          className="question-nav-item"
                          onClick={closeMenus}
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 10,
                            padding: '8px 10px',
                            borderRadius: 'var(--radius-sm)',
                            background: isCurrent ? 'var(--theme-accent-bg)' : 'transparent',
                            border: isCurrent ? '1px solid var(--theme-accent-border)' : '1px solid transparent',
                            textDecoration: 'none',
                            cursor: 'pointer',
                          }}
                          role="menuitem"
                        >
                          <span style={{
                            color: isCurrent ? '#fff' : q.color,
                            fontWeight: 700,
                            fontSize: 10.5,
                            background: isCurrent ? q.color : `${q.color}18`,
                            border: `1px solid ${q.color}40`,
                            padding: '2px 7px',
                            borderRadius: 6,
                            minWidth: 28,
                            textAlign: 'center',
                            flexShrink: 0,
                            fontFamily: "'Space Grotesk', sans-serif",
                          }}>
                            Q{q.id}
                          </span>
                          <span style={{
                            fontWeight: 500,
                            fontSize: 12.5,
                            color: isCurrent ? 'var(--brand-primary)' : 'var(--text-primary)',
                            lineHeight: 1.3,
                            display: 'flex',
                            alignItems: 'center',
                            gap: 6,
                          }}>
                            <span>{q.short}</span>
                            {q.isCoreBrief && (
                              <span
                                style={{
                                  fontSize: 9.5,
                                  background: 'rgba(59, 130, 246, 0.12)',
                                  color: 'var(--semantic-blue)',
                                  border: '1px solid rgba(59, 130, 246, 0.3)',
                                  padding: '1px 5px',
                                  borderRadius: 4,
                                  fontWeight: 700,
                                }}
                              >
                                Core
                              </span>
                            )}
                          </span>
                        </Link>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <Link href="/gaps" className={`nav-link ${isActive('/gaps') ? 'active' : ''}`} onClick={closeMenus}>
          Gap Analysis
        </Link>

        <Link
          href="/ask"
          className={`nav-link ${isActive('/ask') ? 'active' : ''}`}
          onClick={closeMenus}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 5,
            padding: '5px 12px',
            borderRadius: 'var(--radius-md)',
            border: isActive('/ask') ? '1px solid var(--theme-accent-border)' : '1px solid var(--border)',
            background: isActive('/ask') ? 'var(--theme-accent-bg)' : 'rgba(255, 255, 255, 0.03)',
            color: isActive('/ask') ? 'var(--brand-primary)' : 'var(--text-secondary)',
            fontWeight: 500,
            fontSize: 13,
            transition: 'all 0.2s ease',
          }}
          aria-label="Ask AI"
        >
          <span style={{ fontSize: 11, color: 'var(--brand-primary)', opacity: 0.85 }} aria-hidden="true">✦</span>
          <span>Ask AI</span>
        </Link>
      </div>

      {/* Right Controls */}
      <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 10 }} suppressHydrationWarning>
        <button
          type="button"
          onClick={() => setDictionaryOpen(true)}
          title="View plain-language terminology reference"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 5,
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            color: 'var(--text-secondary)',
            borderRadius: 16,
            padding: '4px 12px',
            fontSize: 11.5,
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.15s ease',
            backdropFilter: 'blur(12px)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = 'var(--brand-primary)';
            e.currentTarget.style.color = 'var(--brand-primary)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = 'var(--border)';
            e.currentTarget.style.color = 'var(--text-secondary)';
          }}
        >
          <span>Terminology</span>
        </button>

        <ThemeControls />
        <div
          className="corpus-status-badge"
          title="Analyzed corpus: 2,223 reviews"
          suppressHydrationWarning
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 20,
            padding: '4px 12px',
            fontSize: 11.5,
            color: 'var(--semantic-green)',
            fontWeight: 600,
            whiteSpace: 'nowrap',
            backdropFilter: 'blur(12px)',
          }}
        >
          <span className="beacon-dot" style={{ width: 6, height: 6 }} />
          2,223 Reviews
        </div>
      </div>

      {/* Global Data Dictionary Modal */}
      <DataDictionaryModal isOpen={dictionaryOpen} onClose={() => setDictionaryOpen(false)} />
    </nav>
  );
}
