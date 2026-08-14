'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Footer } from '@/components/Footer';
import { ScrollReveal } from '@/components/ScrollReveal';
import { getCompleteSaju, type SajuInput } from '@/lib/saju';

interface Person {
  name: string;
  year: string;
  month: string;
  day: string;
  hour: string;
  gender: 'male' | 'female';
}

interface CompatibilityResult {
  score: number;
  level: string;
  summary: string;
  strengths: string[];
  challenges: string[];
  advice: string;
  elementRelation: string;
  elementDetail: string;
}

const ELEMENTS: Record<string, string> = { 목: '목', 화: '화', 토: '토', 금: '금', 수: '수' };
const STEM_ELEMENTS: Record<string, string> = { 갑: '목', 을: '목', 병: '화', 정: '화', 무: '토', 기: '토', 경: '금', 신: '금', 임: '수', 계: '수' };

function getElementOfDayStem(dayStem: string): string {
  return STEM_ELEMENTS[dayStem] || '목';
}

function analyzeCompatibility(p1: SajuInput, p2: SajuInput): CompatibilityResult {
  const saju1 = getCompleteSaju(p1);
  const saju2 = getCompleteSaju(p2);

  const el1 = getElementOfDayStem(saju1.saju.day.heavenlyStem);
  const el2 = getElementOfDayStem(saju2.saju.day.heavenlyStem);

  const GENERATES: Record<string, string> = { 목: '화', 화: '토', 토: '금', 금: '수', 수: '목' };
  const CONTROLS: Record<string, string> = { 목: '토', 토: '수', 수: '화', 화: '금', 금: '목' };

  // 오행 관계
  let elementRelation: string;
  let elementDetail: string;
  let baseScore = 70;

  if (el1 === el2) {
    elementRelation = '동일 오행 (相生 기반)';
    elementDetail = `${el1}와(과) ${el2}는(은) 같은 오행입니다. 서로 잘 통하고 이해가 빠르지만, 때로는 너무 같아 지루할 수 있습니다.`;
    baseScore += 10;
  } else if (GENERATES[el1] === el2) {
    elementRelation = '상생 관계 (生)';
    elementDetail = `${el1}이(가) ${el2}을(를) 생합니다. 자연스러운 흐름이 돕습니다. ${p1.name || '첫 번째 분'}이 ${p2.name || '두 번째 분'}을(를) 이끌어주는 관계입니다.`;
    baseScore += 15;
  } else if (GENERATES[el2] === el1) {
    elementRelation = '상생 관계 (被生)';
    elementDetail = `${el2}이(가) ${el1}을(를) 생합니다. ${p2.name || '두 번째 분'}의 에너지가 ${p1.name || '첫 번째 분'}을(를) 키워줍니다.`; baseScore += 12;
  } else if (CONTROLS[el1] === el2) {
    elementRelation = '상극 관계 (克)';
    elementDetail = `${el1}이(가) ${el2}을(를) 극합니다. 긴장과 자극이 있는 관계입니다. 서로 다듬어 주면 좋지만, 주의가 필요합니다.`;
    baseScore -= 8;
  } else if (CONTROLS[el2] === el1) {
    elementRelation = '상극 관계 (被克)';
    elementDetail = `${el2}이(가) ${el1}을(를) 극합니다. ${p2.name || '두 번째 분'}이(가) 주도권을 쥐는 경향이 있습니다.`;
    baseScore -= 5;
  } else {
    elementRelation = '중립 관계 (友)';
    elementDetail = `${el1}와(과) ${el2}는(은) 서로 극하거나 생하지 않는 중립 관계입니다. 편안하지만 특별한 케미는 만들어야 합니다.`;
    baseScore += 2;
  }

  // 십성 기반 분석
  const tenGod1To2 = getTenGodBetween(saju1.saju.day.heavenlyStem, saju2.saju.day.heavenlyStem);
  const tenGod2To1 = getTenGodBetween(saju2.saju.day.heavenlyStem, saju1.saju.day.heavenlyStem);

  const strengths: string[] = [];
  const challenges: string[] = [];

  if (tenGod1To2 === '정인' || tenGod1To2 === '편인') {
    strengths.push(`${p1.name || '첫째'}는(은) ${p2.name || '둘째'}를(을) 보호하고 돌보는 마음이 큽니다.`);
  }
  if (tenGod1To2 === '정관' || tenGod1To2 === '편관') {
    strengths.push(`${p1.name || '첫째'}는(은) ${p2.name || '둘째'}에게 안정감과 규율을 줍니다.`);
  }
  if (tenGod1To2 === '정재' || tenGod1To2 === '편재') {
    strengths.push(`${p1.name || '첫째'}는(은) ${p2.name || '둘째'}에게 실질적 도움을 줍니다.`);
  }
  if (tenGod1To2 === '식신' || tenGod1To2 === '상관') {
    strengths.push(`${p1.name || '첫째'}는(은) ${p2.name || '둘째'}와 함께할 때 표현력이 살아납니다.`);
  }
  if (tenGod1To2 === '비겁' || tenGod1To2 === '겁재') {
    strengths.push(`${p1.name || '첫째'}는(은) ${p2.name || '둘째'}를(을) 동반자로 느낍니다.`);
  }

  if (tenGod1To2 === '상관' || tenGod2To1 === '상관') {
    challenges.push('서로의 자유와 개성을 존중하는 연습이 필요합니다.');
  }
  if (elementRelation.includes('상극')) {
    challenges.push('오행이 서로 극하는 관계로, 대화 방식에 주의가 필요합니다.');
  }
  if (tenGod1To2 === '겁재' || tenGod2To1 === '겁재') {
    challenges.push('재물이나 주도권 다툼이 생길 수 있으니 명확한 합의가 필요합니다.');
  }

  if (strengths.length === 0) strengths.push(`${p1.name || '첫째'}와(과) ${p2.name || '둘째'}는(은) 서로 다른 매력을 지녀 보완 관계를 이룹니다.`);
  if (challenges.length === 0) challenges.push('큰 갈등 요인은 없으나, 사소한 습관 차이를 이해하는 노력이 필요합니다.');

  // 점수 보정
  const score = Math.max(20, Math.min(98, baseScore + (strengths.length - challenges.length) * 3));

  const level = score >= 85 ? '천생연분 💕' : score >= 70 ? '좋은 인연 😊' : score >= 55 ? '무난한 사이 🤝' : score >= 40 ? '노력 필요 💪' : '주의 필요 ⚠️';

  const summary = `${p1.name || '첫 번째 분'}의 일간 ${saju1.saju.day.heavenlyStem}(${el1})과(와) ${p2.name || '두 번째 분'}의 일간 ${saju2.saju.day.heavenlyStem}(${el2})은(는) ${elementRelation}입니다. ${elementDetail}`;

  const advice = score >= 70
    ? '서로의 다름을 즐기는 관계입니다. 이 흐름을 유지하세요.'
    : score >= 50
    ? '차이를 인정하고 대화하는 습관을 들이면 좋아집니다.'
    : '서로의 경계를 존중하며 천천히 신뢰를 쌓아가세요.';

  return { score, level, summary, strengths, challenges, advice, elementRelation, elementDetail };
}

