'use client';
import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import dynamic from 'next/dynamic';

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
  { id: 1, phase: 'Memory Gap', short: 'Struggled Photo Types', color: '#818cf8' },
  { id: 2, phase: 'Memory Gap', short: 'Retained Memory Clues', color: '#a78bfa' },
  { id: 3, phase: 'Memory Gap', short: 'Forgotten Metadata', color: '#c084fc' },
  { id: 4, phase: 'Search Breakdown', short: 'Incomplete Query Formulation', color: '#38bdf8' },
  { id: 5, phase: 'Search Breakdown', short: 'Irrelevant Results & False Misses', color: '#22d3ee' },
  { id: 6, phase: 'Library Friction', short: 'Endless Timeline Scrolling', color: '#f472b6' },
  { id: 7, phase: 'Library Friction', short: 'Screenshot & Junk Clutter', color: '#fb923c' },
  { id: 8, phase: 'Library Friction', short: 'Face Recognition Failures', color: '#4ade80' },
  { id: 9, phase: 'Library Friction', short: 'Text & Document Search', color: '#fbbf24' },
  { id: 10, phase: 'Library Friction', short: 'Workarounds & Switching', color: '#f87171' },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [questionsOpen, setQuestionsOpen] = useState(false);
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
  const phases = ['Memory Gap', 'Search Breakdown', 'Library Friction'];
  const phaseColors: Record<string, string> = {
    'Memory Gap': '#a78bfa',
    'Search Breakdown': '#38bdf8',
    'Library Friction': '#fb923c',
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
          Summary
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
            <span>Inquiries</span>
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
                          }}>
                            {q.short}
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
          Gaps
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
        <ThemeControls />
        <div
          className="corpus-status-badge"
          title="Live corpus: 2,223 documents"
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
            color: '#4ade80',
            fontWeight: 600,
            whiteSpace: 'nowrap',
            backdropFilter: 'blur(12px)',
          }}
        >
          <span className="beacon-dot" style={{ width: 6, height: 6 }} />
          2,223 Docs
        </div>
      </div>
    </nav>
  );
}
