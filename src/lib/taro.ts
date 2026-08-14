/**
 * Tarot Card Data & Logic
 * 78장 (메이저 22 + 마이너 56)
 */

export interface TarotCard {
  id: number;
  name: string;
  nameEn: string;
  arcana: 'major' | 'minor';
  suit?: 'wands' | 'cups' | 'swords' | 'pentacles';
  number?: number;
  keywords: string[];
  meaningUpright: string;
  meaningReversed: string;
  description: string;
}

export const TAROT_CARDS: TarotCard[] = [
  // Major Arcana (0-21)
  { id: 0, name: '광대', nameEn: 'The Fool', arcana: 'major', keywords: ['새로운 시작', '순수', '자유', '모험'], meaningUpright: '새로운 여정의 시작, 무한한 가능성, 직관을 따름', meaningReversed: '무모함, 준비 부족, 경솔함, 방향 상실', description: '절벽 끝에 선 광대는 새로운 시작을 상징합니다. 두려움 없이 첫 발을 내��는 용기.' },
  { id: 1, name: '마법사', nameEn: 'The Magician', arcana: 'major', keywords: ['의지', '기술', '실현', '도구'], meaningUpright: '재능 발휘, 의지대로 현실 창조, 소통 능력', meaningReversed: '속임수, 재능 ��비, 조작, 계획 부족', description: '네 가지 원소의 도구를 가진 마법사. 의지만 있으면 무엇이든 실현할 수 있다.' },
  { id: 2, name: '여교황', nameEn: 'The High Priestess', arcana: 'major', keywords: ['직관', '비밀', '지혜', '내면'], meaningUpright: '��은 직관, 숨겨진 지식, 내면의 목소리 경청', meaningReversed: '직관 무시, 비밀 누설, 표면적 판단, 억��린 감정', description: '베일 뒤에 앉은 여교황. ��이 아닌 속을 볼 줄 아는 지혜.' },
  { id: 3, name: '여황제', nameEn: 'The Empress', arcana: 'major', keywords: ['풍요', '모성', '창조', '자연'], meaningUpright: '풍요로움, 창조적 에너지, 돌��, 번영', meaningReversed: '창조성 막��, 의존성, 소��함, 빈곤', description: '자연의 여신. 생명을 잉태하고 기르는 모성의 원리.' },
  { id: 4, name: '황제', nameEn: 'The Emperor', arcana: 'major', keywords: ['권위', '구조', '통제', '아버지'], meaningUpright: '안정된 권위, 체계적 리더십, 규칙 수호', meaningReversed: '독재, 경직��, 통제 불능, 무책임', description: '왕좌에 앉은 황제. 질서와 구조를 세우는 부성의 원리.' },
  { id: 5, name: '교황', nameEn: 'The Hierophant', arcana: 'major', keywords: ['전통', '가르침', '영적 권위', '관습'], meaningUpright: '전통적 지혜, ��토링, 제도권 교육, 신앙', meaningReversed: '독단, 전통 거부, 잘못된 가르침, 위선', description: '종교적 권위자. 검증된 전통과 가르침을 전수하는 역할.' },
  { id: 6, name: '연인', nameEn: 'The Lovers', arcana: 'major', keywords: ['사랑', '선택', '조화', '관계'], meaningUpright: '��은 유대, 중요한 선택, 가치관 공유, 연합', meaningReversed: '갈등, 잘못된 선택, 불균형, 이별', description: '에덴동산의 아��과 이브. 사랑을 위한 선택, 가치관의 일치.' },
  { id: 7, name: '전차', nameEn: 'The Chariot', arcana: 'major', keywords: ['승리', '의지', '전진', '통제'], meaningUpright: '어려움 극복, 강한 의지로 전진, 자기 통제', meaningReversed: '방향 상실, 통제 실패, 공격성, 패배', description: '두 마리 스��크스를 몰고 나아가는 전차. 상반된 힘을 통합해 전진.' },
  { id: 8, name: '��', nameEn: 'Strength', arcana: 'major', keywords: ['용기', '인내', '내면의 힘', '연민'], meaningUpright: '내면의 용기, 부드러운 힘으로 제압, 인내', meaningReversed: '자기 의심, 충동적, 나약함, 잔인함', description: '사자의 입을 벌리는 여인. 힘으로 누르는 게 아닌 사랑으로 다스림.' },
  { id: 9, name: '은둔자', nameEn: 'The Hermit', arcana: 'major', keywords: ['성찰', '고독', '내면 탐구', '현자'], meaningUpright: '��은 성찰, 내면의 빛 찾기, 현명한 고독', meaningReversed: '고립, 회피, 우울, 지혜 거부', description: '등��을 든 은둔자. 바깥이 아닌 안을 비추는 지혜의 빛.' },
  { id: 10, name: '운명의 수레바��', nameEn: 'Wheel of Fortune', arcana: 'major', keywords: ['순환', '운명', '변화', '기회'], meaningUpright: '운명의 전환점, 좋은 순환, 예상치 못한 행운', meaningReversed: '불운, 저항, 순환 정체, 통제 불능', description: '돌아가는 수레바��. 오르막이 있으면 내리막도 있다. 순환을 받아들임.' },
  { id: 11, name: '정의', nameEn: 'Justice', arcana: 'major', keywords: ['균형', '공정', '진실', '인과'], meaningUpright: '공정한 판단, 인과응보, 진실 규명, 법적 문제 해결', meaningReversed: '편향, 불공정, 거짓, 법적 분쟁', description: '저울과 칼을 든 정의의 여신. 감정 아닌 원칙으로 판단.' },
  { id: 12, name: '매달린 남자', nameEn: 'The Hanged Man', arcana: 'major', keywords: ['희생', '관점 전환', '기다림', '내려놓음'], meaningUpright: '자발적 희생, 새로운 관점, 내려놓음으로 얻음', meaningReversed: '희생 강요, 고집, 멈��, 회피', description: '거꾸로 매달린 남자. 세상을 거꾸로 보니 새로운 진실이 보인다.' },
  { id: 13, name: '죽음', nameEn: 'Death', arcana: 'major', keywords: ['끝', '변화', '재생', '필연'], meaningUpright: '필연적 종결, 근본적 변화, 새 출발을 위한 끝', meaningReversed: '변화 저항, 정체, 느린 종말, 미련', description: '백마 탄 죽음. 끝이 있어야 새로운 시작이 온다. 두려움 아닌 수용.' },
  { id: 14, name: '절제', nameEn: 'Temperance', arcana: 'major', keywords: ['조화', '절제', '치유', '중용'], meaningUpright: '균형 잡힌 삶, 치유의 과정, 인내와 조화', meaningReversed: '과도함, 불균형, 성급함, 극단', description: '두 잔 사이에 물을 ��는 천사. 극단을 피하고 중용을 지���.' },
  { id: 15, name: '악마', nameEn: 'The Devil', arcana: 'major', keywords: ['속박', '욕망', '집착', '그림자'], meaningUpright: '물질적 속박, 중독적 패턴, 그림자 직면, 환상', meaningReversed: '해방, 자각, 속박에서 벗어남, 각성', description: '사슬에 묶인 남녀. 스스로 채운 ��쇄. 자각만으로도 풀린다.' },
  { id: 16, name: '��', nameEn: 'The Tower', arcana: 'major', keywords: ['��괴', '충격', '해방', '각성'], meaningUpright: '갑작스러운 붕괴, 거짓 구조 파괴, 강제적 각성', meaningReversed: '��괴 지연, 내면의 무너짐, 공포 회피', description: '번개 맞은 탑. 견고해 보이던 가짜가 무너지고 진짜가 드러난다.' },
  { id: 17, name: '별', nameEn: 'The Star', arcana: 'major', keywords: ['희망', '영감', '치유', '평온'], meaningUpright: '어�� 속 희망, 영감의 ��, 치유와 ��신', meaningReversed: '희망 상실, 냉소, 영감 고갈, 환멸', description: '별빛 아래 물 따르는 여인. 절망 뒤엔 항상 별이 빛난다.' },
  { id: 18, name: '달', nameEn: 'The Moon', arcana: 'major', keywords: ['환상', '무의식', '불안', '직관'], meaningUpright: '흐릿한 진실, 무의식의 메시지, 직관 따름', meaningReversed: '환상 ��어남, 혼란 해소, 진실 직면, 공포 극복', description: '달빛 아래 ��는 개와 ��대. 보이는 게 다가 아니다. 직관으로 ����어라.' },
  { id: 19, name: '태양', nameEn: 'The Sun', arcana: 'major', keywords: ['성공', '기��', '활력', '진실'], meaningUpright: '눈부신 성공, 순수한 기��, 활력 충만, 진실 드러남', meaningReversed: '일시적 좌절, 자만, 과신, 기�� 지연', description: '해바라기 아래 아이. 모든 그림자가 사라진 완전한 빛.' },
  { id: 20, name: '심판', nameEn: 'Judgement', arcana: 'major', keywords: ['부활', '심판', '소명', '용서'], meaningUpright: '과거 청산, 소명 각성, 용서와 화해, 새 생명', meaningReversed: '자기 비판, 과거 집착, 소명 거부, 심판 공포', description: '나�� 소리에 일어나는 죽은 자들. 과거를 심판받고 새로 태어나라.' },
  { id: 21, name: '세계', nameEn: 'The World', arcana: 'major', keywords: ['완성', '통합', '성취', '여정의 끝'], meaningUpright: '목표 달성, 완전한 통합, 여정의 완성, 보상', meaningReversed: '미완성, 지연, 통합 실패, 공허함', description: '월계관 안의 무희. 한 주기가 끝나고 새로운 차원으로 진입.' },
];

