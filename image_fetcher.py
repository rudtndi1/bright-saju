# -*- coding: utf-8 -*-
"""
이미지 확보 모듈
- 대표 이미지: Pillow로 카드뉴스형 이미지 생성 (제목 오버레이 → 매 글마다 유니크)
- 본문 이미지: Unsplash / Pexels 실사 사진을 로컬 images/ 폴더에 다운로드
  (API 키가 없어도 카테고리별 안정적인 Unsplash 사진 풀에서 동작)
- Selenium 발행은 반드시 '로컬 파일 경로'만 사용 (base64/클립보드 방식 금지)

사용법:
    results = fetch_images(topic, main_category, title, image_prompts)
    # results = [ {local_path, url}, ... ]  (첫 번째가 대표 카드뉴스)
"""
import os
import re
import random
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
FONT_DIR = os.path.join(BASE_DIR, "fonts")

# ---------- 브랜드 톤 (베이지/아이보리) ----------
BRAND_BG = (245, 239, 224)        # 아이보리 베이지 배경
BRAND_ACCENT = (196, 164, 108)    # 골드 브라운 포인트
BRAND_TEXT = (74, 59, 41)         # 진한 브라운 텍스트
BRAND_SUB = (140, 122, 96)        # 보조 텍스트


def _font(size, bold=True):
    """프로젝트 폴더의 나눔고딕 사용, 없으면 맑은 고딕 폴백"""
    candidates = []
    if bold:
        candidates = [
            os.path.join(FONT_DIR, "NanumGothic-Bold.ttf"),
            r"C:\Windows\Fonts\malgunbd.ttf",
        ]
    else:
        candidates = [
            os.path.join(FONT_DIR, "NanumGothic-Regular.ttf"),
            r"C:\Windows\Fonts\malgun.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _wrap_title(draw, text, font, max_width):
    """제목을 max_width 안에 들어가도록 줄바꿈"""
    lines = []
    for raw_line in text.split("\n"):
        line = ""
        for ch in raw_line:
            test = line + ch
            if draw.textlength(test, font=font) <= max_width or not line:
                line = test
            else:
                lines.append(line)
                line = ch
        if line:
            lines.append(line)
    return lines


def make_card_news(title, category_label, blog_name="좋은 기운 하루"):
    """카드뉴스형 대표 이미지 생성 → 로컬 경로 반환"""
    W, H = 800, 600
    img = Image.new("RGB", (W, H), BRAND_BG)
    draw = ImageDraw.Draw(img)

    # 상단 장식 라인
    draw.rectangle([70, 70, W - 70, 76], fill=BRAND_ACCENT)
    # 하단 장식 원 (오른쪽 아래)
    draw.ellipse([W - 160, H - 160, W - 40, H - 40], fill=(228, 216, 190))

    # 카테고리 라벨
    cat_font = _font(30, bold=False)
    cat_text = category_label or "좋은 기운 하루"
    draw.text((70, 110), cat_text, font=cat_font, fill=BRAND_SUB)

    # 제목 (여러 줄로 감싸기, 최대 4줄)
    title_font = _font(52, bold=True)
    lines = _wrap_title(draw, title, title_font, W - 140)
    lines = lines[:4]
    y = 210
    line_h = 70
    for ln in lines:
        draw.text((70, y), ln, font=title_font, fill=BRAND_TEXT)
        y += line_h

    # 하단 블로그명 + 날짜
    small_font = _font(26, bold=False)
    today = datetime.now().strftime("%Y.%m.%d")
    draw.text((70, H - 120), blog_name, font=small_font, fill=BRAND_TEXT)
    draw.text((W - 300, H - 120), today, font=small_font, fill=BRAND_SUB)

    os.makedirs(IMAGES_DIR, exist_ok=True)
    path = os.path.join(IMAGES_DIR, f"cover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
    img.save(path, "JPEG", quality=90)
    return path


# ---------- 본문 실사 사진 풀 (키 없이도 동작하는 안정적인 Unsplash URL) ----------
CATEGORY_PHOTO_POOL = {
    "무료운세": [
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=900&q=80",
        "https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?w=900&q=80",
        "https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=900&q=80",
        "https://images.unsplash.com/photo-1509248961158-e54f6934749c?w=900&q=80",
        "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=900&q=80",
        "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?w=900&q=80",
    ],
    "손없는날_길일": [
        "https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=900&q=80",
        "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=900&q=80",
        "https://images.unsplash.com/photo-1484154218962-a1c002085d2f?w=900&q=80",
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=900&q=80",
        "https://images.unsplash.com/photo-1554995207-c18c203602cb?w=900&q=80",
        "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=900&q=80",
    ],
    "작명_출산": [
        "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=900&q=80",
        "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=900&q=80",
        "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=900&q=80",
        "https://images.unsplash.com/photo-1509869175650-a1d97972541a?w=900&q=80",
        "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=900&q=80",
        "https://images.unsplash.com/photo-1476703993599-0035a21b17a9?w=900&q=80",
    ],
    "이사_생활정보": [
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=900&q=80",
        "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?w=900&q=80",
        "https://images.unsplash.com/photo-1523413651479-597eb2da0ad6?w=900&q=80",
        "https://images.unsplash.com/photo-1560184897-ae75f418493e?w=900&q=80",
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=900&q=80",
        "https://images.unsplash.com/photo-1598928506311-c55ded91a20c?w=900&q=80",
    ],
    "선물_경조사": [
        "https://images.unsplash.com/photo-1512909006721-3d6018887383?w=900&q=80",
        "https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=900&q=80",
        "https://images.unsplash.com/photo-1607344645866-009c320b63e0?w=900&q=80",
        "https://images.unsplash.com/photo-1513201099705-a9746e1e201f?w=900&q=80",
        "https://images.unsplash.com/photo-1489749798305-4fea3ae63d43?w=900&q=80",
        "https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=900&q=80",
    ],
}

DEFAULT_POOL = CATEGORY_PHOTO_POOL["선물_경조사"]


def _unsplash_query_from_prompt(prompt):
    """AI 이미지 프롬프트에서 Unsplash 검색 키워드(영문) 추출"""
    # 스타일 접미사 제거 (beige tone, ivory tone, 4k 등)
    text = prompt
    for token in ["beige", "ivory", "tone", "Korean", "lifestyle", "premium",
                  "branding", "minimal", "design", "elegant", "traditional",
                  "mood", "warm", "sunlight", "no tarot", "no crystal",
                  "no shamanism", "4k"]:
        text = text.replace(token, " ")
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()[:4]
    return " ".join(words) if words else "korean home lifestyle"


def _search_unsplash(query, per_page=5):
    """Unsplash API로 실사 사진 검색 (키 없으면 None)"""
    key = os.getenv("UNSPLASH_ACCESS_KEY", "")
    if not key:
        return None
    try:
        resp = requests.get(
            "https://api.unsplash.com/search/photos",
            headers={"Authorization": f"Client-ID {key}"},
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
            timeout=15,
        )
        data = resp.json()
        results = data.get("results") or []
        urls = [r["urls"]["regular"] for r in results]
        return urls or None
    except Exception:
        return None


def _search_pexels(query, per_page=5):
    """Pexels API로 실사 사진 검색 (키 없으면 None)"""
    key = os.getenv("PEXELS_API_KEY", "")
    if not key:
        return None
    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": key},
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
            timeout=15,
        )
        data = resp.json()
        urls = [p["src"]["large2x"] for p in data.get("photos", [])]
        return urls or None
    except Exception:
        return None


def _pool_urls(main_category, count):
    """카테고리 사진 풀에서 count개 URL (랜덤, 중복 없이)"""
    pool = CATEGORY_PHOTO_POOL.get(main_category, DEFAULT_POOL)
    pool = list(dict.fromkeys(pool))  # 중복 제거
    random.shuffle(pool)
    return pool[:count]


def _download(url, prefix):
    """URL에서 이미지 다운로드 → 로컬 경로. 실패 시 None."""
    try:
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200 or len(resp.content) < 2000:
            return None
        content_type = resp.headers.get("content-type", "")
        if "image" not in content_type:
            return None
        ext = ".jpg"
        if "png" in content_type:
            ext = ".png"
        os.makedirs(IMAGES_DIR, exist_ok=True)
        path = os.path.join(
            IMAGES_DIR,
            f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(100, 999)}{ext}",
        )
        with open(path, "wb") as f:
            f.write(resp.content)
        return path
    except Exception:
        return None


