'use client';

import { useEffect, useState } from 'react';

interface Pillar {
  heavenlyStem: string;
  earthlyBranch: string;
  heavenlyStemHanja: string;
  earthlyBranchHanja: string;
  element: string;
  yinYang: string;
}

interface SajupaeProps {
  pillars: {
    year: Pillar;
    month: Pillar;
    day: Pillar;
    time: Pillar;
  };
  animated?: boolean;
}

const PILLAR_LABELS = ['년주', '월주', '일주', '시주'] as const;
const PILLAR_KEYS = ['year', 'month', 'day', 'time'] as const;
const PILLAR_COLORS = [
  'var(--color-ink)',
  'var(--color-jujube-soft)',
  'var(--color-indigo)',
  'var(--color-gold)',
] as const;

export function Sajupae({ pillars, animated = true }: SajupaeProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (animated) {
      const timer = setTimeout(() => setVisible(true), 100);
      return () => clearTimeout(timer);
    } else {
      setVisible(true);
    }
  }, [animated]);

  const pillarData = PILLAR_KEYS.map((key, idx) => ({
    label: PILLAR_LABELS[idx],
    ...pillars[key as keyof typeof pillars],
    color: PILLAR_COLORS[idx],
    delay: idx * 120,
  }));

  return (
    <div
      className="sajupae"
      role="img"
      aria-label={`사주��자: ${pillarData.map(p => `${p.label} ${p.heavenlyStem}${p.earthlyBranch}`).join(', ')}`}
      style={{
        position: 'relative',
        height: '480px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <div
        className="pillars"
        style={{
          display: 'flex',
          gap: 'var(--space-4)',
          opacity: visible ? 1 : 0,
          transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'opacity 0.8s ease, transform 0.8s cubic-bezier(0.25, 0.8, 0.25, 1)',
        }}
      >
        {pillarData.map((pillar, idx) => (
          <div
            key={pillar.label}
            className="pillar"
            style={{
              width: '78px',
              height: '380px',
              background: 'var(--color-bg-card)',
              border: '1px solid var(--color-line)',
              borderRadius: 'var(--radius-md)',
              boxShadow: 'var(--shadow-lg)',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              padding: 'var(--space-5) 0',
              position: 'relative',
              opacity: visible ? 1 : 0,
              transform: visible ? `translateY(${[-10, -22, -30, -16][idx]}px)` : 'translateY(40px)',
              transition: `opacity 0.8s ease ${pillar.delay}ms, transform 0.8s cubic-bezier(0.25, 0.8, 0.25, 1) ${pillar.delay}ms`,
            }}
          >
            <span
              className="label"
              style={{
                fontSize: 'var(--fs-xs)',
                color: 'var(--color-ink-soft)',
                letterSpacing: '0.1em',
                marginBottom: 'var(--space-5)',
                fontWeight: 600,
              }}
            >
              {pillar.label}
            </span>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--space-2)' }}>
              <span
                className="glyph serif"
                style={{
                  fontSize: '36px',
                  fontWeight: 700,
                  color: pillar.color,
                  lineHeight: 1.2,
                  textShadow: `0 0 20px ${pillar.color}33`,
                }}
              >
                {pillar.heavenlyStemHanja}
              </span>
              <span
                className="glyph serif"
                style={{
                  fontSize: '36px',
                  fontWeight: 700,
                  color: pillar.color,
                  lineHeight: 1.2,
                  textShadow: `0 0 20px ${pillar.color}33`,
                }}
              >
                {pillar.earthlyBranchHanja}
              </span>
            </div>

            <div
              style={{
                marginTop: 'auto',
                paddingTop: 'var(--space-4)',
                borderTop: '1px solid var(--color-line)',
                width: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 'var(--space-1)',
              }}
            >
              <span
                style={{
                  fontSize: 'var(--fs-xs)',
                  color: 'var(--color-ink-soft)',
                  opacity: 0.7,
                }}
              >
                {pillar.yinYang} · {pillar.element}
              </span>
              <span
                style={{
                  fontSize: 'var(--fs-xs)',
                  color: 'var(--color-ink-soft)',
                  opacity: 0.7,
                }}
              >
                {pillar.heavenlyStem} {pillar.earthlyBranch}
              </span>
            </div>
          </div>
        ))}
      </div>

      <p
        className="sajupae-caption"
        style={{
          position: 'absolute',
          bottom: '-var(--space-6)',
          left: '50%',
          transform: 'translateX(-50%)',
          fontSize: 'var(--fs-sm)',
          color: 'var(--color-ink-soft)',
          textAlign: 'center',
          width: '100%',
          opacity: visible ? 1 : 0,
          transition: 'opacity 0.8s ease 0.6s',
        }}
      >
        네 기둥 여�� 글자, 당신의 고유한 운명의 지도
      </p>
    </div>
  );
}