/**
 * manseryeok calendar calculations
 */

import { HEAVENLY_STEMS, EARTHLY_BRANCHES, MONTH_BRANCHES, BRANCH_MAIN_STEM, type Pillar, type HeavenlyStem, type EarthlyBranch } from './constants';
import { getLeapMonth, getLeapMonthDays, getLunarMonthDays, getLunarYearDays, LUNAR_BASE_UTC_MS } from './lunar-data';
import { assertIntegerInRange, assertFiniteNumber, assertHeavenlyStem, assertEarthlyBranch, assertGender, assertDayBoundary } from './validation';

export type DayBoundary = 'midnight' | 'jasi' | 'splitJasi';

export interface CalendarInput {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute?: number;
  isLunar?: boolean;
  leapMonth?: boolean;
  gender?: 'male' | 'female';
  dayBoundary?: DayBoundary;
}

export interface CalendarResult {
  solarYear: number;
  solarMonth: number;
  solarDay: number;
  solarHour: number;
  solarMinute: number;
  lunarYear: number;
  lunarMonth: number;
  lunarDay: number;
  leapMonth: boolean;
  dayBoundary: DayBoundary;
}

/**
 * 양력 → 음력 변환
 */
export function solarToLunar(input: CalendarInput): CalendarResult {
  const { year, month, day, hour, minute = 0, dayBoundary = 'midnight' } = input;

  assertIntegerInRange(year, 1900, 2100, 'year');
  assertIntegerInRange(month, 1, 12, 'month');
  assertIntegerInRange(day, 1, 31, 'day');
  assertIntegerInRange(hour, 0, 23, 'hour');
  assertIntegerInRange(minute, 0, 59, 'minute');
  assertDayBoundary(dayBoundary);

  // 기준일(1900-01-31)부터 입력일까지 일수 계산
  const inputDate = new Date(Date.UTC(year, month - 1, day, hour, minute));
  const baseDate = new Date(LUNAR_BASE_UTC_MS);
  const diffDays = Math.floor((inputDate.getTime() - baseDate.getTime()) / 86400000);

  let lunarYear = 1900;
  let daysPassed = diffDays;
  let leapMonth = 0;

  // 년도 찾기
  while (true) {
    const yearDays = getLunarYearDays(lunarYear);
    if (daysPassed < yearDays) break;
    daysPassed -= yearDays;
    lunarYear++;
  }

  // 윤달 여부
  leapMonth = getLeapMonth(lunarYear);

  // 월 찾기
  let lunarMonth = 1;
  let isLeapMonth = false;

  for (let m = 1; m <= 12; m++) {
    const monthDays = getLunarMonthDays(lunarYear, m);
    if (daysPassed < monthDays) {
      lunarMonth = m;
      break;
    }
    daysPassed -= monthDays;

    // 윤달 체크
    if (leapMonth === m) {
      const leapDays = getLeapMonthDays(lunarYear);
      if (daysPassed < leapDays) {
        isLeapMonth = true;
        break;
      }
      daysPassed -= leapDays;
    }
  }

  const lunarDay = daysPassed + 1;

  return {
    solarYear: year,
    solarMonth: month,
    solarDay: day,
    solarHour: hour,
    solarMinute: minute,
    lunarYear,
    lunarMonth,
    lunarDay,
    leapMonth: isLeapMonth,
    dayBoundary,
  };
}

/**
 * 음력 → 양력 변환
 */
export function lunarToSolar(input: CalendarInput): CalendarResult {
  const { year, month, day, hour, minute = 0, leapMonth = false, dayBoundary = 'midnight' } = input;

  assertIntegerInRange(year, 1900, 2100, 'year');
  assertIntegerInRange(month, 1, 12, 'month');
  assertIntegerInRange(day, 1, 30, 'day');
  assertIntegerInRange(hour, 0, 23, 'hour');
  assertIntegerInRange(minute, 0, 59, 'minute');
  assertDayBoundary(dayBoundary);

  // 기준일부터 해당 음력일까지 총 일수 계산
  let daysPassed = 0;

  // 년도별 일수 누적
  for (let y = 1900; y < year; y++) {
    daysPassed += getLunarYearDays(y);
  }

  // 월별 일수 누적
  for (let m = 1; m < month; m++) {
    daysPassed += getLunarMonthDays(year, m);
    const lm = getLeapMonth(year);
    if (lm === m) {
      daysPassed += getLeapMonthDays(year);
    }
  }

  // 윤달인 경우
  if (leapMonth) {
    const lm = getLeapMonth(year);
    if (lm < month) {
      daysPassed += getLeapMonthDays(year);
    } else if (lm === month) {
      // 윤달의 해당 월
    }
  }

  daysPassed += day - 1;

  // 양력 날짜 계산
  const targetTime = LUNAR_BASE_UTC_MS + daysPassed * 86400000;
  const targetDate = new Date(targetTime + hour * 3600000 + minute * 60000);

  return {
    solarYear: targetDate.getUTCFullYear(),
    solarMonth: targetDate.getUTCMonth() + 1,
    solarDay: targetDate.getUTCDate(),
    solarHour: hour,
    solarMinute: minute,
    lunarYear: year,
    lunarMonth: month,
    lunarDay: day,
    leapMonth,
    dayBoundary,
  };
}

