'use client';

import { useState, useEffect, useCallback } from 'react';
import { Navigation } from '@/components/Navigation';
import { Footer } from '@/components/Footer';
import { TarotCard, TarotCardDetail } from '@/components/TarotCard';
import { TAROT_CARDS, SPREADS, getRandomCards, type SpreadType, type TarotCard as TarotCardType } from '@/lib/taro';

export default function TaroPage() {
  const [mounted, setMounted] = useState(false);
  const [spread, setSpread] = useState<SpreadType>('three');
  const [drawnCards, setDrawnCards] = useState<{ card: TarotCardType; reversed: boolean }[]>([]);
  const [selectedCard, setSelectedCard] = useState<{ card: TarotCardType; reversed: boolean } | null>(null);
  const [animating, setAnimating] = useState(false);

  useEffect(() => setMounted(true), []);

  const drawCards = useCallback(() => {
    setAnimating(true);
    const count = SPREADS[spread].count;

    // Staggered animation
    setTimeout(() => {
      const cards = getRandomCards(count);
      setDrawnCards(cards);
      setAnimating(false);
    }, 300);
  }, [spread]);

  useEffect(() => {
    drawCards();
  }, [drawCards]);

  const handleCardClick = (card: TarotCardType, reversed: boolean) => {
    setSelectedCard({ card, reversed });
  };

  const spreadLabels: Record<SpreadType, string> = {
    one: '원카드',
    three: '쓰리카드',
    celtic: '���� 크로스',
  };

  const spreadDescriptions: Record<SpreadType, string> = {
    one: '간단한 질문, 하루 운세',
    three: '과거 · 현재 · 미래',
    celtic: '종합적 상황 분석',
  };

  if (!mounted) {
    return (
      <div style={{ paddingTop: 'var(--nav-height)' }}>
        <div className="container" style={{ padding: 'var(--space-20) 0', textAlign: 'center' }}>
          <p style={{ color: 'var(--color-ink-soft)' }}>불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Navigation />

      {/* ── Hero ── */}
      <section className="hero" style={{ minHeight: '70vh', display: 'flex', alignItems: 'center', paddingTop: 'var(--nav-height)', textAlign: 'center' }}>
        <div className="container">
          <h1 className="serif" style={{ fontSize: 'var(--fs-5xl)', fontWeight: 900, letterSpacing: '-0.02em', lineHeight: 1.3, marginBottom: 'var(--space-3)' }}>
            <em style={{ fontStyle: 'normal', color: 'var(--color-gold)' }}>타로</em> 리딩
          </h1>
          <p style={{ fontSize: 'var(--fs-lg)', color: 'var(--color-ink-soft)', fontWeight: 300, letterSpacing: '0.08em' }}>
            카드가 전하는 오늘의 메시지
          </p>
        </div>
      </section>

      {/* ── Spread Selector ── */}
      <section className="section" style={{ background: 'var(--color-bg-deep)' }}>
        <div className="container" style={{ maxWidth: '600px' }}>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '0', marginBottom: 'var(--space-10)' }} role="tablist" aria-label="스프레드 선택">
            {(Object.keys(SPREADS) as SpreadType[]).map((s, idx) => (
              <button
                key={s}
                role="tab"
                aria-selected={spread === s}
                aria-controls={`panel-${s}`}
                id={`tab-${s}`}
                onClick={() => setSpread(s)}
                className={`spread-btn ${spread === s ? 'active' : ''}`}
                style={{
                  padding: 'var(--space-3) var(--space-7)',
                  border: `1px solid ${spread === s ? 'rgba(184,148,60,0.3)' : 'rgba(184,148,60,0.12)'}`,
                  background: spread === s ? 'rgba(184,148,60,0.08)' : 'transparent',
                  color: spread === s ? 'var(--color-gold)' : 'var(--color-ink-soft)',
                  fontSize: 'var(--fs-sm)',
                  fontWeight: 500,
                  cursor: 'pointer',
                  fontFamily: 'inherit',
                  letterSpacing: '0.04em',
                  transition: 'all 0.4s',
                  borderRadius: idx === 0 ? 'var(--radius-md) 0 0 var(--radius-md)' : idx === 2 ? '0 var(--radius-md) var(--radius-md) 0' : 0,
                  borderRight: idx !== 2 ? 'none' : undefined,
                }}
              >
                {SPREADS[s].name}
              </button>
            ))}
          </div>

          <div style={{ textAlign: 'center', marginBottom: 'var(--space-8)' }}>
            <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--color-ink-muted)' }}>
              {spreadDescriptions[spread]}
            </p>
          </div>

          {/* ── Cards ── */}
          <div style={{ position: 'relative', minHeight: '320px' }} role="tabpanel" id={`panel-${spread}`} aria-labelledby={`tab-${spread}`}>
            {/* Table surface */}
            <div style={{
              position: 'absolute',
              bottom: 0,
              left: '50%',
              transform: 'translateX(-50%)',
              width: '88%',
              maxWidth: '720px',
              height: '160px',
              borderRadius: '0 0 var(--radius-md) var(--radius-md)',
              background: 'radial-gradient(ellipse at 50% 0%, rgba(25,18,10,0.7), rgba(12,8,4,0.95))',
              boxShadow: '0 -30px 80px rgba(0,0,0,0.5) inset, 0 0 0 1px rgba(184,148,60,0.04)',
            }}>
              <div style={{
                position: 'absolute',
                inset: 0,
                background: 'radial-gradient(ellipse at 50% 0%, rgba(184,148,60,0.03) 0, transparent 70%)',
                borderRadius: 'inherit',
              }} />
            </div>

            {/* Cards */}
            <div style={{
              display: 'flex',
              perspective: '1200px',
              justifyContent: 'center',
              alignItems: 'flex-end',
              gap: spread === 'celtic' ? 'var(--space-2)' : 'var(--space-4)',
              position: 'relative',
              zIndex: 2,
              paddingBottom: '16px',
              flexWrap: 'wrap',
            }}>
              {drawnCards.map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    transform: `rotate(${spread === 'three' ? [-4, -1.5, 1.5][idx] : 0}deg) translateY(${spread === 'three' ? [2, -2, -2][idx] : 0}px)`,
                    opacity: animating ? 0 : 1,
                    transition: 'opacity 0.3s ease, transform 0.8s cubic-bezier(0.2,0.6,0.3,1.1)',
                  }}
                >
                  <TarotCard
                    card={item.card}
                    reversed={item.reversed}
                    index={idx}
                    onClick={() => handleCardClick(item.card, item.reversed)}
                    disabled={animating}
                    size={spread === 'celtic' ? 'small' : 'medium'}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Redraw button */}
          <div style={{ textAlign: 'center', marginTop: 'var(--space-10)' }}>
            <button
              onClick={drawCards}
              disabled={animating}
              className="btn btn-ghost"
              style={{ fontSize: 'var(--fs-sm)', padding: 'var(--space-3) var(--space-8)' }}
            >
              {animating ? '��는 중...' : '다시 뽑기'}
            </button>
          </div>
        </div>
      </section>

      {/* ── Guide ── */}
      <section className="section" style={{ background: 'var(--color-bg)' }}>
        <div className="container" style={{ maxWidth: '800px' }}>
          <h2 className="section-title serif" style={{ textAlign: 'center', marginBottom: 'var(--space-12)' }}>타로 읽는 법</h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 'var(--space-6)' }}>
            {[
              { title: '질문 정하기', desc: '구체적이고 열린 질문일수록 명확한 답이 ��니다. "어��게 하면~" "무엇이~" 형태가 좋습니다.' },
              { title: '직관 믿기', desc: '카드를 보며 가장 먼저 떠오르는 느낌을 믿으세요. 논리보다 직관이 정확합니다.' },
              { title: '맥락 보기', desc: '한 장만 보지 말고 전체 흐름을 보세요. 카드 간의 관계에서 깊은 의미가 나��니다.' },
              { title: '행동으로', desc: '카드는 운명이 아닌 가능성을 보여��니다. 메시지를 받아 행동으로 옮기세요.' },
            ].map((item, idx) => (
              <div key={idx} className="card" style={{ padding: 'var(--space-6)', textAlign: 'center' }}>
                <h3 style={{ fontSize: 'var(--fs-lg)', fontWeight: 700, marginBottom: 'var(--space-3)' }}>{item.title}</h3>
                <p style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)', lineHeight: 'var(--lh-relaxed)' }}>{item.desc}</p>
              </div>
            ))}
          </div>

          {/* Spread details */}
          <div style={{ marginTop: 'var(--space-16)' }}>
            <h3 className="serif" style={{ fontSize: 'var(--fs-2xl)', fontWeight: 700, textAlign: 'center', marginBottom: 'var(--space-8)' }}>스프레드별 상세</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-6)' }}>
              {(Object.entries(SPREADS) as [SpreadType, typeof SPREADS[keyof typeof SPREADS]][]).map(([key, value]) => (
                <div key={key} className="card" style={{ padding: 'var(--space-6)' }}>
                  <h4 style={{ fontSize: 'var(--fs-xl)', fontWeight: 700, color: 'var(--color-gold)', marginBottom: 'var(--space-2)' }}>{value.name} ({value.count}장)</h4>
                  <p style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)', marginBottom: 'var(--space-4)', lineHeight: 'var(--lh-relaxed)' }}>{value.description}</p>
                  <button
                    onClick={() => setSpread(key)}
                    className="btn btn-gold"
                    style={{ width: '100%', fontSize: 'var(--fs-sm)' }}
                  >
                    {spread === key ? '현재 선택��' : '선택하기'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Card Detail Modal */}
      {selectedCard && (
        <TarotCardDetail
          card={selectedCard.card}
          reversed={selectedCard.reversed}
          onClose={() => setSelectedCard(null)}
        />
      )}

      <Footer />

      <style jsx global>{`
        .spread-btn:hover {
          color: var(--color-gold);
          border-color: rgba(184,148,60,0.25);
        }
        .spread-btn.active {
          background: rgba(184,148,60,0.08);
          color: var(--color-gold);
          border-color: rgba(184,148,60,0.3);
        }

        @media (max-width: 768px) {
          .tarot-card { transform: none !important; }
        }
      `}</style>
    </>
  );
}