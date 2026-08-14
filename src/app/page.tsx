'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { Navigation } from '@/components/Navigation';
import { Footer } from '@/components/Footer';
import { Sajupae } from '@/components/Sajupae';
import { ScrollReveal } from '@/components/ScrollReveal';
import { getCompleteSaju } from '@/lib/saju';
import type { Pillar } from '@/lib/saju/constants';

const PRICING_PLANS = [
  { name: '정밀풀이', price: '19,900', original: '29,900', desc: '내 사주의 핵심 흐름을 정밀하게', features: ['사주 원국 분석', '십성 기반 성격풀이', '올해 대운 흐름', 'PDF 리포트 제공'], highlight: false },
  { name: '운세 정밀패키지', price: '49,000', original: '69,000', desc: '사주 + 올해 운세 종합', features: ['정밀풀이 전체', '월별 운세 가이드', '취업/이직 타이밍', '방향성 조언'], highlight: true },
  { name: '심층 심리분석 솔루션', price: '99,000', original: '149,000', desc: '사주 기반 심리/관계 심층 분석', features: ['운세 정밀패키지 전체', '인간관계/연애 패턴', '트라우마/그림자 분석', '1:1 상담 30분 포함'], highlight: false },
];

const COUNSELOR_BADGES = ['사주명리학', '심리상담', '운세컨설팅', '인간관계'];

// 데모용 AI 풀이 템플릿
const DEMO_TEMPLATES = [
  "당신의 사주를 보면 {dayStem}일간으로서 {element}의 기운이 강합니다. 타고난 성품이 {word1}하며, 주변 사람들에게 {word2}한 인상을 줍니다.",
  "현재 대운은 {daewoonStem}{daewoonBranch}대운으로, {daewoonDesc} 시기입니다. {word3}에 주의하며 {word4}를 키우면 좋겠습니다.",
  "십성 중 {tenGod1}와(과) {tenGod2}가 돋보입니다. 이는 {word5}을(를) 잘하는 타고난 재주가 있음을 말합니다.",
];

const ELEMENT_WORDS: Record<string, { word1: string; word2: string; word3: string; word4: string; word5: string }> = {
  목: { word1: '활동적', word2: '신뢰감', word3: '감정 기복', word4: '인내', word5: '도전' },
  화: { word1: '열정적', word2: '친근', word3: '성급함', word4: '배려', word5: '표현' },
  토: { word1: '안정적', word2: '든든', word3: '고집', word4: '유연함', word5: '실행' },
  금: { word1: '논리적', word2: '단호', word3: '경직', word4: '소통', word5: '판단' },
  수: { word1: '유연한', word2: '차분', word3: '변덕', word4: '집중', word5: '통찰' },
};

const DAEWOON_DESC = ['새로운 기회가', '안정이', '변화가', '도약이'];

