/**
 * manseryeok - Korean Saju (Four Pillars) Calculation Library
 * Ported to TypeScript for SAJU HUB
 * Original: https://github.com/yhj1024/manseryeok (MIT License)
 */

export * from './constants';
export * from './validation';
export * from './elements';
export * from './lunar-data';
export * from './calendar';
export * from './ten-gods';
export * from './daewoon';

// 편의 함수: 한 번에 사주 + 십성 + 대운 계산
import { calculateSaju, type SajuInput, type SajuOutput } from './calendar';
import { analyzeTenGods, type TenGodAnalysis } from './ten-gods';
import { generateDaewoon, type DaewoonResult } from './daewoon';

export interface CompleteSajuResult {
  saju: SajuOutput;
  tenGods: TenGodAnalysis;
  daewoon: DaewoonResult;
}

export function getCompleteSaju(input: SajuInput, currentYear?: number): CompleteSajuResult {
  const saju = calculateSaju(input);
  const tenGods = analyzeTenGods(saju);
  const daewoon = generateDaewoon(
    saju.lunar.lunarYear,
    saju.lunar.lunarMonth,
    saju.lunar.lunarDay,
    saju.lunar.solarHour,
    input.gender || 'male',
    input.isLunar || false,
    currentYear
  );

  return { saju, tenGods, daewoon };
}