// Minor Arcana 생성 (56장)
const SUITS = [
  { key: 'wands', name: '완드', element: '불', keywords: ['열정', '행동', '창의', '의지'] },
  { key: 'cups', name: '컵', element: '물', keywords: ['감정', '사랑', '직관', '관계'] },
  { key: 'swords', name: '소드', element: '바람', keywords: ['지성', '갈등', '진실', '결단'] },
  { key: 'pentacles', name: '��타클', element: '��', keywords: ['물질', '일', '건강', '현실'] },
] as const;

const MINOR_NAMES = [
  '에이스', '2', '3', '4', '5', '6', '7', '8', '9', '10',
  '페이지', '나이트', '��', '��',
];

SUITS.forEach(suit => {
  MINOR_NAMES.forEach((numName, idx) => {
    const number = idx + 1;
    const isCourt = number >= 11;
    TAROT_CARDS.push({
      id: 22 + SUITS.indexOf(suit) * 14 + idx,
      name: `${suit.name} ${numName}`,
      nameEn: `${suit.key.charAt(0).toUpperCase() + suit.key.slice(1)} ${numName}`,
      arcana: 'minor',
      suit: suit.key,
      number,
      keywords: [...suit.keywords, isCourt ? '인물' : '상황'],
      meaningUpright: `${suit.name} ${numName} 정방향: ${suit.keywords.join(', ')}의 긍정적 발현`,
      meaningReversed: `${suit.name} ${numName} 역방향: ${suit.keywords.join(', ')}의 막�� 또는 과도`,
      description: `${suit.element}의 원소 ${suit.name} ${numName}. ${isCourt ? '궁정 카드로 인물을 나타��' : `��자 ${number}의 에너지 발현`}`,
    });
  });
});

export function getRandomCards(count: number, allowReversed = true): { card: TarotCard; reversed: boolean }[] {
  const shuffled = [...TAROT_CARDS].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count).map(card => ({
    card,
    reversed: allowReversed && Math.random() < 0.5,
  }));
}

export function getCardById(id: number): TarotCard | undefined {
  return TAROT_CARDS.find(c => c.id === id);
}

export const SPREADS = {
  one: { name: '원카드', count: 1, description: '간단한 질문, 하루 운세' },
  three: { name: '쓰리카드', count: 3, description: '과거-현재-미래, 상황-원인-해결' },
  celtic: { name: '���� 크로스', count: 10, description: '종합적 상황 분석, 심층 리딩' },
} as const;

export type SpreadType = keyof typeof SPREADS;