/**
 * manseryeok validation utilities
 */

import { HEAVENLY_STEMS, EARTHLY_BRANCHES, type HeavenlyStem, type EarthlyBranch, type Pillar } from './constants';

export function assertIntegerInRange(value: number, min: number, max: number, name: string): void {
  if (!Number.isInteger(value)) {
    throw new RangeError(`${name}은 정수여야 합니다: ${String(value)}`);
  }
  if (value < min || value > max) {
    throw new RangeError(`${name}은 ${min}~${max} 범위여야 합니다: ${value}`);
  }
}

export function assertFiniteNumber(value: number, name: string): void {
  if (!Number.isFinite(value)) {
    throw new RangeError(`${name}은 유한한 숫자여야 합니다: ${String(value)}`);
  }
}

export function assertHeavenlyStem(value: string, name = '천간'): asserts value is HeavenlyStem {
  if (!HEAVENLY_STEMS.includes(value as HeavenlyStem)) {
    throw new RangeError(`${name}은 유효한 천간이어야 합니다: ${String(value)}`);
  }
}

export function assertEarthlyBranch(value: string, name = '지지'): asserts value is EarthlyBranch {
  if (!EARTHLY_BRANCHES.includes(value as EarthlyBranch)) {
    throw new RangeError(`${name}은 유효한 지지여야 합니다: ${String(value)}`);
  }
}

export function assertPillar(value: unknown, name = '기둥'): asserts value is Pillar {
  if (value === null || typeof value !== 'object') {
    throw new TypeError(`${name}은 객체여야 합니다.`);
  }
  const pillar = value as Record<string, unknown>;
  assertHeavenlyStem(pillar.heavenlyStem as string, `${name}.heavenlyStem`);
  assertEarthlyBranch(pillar.earthlyBranch as string, `${name}.earthlyBranch`);
}

export function assertGender(value: string, name = '성별(gender)'): asserts value is 'male' | 'female' {
  if (value !== 'male' && value !== 'female') {
    throw new RangeError(`${name}은 'male' 또는 'female'이어야 합니다: ${String(value)}`);
  }
}

export function assertDayBoundary(value: string, name = '일 경계(dayBoundary)'): asserts value is 'midnight' | 'jasi' | 'splitJasi' {
  if (value !== 'midnight' && value !== 'jasi' && value !== 'splitJasi') {
    throw new RangeError(`${name}은 'midnight', 'jasi', 'splitJasi' 중 하나여야 합니다: ${String(value)}`);
  }
}