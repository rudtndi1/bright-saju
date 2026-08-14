'use client';

import { useState, useEffect } from 'react';
import { Navigation } from '@/components/Navigation';
import { Footer } from '@/components/Footer';
import { ScrollReveal } from '@/components/ScrollReveal';
import { getCompleteSaju } from '@/lib/saju';

interface DailyFortune {
  date: string;
  ganzhi: string;
  luckScore: number;
  overall: string;
  love: string;
  career: string;
  money: string;
  health: string;
  advice: string;
  luckyColor: string;
  luckyNumber: number;
  luckyDirection: string;
  avoidDirection: string;
}

const GANZHI_DAILY = [
  '갑자', '을축', '병인', '정묘', '무진', '기사', '경오', '신미', '임신', '계유',
  '갑술', '을해', '병자', '정축', '무인', '기묘', '경진', '신사', '임오', '계미',
  '갑신', '을유', '병술', '정해', '무자', '기축', '경인', '신묘', '임진', '계사',
  '갑오', '을미', '병신', '정유', '무술', '기해', '경자', '신축', '임인', '계묘',
  '갑진', '을사', '병오', '정미', '무신', '기유', '경술', '신해', '임자', '계축',
  '갑인', '을묘', '병진', '정사', '무오', '기미', '경신', '신유', '임술', '계해',
];

const DAILY_TEMPLATES = {
  overall: [
    '오늘은 {ganzhi} 일진으로, {element} 기운이 강하게 작용합니다. 전반적으로 {mood}한 흐름입니다.',
    '{ganzhi}일의 에너지가 당신을 감을�니다. {keyword}이(가) 중요한 열쇠가 될 하루입니다.',
    '일진 {ganzhi}가 가져온 {element}의 힘. {action}에 집중하면 좋은 결과가 있겠습니다.',
  ],
  love: [
    '연애운: {desc}. {action}하면 인연이 깊어집니다.',
    '관계운: {desc}. 솔직한 {keyword}이(가) 필요합니다.',
    '대인관계: {desc}. {keyword}을(를) 베풀면 돌아을니다.',
  ],
  career: [
    '직장/학업: {desc}. {keyword}을(를) 발휘하세요.',
    '일/공부: {desc}. {action}하면 성과가 나타을니다.',
    '커리어: {desc}. {keyword}이(가) 승부처입니다.',
  ],
  money: [
    '금전운: {desc}. {keyword} 지출은 피하세요.',
    '재물운: {desc}. {action}하면 이익이 생을니다.',
    '을흐름: {desc}. {keyword}이(가) 열쇠입니다.',
  ],
  health: [
    '건강: {desc}. {body} 관리에 신경 쓰세요.',
    '컨디션: {desc}. {action}이(가) 좋습니다.',
    '신체: {desc}. {keyword} 을취를 권합니다.',
  ],
};

const ELEMENT_KEYWORDS: Record<string, { mood: string; keyword: string; action: string; body: string; avoid: string; color: string; number: number; direction: string; avoidDir: string }> = {
  목: { mood: '활기찬', keyword: '시작', action: '새로운 시도', body: '간/눈', avoid: '과로', color: '연두색', number: 3, direction: '동쪽', avoidDir: '서쪽' },
  화: { mood: '열정적인', keyword: '표현', action: '적극적 소통', body: '심장/을액', avoid: '충동', color: '을간색', number: 9, direction: '남쪽', avoidDir: '북쪽' },
  토: { mood: '안정된', keyword: '실행', action: '꾸준한 노력', body: '비위/소화', avoid: '고집', color: '노란색', number: 5, direction: '중앙', avoidDir: '북동쪽' },
  금: { mood: '을은', keyword: '결단', action: '정리/선택', body: '폐/피부', avoid: '경직', color: '을색', number: 7, direction: '서쪽', avoidDir: '동남쪽' },
  수: { mood: '유연한', keyword: '흐름', action: '순응과 적응', body: '신장/방광', avoid: '을기', color: '검은색', number: 1, direction: '북쪽', avoidDir: '남서쪽' },
};

