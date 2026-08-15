# -*- coding: utf-8 -*-
"""
이미 존재하는 글(텍스트만 발행됨)에 이미지를 추가하는 스크립트
- SmartEditor 편집 모드로 글을 열어
- 본문 적절한 위치에 커서를 놓고 '사진' 툴바로 이미지를 삽입
- 저장

사용법:
    venv\\Scripts\\python.exe add_images_to_posts.py [logNo ...]
    (인자 없으면 아래 POSTS 매핑의 전체 처리)
"""
import os
import sys
import time
import glob
import logging
import argparse
from datetime import datetime

from publish_approved import create_driver, load_cookies_and_login, insert_image_at_cursor
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(PROJECT_DIR, "images")
BLOG_ID = "bright-saju"

# 발행 시각 기준 이미지 매핑 (logNo → 이미지 파일명)
POSTS = [
    {
        "logNo": "224364812750",
        "title": "띠별 운세 운이 좋은 띠 순서",
        "images": [
            "cover_20260801_135733.jpg",
            "body_20260801_135734_923.jpg",
            "body_20260801_135734_877.jpg",
            "body_20260801_135735_611.jpg",
        ],
    },
    {
        "logNo": "224364813421",
        "title": "2월 이사 날짜 잡기 전 확인할 것",
        "images": [
            "cover_20260801_135815.jpg",
            "body_20260801_135818_310.jpg",
            "body_20260801_135818_809.jpg",
            "body_20260801_135817_666.jpg",
        ],
    },
    {
        "logNo": "224364814045",
        "title": "남자아이 이름풀이 방법",
        "images": [
            "cover_20260801_135905.jpg",
            "body_20260801_135906_935.jpg",
            "body_20260801_135906_466.jpg",
            "body_20260801_135907_363.jpg",
        ],
    },
    {
        "logNo": "224364814749",
        "title": "자취 세탁기 추천 완벽 가이드",
        "images": [
            "cover_20260801_140008.jpg",
            "body_20260801_140009_400.jpg",
            "body_20260801_140009_360.jpg",
            "body_20260801_140010_173.jpg",
        ],
    },
    {
        "logNo": "224364815385",
        "title": "추천 명절선물 건강식품 세트 총정리",
        "images": [
            "cover_20260801_140059.jpg",
            "body_20260801_140100_752.jpg",
            "body_20260801_140101_151.jpg",
            "body_20260801_140101_707.jpg",
        ],
    },
]


def _place_caret_before(driver, para_index):
    """본문 N번째 문단 앞에 커서를 놓는다."""
    return driver.execute_script("""
        var paras = document.querySelectorAll('.se-body p, .se-body .se-module-text p');
        var idx = arguments[0];
        var target = paras[Math.min(idx, paras.length - 1)];
        if (!target) return false;
        var range = document.createRange();
        range.setStart(target, 0);
        range.collapse(true);
        var sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
        target.scrollIntoView({block: 'center'});
        return true;
    """, para_index)


def _count_editor_images(driver):
    try:
        # .se-module-image 컨테이너만 세면 정확한 수 (img 태그와 중복 세지 않음)
        return len(driver.find_elements(By.CSS_SELECTOR, ".se-module-image, .se-component .se-image"))
    except Exception:
        return 0


