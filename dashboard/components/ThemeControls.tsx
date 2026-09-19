'use client';
import { useEffect, useState, useSyncExternalStore } from 'react';

type Mode = 'dark' | 'light';
export type Theme = 'midnight-observatory' | 'polar-aurora' | 'volcanic-ember' | 'deep-ocean' | 'noir-film' | 'sunrise-warm';

export const THEMES: {
  id: Theme;
  name: string;
  icon: string;
  preview: string;
}[] = [
  { id: 'midnight-observatory', name: 'Midnight Observatory', icon: '🔭', preview: 'linear-gradient(135deg, #818cf8, #38bdf8, #2dd4bf)' },
  { id: 'polar-aurora',        name: 'Polar Aurora',         icon: '❄️', preview: 'linear-gradient(135deg, #22d3ee, #a78bfa, #6366f1)' },
  { id: 'volcanic-ember',      name: 'Volcanic Ember',       icon: '🌋', preview: 'linear-gradient(135deg, #f97316, #ef4444, #fbbf24)' },
  { id: 'deep-ocean',          name: 'Deep Ocean',           icon: '🌊', preview: 'linear-gradient(135deg, #2dd4bf, #22d3ee, #7dd3fc)' },
  { id: 'noir-film',           name: 'Noir Film',            icon: '🎬', preview: 'linear-gradient(135deg, #e2e8f0, #94a3b8, #64748b)' },
  { id: 'sunrise-warm',        name: 'Sunrise Warm',         icon: '🌅', preview: 'linear-gradient(135deg, #fbbf24, #f59e0b, #ea580c)' },
];