/**
 * 간지 계산 (년/월/일/시)
 */
export function getYearPillar(year: number): Pillar {
  const stemIndex = (year - 4) % 10;
  const branchIndex = (year - 4) % 12;
  return {
    heavenlyStem: HEAVENLY_STEMS[(stemIndex + 10) % 10],
    earthlyBranch: EARTHLY_BRANCHES[(branchIndex + 12) % 12],
  };
}

export function getMonthPillar(year: number, month: number): Pillar {
  const yearStemIndex = (year - 4) % 10;
  const monthBranch = MONTH_BRANCHES[month] as EarthlyBranch;
  const monthBranchIndex = EARTHLY_BRANCHES.indexOf(monthBranch);

  // 월간 계산: 연간 기준 + 월지 인��스 * 2 (60갑자 순환)
  const monthStemIndex = (yearStemIndex * 2 + monthBranchIndex + 2) % 10;

  return {
    heavenlyStem: HEAVENLY_STEMS[monthStemIndex],
    earthlyBranch: monthBranch,
  };
}

export function getDayPillar(date: Date): Pillar {
  // 1992-10-24 (계유일) 기준
  const anchor = new Date(Date.UTC(1992, 9, 24)); // 10월 = 9
  const diffDays = Math.floor((date.getTime() - anchor.getTime()) / 86400000);
  const ganjiIndex = (9 + diffDays) % 60;

  const stemIndex = ganjiIndex % 10;
  const branchIndex = ganjiIndex % 12;

  return {
    heavenlyStem: HEAVENLY_STEMS[stemIndex],
    earthlyBranch: EARTHLY_BRANCHES[branchIndex],
  };
}

export function getTimePillar(dayStem: HeavenlyStem, hour: number, minute: number, dayBoundary: DayBoundary): Pillar {
  // 자시(23:00~01:00) 처리
  let adjustedHour = hour;
  if (dayBoundary === 'jasi' || dayBoundary === 'splitJasi') {
    if (hour === 23) adjustedHour = 0; // 23시를 자시(0시)로
  }

  // 2시간 단위 12지지
  const branchIndex = Math.floor((adjustedHour + 1) / 2) % 12;
  const timeBranch = EARTHLY_BRANCHES[branchIndex];

  // 시간 계산: 일간 기준 + 시간 인��스
  const dayStemIndex = HEAVENLY_STEMS.indexOf(dayStem);
  const timeStemIndex = (dayStemIndex * 2 + branchIndex) % 10;

  return {
    heavenlyStem: HEAVENLY_STEMS[timeStemIndex],
    earthlyBranch: timeBranch,
  };
}

/**
 * 전체 사주 계산
 */
export interface SajuInput {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute?: number;
  isLunar?: boolean;
  leapMonth?: boolean;
  gender?: 'male' | 'female';
  dayBoundary?: DayBoundary;
}

export interface SajuOutput {
  year: Pillar;
  month: Pillar;
  day: Pillar;
  time: Pillar;
  lunar: CalendarResult;
  solar: CalendarResult;
}

export function calculateSaju(input: SajuInput): SajuOutput {
  const { year, month, day, hour, minute = 0, isLunar = false, leapMonth = false, dayBoundary = 'midnight' } = input;

  // 음력/양력 변환
  let lunar: CalendarResult;
  let solar: CalendarResult;

  if (isLunar) {
    lunar = lunarToSolar({ year, month, day, hour, minute, leapMonth, dayBoundary });
    solar = {
      solarYear: lunar.solarYear,
      solarMonth: lunar.solarMonth,
      solarDay: lunar.solarDay,
      solarHour: lunar.solarHour,
      solarMinute: lunar.solarMinute,
      lunarYear: year,
      lunarMonth: month,
      lunarDay: day,
      leapMonth,
      dayBoundary,
    };
  } else {
    solar = solarToLunar({ year, month, day, hour, minute, dayBoundary });
    lunar = {
      solarYear: year,
      solarMonth: month,
      solarDay: day,
      solarHour: hour,
      solarMinute: minute,
      lunarYear: solar.lunarYear,
      lunarMonth: solar.lunarMonth,
      lunarDay: solar.lunarDay,
      leapMonth: solar.leapMonth,
      dayBoundary,
    };
  }

  // 사주��자 계산 (음력 기준)
  const yearPillar = getYearPillar(lunar.lunarYear);
  const monthPillar = getMonthPillar(lunar.lunarYear, lunar.lunarMonth);
  const dayPillar = getDayPillar(new Date(Date.UTC(lunar.solarYear, lunar.solarMonth - 1, lunar.solarDay)));
  const timePillar = getTimePillar(dayPillar.heavenlyStem, lunar.solarHour, lunar.solarMinute, dayBoundary);

  return {
    year: yearPillar,
    month: monthPillar,
    day: dayPillar,
    time: timePillar,
    lunar,
    solar,
  };
}