def _click_save(driver):
    """저장 버튼 클릭 (1단계: 상단 발행 버튼 클릭 → 2단계: 패널 안 최종 발행 확인)"""
    # 1단계: 상단 "발행" 버튼 클릭
    btn = driver.execute_script("""
        var cls = ['button[class*="publish_btn"]', '[class*="publish_btn_area"] button'];
        for (var s=0; s<cls.length; s++) {
            var els = document.querySelectorAll(cls[s]);
            for (var i=0; i<els.length; i++) {
                if (els[i].offsetParent !== null && els[i].offsetWidth > 0) return els[i];
            }
        }
        var all = document.querySelectorAll('button, a');
        for (var i=0; i<all.length; i++) {
            var el = all[i];
            var rect = el.getBoundingClientRect();
            var txt = el.textContent.trim();
            if (rect.y < 60 && (txt.includes('저장') || txt.includes('등록') || txt.includes('발행')) && el.offsetParent !== null) {
                return el;
            }
        }
        return null;
    """)
    if not btn:
        return False
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(3)

    # 2단계: 발행 패널 내 최종 "발행" 버튼 클릭
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        # iframe 내부의 발행 패널 확인 버튼 좌표 탐색
        btn_pos = driver.execute_script("""
            var all = document.querySelectorAll('button');
            var publishBtns = [];
            for (var i = 0; i < all.length; i++) {
                var el = all[i];
                var rect = el.getBoundingClientRect();
                var txt = el.textContent.trim();
                if (txt.includes('발행') && el.offsetParent !== null && el.offsetWidth > 0 && rect.y > 50) {
                    publishBtns.push({cx: rect.x + rect.width/2, cy: rect.y + rect.height/2});
                }
            }
            // 가장 아래쪽(패널 확인) 버튼 선택
            if (publishBtns.length > 0) return publishBtns[publishBtns.length - 1];
            return null;
        """)
        if btn_pos:
            x = int(btn_pos['cx'])
            y = int(btn_pos['cy'])
            print(f"      패널 발행 좌표: ({x}, {y})")
            pyautogui.click(x, y)
            time.sleep(8)
            return True
    except Exception as e:
        print(f"      패널 발행 클릭 실패: {e}")
    return False


def add_images_to_post(driver, post):
    logNo = post["logNo"]
    title = post["title"]
    image_paths = [os.path.join(IMAGES_DIR, fn) for fn in post["images"]]
    image_paths = [p for p in image_paths if os.path.exists(p)]
    if not image_paths:
        print(f"[{logNo}] 이미지 파일 없음 — 건너뜀")
        return False
    print(f"\n===== [{logNo}] {title} =====")

    # 편집 모드로 열기
    edit_url = f"https://blog.naver.com/PostWriteForm.naver?blogId={BLOG_ID}&logNo={logNo}&Redirect=Edit&directAccess=true"
    driver.get(edit_url)
    time.sleep(6)

    if "로그인" in driver.title and "NAVER" in driver.title:
        print("  ⚠️ 로그인 페이지로 리다이렉트됨")
        return False

    # 편집 모드는 메인 프레임에 에디터가 렌더링됨 (쓰기 모드의 mainFrame iframe과 다름)
    time.sleep(3)

    # 본문 문단 수 확인
    para_count = driver.execute_script(
        "return document.querySelectorAll('.se-body p, .se-body .se-module-text p').length;"
    )
    print(f"  본문 문단 수: {para_count}")

    # 대표 이미지 → 본문 맨 앞
    if not _place_caret_before(driver, 0):
        print("  ⚠️ 커서 배치 실패 (대표)")
        return False
    time.sleep(1)
    ok = insert_image_at_cursor(driver, image_paths[0])
    print(f"  대표 이미지 삽입: {ok}")

    # 본문 이미지 → 비례 위치 (25/50/75%)
    body_images = image_paths[1:]
    positions = [max(0, int(para_count * f)) for f in (0.25, 0.5, 0.75)][:len(body_images)]
    for img_path, pos in zip(body_images, positions):
        if not _place_caret_before(driver, pos):
            continue
        time.sleep(1)
        ok = insert_image_at_cursor(driver, img_path)
        print(f"  본문 이미지 @{pos} 삽입: {ok}")

    # 저장
    saved = _click_save(driver)
    print(f"  저장 버튼 클릭: {saved}")
    time.sleep(4)
    img_now = _count_editor_images(driver)
    print(f"  에디터 내 이미지 수: {img_now}")
    try:
        driver.save_screenshot(os.path.join(PROJECT_DIR, f"edit_{logNo}.png"))
    except Exception:
        pass
    return saved


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("logNos", nargs="*", help="처리할 logNo (비우면 전체)")
    args = parser.parse_args()

    targets = [p for p in POSTS if not args.logNos or p["logNo"] in args.logNos]
    if not targets:
        print("대상 글이 없습니다.")
        return

    driver = create_driver(headless=False)
    try:
        ok = load_cookies_and_login(driver)
        if not ok:
            print("로그인 실패 — 재로그인 필요")
            return
        for post in targets:
            add_images_to_post(driver, post)
            time.sleep(3)
    finally:
        try:
            driver.quit()
        except Exception:
            pass
    print("\n===== 완료 =====")


if __name__ == "__main__":
    main()