export default function ThemeControls() {
  const mounted = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false
  );

  const [mode, setMode] = useState<Mode>(() => {
    if (typeof window === 'undefined') return 'dark';
    return (document.documentElement.getAttribute('data-mode') as Mode) ||
      (localStorage.getItem('app-mode') as Mode) || 'dark';
  });

  const [theme, setTheme] = useState<Theme>(() => {
    if (typeof window === 'undefined') return 'midnight-observatory';
    let initialTheme = (document.documentElement.getAttribute('data-theme') as string) ||
      localStorage.getItem('app-theme') || 'midnight-observatory';
    const remap: Record<string, Theme> = {
      'google-lens': 'midnight-observatory', 'tokyo-sakura': 'midnight-observatory', 'sunset': 'midnight-observatory',
      'darkroom': 'sunrise-warm', 'cosmic-nebula': 'sunrise-warm',
      'nordic-gallery': 'deep-ocean', 'cyber-matrix': 'deep-ocean', 'cyber': 'deep-ocean', 'emerald': 'deep-ocean',
      'warm-studio': 'volcanic-ember', 'solar-flare': 'volcanic-ember',
    };
    if (remap[initialTheme]) initialTheme = remap[initialTheme];
    return initialTheme as Theme;
  });

  const [density, setDensity] = useState<'analytical' | 'focus'>(() => {
    if (typeof window === 'undefined') return 'analytical';
    return (localStorage.getItem('app-density') as 'analytical' | 'focus') || 'analytical';
  });
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute('data-mode', mode);
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.setAttribute('data-view-density', density);
  }, [mode, theme, density]);

  const toggleMode = () => {
    const nextMode: Mode = mode === 'dark' ? 'light' : 'dark';
    setMode(nextMode);
    document.documentElement.setAttribute('data-mode', nextMode);
    localStorage.setItem('app-mode', nextMode);
    window.dispatchEvent(new Event('theme-change'));
  };

  const selectTheme = (newTheme: Theme) => {
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('app-theme', newTheme);
    window.dispatchEvent(new Event('theme-change'));
    setExpanded(false);
  };

  const toggleDensity = () => {
    const nextDensity = density === 'analytical' ? 'focus' : 'analytical';
    setDensity(nextDensity);
    document.documentElement.setAttribute('data-view-density', nextDensity);
    localStorage.setItem('app-density', nextDensity);
    window.dispatchEvent(new CustomEvent('density-change', { detail: nextDensity }));
  };

  if (!mounted) {
    return (
      <div
        style={{ display: 'flex', alignItems: 'center', gap: 8, height: 34, minWidth: 180 }}
        suppressHydrationWarning
      />
    );
  }

  const currentTheme = THEMES.find(t => t.id === theme) || THEMES[0];

  return (
    <div
      className="theme-controls-wrapper"
      suppressHydrationWarning
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        position: 'relative',
      }}
    >
      {/* Active theme button — click to expand */}
      <button
        onClick={() => setExpanded(!expanded)}
        title={`Theme: ${currentTheme.name}`}
        aria-label="Open theme selector"
        aria-expanded={expanded}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 7,
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: 20,
          padding: '4px 12px 4px 5px',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          backdropFilter: 'blur(12px)',
        }}
      >
        <span
          style={{
            width: 22, height: 22,
            borderRadius: '50%',
            background: currentTheme.preview,
            border: '2px solid var(--border-strong)',
            flexShrink: 0,
          }}
        />
        <span style={{ fontSize: 11.5, fontWeight: 600, color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
          {currentTheme.name}
        </span>
        <svg width="8" height="5" viewBox="0 0 8 5" fill="none" style={{
          transform: expanded ? 'rotate(180deg)' : 'rotate(0)',
          transition: 'transform 0.2s ease',
          stroke: 'var(--text-muted)', strokeWidth: 1.5, strokeLinecap: 'round', strokeLinejoin: 'round',
        }}>
          <path d="M1 1L4 4L7 1" />
        </svg>
      </button>

      {/* Theme picker dropdown */}
      {expanded && (
        <div
          style={{
            position: 'absolute',
            top: 'calc(100% + 8px)',
            right: 0,
            background: 'var(--dropdown-bg)',
            border: '1px solid var(--border-strong)',
            borderRadius: 'var(--radius-lg)',
            backdropFilter: 'var(--glass-blur)',
            WebkitBackdropFilter: 'var(--glass-blur)',
            padding: 8,
            width: 240,
            zIndex: 400,
            boxShadow: 'var(--shadow-elevated)',
            animation: 'fadeSlideUp 0.15s cubic-bezier(0.16, 1, 0.3, 1)',
          }}
        >
          <div style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-muted)', padding: '4px 8px 8px', borderBottom: '1px solid var(--border)', marginBottom: 4 }}>
            Choose Theme
          </div>
          {THEMES.map((t) => {
            const isActive = theme === t.id;
            return (
              <button
                key={t.id}
                onClick={() => selectTheme(t.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  width: '100%',
                  padding: '8px 10px',
                  borderRadius: 'var(--radius-sm)',
                  background: isActive ? 'var(--theme-accent-bg)' : 'transparent',
                  border: isActive ? '1px solid var(--theme-accent-border)' : '1px solid transparent',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  textAlign: 'left',
                }}
              >
                <span style={{
                  width: 28, height: 28,
                  borderRadius: 8,
                  background: t.preview,
                  flexShrink: 0,
                  border: isActive ? '2px solid var(--brand-primary)' : '1px solid var(--border)',
                  boxShadow: isActive ? '0 0 12px var(--card-glow-color)' : 'none',
                }} />
                <div>
                  <div style={{ fontSize: 12.5, fontWeight: 600, color: isActive ? 'var(--brand-primary)' : 'var(--text-primary)' }}>
                    {t.icon} {t.name}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}

      <div style={{ width: 1, height: 18, background: 'var(--border)', margin: '0 2px' }} />

      {/* Focus / Full toggle */}
      <button
        onClick={toggleDensity}
        title={density === 'focus' ? 'Focus View — Click for Full View' : 'Full View — Click for Focus View'}
        aria-label="Toggle density"
        style={{
          background: density === 'focus' ? 'var(--theme-accent-bg)' : 'transparent',
          border: density === 'focus' ? '1px solid var(--theme-accent-border)' : '1px solid transparent',
          borderRadius: 14,
          padding: '3px 10px',
          fontSize: 11,
          fontWeight: 600,
          color: density === 'focus' ? 'var(--brand-primary)' : 'var(--text-muted)',
          cursor: 'pointer',
          transition: 'all 0.15s ease',
        }}
      >
        {density === 'focus' ? '🎯 Focus' : '📊 Full'}
      </button>

      <div style={{ width: 1, height: 18, background: 'var(--border)', margin: '0 2px' }} />

      {/* Light/Dark mode */}
      <button
        onClick={toggleMode}
        title={mode === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        aria-label={`Switch to ${mode === 'dark' ? 'Light' : 'Dark'} mode`}
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: 28, height: 28,
          borderRadius: '50%',
          color: 'var(--text-primary)',
          transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
          fontSize: 14,
        }}
        onMouseEnter={(e) => { e.currentTarget.style.transform = 'rotate(20deg) scale(1.15)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.transform = 'rotate(0deg) scale(1)'; }}
      >
        {mode === 'dark' ? '🌙' : '☀️'}
      </button>
    </div>
  );
}
