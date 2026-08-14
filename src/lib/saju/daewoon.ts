/**
 * manseryeok 대운(大運) 계산
 */

import { HEAVENLY_STEMS, EARTHLY_BRANCHES, MONTH_BRANCHES, type HeavenlyStem, type EarthlyBranch, type Pillar } from './constants';
import { getMonthPillar, getDayPillar } from './calendar';
import { assertGender } from './validation';

export interface DaewoonItem {
  seq: number;
  startAge: number;
  endAge: number;
  startYear: number;
  endYear: number;
  pillar: Pillar;
  direction: 'forward' | 'reverse';
}

export interface DaewoonResult {
  items: DaewoonItem[];
  currentDaewoon: DaewoonItem | null;
  nextDaewoon: DaewoonItem | null;
}

/** 대운 시작 나이 계산 (절기 기준 간이 계산) */
export function calculateDaewoonStartAge(
  birthYear: number,
  birthMonth: number,
  birthDay: number,
  birthHour: number,
  gender: 'male' | 'female',
  isLunar: boolean
): number {
  // 간이 계산: 다음 절기까지의 일수 / 3 (1일 = 3개월 = 0.25세)
  // 실제로는 정확한 절입시각 계산 필요
  const monthPillar = getMonthPillar(birthYear, birthMonth);
  const monthBranch = monthPillar.earthlyBranch;
  const monthBranchIndex = EARTHLY_BRANCHES.indexOf(monthBranch);

  // 양력 기준 대략적 절기일 (입춘~대한 24절기)
  const solarTerms = [
    { month: 2, day: 4 },  // 입춘
    { month: 3, day: 6 },  // 경��
    { month: 4, day: 5 },  // 청명
    { month: 5, day: 6 },  // 입하
    { month: 6, day: 6 },  // 망종
    { month: 7, day: 7 },  // 소서
    { month: 8, day: 7 },  // 입추
    { month: 9, day: 8 },  // 백로
    { month: 10, day: 8 }, // 한로
    { month: 11, day: 7 }, // 입동
    { month: 12, day: 7 }, // 대설
    { month: 1, day: 6 },  // 소한 (다음해)
  ];

  // 태어난 월의 절기 찾기
  let currentTermIndex = monthBranchIndex * 2; // 월지 1개 = 2절기
  if (currentTermIndex >= 24) currentTermIndex -= 24;

  const currentTerm = solarTerms[currentTermIndex % 12];
  const nextTerm = solarTerms[(currentTermIndex + 1) % 12];

  // 다음 절기까지 일수 계산 (간이)
  const birthDate = new Date(birthYear, birthMonth - 1, birthDay);
  let nextTermDate: Date;

  if (nextTerm.month > birthMonth || (nextTerm.month === birthMonth && nextTerm.day >= birthDay)) {
    nextTermDate = new Date(birthYear, nextTerm.month - 1, nextTerm.day);
  } else {
    nextTermDate = new Date(birthYear + 1, nextTerm.month - 1, nextTerm.day);
  }

  const diffDays = Math.max(1, Math.ceil((nextTermDate.getTime() - birthDate.getTime()) / 86400000));
  const startAge = Math.round(diffDays / 3 * 10) / 10; // 3일 = 1세

  return startAge;
}

/** 대운 리스트 생성 */
export function generateDaewoon(
  birthYear: number,
  birthMonth: number,
  birthDay: number,
  birthHour: number,
  gender: 'male' | 'female',
  isLunar: boolean,
  currentYear: number = new Date().getFullYear()
): DaewoonResult {
  assertGender(gender);

  const monthPillar = getMonthPillar(birthYear, birthMonth);
  const monthStem = monthPillar.heavenlyStem;
  const monthBranch = monthPillar.earthlyBranch;

  const monthStemIndex = HEAVENLY_STEMS.indexOf(monthStem);
  const monthBranchIndex = EARTHLY_BRANCHES.indexOf(monthBranch);

  // 순행/역행 결정
  const yearStemIndex = (birthYear - 4) % 10;
  const yearYinYang = yearStemIndex % 2 === 0 ? '양' : '음';
  const isMale = gender === 'male';

  // 양간 남자 / 음간 여자 = 순행, 반대 = 역행
  const isForward = (yearYinYang === '양' && isMale) || (yearYinYang === '음' && !isMale);

  const startAge = calculateDaewoonStartAge(birthYear, birthMonth, birthDay, birthHour, gender, isLunar);
  let currentAge = startAge;
  let currentYearOffset = Math.floor(startAge);

  const items: DaewoonItem[] = [];

  for (let i = 0; i < 12; i++) {
    let stemIndex: number;
    let branchIndex: number;

    if (isForward) {
      stemIndex = (monthStemIndex + i + 1) % 10;
      branchIndex = (monthBranchIndex + i + 1) % 12;
    } else {
      stemIndex = (monthStemIndex - i - 1 + 100) % 10;
      branchIndex = (monthBranchIndex - i - 1 + 120) % 12;
    }

    const pillar: Pillar = {
      heavenlyStem: HEAVENLY_STEMS[stemIndex],
      earthlyBranch: EARTHLY_BRANCHES[branchIndex],
    };

    const startYear = birthYear + currentYearOffset;
    const endYear = startYear + 9; // 대운은 10년

    items.push({
      seq: i + 1,
      startAge: currentAge,
      endAge: currentAge + 10,
      startYear,
      endYear,
      pillar,
      direction: isForward ? 'forward' : 'reverse',
    });

    currentAge += 10;
    currentYearOffset += 10;
  }

  // 현재 대운 찾기
  const currentDaewoon = items.find(item => currentYear >= item.startYear && currentYear <= item.endYear) || null;
  const currentIndex = items.findIndex(item => item === currentDaewoon);
  const nextDaewoon = currentIndex >= 0 && currentIndex + 1 < items.length ? items[currentIndex + 1] : null;

  return { items, currentDaewoon, nextDaewoon };
}