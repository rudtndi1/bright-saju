# -*- coding: utf-8 -*-
"""
소재 뱅크(topics.json) 선택·관리 모듈
- 발행할 때마다 미사용 키워드를 꺼내고, 발행 후 'used'로 표시해 중복을 막는다.
- topics.json 구조:
  { 대분류: { 세부카테고리: [ {keyword, used, used_date, blog_url}, ... ] } }
"""
import json
import os
import random
from datetime import datetime

TOPICS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "topics.json")


class TopicBank:
    def __init__(self, path=TOPICS_FILE):
        self.path = path
        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    # ---------- 조회 ----------
    def subcategories(self, main_category):
        """대분류의 세부 카테고리 목록"""
        return list(self.data.get(main_category, {}).keys())

    def unused_topics(self, main_category, subcategory):
        """미사용 키워드 목록"""
        items = self.data.get(main_category, {}).get(subcategory, [])
        return [it for it in items if not it.get("used")]

    def used_count(self, main_category, subcategory=None):
        if subcategory:
            items = self.data.get(main_category, {}).get(subcategory, [])
            return sum(1 for it in items if it.get("used"))
        total = sum(1 for it in self.data.get(main_category, {}).values()
                    for t in it if t.get("used"))
        return total

    def pick_subcategory(self, main_category):
        """미사용 키워드가 남아 있는 세부 카테고리를 랜덤 선택.
        전부 소진됐으면 전체에서 랜덤 (재사용 허용)."""
        subs = self.subcategories(main_category)
        with_unused = [s for s in subs if self.unused_topics(main_category, s)]
        return random.choice(with_unused) if with_unused else random.choice(subs)

    def next_topic(self, main_category, subcategory=None):
        """발행할 키워드 1개 선택.
        (대분류, 세부카테고리, 키워드 문자열) 반환. 소진 시 None."""
        if subcategory is None:
            subcategory = self.pick_subcategory(main_category)

        unused = self.unused_topics(main_category, subcategory)
        if not unused:
            return None, None, None
        item = random.choice(unused)
        return main_category, subcategory, item["keyword"]

    def mark_used(self, main_category, subcategory, keyword, blog_url=None):
        """발행 완료 처리"""
        items = self.data.get(main_category, {}).get(subcategory, [])
        for it in items:
            if it["keyword"] == keyword:
                it["used"] = True
                it["used_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                if blog_url:
                    it["blog_url"] = blog_url
                break
        self._save()

    def reset_all(self):
        """전체 초기화 (테스트용)"""
        for subs in self.data.values():
            for items in subs.values():
                for it in items:
                    it["used"] = False
                    it["used_date"] = None
                    it["blog_url"] = None
        self._save()

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def stats(self):
        """카테고리별 사용 현황 요약 문자열"""
        lines = []
        total_all = total_used = 0
        for main_cat, subs in self.data.items():
            for sub, items in subs.items():
                used = sum(1 for it in items if it.get("used"))
                total_all += len(items)
                total_used += used
                lines.append(f"  {main_cat} / {sub}: {used}/{len(items)}")
        lines.append(f"\n전체: {total_used}/{total_all} 발행됨")
        return "\n".join(lines)


if __name__ == "__main__":
    bank = TopicBank()
    print("=== 소재 뱅크 현황 ===")
    print(bank.stats())
    print("\n=== 랜덤 선택 테스트 ===")
    for i in range(3):
        mc, sc, kw = bank.next_topic("무료운세")
        print(f"  {mc} / {sc} → {kw}")
