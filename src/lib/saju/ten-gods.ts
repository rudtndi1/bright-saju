/**
 * manseryeok 십성(십신) 계산
 */

import { HEAVENLY_STEMS, EARTHLY_BRANCHES, STEM_ELEMENTS, BRANCH_ELEMENTS, ELEMENT_GENERATES, ELEMENT_CONTROLS, BRANCH_MAIN_STEM, type HeavenlyStem, type EarthlyBranch, type FiveElement } from './constants';
import { assertHeavenlyStem, assertEarthlyBranch } from './validation';

export type TenGodKey = '비겁' | '겁재' | '식신' | '상관' | '편재' | '정재' | '편관' | '정관' | '편인' | '정인';

export const TEN_GOD_LABELS: Record<TenGodKey, string> = {
  비겁: '비견', 겁재: '겁재', 식신: '식신', 상관: '상관',
  편재: '편재', 정재: '정재', 편관: '편관', 정관: '정관',
  편인: '편인', 정인: '정인',
};

export const TEN_GOD_DESCRIPTIONS: Record<TenGodKey, string> = {
  비겁: '자신과 같은 오행, 같은 음양 — 자아, 형제, 동료, 경쟁',
  겁재: '자신과 같은 오행, 다른 음양 — 재물 다���, 형제간 경쟁',
  식신: '내가 생하는 오행, 같은 음양 — 재능, 표현, 먹거리, 즐거움',
  상관: '내가 생하는 오행, 다른 음양 — 창작, 반항, 기술, 말재주',
  편재: '내가 극하는 오행, 다른 음양 — 부동산, 재테크, 사업, 외재물',
  정재: '내가 극하는 오행, 같은 음양 — 월급, 정직한 수입, 저축, 아내',
  편관: '나를 극하는 오행, 다른 음양 — 직장, 권위, 법, 규율, 남편(여성)',
  정관: '나를 극하는 오행, 같은 음양 — 공직, 명예, 직위, 원칙, 남편(여성)',
  편인: '나를 생하는 오행, 다른 음양 — 학문, 자격증, 종교, 특수기술, 계모',
  정인: '나를 생하는 오행, 같은 음양 — 어머니, 교육, 보호, 자격, 문서',
};

/** 일간(나) 기준으로 다른 천간의 십성 구하기 */
export function getTenGod(dayStem: HeavenlyStem, targetStem: HeavenlyStem): TenGodKey {
  assertHeavenlyStem(dayStem);
  assertHeavenlyStem(targetStem);

  const dayElement = STEM_ELEMENTS[HEAVENLY_STEMS.indexOf(dayStem)];
  const targetElement = STEM_ELEMENTS[HEAVENLY_STEMS.indexOf(targetStem)];
  const dayYinYang = HEAVENLY_STEMS.indexOf(dayStem) % 2 === 0 ? '양' : '음';
  const targetYinYang = HEAVENLY_STEMS.indexOf(targetStem) % 2 === 0 ? '양' : '음';

  // 같은 오행
  if (dayElement === targetElement) {
    return dayYinYang === targetYinYang ? '비겁' : '겁재';
  }

  // 내가 생하는 오행 (식신/상관)
  if (ELEMENT_GENERATES[dayElement] === targetElement) {
    return dayYinYang === targetYinYang ? '식신' : '상관';
  }

  // 내가 극하는 오행 (편재/정재)
  if (ELEMENT_CONTROLS[dayElement] === targetElement) {
    return dayYinYang === targetYinYang ? '정재' : '편재';
  }

  // 나를 극하는 오행 (편관/정관)
  if (ELEMENT_CONTROLS[targetElement] === dayElement) {
    return dayYinYang === targetYinYang ? '정관' : '편관';
  }

  // 나를 생하는 오행 (편인/정인)
  if (ELEMENT_GENERATES[targetElement] === dayElement) {
    return dayYinYang === targetYinYang ? '정인' : '편인';
  }

  return '비겁'; // 기본�� (이론상 도달 불가)
}

/** 지지에 ��어있는 천간(장간)으로 십성 구하기 */
export function getHiddenStems(branch: EarthlyBranch): HeavenlyStem[] {
  assertEarthlyBranch(branch);

  const hidden: Record<EarthlyBranch, HeavenlyStem[]> = {
    자: ['계'],
    축: ['기', '계', '신'],
    인: ['갑', '병', '무'],
    묘: ['을'],
    진: ['무', '을', '계'],
    사: ['병', '무', '경'],
    오: ['정', '기'],
    미: ['기', '정', '을'],
    신: ['경', '무', '임'],
    유: ['신'],
    술: ['무', '신', '정'],
    해: ['임', '갑'],
  };

  return hidden[branch] || [];
}

/** 지지의 주기(主氣) 천간 */
export function getMainStem(branch: EarthlyBranch): HeavenlyStem {
  assertEarthlyBranch(branch);
  return BRANCH_MAIN_STEM[branch] as HeavenlyStem;
}

/** 지지의 모든 십성 구하기 (주기 + 중기 + 여기) */
export function getBranchTenGods(dayStem: HeavenlyStem, branch: EarthlyBranch): TenGodKey[] {
  const hiddenStems = getHiddenStems(branch);
  return hiddenStems.map(stem => getTenGod(dayStem, stem));
}

/** 사주 전체 십성 분석 */
export interface TenGodAnalysis {
  year: { stem: TenGodKey; branch: TenGodKey[] };
  month: { stem: TenGodKey; branch: TenGodKey[] };
  day: { stem: '일간'; branch: TenGodKey[] };
  time: { stem: TenGodKey; branch: TenGodKey[] };
  summary: Record<TenGodKey, number>;
}

export function analyzeTenGods(saju: { year: { heavenlyStem: HeavenlyStem; earthlyBranch: EarthlyBranch }; month: { heavenlyStem: HeavenlyStem; earthlyBranch: EarthlyBranch }; day: { heavenlyStem: HeavenlyStem; earthlyBranch: EarthlyBranch }; time: { heavenlyStem: HeavenlyStem; earthlyBranch: EarthlyBranch } }): TenGodAnalysis {
  const dayStem = saju.day.heavenlyStem;

  const yearStemGod = getTenGod(dayStem, saju.year.heavenlyStem);
  const monthStemGod = getTenGod(dayStem, saju.month.heavenlyStem);
  const timeStemGod = getTenGod(dayStem, saju.time.heavenlyStem);

  const yearBranchGods = getBranchTenGods(dayStem, saju.year.earthlyBranch);
  const monthBranchGods = getBranchTenGods(dayStem, saju.month.earthlyBranch);
  const dayBranchGods = getBranchTenGods(dayStem, saju.day.earthlyBranch);
  const timeBranchGods = getBranchTenGods(dayStem, saju.time.earthlyBranch);

  // 통계
  const allGods = [
    yearStemGod, ...yearBranchGods,
    monthStemGod, ...monthBranchGods,
    ...dayBranchGods,
    timeStemGod, ...timeBranchGods,
  ];

  const summary: Record<TenGodKey, number> = {
    비겁: 0, 겁재: 0, 식신: 0, 상관: 0,
    편재: 0, 정재: 0, 편관: 0, 정관: 0,
    편인: 0, 정인: 0,
  };

  allGods.forEach(god => { summary[god]++; });

  return {
    year: { stem: yearStemGod, branch: yearBranchGods },
    month: { stem: monthStemGod, branch: monthBranchGods },
    day: { stem: '일간', branch: dayBranchGods },
    time: { stem: timeStemGod, branch: timeBranchGods },
    summary,
  };
}