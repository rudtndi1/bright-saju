# -*- coding: utf-8 -*-
"""
블로그 발행 파이프라인 — 생성→검증→이미지→발행 통합

흐름:
  1. content_generator로 HTML 형식 글 생성
  2. validate_post로 품질 검증 (H3·표·이미지·금지표현)
  3. image_fetcher로 대표 카드뉴스 + 본문 실사 확보
  4. Selenium SmartEditor로 발행 (HTML 본문 + 이미지 삽입)

사용법:
  venv\\Scripts\\python.exe blog_publisher.py无偿운세             해당 대분류 1건
  venv\\Scripts\\python.exe blog_publisher.py all               5대분류 전체
  venv\\Scripts\\python.exe blog_publisher.py无偿운세 "이사 준비 총정리"  특정 키워드 지정
"""
import os
import sys
import re
import time
import random
import logging
from datetime import datetime

from content_generator import (
    CATEGORIES, WEEKDAY_MAIN_CATEGORY,
    generate_blog_post, validate_post
)
from topic_bank import TopicBank
from image_fetcher import fetch_images
from publish_approved import (
    create_driver, load_cookies_and_login,
    save_current_cookies
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
BLOG_ID = "bright-saju"

LOG_DIR = os.path.join(PROJECT_DIR, "logs")
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
log = logging.getLogger("blog-publisher")


# ============================================================
# HTML 변환: SmartEditor ONE 호환
# ============================================================
def _html_to_editor_body(html_content):
    """AI 출력 HTML을 SmartEditor ONE 본문 HTML로 변환.
    <!--IMG:N--> 마커를 <div class="img-placeholder" data-img-idx="N"> 로 변환."""

    body = html_content
    # 이미지 마커 변환
    body = re.sub(r'<!--IMG:(\d+)-->',
                  r'<div class="img-placeholder" data-img-idx="\1"></div>', body)
    # <br> 보존, <br/> → <br>
    body = body.replace('<br/>', '<br>').replace('<BR/>', '<br>')
    # p 태그에 SmartEditor 클래스 추가
    body = re.sub(r'<p>(.*?)</p>',
                  r'<p class="se-text-paragraph se-text-paragraph-align-left">'
                  r'<span class="se-ff-nanummyeongjo se-fs30 __se-node">\1</span></p>',
                  body, flags=re.S)
    # h3 태그에 SmartEditor 클래스 추가
    body = re.sub(r'<h3>(.*?)</h3>',
                  r'<h3 class="se-ff-nanummyeongjo se-fs24 __se-node">\1</h3>',
                  body, flags=re.S)
    # table, tr, th, td 태그에 스타일 클래스 추가
    body = body.replace('<table>', '<table style="width:100%;border-collapse:collapse;margin:16px 0;">')
    body = body.replace('<th>', '<th style="border:1px solid #ddd;padding:8px;background:#f5f5f5;text-align:left;">')
    body = body.replace('<td>', '<td style="border:1px solid #ddd;padding:8px;">')
    # ul/ol에 스타일
    body = body.replace('<ul>', '<ul style="margin:8px 0 8px 20px;">')
    body = body.replace('<ol>', '<ol style="margin:8px 0 8px 20px;">')
    # li에 스타일
    body = body.replace('<li>', '<li style="margin:4px 0;">')
    return body


def _build_editor_html(title, html_content):
    """제목 + 본문 HTML을 SmartEditor ONE에 주입할 HTML로 구성."""
    title_html = (
        f'<p><span class="se-ff-nanummyeongjo se-fs32 __se-node">{_escape(title)}</span></p>'
    )
    body_html = _html_to_editor_body(html_content)
    return title_html, body_html


def _escape(text):
    """HTML 특수문자 이스케이프."""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


# ============================================================
# SmartEditor ONE 에디터 조작
# ============================================================
def _open_editor(driver, log_no=None):
    """에디터 열기 (신규 또는 편집). True/False 반환."""
    if log_no:
        url = f"https://blog.naver.com/PostWriteForm.naver?blogId={BLOG_ID}&logNo={log_no}&Redirect=Edit&directAccess=true"
    else:
        url = f"https://blog.naver.com/{BLOG_ID}?Redirect=Write&"
    driver.get(url)
    time.sleep(8)

    if "로그인" in driver.title:
        return False
    return True


def _inject_title(driver, title):
    """제목 입력."""
    result = driver.execute_script(f"""
        var titleModule = document.querySelector('.se-documentTitle .se-module-text');
        if (!titleModule) return '제목 모듈 없음';
        var p = titleModule.querySelector('p');
        if (!p) return '제목 p 없음';
        p.innerHTML = '';
        var span = document.createElement('span');
        span.className = 'se-ff-nanummyeongjo se-fs32 __se-node';
        span.textContent = {repr(title)};
        p.appendChild(span);
        p.dispatchEvent(new Event('input', {{bubbles: true}}));
        return '성공';
    """)
    return result == "성공"


def _inject_body_html(driver, body_html):
    """본문 HTML을 SmartEditor에 주입."""
    result = driver.execute_script(f"""
        var bodyModule = document.querySelector('.se-body .se-module-text');
        if (!bodyModule) return '본문 모듈 없음';
        var p = bodyModule.querySelector('p');
        if (!p) return '본문 p 없음';
        p.innerHTML = '';
        p.insertAdjacentHTML('afterend', {repr(body_html)});
        p.remove();
        bodyModule.dispatchEvent(new Event('input', {{bubbles: true}}));
        return '성공';
    """)
    return result == "성공"


def _insert_images(driver, image_paths):
    """이미지 삽입. 본문의 <!--IMG:N--> 위치를 찾아 커서 놓고 삽입."""
    from publish_approved import insert_image_at_cursor

    inserted = 0
    for img_idx, img_path in enumerate(image_paths):
        if not os.path.exists(img_path):
            log.warning(f"  이미지 파일 없음: {img_path}")
            continue

        # 해당 이미지 마커 위치에 커서 놓기
        placed = driver.execute_script("""
            var placeholders = document.querySelectorAll('.img-placeholder, [data-img-idx]');
            var idx = arguments[0];
            var target = null;
            for (var i = 0; i < placeholders.length; i++) {
                if (placeholders[i].getAttribute('data-img-idx') == idx) {
                    target = placeholders[i];
                    break;
                }
            }
            if (!target) {
                // 마커 없으면 본문 시작 부분에 배치
                var paras = document.querySelectorAll('.se-body p, .se-body .se-module-text p');
                target = paras[0];
            }
            if (!target) return false;
            var range = document.createRange();
            range.setStart(target, 0);
            range.collapse(true);
            var sel = window.getSelection();
            sel.removeAllRanges();
            sel.addRange(range);
            target.scrollIntoView({block: 'center'});
            return true;
        """, img_idx)

        if not placed:
            # 대체: 본문 시작 부분에 배치
            driver.execute_script("""
                var paras = document.querySelectorAll('.se-body p, .se-body .se-module-text p');
                if (paras.length > 0) {
                    var range = document.createRange();
                    range.setStart(paras[0], 0);
                    range.collapse(true);
                    var sel = window.getSelection();
                    sel.removeAllRanges();
                    sel.addRange(range);
                }
            """)

        time.sleep(1)
        ok = insert_image_at_cursor(driver, img_path)
        if ok:
            inserted += 1
            log.info(f"  ✅ 이미지 {img_idx+1}/{len(image_paths)} 삽입 완료")
        else:
            log.warning(f"  ⚠️ 이미지 {img_idx+1} 삽입 실패")
        time.sleep(1)

    return inserted


def _click_publish(driver):
    """발행 버튼 클릭 → 패널 확인 → 저장 완료."""
    # 1단계: 상단 발행 버튼
    result = driver.execute_script("""
        var cls = ['button[class*="publish_btn"]', '[class*="publish_btn_area"] button'];
        for (var s=0; s<cls.length; s++) {
            var els = document.querySelectorAll(cls[s]);
            for (var i=0; i<els.length; i++) {
                if (els[i].offsetParent !== null && els[i].offsetWidth > 0) return els[i];
            }
        }
        var all = document.querySelectorAll('button');
        for (var i=0; i<all.length; i++) {
            var el = all[i];
            var r = el.getBoundingClientRect();
            if (r.y < 60 && el.textContent.trim().includes('발행') && el.offsetParent !== null) {
                return el;
            }
        }
        return null;
    """)
    if not result:
        driver.save_screenshot(os.path.join(PROJECT_DIR, "publish_error.png"))
        return False
    driver.execute_script("arguments[0].click();", result)
    time.sleep(4)

    # 2단계: 패널 내 확인 버튼 클릭 (JS)
    confirm = driver.execute_script("""
        // y > 300인 발행 버튼 = 패널 확인 버튼
        var all = document.querySelectorAll('button');
        var candidates = [];
        for (var i=0; i<all.length; i++) {
            var el = all[i];
            var r = el.getBoundingClientRect();
            if (el.textContent.trim().includes('발행') && el.offsetParent !== null &&
                el.offsetWidth > 0 && r.y > 300) {
                candidates.push({el: el, y: r.y});
            }
        }
        if (candidates.length > 0) {
            candidates.sort(function(a,b){ return b.y - a.y; });
            candidates[0].el.click();
            return 'clicked_y=' + Math.round(candidates[0].y);
        }
        return 'no_confirm';
    """)
    log.info(f"  패널 확인: {confirm}")
    time.sleep(8)
    return confirm != "no_confirm"


def _save(driver):
    """발행/저장 완료 대기 및 확인."""
    try:
        current_url = driver.current_url
        if "PostView" in current_url or "post" in current_url.lower():
            log.info(f"  발행 성공 URL: {current_url}")
            return current_url
    except Exception:
        pass
    return None


# ============================================================
# 메인 파이프라인
# ============================================================
def publish_one(main_category, topic=None, bank=None, driver=None):
    """1건 생성→검증→이미지→발행. 발행 URL 반환."""
    log.info(f"\n===== [{main_category}] 발행 시작 =====")

    # 1) 소재 뱅크에서 키워드 선택
    if bank:
        mc, subcategory, keyword = bank.next_topic(main_category)
        if keyword is None:
            log.warning(f"{main_category}: 소재 소진")
            return None
    else:
        subcategory = random.choice(CATEGORIES[main_category])
        keyword = topic or subcategory
    log.info(f"  소재: {subcategory} → {keyword}")

    # 2) 글 생성
    try:
        result = generate_blog_post(main_category, subcategory=subcategory, topic=keyword)
    except Exception as e:
        log.error(f"  글 생성 실패: {e}")
        return None
    log.info(f"  제목: {result['title']}")

    # 3) 품질 검증
    ok, issues = validate_post(result)
    if not ok:
        log.warning(f"  ⚠️ 검증 경고: {issues}")
        # 경고가 있어도 발행 진행 (단, 심각한 문제는 중단)
        fatal = [i for i in issues if "너무 짧음" in i or "소제목 부족" in i]
        if fatal:
            log.error(f"  치명적 검증 실패: {fatal}")
            return None
    else:
        log.info("  ✅ 검증 통과")

    # 4) 이미지 확보
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
        log.info(f"  이미지 확보: {len(image_paths)}장")
    except Exception as e:
        log.warning(f"  이미지 확보 실패: {e}")

    # 5) Selenium 발행
    own_driver = driver is None
    if own_driver:
        driver = create_driver(headless=False)
        try:
            if not load_cookies_and_login(driver):
                log.error("  로그인 실패")
                return None
        except Exception as e:
            log.error(f"  로그인 오류: {e}")
            return None

    try:
        # 에디터 열기 (신규 발행)
        if not _open_editor(driver):
            log.error("  에디터 열기 실패")
            return None

        # 제목 입력
        _inject_title(driver, result["title"])
        time.sleep(1)

        # 본문 HTML 주입
        body_html = _html_to_editor_body(result["content"])
        _inject_body_html(driver, body_html)
        time.sleep(2)

        # 이미지 삽입
        if image_paths:
            inserted = _insert_images(driver, image_paths)
            log.info(f"  이미지 삽입: {inserted}/{len(image_paths)}장")
        else:
            log.info("  이미지 없이 발행")

        # 발행
        if _click_publish(driver):
            url = _save(driver)
            if url:
                log.info(f"  ✅ 발행 완료: {url}")
                if bank:
                    bank.mark_used(main_category, subcategory, keyword, blog_url=url)
                return url

        log.error("  발행 실패 (저장 안 됨)")
        return None

    except Exception as e:
        log.error(f"  발행 오류: {e}")
        return None
    finally:
        if own_driver:
            try:
                driver.quit()
            except Exception:
                pass


def publish_all(topics=None):
    """5대분류 전체 발행."""
    bank = TopicBank()
    results = []
    cat_list = list(CATEGORIES.keys())

    driver = create_driver(headless=False)
    try:
        if not load_cookies_and_login(driver):
            log.error("로그인 실패")
            return []
        for idx, main_category in enumerate(cat_list):
            result = publish_one(main_category, bank=bank, driver=driver)
            if result:
                results.append(result)
            if idx < len(cat_list) - 1:
                wait = random.randint(20, 40)
                log.info(f"다음 카테고리까지 {wait}초 대기")
                time.sleep(wait)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    log.info(f"\n===== 전체 완료: {len(results)}/{len(cat_list)} =====")
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="블로그 발행 파이프라인")
    parser.add_argument("command", choices=["auto", "all", "test"],
                        help="auto=오늘 요일 카테고리, all=5대분류, test=무료운세 테스트")
    parser.add_argument("topic", nargs="?", help="지정 키워드")
    args = parser.parse_args()

    if args.command == "all":
        publish_all()
    elif args.command == "test":
        publish_one("무료운세", topic=args.topic)
    else:
        weekday = datetime.now().weekday()
        main_cat = WEEKDAY_MAIN_CATEGORY[weekday]
        publish_one(main_cat, topic=args.topic)
