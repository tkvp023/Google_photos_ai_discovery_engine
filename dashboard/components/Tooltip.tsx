'use client';
import { useState, useRef, useEffect } from 'react';

interface TooltipProps {
  content: string;
  children: React.ReactNode;
  title?: string;
}

export default function Tooltip({ content, children, title }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const containerRef = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsVisible(false);
      }
    }
    if (isVisible) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isVisible]);

  return (
    <span
      ref={containerRef}
      className="inline-tooltip-container"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      onFocus={() => setIsVisible(true)}
      onBlur={() => setIsVisible(false)}
      onClick={() => setIsVisible((v) => !v)}
      tabIndex={0}
      role="button"
      aria-label={title || typeof children === 'string' ? `${children}: ${content}` : content}
      style={{
        position: 'relative',
        display: 'inline-flex',
        alignItems: 'baseline',
        cursor: 'help',
        borderBottom: '1px dashed var(--semantic-blue)',
        paddingBottom: '1px',
      }}
    >
      {children}
      {isVisible && (
        <span
          role="tooltip"
          className="inline-tooltip-bubble"
          style={{
            position: 'absolute',
            bottom: 'calc(100% + 8px)',
            left: '50%',
            transform: 'translateX(-50%)',
            width: 'max-content',
            maxWidth: '280px',
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-strong)',
            borderRadius: 'var(--radius-sm)',
            padding: '8px 12px',
            fontSize: '11.5px',
            lineHeight: '1.45',
            color: 'var(--text-primary)',
            boxShadow: 'var(--shadow-elevated)',
            zIndex: 9999,
            pointerEvents: 'none',
            whiteSpace: 'normal',
            fontWeight: 400,
            textAlign: 'left',
          }}
        >
          {title && (
            <span
              style={{
                display: 'block',
                fontWeight: 700,
                color: 'var(--semantic-blue)',
                marginBottom: '3px',
                fontSize: '11px',
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
              }}
            >
              {title}
            </span>
          )}
          {content}
          <span
            style={{
              position: 'absolute',
              top: '100%',
              left: '50%',
              transform: 'translateX(-50%)',
              borderWidth: '5px',
              borderStyle: 'solid',
              borderColor: 'var(--border-strong) transparent transparent transparent',
              display: 'block',
              width: 0,
              height: 0,
            }}
          />
        </span>
      )}
    </span>
  );
}