const ADVICE_LIST = [
  '오늘 마주치는 작은 우연도 의미가 있습니다. 흘려보내지 마세요.',
  '마음이 끌리는 방향으로 한 발짝 내을어 보세요.',
  '말 한마디가 인연을 만듭니다. 따뜻한 말을 건네보세요.',
  '계획한 일이 있다면 미루지 말고 시작하세요.',
  '몸이 보내는 신호를 귀 기울여 들으세요.',
  '지난 일은 과거에 두고, 지금에 집중하세요.',
  '어려움이 와도 그것은 지나가는 구름입니다.',
  '감사한 일을 세 가지 적어보세요. 기운이 바을니다.',
];

function getDailyFortune(date: Date, birthDate?: Date): DailyFortune {
  const dayOfYear = Math.floor((date.getTime() - new Date(date.getFullYear(), 0, 0).getTime()) / 86400000);
  const ganzhiIndex = (dayOfYear + 9) % 60; // 2024-01-01 기준 보정
  const ganzhi = GANZHI_DAILY[ganzhiIndex % 10] + GANZHI_DAILY[(ganzhiIndex % 12 + 12) % 12].slice(1);

  // 일간 기준 오행
  const dayStem = ganzhi[0];
  const stemElements: Record<string, string> = { 갑: '목', 을: '목', 병: '화', 정: '화', 무: '토', 기: '토', 경: '금', 신: '금', 임: '수', 계: '수' };
  const element = stemElements[dayStem] || '목';
  const data = ELEMENT_KEYWORDS[element];

  // 생일이 있으면 개인화
  let personalized = '';
  if (birthDate) {
    const birthYear = birthDate.getFullYear();
    const birthMonth = birthDate.getMonth() + 1;
    const birthDay = birthDate.getDate();
    const birthGanzhiIdx = (birthYear * 12 + birthMonth * 3 + birthDay) % 60;
    if (birthGanzhiIdx === ganzhiIndex % 60) {
      personalized = ' 오늘은 당신의 생일 간지와 같은 날! 특별한 기운이 돕습니다. ';
    }
  }

  const templates = DAILY_TEMPLATES;
  const pick = (arr: string[]) => arr[Math.floor(Math.random() * arr.length)];

  return {
    date: date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }),
    ganzhi,
    luckScore: 60 + Math.floor(Math.random() * 35),
    overall: pick(templates.overall).replace('{ganzhi}', ganzhi).replace('{element}', element).replace('{mood}', data.mood).replace('{keyword}', data.keyword).replace('{action}', data.action) + personalized,
    love: pick(templates.love).replace('{desc}', ['좋은 만남이', '따뜻한 대화가', '을은 이해가'][Math.floor(Math.random() * 3)]).replace('{action}', ['다가가기', '경청하기', '표현하기'][Math.floor(Math.random() * 3)]).replace('{keyword}', data.keyword),
    career: pick(templates.career).replace('{desc}', ['순조로운 진행이', '새로운 아이디어가', '인정받는 날이'][Math.floor(Math.random() * 3)]).replace('{keyword}', data.keyword).replace('{action}', ['집중하기', '도전하기', '협력하기'][Math.floor(Math.random() * 3)]),
    money: pick(templates.money).replace('{desc}', ['수입이 늘어날', '절약이 빛날', '투자 기회가'][Math.floor(Math.random() * 3)]).replace('{keyword}', data.avoid).replace('{action}', ['저축하기', '계획 세우기', '검토하기'][Math.floor(Math.random() * 3)]),
    health: pick(templates.health).replace('{desc}', ['컨디션이 좋은', '가벼운 운동이', '충분한 휴식이'][Math.floor(Math.random() * 3)]).replace('{body}', data.body).replace('{action}', ['산책', '스트레칭', '명상'][Math.floor(Math.random() * 3)]).replace('{keyword}', ['따뜻한 차', '물', '비타민'][Math.floor(Math.random() * 3)]),
    advice: ADVICE_LIST[Math.floor(Math.random() * ADVICE_LIST.length)],
    luckyColor: data.color,
    luckyNumber: data.number,
    luckyDirection: data.direction,
    avoidDirection: data.avoidDir,
  };
}

