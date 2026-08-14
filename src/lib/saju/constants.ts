/**
 * manseryeok (https://github.com/yhj1024/manseryeok)
 * Copyright (c) 2025 Yoohyojun
 * MIT License
 */

/** 천간 (Heavenly Stems) */
export const HEAVENLY_STEMS = ['갑', '을', '병', '정', '무', '기', '경', '신', '임', '계'] as const;
export const HEAVENLY_STEMS_HANJA = ['甲', '��', '��', '丁', '��', '己', '��', '辛', '��', '��'] as const;

/** 지지 (Earthly Branches) */
export const EARTHLY_BRANCHES = ['자', '축', '인', '묘', '진', '사', '오', '미', '신', '유', '술', '해'] as const;
export const EARTHLY_BRANCHES_HANJA = ['子', '��', '��', '��', '��', '��', '午', '未', '申', '��', '��', '��'] as const;

export const YIN_YANG = ['양', '음'] as const;
export const FIVE_ELEMENTS = ['목', '화', '토', '금', '수'] as const;

export const STEM_ELEMENTS = ['목', '목', '화', '화', '토', '토', '금', '금', '수', '수'] as const;

export const BRANCH_ELEMENTS = [
  '수', // 자
  '토', // 축
  '목', // 인
  '목', // 묘
  '토', // 진
  '화', // 사
  '화', // 오
  '토', // 미
  '금', // 신
  '금', // 유
  '토', // 술
  '수', // 해
] as const;

export const BRANCH_MAIN_STEM: Record<string, string> = {
  자: '계', 축: '기', 인: '갑', 묘: '을', 진: '무', 사: '병',
  오: '정', 미: '기', 신: '경', 유: '신', 술: '무', 해: '임',
};

export const MONTH_BRANCHES: Record<number, string> = {
  1: '인', 2: '묘', 3: '진', 4: '사', 5: '오', 6: '미',
  7: '신', 8: '유', 9: '술', 10: '해', 11: '자', 12: '축',
};

export const ELEMENT_GENERATES: Record<string, string> = {
  목: '화', 화: '토', 토: '금', 금: '수', 수: '목',
};

export const ELEMENT_CONTROLS: Record<string, string> = {
  목: '토', 토: '수', 수: '화', 화: '금', 금: '목',
};

export const TEN_GOD_HANJA: Record<string, string> = {
  비겁: '比肩', 겁재: '����', 식신: '食神', 상관: '傷官',
  편재: '����', 정재: '正��', 편관: '��官', 정관: '正官',
  편인: '��印', 정인: '正印',
};

export const DAY_PILLAR_ANCHOR = {
  year: 1992, month: 10, day: 24, ganjiIndex: 9,
} as const;

export type HeavenlyStem = typeof HEAVENLY_STEMS[number];
export type EarthlyBranch = typeof EARTHLY_BRANCHES[number];
export type FiveElement = typeof FIVE_ELEMENTS[number];
export type YinYang = typeof YIN_YANG[number];
export type TenGod = keyof typeof TEN_GOD_HANJA;

export interface Pillar {
  heavenlyStem: HeavenlyStem;
  earthlyBranch: EarthlyBranch;
}

export interface SajuResult {
  year: Pillar;
  month: Pillar;
  day: Pillar;
  time: Pillar;
}