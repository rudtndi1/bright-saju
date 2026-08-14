/**
 * manseryeok element utilities
 */

import { HEAVENLY_STEMS, EARTHLY_BRANCHES, STEM_ELEMENTS, BRANCH_ELEMENTS, type HeavenlyStem, type EarthlyBranch, type FiveElement, type YinYang } from './constants';
import { assertHeavenlyStem, assertEarthlyBranch } from './validation';

export function getHeavenlyStemYinYang(stem: HeavenlyStem): YinYang {
  assertHeavenlyStem(stem);
  return HEAVENLY_STEMS.indexOf(stem) % 2 === 0 ? '양' : '음';
}

export function getHeavenlyStemElement(stem: HeavenlyStem): FiveElement {
  assertHeavenlyStem(stem);
  return STEM_ELEMENTS[HEAVENLY_STEMS.indexOf(stem)];
}

export function getEarthlyBranchYinYang(branch: EarthlyBranch): YinYang {
  assertEarthlyBranch(branch);
  return EARTHLY_BRANCHES.indexOf(branch) % 2 === 0 ? '양' : '음';
}

export function getEarthlyBranchElement(branch: EarthlyBranch): FiveElement {
  assertEarthlyBranch(branch);
  return BRANCH_ELEMENTS[EARTHLY_BRANCHES.indexOf(branch)];
}

export function getStemHanja(stem: HeavenlyStem): string {
  assertHeavenlyStem(stem);
  const HEAVENLY_STEMS_HANJA = ['甲', '��', '��', '丁', '��', '己', '��', '辛', '��', '��'];
  return HEAVENLY_STEMS_HANJA[HEAVENLY_STEMS.indexOf(stem)];
}

export function getBranchHanja(branch: EarthlyBranch): string {
  assertEarthlyBranch(branch);
  const EARTHLY_BRANCHES_HANJA = ['子', '��', '��', '��', '��', '��', '午', '未', '申', '��', '��', '��'];
  return EARTHLY_BRANCHES_HANJA[EARTHLY_BRANCHES.indexOf(branch)];
}