def fetch_images(topic, main_category, title, image_prompts=None, max_body_images=3):
    """
    이미지 확보. [ {local_path, url}, ... ] 반환.
    - 첫 항목: Pillow 카드뉴스 대표 이미지 (local_path만, url은 빈 값)
    - 이후: 본문 실사 사진 (Unsplash API → Pexels API → 카테고리 풀)
    실패해도 전체 흐름이 죽지 않도록, 각 이미지는 독립적으로 예외처리한다.
    """
    print(f"\n🖼️  이미지 확보 시작 (주제: {topic})")
    results = []

    # 1) 대표 카드뉴스 (항상 성공)
    try:
        card_path = make_card_news(title, main_category)
        results.append({"local_path": card_path, "url": ""})
        print(f"   ✅ 대표 카드뉴스 생성: {os.path.basename(card_path)}")
    except Exception as e:
        print(f"   ⚠️ 카드뉴스 생성 실패: {e}")

    # 2) 본문 실사 사진
    count = min(max_body_images, len(image_prompts or []))
    if count == 0:
        count = 2

    # 검색 키워드 (첫 번째 프롬프트 기준 + 주제)
    query = ""
    if image_prompts:
        query = _unsplash_query_from_prompt(image_prompts[0])
    if not query:
        query = topic

    photo_urls = _search_unsplash(query, count) or _search_pexels(query, count)
    if photo_urls is None:
        photo_urls = _pool_urls(main_category, count + 2)  # 여유분 포함

    ok_count = 0
    for url in photo_urls:
        if ok_count >= count:
            break
        local = _download(url, "body")
        if local:
            results.append({"local_path": local, "url": url})
            ok_count += 1
            print(f"   ✅ 본문 이미지 다운로드: {os.path.basename(local)}")

    if ok_count == 0:
        print("   ⚠️ 본문 이미지를 확보하지 못했습니다. (텍스트만 발행될 수 있음)")

    print(f"   🖼️  총 {len(results)}장 확보")
    return results


if __name__ == "__main__":
    # 테스트: 카드뉴스 + 본문 이미지 2장 확보
    from content_generator import CATEGORIES
    test_topic = "2026년 이사 날짜 잡는 법"
    results = fetch_images(
        test_topic,
        "이사_생활정보",
        "2026년 이사 날짜, 언제 잡아야 할까요?",
        ["moving boxes interior warm light"] * 3,
        max_body_images=2,
    )
    for r in results:
        print(r)