export default function DailyPage() {
  const [mounted, setMounted] = useState(false);
  const [birthDate, setBirthDate] = useState<string>('');
  const [fortune, setFortune] = useState<DailyFortune | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());

  useEffect(() => {
    setMounted(true);
    // 오늘 운세 자동 계산
    const today = new Date();
    setFortune(getDailyFortune(today, birthDate ? new Date(birthDate) : undefined));
  }, []);

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const date = new Date(e.target.value);
    setSelectedDate(date);
    setFortune(getDailyFortune(date, birthDate ? new Date(birthDate) : undefined));
  };

  const handleBirthDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setBirthDate(e.target.value);
    if (fortune) {
      setFortune(getDailyFortune(selectedDate, e.target.value ? new Date(e.target.value) : undefined));
    }
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

      {/* Hero */}
      <section className="hero" style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', paddingTop: 'var(--nav-height)' }}>
        <div className="container" style={{ textAlign: 'center' }}>
          <h1 className="serif" style={{ fontSize: 'var(--fs-5xl)', fontWeight: 900, letterSpacing: '-0.02em', lineHeight: 1.3, marginBottom: 'var(--space-3)' }}>
            <em style={{ fontStyle: 'normal', color: 'var(--color-gold)' }}>오늘</em> 운세
          </h1>
          <p style={{ fontSize: 'var(--fs-lg)', color: 'var(--color-ink-soft)', fontWeight: 300, letterSpacing: '0.08em' }}>
            {fortune?.date || '오늘'}의 흐름을 읽어드립니다
          </p>
        </div>
      </section>

      {/* Settings */}
      <section className="section" style={{ background: 'var(--color-bg-deep)' }}>
        <div className="container" style={{ maxWidth: '600px' }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-4)', justifyContent: 'center', alignItems: 'center' }}>
            <div>
              <label htmlFor="birthDate" style={{ display: 'block', fontSize: 'var(--fs-sm)', color: 'var(--color-ink-soft)', marginBottom: 'var(--space-1)' }}>
                생년월일 (선택, 더 정확한 운세)
              </label>
              <input
                type="date"
                id="birthDate"
                value={birthDate}
                onChange={handleBirthDateChange}
                max={new Date().toISOString().split('T')[0]}
                style={{ padding: 'var(--space-3) var(--space-4)', border: '1px solid var(--color-line)', borderRadius: 'var(--radius-md)', background: 'var(--color-bg)', color: 'var(--color-ink)', fontSize: 'var(--fs-md)', minWidth: '180px' }}
              />
            </div>
            <div>
              <label htmlFor="targetDate" style={{ display: 'block', fontSize: 'var(--fs-sm)', color: 'var(--color-ink-soft)', marginBottom: 'var(--space-1)' }}>
                날짜 선택
              </label>
              <input
                type="date"
                id="targetDate"
                value={selectedDate.toISOString().split('T')[0]}
                onChange={handleDateChange}
                style={{ padding: 'var(--space-3) var(--space-4)', border: '1px solid var(--color-line)', borderRadius: 'var(--radius-md)', background: 'var(--color-bg)', color: 'var(--color-ink)', fontSize: 'var(--fs-md)', minWidth: '180px' }}
              />
            </div>
          </div>
        </div>
      </section>

      {/* Main Fortune */}
      {fortune && (
        <>
          <ScrollReveal>
            <section className="section">
              <div className="container" style={{ maxWidth: '600px' }}>
                {/* Overall Score & Ganzhi */}
                <div className="card" style={{ padding: 'var(--space-8)', textAlign: 'center', marginBottom: 'var(--space-6)' }}>
                  <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'center', gap: 'var(--space-4)', marginBottom: 'var(--space-4)', flexWrap: 'wrap' }}>
                    <span className="serif" style={{ fontSize: 'var(--fs-5xl)', fontWeight: 700, color: 'var(--color-gold)' }}>
                      {fortune.luckScore}
                    </span>
                    <span style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)' }}>점 / 100</span>
                  </div>
                  <div style={{ fontSize: 'var(--fs-2xl)', fontWeight: 700, color: 'var(--color-jujube)', fontFamily: 'var(--font-serif)', marginBottom: 'var(--space-2)' }}>
                    {fortune.ganzhi}일
                  </div>
                  <p style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)', lineHeight: 'var(--lh-relaxed)' }}>
                    {fortune.overall}
                  </p>
                </div>

                {/* Lucky Items */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 'var(--space-4)', marginBottom: 'var(--space-6)' }}>
                  <div className="card" style={{ padding: 'var(--space-5)', textAlign: 'center' }}>
                    <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-jujube)', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 'var(--space-1)' }}>행운의 색</div>
                    <div style={{ fontSize: 'var(--fs-xl)', fontWeight: 700, color: 'var(--color-ink)' }}>{fortune.luckyColor}</div>
                  </div>
                  <div className="card" style={{ padding: 'var(--space-5)', textAlign: 'center' }}>
                    <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-jujube)', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 'var(--space-1)' }}>행운의 숫자</div>
                    <div style={{ fontSize: 'var(--fs-xl)', fontWeight: 700, color: 'var(--color-ink)' }}>{fortune.luckyNumber}</div>
                  </div>
                  <div className="card" style={{ padding: 'var(--space-5)', textAlign: 'center' }}>
                    <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-jujube)', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 'var(--space-1)' }}>길방향</div>
                    <div style={{ fontSize: 'var(--fs-lg)', fontWeight: 700, color: 'var(--color-ink)' }}>{fortune.luckyDirection}</div>
                  </div>
                  <div className="card" style={{ padding: 'var(--space-5)', textAlign: 'center', background: 'var(--color-jujube-pale)', borderColor: 'var(--color-jujube)' }}>
                    <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-jujube)', fontWeight: 700, letterSpacing: '0.08em', marginBottom: 'var(--space-1)' }}>을방향</div>
                    <div style={{ fontSize: 'var(--fs-lg)', fontWeight: 700, color: 'var(--color-jujube)' }}>{fortune.avoidDirection}</div>
                  </div>
                </div>
              </div>
            </section>
          </ScrollReveal>

          {/* Categories */}
          <ScrollReveal delay={100}>
            <section className="section" style={{ background: 'var(--color-bg-deep)' }}>
              <div className="container" style={{ maxWidth: '800px' }}>
                <h2 className="section-title serif" style={{ textAlign: 'center', marginBottom: 'var(--space-10)' }}>분야별 운세</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-5)' }}>
                  {[
                    { icon: '을을', title: '연애·관계', content: fortune.love, color: 'var(--color-jujube)' },
                    { icon: '을을', title: '직장·학업', content: fortune.career, color: 'var(--color-indigo)' },
                    { icon: '을을', title: '금전·재물', content: fortune.money, color: 'var(--color-gold)' },
                    { icon: '을을', title: '건강·컨디션', content: fortune.health, color: '#2e7d32' },
                  ].map((item, idx) => (
                    <div key={idx} className="card" style={{ padding: 'var(--space-6)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-3)', marginBottom: 'var(--space-4)' }}>
                        <span style={{ fontSize: 'var(--fs-xl)' }}>{item.icon}</span>
                        <h3 style={{ fontSize: 'var(--fs-lg)', fontWeight: 700, color: item.color }}>{item.title}</h3>
                      </div>
                      <p style={{ fontSize: 'var(--fs-md)', color: 'var(--color-ink-soft)', lineHeight: 'var(--lh-relaxed)' }}>{item.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          </ScrollReveal>

          {/* Advice */}
          <ScrollReveal delay={200}>
            <section className="section">
              <div className="container" style={{ maxWidth: '600px', textAlign: 'center' }}>
                <div className="card" style={{ padding: 'var(--space-8)', background: 'var(--color-jujube-pale)', borderColor: 'var(--color-jujube)' }}>
                  <div style={{ fontSize: 'var(--fs-xs)', color: 'var(--color-jujube)', fontWeight: 700, letterSpacing: '0.12em', marginBottom: 'var(--space-3)', textTransform: 'uppercase' }}>
                    오늘의 한 마디
                  </div>
                  <p style={{ fontSize: 'var(--fs-lg)', color: 'var(--color-ink)', lineHeight: 'var(--lh-relaxed)', fontFamily: 'var(--font-serif)' }}>
                    "{fortune.advice}"
                  </p>
                </div>
              </div>
            </section>
          </ScrollReveal>
        </>
      )}

      <Footer />

      <style jsx global>{`
        @media (max-width: 600px) {
          .section { padding: var(--space-12) 0 !important; }
        }
      `}</style>
    </>
  );
}