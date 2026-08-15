# -*- coding: utf-8 -*-
"""
전체 대분류(5개) 1건씩 발행 스크립트
- 소재 뱅크에서 미사용 키워드 선택
- content_generator 프롬프트로 글 생성
- image_fetcher로 대표 카드뉴스 + 본문 실사 확보
- publish_naver_api (HTTP API)로 발행
- 성공 시 소재 뱅크 사용 처리

사용법:
    venv\\Scripts\\python.exe publish_all_categories.py            # 5대분류 발행
    venv\\Scripts\\python.exe publish_all_categories.py --dry-run   # 생성/이미지까지만, 발행 안 함
"""
import os
import sys
import time
import random
import logging
import argparse
from datetime import datetime

from content_generator import CATEGORIES, generate_blog_post
from topic_bank import TopicBank
from image_fetcher import fetch_images
from publish_naver_api import full_publish

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log"),
                            encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("publish-all")


def publish_one(main_category, bank, dry_run=False):
    """대분류 1건 생성→이미지→발행. 성공 시 dict 반환, 실패 시 None."""
    log.info(f"\n===== [{main_category}] 발행 시작 =====")

    # 1) 소재 뱅크에서 미사용 키워드 선택
    mc, subcategory, keyword = bank.next_topic(main_category)
    if keyword is None:
        log.warning(f"{main_category}: 소재 뱅크 소진 — 건너뜀")
        return None
    log.info(f"소재: {subcategory} → {keyword}")

    # 2) 글 생성 (카테고리별 톤 프롬프트 기반)
    try:
        result = generate_blog_post(main_category, subcategory=subcategory, topic=keyword)
    except Exception as e:
        log.error(f"글 생성 실패: {e}")
        return None
    log.info(f"제목: {result['title']}")

    # 3) 이미지 확보 (대표 카드뉴스 + 본문 실사)
    image_paths = []
    try:
        images = fetch_images(
            topic=keyword,
            main_category=main_category,
            title=result["title"],
            image_prompts=[result["cover_image_prompt"]] + result["image_prompts"],
            max_body_images=3,
        )
        image_paths = [img["local_path"] for img in images]
    except Exception as e:
        log.warning(f"이미지 확보 실패 (텍스트만 발행): {e}")

    if dry_run:
        log.info(f"[dry-run] 발행 생략 — 이미지 {len(image_paths)}장 확보됨")
        return {"title": result["title"], "dry_run": True}

    # 4) HTTP API 발행
    try:
        url = full_publish(
            title=result["title"],
            content=result["content"],
            tags=result["tags"],
            image_paths=image_paths,
            main_category=main_category,
        )
    except Exception as e:
        log.error(f"발행 실패: {e}")
        return None

    log.info(f"발행 완료: {url}")

    # 5) 소재 뱅크 사용 처리
    bank.mark_used(main_category, subcategory, keyword, blog_url=url)

    return {"title": result["title"], "url": url, "keyword": keyword, "subcategory": subcategory}


def main():
    parser = argparse.ArgumentParser(description="전체 대분류(5개) 1건씩 발행")
    parser.add_argument("--dry-run", action="store_true", help="생성/이미지까지만 하고 발행 안 함")
    args = parser.parse_args()

    bank = TopicBank()
    results = []
    cat_list = list(CATEGORIES.keys())

    for idx, main_category in enumerate(cat_list):
        r = publish_one(main_category, bank, dry_run=args.dry_run)
        if r:
            results.append(r)
        # 카테고리 사이 짧은 대기 (자연스러운 간격)
        if idx < len(cat_list) - 1:
            wait = random.randint(15, 30)
            log.info(f"다음 카테고리까지 {wait}초 대기")
            time.sleep(wait)

    log.info("\n===== 전체 발행 결과 =====")
    for r in results:
        if r.get("dry_run"):
            log.info(f"  [dry-run] {r['title']}")
        else:
            log.info(f"  ✅ {r['title']}\n     {r.get('url')}")
    log.info(f"성공: {len(results)}/{len(cat_list)}")

    return results


if __name__ == "__main__":
    main()
