'use client';

import { useState } from 'react';
import type { TarotCard } from '@/lib/taro';

interface TarotCardProps {
  card: TarotCard;
  reversed?: boolean;
  index?: number;
  onClick?: () => void;
  disabled?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const CARD_SIZES = {
  small: { width: '80px', height: '120px', fontSize: '10px' },
  medium: { width: '110px', height: '165px', fontSize: '11px' },
  large: { width: '140px', height: '210px', fontSize: '12px' },
};

export function TarotCard({ card, reversed = false, index = 0, onClick, disabled = false, size = 'medium' }: TarotCardProps) {
  const [flipped, setFlipped] = useState(false);
  const dimensions = CARD_SIZES[size];

  const handleClick = () => {
    if (!disabled && onClick) onClick();
    if (!disabled) setFlipped(f => !f);
  };

  const rotation = reversed ? 180 : 0;
  const flipRotation = flipped ? 180 : 0;

  return (
    <div
      className="tarot-card"
      onClick={handleClick}
      style={{
        width: dimensions.width,
        height: dimensions.height,
        perspective: '1200px',
        cursor: disabled ? 'default' : 'pointer',
        filter: 'drop-shadow(0 12px 28px rgba(0,0,0,0.6))',
        transformStyle: 'preserve-3d',
        transition: 'transform 0.8s cubic-bezier(0.2,0.6,0.3,1.1), filter 0.4s',
        opacity: disabled ? 0.5 : 1,
      }}
      role="button"
      tabIndex={disabled ? -1 : 0}
      onKeyDown={e => (e.key === 'Enter' || e.key === ' ') && handleClick()}
      aria-label={flipped ? `${card.name} ${reversed ? '(역방향)' : '(정방향)'}, 상세 보기` : `${card.name} ${reversed ? '(역방향)' : '(정방향)'}, 클릭하여 열기`}
    >
      <div
        style={{
          position: 'relative',
          width: '100%',
          height: '100%',
          transformStyle: 'preserve-3d',
          transition: 'transform 0.8s cubic-bezier(0.2,0.6,0.3,1.1)',
          transform: `rotateY(${flipRotation}deg) rotateZ(${rotation}deg)`,
        }}
      >
        {/* Front */}
        <div style={{
          position: 'absolute',
          inset: 0,
          backfaceVisibility: 'hidden',
          borderRadius: '12px',
          background: flipped ? 'transparent' : 'linear-gradient(145deg, #1a1410 0%, #0d0805 100%)',
          border: '1px solid rgba(184,148,60,0.15)',
          boxShadow: 'inset 0 2px 4px rgba(184,148,60,0.1), inset 0 -2px 4px rgba(0,0,0,0.3)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}>
          {/* Card number */}
          <div style={{
            position: 'absolute',
            top: '8px',
            left: '8px',
            right: '8px',
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: dimensions.fontSize,
            fontWeight: 700,
            color: '#b8943c',
            fontFamily: 'Noto Serif KR, serif',
            pointerEvents: 'none',
          }}>
            <span>{card.arcana === 'major' ? '0' : card.number}</span>
            <span>{card.arcana === 'major' ? '0' : card.number}</span>
          </div>

          {/* Card artwork area */}
          <div style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '16px',
            position: 'relative',
          }}>
            {/* Arcana symbol */}
            <div style={{
              width: size === 'large' ? '70px' : size === 'medium' ? '55px' : '40px',
              height: size === 'large' ? '70px' : size === 'medium' ? '55px' : '40px',
              borderRadius: '50%',
              background: 'radial-gradient(circle at 30% 30%, rgba(184,148,60,0.2), transparent 70%), rgba(10,10,10,0.8)',
              border: '1px solid rgba(184,148,60,0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '12px',
              boxShadow: '0 4px 16px rgba(0,0,0,0.4), inset 0 1px 0 rgba(184,148,60,0.1)',
            }}>
              <span style={{
                fontSize: size === 'large' ? '28px' : size === 'medium' ? '22px' : '16px',
                filter: 'drop-shadow(0 0 8px rgba(184,148,60,0.6))',
              }}>
                {card.arcana === 'major' ? '���' : '◆'}
              </span>
            </div>

            {/* Card name */}
            <h3 style={{
              fontSize: size === 'large' ? '14px' : size === 'medium' ? '12px' : '10px',
              fontWeight: 700,
              color: '#f0ebe5',
              textAlign: 'center',
              lineHeight: 1.3,
              marginBottom: '4px',
              fontFamily: 'Noto Serif KR, serif',
            }}>
              {card.name}
            </h3>
            <span style={{
              fontSize: size === 'large' ? '9px' : '8px',
              color: '#b8943c',
              textTransform: 'uppercase',
              letterSpacing: '0.08em',
              fontWeight: 500,
            }}>
              {card.nameEn}
            </span>
          </div>

          {/* Bottom number */}
          <div style={{
            position: 'absolute',
            bottom: '8px',
            left: '8px',
            right: '8px',
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: dimensions.fontSize,
            fontWeight: 700,
            color: '#b8943c',
            fontFamily: 'Noto Serif KR, serif',
            transform: 'rotate(180deg)',
            pointerEvents: 'none',
          }}>
            <span>{card.arcana === 'major' ? '0' : card.number}</span>
            <span>{card.arcana === 'major' ? '0' : card.number}</span>
          </div>
        </div>

        {/* Back */}
        <div style={{
          position: 'absolute',
          inset: 0,
          backfaceVisibility: 'hidden',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, #0a0a0f 0%, #1a1410 100%)',
          border: '1px solid rgba(184,148,60,0.25)',
          boxShadow: 'inset 0 2px 4px rgba(184,148,60,0.08), inset 0 -2px 4px rgba(0,0,0,0.3)',
          transform: 'rotateY(180deg)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '16px',
          overflow: 'hidden',
        }}>
          {/* Card back pattern */}
          <div style={{
            position: 'absolute',
            inset: 0,
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cdefs%3E%3Cpattern id='grid' width='20' height='20' patternUnits='userSpaceOnUse'%3E%3Cpath d='M 20 0 L 0 0 0 20' fill='none' stroke='%23b8943c' stroke-width='0.5' opacity='0.08'/%3E%3C/pattern%3E%3C/defs%3E%3Crect width='100%25' height='100%25' fill='url(%23grid)'/%3E%3C/svg%3E")`,
            backgroundSize: '20px',
            opacity: 0.5,
          }} />

          <div style={{
            position: 'relative',
            zIndex: 1,
            textAlign: 'center',
          }}>
            <div style={{
              width: size === 'large' ? '80px' : size === 'medium' ? '65px' : '50px',
              height: size === 'large' ? '80px' : size === 'medium' ? '65px' : '50px',
              borderRadius: '50%',
              background: 'radial-gradient(circle at 30% 30%, rgba(184,148,60,0.3), rgba(10,10,10,0.9) 70%)',
              border: '2px solid rgba(184,148,60,0.4)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '12px',
              boxShadow: '0 0 32px rgba(184,148,60,0.2), inset 0 2px 4px rgba(184,148,60,0.1)',
            }}>
              <span style={{
                fontSize: size === 'large' ? '32px' : size === 'medium' ? '26px' : '20px',
              }}>���</span>
            </div>
            <p style={{
              fontSize: size === 'large' ? '11px' : '10px',
              color: '#b8943c',
              fontWeight: 600,
              letterSpacing: '0.12em',
              textTransform: 'uppercase',
              fontFamily: 'Noto Serif KR, serif',
            }}>
              TAROT
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export function TarotCardDetail({ card, reversed = false, onClose }: { card: TarotCard; reversed?: boolean; onClose: () => void }) {
  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 100,
        background: 'rgba(0,0,0,0.85)',
        backdropFilter: 'blur(8px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
        animation: 'fadeIn 0.2s ease',
      }}
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="tarot-detail-title"
    >
      <div
        style={{
          width: '100%',
          maxWidth: '480px',
          maxHeight: '90vh',
          overflow: 'auto',
          background: 'linear-gradient(145deg, #1a1410 0%, #0d0805 100%)',
          border: '1px solid rgba(184,148,60,0.2)',
          borderRadius: '20px',
          boxShadow: '0 32px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(184,148,60,0.1)',
          animation: 'slideUp 0.3s cubic-bezier(0.2,0.6,0.3,1.1)',
        }}
        onClick={e => e.stopPropagation()}
      >
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          padding: '20px 24px 0',
        }}>
          <div>
            <span style={{
              fontSize: '11px',
              color: '#b8943c',
              fontWeight: 600,
              letterSpacing: '0.08em',
              textTransform: 'uppercase',
            }}>
              {card.arcana === 'major' ? '메이저 아르카나' : `마이너 · ${card.suit === 'wands' ? '완드' : card.suit === 'cups' ? '컵' : card.suit === 'swords' ? '소드' : '��타클'}`}
            </span>
            <h2 id="tarot-detail-title" style={{
              fontSize: '22px',
              fontWeight: 700,
              color: '#f0ebe5',
              marginTop: '4px',
              fontFamily: 'Noto Serif KR, serif',
            }}>
              {card.name} {reversed && <span style={{ color: '#b8943c', fontSize: '14px', fontWeight: 500 }}>(역방향)</span>}
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              background: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(184,148,60,0.15)',
              color: '#b8943c',
              fontSize: '18px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s',
            }}
            aria-label="닫기"
          >
            ��
          </button>
        </div>

        <div style={{ padding: '24px' }}>
          {/* Keywords */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '20px' }}>
            {card.keywords.map((kw, i) => (
              <span key={i} style={{
                fontSize: '12px',
                color: '#b8943c',
                background: 'rgba(184,148,60,0.1)',
                padding: '4px 12px',
                borderRadius: '9999px',
                fontWeight: 500,
              }}>
                {kw}
              </span>
            ))}
          </div>

          {/* Meaning */}
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '13px', fontWeight: 700, color: '#b8943c', marginBottom: '8px', letterSpacing: '0.04em' }}>
              {reversed ? '역방향 의미' : '정방향 의미'}
            </h3>
            <p style={{ fontSize: '14px', lineHeight: 1.7, color: '#c4bfb8' }}>
              {reversed ? card.meaningReversed : card.meaningUpright}
            </p>
          </div>

          {/* Description */}
          <div style={{ paddingTop: '16px', borderTop: '1px solid rgba(184,148,60,0.1)' }}>
            <h3 style={{ fontSize: '13px', fontWeight: 700, color: '#b8943c', marginBottom: '8px', letterSpacing: '0.04em' }}>
              해설
            </h3>
            <p style={{ fontSize: '14px', lineHeight: 1.7, color: '#c4bfb8' }}>
              {card.description}
            </p>
          </div>
        </div>
      </div>

      <style jsx global>{`
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
      `}</style>
    </div>
  );
}