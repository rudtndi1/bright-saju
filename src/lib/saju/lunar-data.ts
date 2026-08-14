/**
 * manseryeok lunar calendar data (1900-2100)
 * Based on Korean lunar calendar
 */

export const LUNAR_MIN_YEAR = 1900;
export const LUNAR_MAX_YEAR = 2100;
export const LUNAR_BASE_UTC_MS = new Date('1900-01-31T15:10:00Z').getTime(); // 1900년 1월 1일(음력) 기준점

// Lunar data: each entry encodes leap month and days per month
// Bit layout: bits 0-3 = leap month (0 = no leap), bits 4-15 = month days (1=30, 0=29)
export const LUNAR_DATA: number[] = [
  25904, 92828, 23200, 43856, 76632, 11104, 41840, 21221, 53600, 58544,
  87331, 55968, 88907, 22224, 10976, 106967, 41680, 53584, 117076, 46368,
  112268, 44448, 21968, 75193, 17840, 41648, 107189, 43344, 46368, 92833,
  43872, 87468, 19312, 17776, 86391, 21168, 26960, 92500, 23200, 109388,
  42720, 19168, 107752, 42336, 53920, 60070, 54608, 22176, 103842, 38352,
  84699, 18864, 42192, 118999, 45728, 46416, 27987, 11680, 38320, 71025,
  18864, 107641, 25776, 27280, 109222, 27472, 11104, 43746, 37744, 84331,
  51552, 58544, 92455, 55968, 23248, 71379, 9952, 37600, 103122, 51536,
  119897, 46240, 46736, 87462, 21936, 9680, 42418, 37552, 108858, 26960,
  29856, 111784, 43872, 21424, 11124, 9584, 21168, 86705, 26960, 92761,
  23200, 43856, 83669, 19168, 42352, 83171, 53920, 121163, 46416, 22176,
  103847, 38352, 19168, 43444, 42192, 53840, 109217, 46416, 87641, 11680,
  38320, 82805, 18800, 42160, 107700, 27280, 109900, 23376, 11104, 103656,
  37616, 18800, 26980, 54432, 125516, 54928, 22224, 76634, 9952, 37600,
  51926, 51536, 54432, 111778, 46480, 87756, 21936, 9680, 102839, 37552,
  43344, 110933, 27808, 44368, 76641, 19376, 75129, 9584, 21168, 43686,
  59728, 27296, 105123, 43856, 84827, 19168, 42352, 86231, 53856, 55632,
  87381, 22176, 38608, 71122, 19168, 107706, 42192, 53840, 119446, 46416,
  13728, 43938, 38320, 84412, 18800, 42160, 45752, 27216, 27968, 109396,
  11104, 37744, 21234, 18800, 25833, 54432, 59984, 92822, 22224, 11104,
  99811, 37600, 51579, 43344, 54432, 55976, 46416, 22192, 11700, 9680,
  37584, 53938, 43344, 46297, 27296, 44368, 22358, 19376, 9648, 83315,
  21168, 108875, 59728, 27296, 44456, 39760, 19296, 43748, 42224, 21088,
  119394, 54608, 88730, 22176, 38608, 84438, 18912, 42192, 54484, 53840,
  54587, 46400, 46496, 103848, 38320, 18864, 43380, 42160, 43600, 59985,
  27968, 44475, 11104, 37744, 19190, 18800, 25776, 29859, 59984, 28056,
  23248, 11104, 38629, 37600, 51552, 59732, 54432, 55888, 30034, 22208,
  43959, 9680, 37584, 51893, 43344, 46240, 111779, 46416, 21977, 19360,
];

export function getLeapMonth(year: number): number {
  if (year < LUNAR_MIN_YEAR || year > LUNAR_MAX_YEAR) return 0;
  return LUNAR_DATA[year - LUNAR_MIN_YEAR] & 0xf;
}

export function getLeapMonthDays(year: number): number {
  if (year < LUNAR_MIN_YEAR || year > LUNAR_MAX_YEAR) return 0;
  const leapMonth = getLeapMonth(year);
  if (leapMonth === 0) return 0;
  const leapBit = 1 << (15 - leapMonth);
  return (LUNAR_DATA[year - LUNAR_MIN_YEAR] & leapBit) ? 30 : 29;
}

export function getLunarMonthDays(year: number, month: number): number {
  if (year < LUNAR_MIN_YEAR || year > LUNAR_MAX_YEAR) return 0;
  if (month < 1 || month > 12) return 0;
  const monthBit = 1 << (15 - month);
  return (LUNAR_DATA[year - LUNAR_MIN_YEAR] & monthBit) ? 30 : 29;
}

export function getLunarYearDays(year: number): number {
  if (year < LUNAR_MIN_YEAR || year > LUNAR_MAX_YEAR) return 0;
  let days = 0;
  for (let m = 1; m <= 12; m++) {
    days += getLunarMonthDays(year, m);
  }
  const leap = getLeapMonth(year);
  if (leap > 0) days += getLeapMonthDays(year);
  return days;
}