function getTenGodBetween(dayStem1: string, dayStem2: string): string {
  const ELEMENTS: Record<string, string> = { 갑: '목', 을: '목', 병: '화', 정: '화', 무: '토', 기: '토', 경: '금', 신: '금', 임: '수', 계: '수' };
  const GENERATES: Record<string, string> = { 목: '화', 화: '토', 토: '금', 금: '수', 수: '목' };
  const CONTROLS: Record<string, string> = { 목: '토', 토: '수', 수: '화', 화: '금', 금: '목' };

  const el1 = ELEMENTS[dayStem1];
  const el2 = ELEMENTS[dayStem2];
  const yy1 = ['갑', '병', '무', '경', '임'].includes(dayStem1) ? '양' : '음';
  const yy2 = ['갑', '병', '무', '경', '임'].includes(dayStem2) ? '양' : '음';

  if (el1 === el2) return yy1 === yy2 ? '비겁' : '겁재';
  if (GENERATES[el1] === el2) return yy1 === yy2 ? '식신' : '상관';
  if (CONTROLS[el1] === el2) return yy1 === yy2 ? '정재' : '편재';
  if (CONTROLS[el2] === el1) return yy1 === yy2 ? '정관' : '편관';
  if (GENERATES[el2] === el1) return yy1 === yy2 ? '정인' : '편인';
  return '비겁';
}