export default function HomePage() {
  const [mounted, setMounted] = useState(false);
  const [formData, setFormData] = useState({
    name: '', gender: 'male', year: '', month: '', day: '', hour: '0', minute: '0',
    isLunar: false, leapMonth: false, contact: '', question: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => setMounted(true), []);

  const heroPillars = {
    year: { heavenlyStem: '갑', earthlyBranch: '자', heavenlyStemHanja: '甲', earthlyBranchHanja: '子', element: '목', yinYang: '양' },
    month: { heavenlyStem: '병', earthlyBranch: '인', heavenlyStemHanja: '丙', earthlyBranchHanja: '寅', element: '화', yinYang: '양' },
    day: { heavenlyStem: '무', earthlyBranch: '진', heavenlyStemHanja: '戊', earthlyBranchHanja: '辰', element: '토', yinYang: '양' },
    time: { heavenlyStem: '경', earthlyBranch: '신', heavenlyStemHanja: '庚', earthlyBranchHanja: '申', element: '금', yinYang: '양' },
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const calculateDemo = (data: typeof formData) => {
    try {
      const saju = getCompleteSaju({
        year: parseInt(data.year) || 1990,
        month: parseInt(data.month) || 1,
        day: parseInt(data.day) || 1,
        hour: parseInt(data.hour) || 0,
        minute: parseInt(data.minute) || 0,
        isLunar: data.isLunar,
        leapMonth: data.leapMonth,
        gender: data.gender as 'male' | 'female',
      });

      const dayStem = saju.saju.day.heavenlyStem;
      const element = ['목', '화', '토', '금', '수'][['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'].indexOf(dayStem) % 5];
      const words = ELEMENT_WORDS[element] || ELEMENT_WORDS['목'];

      const daewoon = saju.daewoon.currentDaewoon;
      const daewoonDesc = DAEWOON_DESC[Math.floor(Math.random() * DAEWOON_DESC.length)];

      const topGods = Object.entries(saju.tenGods.summary)
        .filter(([k]) => k !== '비겁')
        .sort((a, b) => b[1] - a[1])
        .slice(0, 2)
        .map(([k]) => k);

      const demoText = DEMO_TEMPLATES.map(t =>
        t.replace('{dayStem}', dayStem)
          .replace('{element}', element)
          .replace('{word1}', words.word1)
          .replace('{word2}', words.word2)
          .replace('{word3}', words.word3)
          .replace('{word4}', words.word4)
          .replace('{word5}', words.word5)
          .replace('{daewoonStem}', daewoon?.pillar.heavenlyStem || '무')
          .replace('{daewoonBranch}', daewoon?.pillar.earthlyBranch || '술')
          .replace('{daewoonDesc}', daewoonDesc)
          .replace('{tenGod1}', topGods[0] || '정인')
          .replace('{tenGod2}', topGods[1] || '식신')
      ).join('\n\n');

      return { saju, demoText, dayStem, element, words };
    } catch (err) {
      console.error(err);
      return null;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(false);
    setResult(null);
    setSuccess(false);

    // 입력 검증
    if (!formData.name || !formData.year || !formData.month || !formData.day || !formData.contact) {
      setError(true);
      setSubmitting(false);
      return;
    }

    // AI 데모 계산 (실제론 API 호출)
    setTimeout(() => {
      const demo = calculateDemo(formData);
      if (!demo) {
        setError(true);
        setSubmitting(false);
        return;
      }
      setResult(demo);
      setSubmitting(false);
    }, 2000); // 로딩 시뮬레이션
  };

  const handleDemoOnly = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(false);
    setResult(null);
    setSuccess(false);

    const demoData = { ...formData };
    if (!demoData.year) {
      demoData.year = '1990';
      demoData.month = '1';
      demoData.day = '1';
      demoData.name = demoData.name || '고객';
    }

    setTimeout(() => {
      const demo = calculateDemo(demoData);
      if (!demo) {
        setError(true);
        setSubmitting(false);
        return;
      }
      setResult(demo);
      setSubmitting(false);
    }, 1500);
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
      <section className="hero" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', paddingTop: 'var(--nav-height)' }}>
        <div className="container">
          <div className="hero-grid" style={{ display: 'grid', gridTemplateColumns: '1.1fr 0.9fr', gap: 'var(--space-16)', alignItems: 'center' }}>
            <div>
              <span className="eyebrow" style={{ display: 'inline-flex', alignItems: 'center', gap: 'var(--space-2)', fontSize: 'var(--fs-sm)', fontWeight: 600, letterSpacing: '0.12em', color: 'var(--color-jujube)', marginBottom: 'var(--space-6)' }}>
                <span style={{ width: '28px', height: '1px', background: 'var(--color-jujube)', display: 'inline-block' }} />
                사주 · 타로 · 운세 · 궁합
              </span>
              <h1 className="serif" style={{ fontSize: 'var(--fs-5xl)', fontWeight: 700, lineHeight: 1.28, letterSpacing: '-0.01em', marginBottom: 'var(--space-6)' }}>
                태어난 네 글자를,<br />
                <span style={{ color: 'var(--color-jujube)', position: 'relative' }}>오늘의 언어</span>로
              </h1>
              <p className="lead" style={{ fontSize: 'var(--fs-lg)', color: 'var(--color-ink-soft)', maxWidth: '460px', marginBottom: 'var(--space-8)', lineHeight: 'var(--lh-relaxed)' }}>
                1992년생 갑자일부터 2100년까지, 당신의 사주를 정밀하게 풀어드립니다.
                사주·타로·궁합·오늘운세까지 한 곳에서.
              </p>
              <div className="hero-ctas" style={{ display: 'flex', gap: 'var(--space-4)', flexWrap: 'wrap' }}>
                <a href="#apply" className="btn btn-primary" style={{ fontSize: 'var(--fs-md)' }}>
                  무료 맛보기 받기 →
                </a>
                <Link href="/taro" className="btn btn-ghost" style={{ fontSize: 'var(--fs-md)' }}>
                  🔮 타로 보기
                </Link>
              </div>
            </div>

            <Sajupae pillars={heroPillars} animated />
          </div>
        </div>
      </section>

      {/* ── About / Why Us ── */}
      <ScrollReveal>
        <section className="section" style={{ background: 'var(--color-bg-deep)' }}>
          <div className="container">
            <div className="kicker">왜 우리인가</div>
            <h2 className="section-title serif">사주, 다시 읽다가 다른 이유</h2>
            <p className="section-sub">단순한 운세가 아닙니다. 당신의 사주를 오늘 산다는 언어로 번역합니다.</p>

            <div style={{ marginTop: 'var(--space-16)', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 'var(--space-6)' }}>
              {[
                { num: '壹', title: '정밀 사주 계산', desc: '만세력 기반 정확한 사주 원국과 대운을 계산합니다.' },
                { num: '貳', title: '십성 기반 심리풀이', desc: '십성(십신)을 통해 당신의 성격과 관계 패턴을 읽습니다.' },
                { num: '參', title: '통합 운세 허브', desc: '사주·타로·궁합·오늘운세를 한 사이트에서.' },
                { num: '四', title: '전문가 직접 검토', desc: 'AI 데모 후, 상담가가 정밀하게 검토해 드립니다.' },
              ].map((item, idx) => (
                <ScrollReveal key={item.num} delay={idx * 100}>
                  <div className="card" style={{ padding: 'var(--space-8)', height: '100%' }}>
                    <div className="serif" style={{ fontSize: 'var(--fs-3xl)', color: 'var(--color-jujube)', fontFamily: 'var(--font-serif)', marginBottom: 'var(--space-4)', opacity: 0.8 }}>
                      {item.num}
                    </div>
                    <h3 style={{ fontSize: 'var(--fs-xl)', fontWeight: 700, marginBottom: 'var(--space-2)' }}>{item.title}</h3>
                    <p style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)', lineHeight: 'var(--lh-relaxed)' }}>{item.desc}</p>
                  </div>
                </ScrollReveal>
              ))}
            </div>
          </div>
        </section>
      </ScrollReveal>

      {/* ── Counselor Profile ── */}
      <ScrollReveal>
        <section className="section" style={{ background: 'var(--color-bg)' }}>
          <div className="container">
            <div className="kicker">상담가 소개</div>
            <h2 className="section-title serif">당신의 사주를 읽는 사람</h2>

            <div className="card" style={{ marginTop: 'var(--space-12)', display: 'flex', gap: 'var(--space-10)', padding: 'var(--space-10)', flexWrap: 'wrap', alignItems: 'flex-start' }}>
              <div
                className="counselor-photo"
                style={{
                  width: '152px',
                  height: '152px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #eef2ff, #fdf2f8)',
                  border: '1px solid var(--color-line)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
                aria-hidden="true"
              >
                <span style={{ fontSize: '56px', fontWeight: 700, color: 'var(--color-jujube-soft)', opacity: 0.7 }}>易</span>
              </div>

              <div style={{ flex: 1, minWidth: '280px' }}>
                <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 700, color: 'var(--color-jujube)', letterSpacing: '0.04em', marginBottom: 'var(--space-3)' }}>
                  대표 상담가 · 명리학 연구자
                </div>
                <p style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)', lineHeight: 'var(--lh-relaxed)', marginBottom: 'var(--space-5)' }}>
                  사주명리학과 심리학을 결합해, 단순한 '운'이 아닌 '성향과 흐름'을 풀어드립니다.
                  당신의 사주가 가진 고유한 리듬을 오늘의 언어로 번역해 드립니다.
                </p>
                <div style={{ display: 'flex', gap: 'var(--space-2)', flexWrap: 'wrap', marginBottom: 'var(--space-5)' }}>
                  {COUNSELOR_BADGES.map(badge => (
                    <span key={badge} style={{ background: 'var(--color-bg-deep)', border: '1px solid var(--color-line)', color: 'var(--color-ink)', fontSize: 'var(--fs-sm)', fontWeight: 600, padding: 'var(--space-2) var(--space-4)', borderRadius: 'var(--radius-full)' }}>
                      {badge}
                    </span>
                  ))}
                </div>
                <blockquote className="serif" style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink)', lineHeight: 'var(--lh-relaxed)', paddingLeft: 'var(--space-4)', borderLeft: '3px solid var(--color-gold)' }}>
                  "사주는 운명이 아닙니다. 당신이 타고난 리듬의 지도일 뿐입니다."
                </blockquote>
              </div>
            </div>
          </div>
        </section>
      </ScrollReveal>

      {/* ── Pricing ── */}
      <ScrollReveal>
        <section className="section" style={{ background: 'var(--color-bg-deep)' }}>
          <div className="container">
            <div className="kicker">상담 상품</div>
            <h2 className="section-title serif">필요에 맞는 풀이를 선택하세요</h2>
            <p className="section-sub">모든 상품은 사주 원국 정밀 분석을 포함합니다. 결제는 신청 확인 후 별도 안내드립니다.</p>

            <div style={{ marginTop: 'var(--space-12)', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-6)', alignItems: 'stretch' }}>
              {PRICING_PLANS.map((plan, idx) => (
                <ScrollReveal key={plan.name} delay={idx * 100}>
                  <div
                    className={`card ${plan.highlight ? '' : ''}`}
                    style={{
                      position: 'relative',
                      background: plan.highlight ? 'var(--color-ink)' : 'var(--color-bg-card)',
                      color: plan.highlight ? 'var(--color-bg)' : 'var(--color-ink)',
                      border: plan.highlight ? '1px solid var(--color-ink)' : '1px solid var(--color-line)',
                      borderRadius: 'var(--radius-xl)',
                      padding: 'var(--space-8)',
                      display: 'flex',
                      flexDirection: 'column',
                      height: '100%',
                    }}
                  >
                    {plan.highlight && (
                      <span style={{ position: 'absolute', top: '-14px', left: 'var(--space-8)', background: 'var(--color-jujube)', color: 'var(--color-bg-card)', fontSize: 'var(--fs-xs)', fontWeight: 700, padding: 'var(--space-2) var(--space-4)', borderRadius: 'var(--radius-full)' }}>
                        가장 인기
                      </span>
                    )}
                    <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 700, letterSpacing: '0.06em', color: plan.highlight ? 'var(--color-gold)' : 'var(--color-jujube)', marginBottom: 'var(--space-3)' }}>
                      {plan.name}
                    </div>
                    <p style={{ fontSize: 'var(--fs-md)', color: plan.highlight ? 'rgba(243,237,226,0.7)' : 'var(--color-ink-soft)', marginBottom: 'var(--space-5)', lineHeight: 'var(--lh-normal)' }}>
                      {plan.desc}
                    </p>
                    <div style={{ marginBottom: 'var(--space-6)' }}>
                      <span className="serif" style={{ fontSize: 'var(--fs-4xl)', fontWeight: 800 }}>
                        {plan.price}<span style={{ fontSize: 'var(--fs-md)', fontWeight: 500, marginLeft: 'var(--space-1)' }}>원</span>
                      </span>
                      <span style={{ marginLeft: 'var(--space-3)', fontSize: 'var(--fs-sm)', color: plan.highlight ? 'rgba(243,237,226,0.5)' : 'var(--color-ink-muted)', textDecoration: 'line-through' }}>
                        {plan.original}원
                      </span>
                    </div>
                    <ul style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', marginBottom: 'var(--space-8)', flex: 1 }}>
                      {plan.features.map(feature => (
                        <li key={feature} style={{ fontSize: 'var(--fs-md)', color: plan.highlight ? 'rgba(243,237,226,0.85)' : 'var(--color-ink-soft)', paddingLeft: 'var(--space-5)', position: 'relative' }}>
                          <span style={{ position: 'absolute', left: 0, color: plan.highlight ? 'var(--color-gold)' : 'var(--color-jujube)', fontWeight: 700 }}>✓</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <a
                      href="#apply"
                      className={`btn ${plan.highlight ? 'btn-gold' : 'btn-primary'}`}
                      style={{ width: '100%', fontSize: 'var(--fs-md)' }}
                    >
                      신청하기
                    </a>
                  </div>
                </ScrollReveal>
              ))}
            </div>
          </div>
        </section>
      </ScrollReveal>

      {/* ── Apply Form + AI Demo ── */}
      <ScrollReveal>
        <section id="apply" className="section" style={{ background: 'var(--color-bg)' }}>
          <div className="container">
            <div className="kicker">무료 맛보기</div>
            <h2 className="section-title serif">내 사주, 무료로 미리 보기</h2>
            <p className="section-sub">정보를 입력하시면 AI가 사주를 간단히 풀어드립니다. 정식 풀이는 상담가가 검토합니다.</p>

            <div style={{ marginTop: 'var(--space-12)', display: 'grid', gridTemplateColumns: '0.85fr 1.15fr', gap: 'var(--space-14)', alignItems: 'start' }} className="apply-grid">

              {/* Left: benefits */}
              <div>
                <h3 style={{ fontSize: 'var(--fs-2xl)', fontWeight: 700, marginBottom: 'var(--space-4)' }}>무료 맛보기 포함 사항</h3>
                <p style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)', marginBottom: 'var(--space-6)', lineHeight: 'var(--lh-relaxed)' }}>
                  AI가 계산한 사주 원국과 기본 풀이를 즉시 확인하실 수 있습니다.
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                  {[
                    '사주 4주(년·월·일·시) 원국',
                    '일간 기반 성격 풀이',
                    '현재 대운 흐름',
                    '십성 기반 강점 분석',
                  ].map(point => (
                    <div key={point} style={{ display: 'flex', gap: 'var(--space-3)', fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)' }}>
                      <span style={{ color: 'var(--color-jujube)', fontWeight: 700, flexShrink: 0 }}>✦</span>
                      <span>{point}</span>
                    </div>
                  ))}
                </div>

                <div className="card" style={{ marginTop: 'var(--space-8)', padding: 'var(--space-6)', background: 'var(--color-bg-deep)', border: '1px solid var(--color-line)' }}>
                  <p style={{ fontSize: 'var(--fs-sm)', color: 'var(--color-ink-soft)', lineHeight: 'var(--lh-relaxed)' }}>
                    💡 정밀풀이는 상담가의 직접 검토가 포함됩니다. 정확한 출생 시간과 절기를 반영한 분석을 원하시면 유료 상품을 선택해 주세요.
                  </p>
                </div>
              </div>

              {/* Right: form + result */}
              <div>
                {!result && !submitting && !success && (
                  <form onSubmit={handleSubmit} className="card" style={{ background: 'var(--color-bg-card)', borderRadius: 'var(--radius-xl)', padding: 'var(--space-10)', border: '1px solid var(--color-line)', boxShadow: 'var(--shadow-lg)' }}>
                    <div className="form-row">
                      <label htmlFor="name">이름 (또는 닉네임)</label>
                      <input
                        type="text"
                        id="name"
                        name="name"
                        value={formData.name}
                        onChange={handleInputChange}
                        placeholder="홍길동"
                        maxLength={20}
                        required
                      />
                    </div>

                    <div className="form-row">
                      <label>성별</label>
                      <div className="radio-pills" style={{ display: 'flex', gap: 'var(--space-3)' }}>
                        {['male', 'female'].map(g => (
                          <div key={g} style={{ flex: 1 }}>
                            <input
                              type="radio"
                              id={`gender-${g}`}
                              name="gender"
                              value={g}
                              checked={formData.gender === g}
                              onChange={handleInputChange}
                              style={{ display: 'none' }}
                            />
                            <label
                              htmlFor={`gender-${g}`}
                              style={{
                                display: 'block',
                                textAlign: 'center',
                                padding: 'var(--space-3) 0',
                                border: '1px solid var(--color-line)',
                                borderRadius: 'var(--radius-md)',
                                fontSize: 'var(--fs-md)',
                                fontWeight: 500,
                                color: 'var(--color-ink-soft)',
                                cursor: 'pointer',
                                transition: 'all var(--transition-fast)',
                                background: formData.gender === g ? 'var(--color-jujube)' : 'transparent',
                                color: formData.gender === g ? 'var(--color-bg-card)' : 'var(--color-ink-soft)',
                                fontWeight: formData.gender === g ? 600 : 500,
                              }}
                            >
                              {g === 'male' ? '남성' : '여성'}
                            </label>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="form-row">
                      <label>생년월일</label>
                      <div className="form-3col" style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr 1fr', gap: 'var(--space-3)' }}>
                        <input
                          type="number"
                          name="year"
                          value={formData.year}
                          onChange={handleInputChange}
                          placeholder="1990"
                          min={1900}
                          max={2100}
                          required
                        />
                        <select name="month" value={formData.month} onChange={handleInputChange} required>
                          <option value="">월</option>
                          {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
                            <option key={m} value={m}>{m}월</option>
                          ))}
                        </select>
                        <input
                          type="number"
                          name="day"
                          value={formData.day}
                          onChange={handleInputChange}
                          placeholder="일"
                          min={1}
                          max={31}
                          required
                        />
                      </div>
                      <p className="birth-hint" style={{ fontSize: 'var(--fs-sm)', color: 'var(--color-ink-soft)', marginTop: 'var(--space-2)', opacity: 0.8 }}>
                        양력 기준입니다. 음력인 경우 아래 체크박스를 선택하세요.
                      </p>
                      <div style={{ marginTop: 'var(--space-3)', display: 'flex', gap: 'var(--space-4)' }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', fontSize: 'var(--fs-sm)', color: 'var(--color-ink-soft)', cursor: 'pointer' }}>
                          <input type="checkbox" name="isLunar" checked={formData.isLunar} onChange={handleInputChange} style={{ width: 'auto' }} />
                          음력出生
                        </label>
                        {formData.isLunar && (
                          <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-2)', fontSize: 'var(--fs-sm)', color: 'var(--color-ink-soft)', cursor: 'pointer' }}>
                            <input type="checkbox" name="leapMonth" checked={formData.leapMonth} onChange={handleInputChange} style={{ width: 'auto' }} />
                            윤달
                          </label>
                        )}
                      </div>
                    </div>

                    <div className="form-row">
                      <label>태어난 시간</label>
                      <div className="form-2col" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
                        <select name="hour" value={formData.hour} onChange={handleInputChange}>
                          {Array.from({ length: 24 }, (_, i) => i).map(h => (
                            <option key={h} value={h}>{h}시</option>
                          ))}
                        </select>
                        <select name="minute" value={formData.minute} onChange={handleInputChange}>
                          {[0, 15, 30, 45].map(m => (
                            <option key={m} value={m}>{m}분</option>
                          ))}
                        </select>
                      </div>
                      <p className="birth-hint" style={{ fontSize: 'var(--fs-sm)', color: 'var(--color-ink-soft)', marginTop: 'var(--space-2)', opacity: 0.8 }}>
                        모를 경우 0시(자시)로 두세요. 정밀풀이에서 확인 가능합니다.
                      </p>
                    </div>

                    <div className="form-row">
                      <label htmlFor="contact">연락받을 곳 (카카오톡 ID 또는 이메일)</label>
                      <input
                        type="text"
                        id="contact"
                        name="contact"
                        value={formData.contact}
                        onChange={handleInputChange}
                        placeholder="카카오톡 ID 또는 이메일 주소"
                        maxLength={100}
                        required
                      />
                      <div className="field-error" style={{ display: !formData.contact ? 'block' : 'none', color: 'var(--color-jujube)' }}>
                        연락받을 곳을 입력해주세요.
                      </div>
                    </div>

                    <div className="form-row">
                      <label htmlFor="question">궁금한 점 (선택)</label>
                      <textarea
                        id="question"
                        name="question"
                        value={formData.question}
                        onChange={handleInputChange}
                        maxLength={500}
                        placeholder="예: 지금 다니는 일이 저랑 잘 맞는지 궁금해요. 비워두시면 종합풀이로 안내드립니다."
                        rows={3}
                      />
                    </div>

                    <button type="submit" className="btn btn-primary" style={{ width: '100%', fontSize: 'var(--fs-md)' }}>
                      신청하기
                    </button>
                    <p className="submit-note" style={{ textAlign: 'center', fontSize: 'var(--fs-sm)', color: 'var(--color-ink-soft)', marginTop: 'var(--space-3)', opacity: 0.75 }}>
                      신청해주신 분께는 순서대로 정성껏 풀이해 연락드립니다.
                    </p>
                  </form>
                )}

                {/* Loading */}
                {submitting && (
                  <div className="card" style={{ padding: 'var(--space-20) var(--space-8)', textAlign: 'center', borderRadius: 'var(--radius-xl)' }}>
                    <div style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-6)' }}>
                      {['甲', '丁', '庚', '乙'].map((glyph, i) => (
                        <span
                          key={i}
                          className="serif"
                          style={{
                            width: '52px',
                            height: '64px',
                            borderRadius: 'var(--radius-md)',
                            background: 'var(--color-bg)',
                            border: '1.5px solid var(--color-line)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: 'var(--fs-xl)',
                            color: 'var(--color-jujube-soft)',
                            animation: `sajuPulse 1.1s ease-in-out infinite ${i * 0.15}s`,
                          }}
                        >
                          {glyph}
                        </span>
                      ))}
                    </div>
                    <p style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)', fontWeight: 500 }}>사주 원국을 분석하고 있어요…</p>
                    <p style={{ marginTop: 'var(--space-2)', fontSize: 'var(--fs-sm)', color: 'var(--color-ink-soft)', opacity: 0.65 }}>잠시만 기다려 주세요 (최대 30초 정도 걸릴 수 있어요)</p>
                  </div>
                )}

                {/* Error */}
                {error && !submitting && (
                  <div className="card" style={{ padding: 'var(--space-12) var(--space-8)', textAlign: 'center', borderRadius: 'var(--radius-xl)', borderColor: 'var(--color-jujube)' }}>
                    <div className="serif" style={{ fontSize: 'var(--fs-3xl)', color: 'var(--color-jujube)', marginBottom: 'var(--space-3)' }}>⚠</div>
                    <h3 style={{ fontSize: 'var(--fs-xl)', marginBottom: 'var(--space-2)' }}>풀이를 불러오지 못했어요</h3>
                    <p style={{ color: 'var(--color-ink-soft)', fontSize: 'var(--fs-md)', marginBottom: 'var(--space-5)' }}>
                      잠시 문제가 발생했어요. 다시 시도해주시거나, 무료 신청서로 접수해주시면 직접 풀이해서 연락드릴게요.
                    </p>
                    <button
                      onClick={() => setError(false)}
                      className="btn btn-primary"
                      style={{ fontSize: 'var(--fs-md)' }}
                    >
                      다시 시도하기
                    </button>
                  </div>
                )}

                {/* Success */}
                {success && !submitting && !result && (
                  <div className="card" style={{ padding: 'var(--space-16) var(--space-8)', textAlign: 'center', borderRadius: 'var(--radius-xl)' }}>
                    <div className="serif" style={{ fontSize: 'var(--fs-3xl)', color: 'var(--color-jujube)', marginBottom: 'var(--space-4)' }}>已</div>
                    <h3 className="serif" style={{ fontSize: 'var(--fs-xl)', marginBottom: 'var(--space-3)' }}>신청이 접수되었습니다</h3>
                    <p style={{ color: 'var(--color-ink-soft)', fontSize: 'var(--fs-md)' }}>
                      남겨주신 연락처로 풀이 결과를 보내드릴게요.<br />조금만 기다려 주세요.
                    </p>
                  </div>
                )}

                {/* Result */}
                {result && !submitting && (
                  <div className="card" style={{ padding: 'var(--space-8)', borderRadius: 'var(--radius-xl)', borderColor: 'var(--color-jujube)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 'var(--space-3)', marginBottom: 'var(--space-5)', flexWrap: 'wrap' }}>
                      <div style={{ fontSize: 'var(--fs-xl)', fontWeight: 700 }}>
                        {formData.name || '고객'}님의 사주 <span style={{ fontWeight: 400, fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)', marginLeft: 'var(--space-2)' }}>무료 맛보기 풀이</span>
                      </div>
                      <span style={{ fontSize: 'var(--fs-xs)', fontWeight: 700, color: 'var(--color-jujube)', background: 'var(--color-jujube-pale)', padding: 'var(--space-2) var(--space-3)', borderRadius: 'var(--radius-full)', whiteSpace: 'nowrap' }}>
                        AI 데모 · 맛보기
                      </span>
                    </div>

                    {/* Result pillars */}
                    <div style={{ display: 'flex', gap: 'var(--space-2)', marginBottom: 'var(--space-6)' }}>
                      {[
                        { label: '년', p: result.saju.saju.year },
                        { label: '월', p: result.saju.saju.month },
                        { label: '일', p: result.saju.saju.day },
                        { label: '시', p: result.saju.saju.time },
                      ].map((item, idx) => (
                        <div key={idx} style={{ flex: 1, textAlign: 'center', background: 'var(--color-bg)', border: '1px solid var(--color-line)', borderRadius: 'var(--radius-md)', padding: 'var(--space-3) var(--space-1)' }}>
                          <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-ink-soft)', marginBottom: 'var(--space-1)' }}>{item.label}</div>
                          <div className="serif" style={{ fontSize: 'var(--fs-lg)', fontWeight: 700, lineHeight: 1.3 }}>
                            {item.p.heavenlyStem}{item.p.earthlyBranch}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Demo text */}
                    <div style={{ background: 'var(--color-bg)', border: '1px solid var(--color-line)', borderRadius: 'var(--radius-lg)', padding: 'var(--space-6)', fontSize: 'var(--fs-md)', lineHeight: 'var(--lh-relaxed)', color: 'var(--color-ink)', whiteSpace: 'pre-line' }}>
                      {result.demoText}
                    </div>

                    {/* Daewoon info */}
                    {result.saju.daewoon.currentDaewoon && (
                      <div className="card" style={{ marginTop: 'var(--space-5)', padding: 'var(--space-5)', background: 'var(--color-bg-deep)', border: '1px solid var(--color-line)' }}>
                        <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 700, color: 'var(--color-jujube)', marginBottom: 'var(--space-2)' }}>현재 대운</div>
                        <div style={{ display: 'flex', alignItems: 'baseline', gap: 'var(--space-2)' }}>
                          <span className="serif" style={{ fontSize: 'var(--fs-2xl)', fontWeight: 700 }}>
                            {result.saju.daewoon.currentDaewoon.pillar.heavenlyStem}{result.saju.daewoon.currentDaewoon.pillar.earthlyBranch}
                          </span>
                          <span style={{ fontSize: 'var(--fs-sm)', color: 'var(--color-ink-soft)' }}>
                            대운 ({result.saju.daewoon.currentDaewoon.startYear} ~ {result.saju.daewoon.currentDaewoon.endYear})
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Footer note */}
                    <div style={{ marginTop: 'var(--space-5)', fontSize: 'var(--fs-sm)', color: 'var(--color-ink-soft)', lineHeight: 'var(--lh-relaxed)', padding: 'var(--space-4)', background: 'var(--color-bg-deep)', borderRadius: 'var(--radius-md)' }}>
                      이 풀이는 무료 맛보기를 위해 AI가 간단히 생성한 데모입니다. 절기와 정확한 출생 시간을 반영한 정식 사주 원국, 그리고 상담가의 직접 검토는 정밀풀이에서 제공됩니다.
                    </div>

                    {/* CTA */}
                    <div style={{ marginTop: 'var(--space-6)', display: 'flex', gap: 'var(--space-3)', flexWrap: 'wrap' }}>
                      <a href="#pricing" className="btn btn-primary" style={{ flex: 1, fontSize: 'var(--fs-md)' }}>
                        정밀풀이 자세히 보기
                      </a>
                      <a href="https://pf.kakao.com/" target="_blank" rel="noopener noreferrer" className="btn btn-ghost" style={{ flex: 1, fontSize: 'var(--fs-md)' }}>
                        카카오톡 채널 추가
                      </a>
                    </div>

                    <button
                      onClick={() => { setResult(null); setSuccess(false); }}
                      style={{ marginTop: 'var(--space-4)', display: 'block', width: '100%', textAlign: 'center', fontSize: 'var(--fs-sm)', color: 'var(--color-jujube)', fontWeight: 600, textDecoration: 'underline', background: 'none', border: 'none', cursor: 'pointer' }}
                    >
                      다시 입력하기
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>
      </ScrollReveal>

      <Footer />

      <style jsx global>{`
        @keyframes sajuPulse {
          0%, 100% { opacity: 0.35; transform: translateY(0); }
          50% { opacity: 1; transform: translateY(-6px); }
        }

        @media (max-width: 768px) {
          .hero-grid { grid-template-columns: 1fr !important; gap: var(--space-12) !important; }
          .apply-grid { grid-template-columns: 1fr !important; gap: var(--space-8) !important; }
          .form-3col { grid-template-columns: 1fr 1fr 1fr !important; }
          .sajupae { height: 360px !important; }
          .pillar { width: 60px !important; height: 300px !important; }
          .glyph { font-size: 28px !important; }
        }
      `}</style>
    </>
  );
}