export default function CompatibilityPage() {
  const [mounted, setMounted] = useState(false);
  const [person1, setPerson1] = useState<Person>({ name: '', year: '1990', month: '1', day: '1', hour: '0', gender: 'male' });
  const [person2, setPerson2] = useState<Person>({ name: '', year: '1992', month: '6', day: '15', hour: '12', gender: 'female' });
  const [result, setResult] = useState<CompatibilityResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => setMounted(true), []);

  const handleChange = (person: 'p1' | 'p2', field: keyof Person, value: string) => {
    if (person === 'p1') setPerson1(prev => ({ ...prev, [field]: value }));
    else setPerson2(prev => ({ ...prev, [field]: value }));
  };

  const handleAnalyze = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // 검증
    if (!person1.year || !person1.month || !person1.day || !person2.year || !person2.month || !person2.day) {
      setError('두 분의 생년월일을 모두 입력해주세요.');
      setLoading(false);
      return;
    }

    if (parseInt(person1.year) < 1900 || parseInt(person1.year) > 2100 ||
        parseInt(person2.year) < 1900 || parseInt(person2.year) > 2100) {
      setError('1900년~2100년 사이의 연도를 입력해주세요.');
      setLoading(false);
      return;
    }

    setTimeout(() => {
      const res = analyzeCompatibility(
        { year: parseInt(person1.year), month: parseInt(person1.month), day: parseInt(person1.day), hour: parseInt(person1.hour), gender: person1.gender },
        { year: parseInt(person2.year), month: parseInt(person2.month), day: parseInt(person2.day), hour: parseInt(person2.hour), gender: person2.gender }
      );
      setResult(res);
      setLoading(false);
    }, 1500);
  };

  const PersonForm = ({ person, onChange, title, accent }: { person: Person; onChange: (field: keyof Person, value: string) => void; title: string; accent: string }) => (
    <div className="card" style={{ padding: 'var(--space-6)', background: 'var(--color-bg-card)' }}>
      <h3 style={{ fontSize: 'var(--fs-lg)', fontWeight: 700, marginBottom: 'var(--space-5)', color: accent }}>{title}</h3>

      <div className="form-row">
        <label>이름 (선택)</label>
        <input
          type="text"
          value={person.name}
          onChange={e => onChange('name', e.target.value)}
          placeholder="이름 또는 닉네임"
          maxLength={10}
        />
      </div>

      <div className="form-row">
        <label>성별</label>
        <div style={{ display: 'flex', gap: 'var(--space-3)' }}>
          {(['male', 'female'] as const).map(g => (
            <div key={g} style={{ flex: 1 }}>
              <input
                type="radio"
                id={`${title}-${g}`}
                name={`${title}-gender`}
                checked={person.gender === g}
                onChange={() => onChange('gender', g)}
                style={{ display: 'none' }}
              />
              <label
                htmlFor={`${title}-${g}`}
                style={{
                  display: 'block',
                  textAlign: 'center',
                  padding: 'var(--space-3) 0',
                  border: '1px solid var(--color-line)',
                  borderRadius: 'var(--radius-md)',
                  fontSize: 'var(--fs-md)',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)',
                  background: person.gender === g ? accent : 'transparent',
                  color: person.gender === g ? '#fff' : 'var(--color-ink-soft)',
                  fontWeight: person.gender === g ? 600 : 500,
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
        <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr 1fr', gap: 'var(--space-2)' }}>
          <input type="number" value={person.year} onChange={e => onChange('year', e.target.value)} placeholder="년" min={1900} max={2100} />
          <select value={person.month} onChange={e => onChange('month', e.target.value)}>
            {Array.from({ length: 12 }, (_, i) => i + 1).map(m => <option key={m} value={m}>{m}월</option>)}
          </select>
          <input type="number" value={person.day} onChange={e => onChange('day', e.target.value)} placeholder="일" min={1} max={31} />
        </div>
      </div>

      <div className="form-row">
        <label>태어난 시간</label>
        <select value={person.hour} onChange={e => onChange('hour', e.target.value)}>
          {Array.from({ length: 24 }, (_, i) => i).map(h => <option key={h} value={h}>{h}시</option>)}
        </select>
      </div>
    </div>
  );

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

      {/* Hero */}
      <section className="hero" style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', paddingTop: 'var(--nav-height)' }}>
        <div className="container" style={{ textAlign: 'center' }}>
          <h1 className="serif" style={{ fontSize: 'var(--fs-5xl)', fontWeight: 900, letterSpacing: '-0.02em', lineHeight: 1.3, marginBottom: 'var(--space-3)' }}>
            <em style={{ fontStyle: 'normal', color: 'var(--color-jujube)' }}>궁합</em> 보기
          </h1>
          <p style={{ fontSize: 'var(--fs-lg)', color: 'var(--color-ink-soft)', fontWeight: 300, letterSpacing: '0.08em' }}>
            두 사람의 사주가 만들어내는 케미
          </p>
        </div>
      </section>

      {/* Form + Result */}
      <section className="section" style={{ background: 'var(--color-bg-deep)' }}>
        <div className="container" style={{ maxWidth: '900px' }}>
          <form onSubmit={handleAnalyze}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: 'var(--space-5)', alignItems: 'stretch', marginBottom: 'var(--space-8)' }}>
              <PersonForm person={person1} onChange={(field, value) => handleChange('p1', field, value)} title="첫 번째 분" accent="var(--color-jujube)" />
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 'var(--fs-2xl)', color: 'var(--color-gold)' }}>💞</div>
              <PersonForm person={person2} onChange={(field, value) => handleChange('p2', field, value)} title="두 번째 분" accent="var(--color-indigo)" />
            </div>

            {error && (
              <div style={{ background: 'var(--color-jujube-pale)', border: '1px solid var(--color-jujube)', borderRadius: 'var(--radius-md)', padding: 'var(--space-4)', marginBottom: 'var(--space-5)', fontSize: 'var(--fs-md)', color: 'var(--color-jujube)', textAlign: 'center' }}>
                {error}
              </div>
            )}

            <div style={{ textAlign: 'center' }}>
              <button
                type="submit"
                disabled={loading}
                className="btn btn-primary"
                style={{ fontSize: 'var(--fs-md)', padding: 'var(--space-4) var(--space-12)' }}
              >
                {loading ? '궁합 분석 중...' : '궁합 분석하기'}
              </button>
            </div>
          </form>

          {/* Result */}
          {loading && (
            <div style={{ textAlign: 'center', padding: 'var(--space-16) 0' }}>
              <div style={{ fontSize: 'var(--fs-4xl)', marginBottom: 'var(--space-4)' }}>🔮</div>
              <p style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)' }}>두 분의 사주를 비교 분석하고 있어요...</p>
            </div>
          )}

          {result && !loading && (
            <ScrollReveal>
              <div className="card" style={{ padding: 'var(--space-8)', marginTop: 'var(--space-8)', background: 'var(--color-bg-card)' }}>
                {/* Score */}
                <div style={{ textAlign: 'center', marginBottom: 'var(--space-8)' }}>
                  <div className="serif" style={{ fontSize: 'var(--fs-5xl)', fontWeight: 800, color: 'var(--color-jujube)' }}>
                    {result.score}점
                  </div>
                  <div style={{ fontSize: 'var(--fs-xl)', fontWeight: 600, color: 'var(--color-ink)', marginTop: 'var(--space-2)' }}>
                    {result.level}
                  </div>
                </div>

                {/* Element relation */}
                <div style={{ background: 'var(--color-bg-deep)', border: '1px solid var(--color-line)', borderRadius: 'var(--radius-lg)', padding: 'var(--space-6)', marginBottom: 'var(--space-6)' }}>
                  <div style={{ fontSize: 'var(--fs-sm)', fontWeight: 700, color: 'var(--color-gold)', letterSpacing: '0.08em', marginBottom: 'var(--space-2)' }}>
                    오행 관계
                  </div>
                  <h3 style={{ fontSize: 'var(--fs-lg)', fontWeight: 700, marginBottom: 'var(--space-2)' }}>{result.elementRelation}</h3>
                  <p style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)', lineHeight: 'var(--lh-relaxed)' }}>{result.elementDetail}</p>
                </div>

                {/* Summary */}
                <div style={{ marginBottom: 'var(--space-6)' }}>
                  <p style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink)', lineHeight: 'var(--lh-relaxed)' }}>{result.summary}</p>
                </div>

                {/* Strengths & Challenges */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-5)', marginBottom: 'var(--space-6)' }}>
                  <div className="card" style={{ padding: 'var(--space-5)', background: 'var(--color-bg-deep)', borderColor: 'var(--color-gold)' }}>
                    <h4 style={{ fontSize: 'var(--fs-md)', fontWeight: 700, color: 'var(--color-gold)', marginBottom: 'var(--space-3)' }}>💚 잘 맞는 포인트</h4>
                    <ul style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                      {result.strengths.map((s, i) => (
                        <li key={i} style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)', lineHeight: 'var(--lh-normal)', paddingLeft: 'var(--space-4)', position: 'relative' }}>
                          <span style={{ position: 'absolute', left: 0, color: 'var(--color-gold)' }}>✦</span>
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="card" style={{ padding: 'var(--space-5)', background: 'var(--color-jujube-pale)', borderColor: 'var(--color-jujube)' }}>
                    <h4 style={{ fontSize: 'var(--fs-md)', fontWeight: 700, color: 'var(--color-jujube)', marginBottom: 'var(--space-3)' }}>⚠️ 신경 쓸 부분</h4>
                    <ul style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-2)' }}>
                      {result.challenges.map((c, i) => (
                        <li key={i} style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)', lineHeight: 'var(--lh-normal)', paddingLeft: 'var(--space-4)', position: 'relative' }}>
                          <span style={{ position: 'absolute', left: 0, color: 'var(--color-jujube)' }}>•</span>
                          {c}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Advice */}
                <div className="card" style={{ padding: 'var(--space-6)', background: 'var(--color-jujube-pale)', borderColor: 'var(--color-jujube)', textAlign: 'center' }}>
                  <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-jujube)', fontWeight: 700, letterSpacing: '0.12em', marginBottom: 'var(--space-2)', textTransform: 'uppercase' }}>
                    조언
                  </div>
                  <p style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink)', lineHeight: 'var(--lh-relaxed)', fontFamily: 'var(--font-serif)' }}>
                    "{result.advice}"
                  </p>
                </div>

                <div style={{ textAlign: 'center', marginTop: 'var(--space-6)' }}>
                  <Link href="/" className="btn btn-ghost" style={{ fontSize: 'var(--fs-sm)' }}>
                    사주 풀이받기
                  </Link>
                </div>
              </div>
            </ScrollReveal>
          )}
        </div>
      </section>

      <Footer />

      <style jsx global>{`
        @media (max-width: 768px) {
          .section > .container > form > div:first-child {
            grid-template-columns: 1fr !important;
          }
          .section > .container > form > div:first-child > div:nth-child(2) {
            transform: rotate(90deg);
          }
        }
      `}</style>
    </>
  );
}