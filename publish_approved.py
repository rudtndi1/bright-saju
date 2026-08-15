# -*- coding: utf-8 -*-
"""
네이버 블로그 자동 발행 모듈 (Selenium)
- 전용 프로필(chrome_profile/) 사용 → Default 프로필 충돌 방지
- 쿠키 기반 로그인 + 세션 만료 감지
- 이미지: 로컬 파일 경로 사용 (send_keys)
- 캡차 감지: 캡차 발견 시 즉시 중단 (무한 루프 방지)

변경 이력:
- 2026-08-01: 전용 프로필로 전환, 캡차 감지, 이미지 로컬 파일 직접 삽입
- 기존: Default Chrome 프로필 사용 (Chrome 실행 시 충돌)
"""
import os
import re
import time
import random
import pickle
import tempfile
import requests
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(PROJECT_DIR, "chrome_profile")
COOKIE_PATH = os.path.join(PROJECT_DIR, "naver_cookies.pkl")
BLOG_ID = "bright-saju"


# ============================================================
# 드라이버 생성 (전용 프로필 사용)
# ============================================================
def create_driver(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")

    chrome_options.add_argument(f"--user-data-dir={PROFILE_DIR}")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--lang=ko-KR,ko")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--no-default-browser-check")

    # 셀레니움 탐지 방어 (기본)
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
    )
    driver.set_page_load_timeout(30)

    # navigator.webdriver 속성 숨기기 (보조적 — 프로필이 더 중요)
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        })
    except Exception:
        pass

    return driver


# ============================================================
# 로그인 확인 / 쿠키 로드 / 세션 만료 감지
# ============================================================
def _is_logged_in(driver):
    """네이버 로그인 여부 빠르게 확인"""
    cookies = driver.get_cookies()
    naver_cookie_names = [c["name"] for c in cookies]
    # NID_AUT 또는 NID_SES 쿠키 존재 = 로그인 세션 존재
    if any(n in naver_cookie_names for n in ("NID_AUT", "NID_SES")):
        return True
    return False


def _is_captcha_present(driver):
    """캡차가 떠 있는지 감지 (무한 루프 방지용)"""
    try:
        page = driver.page_source.lower()
        if any(kw in page for kw in ["captcha", "캡차", "로봇이 아닙니다", "recaptcha"]):
            return True
        captcha_iframes = driver.find_elements(By.CSS_SELECTOR, "iframe[src*='captcha'], iframe[src*='recaptcha']")
        if captcha_iframes:
            return True
    except Exception:
        pass
    return False


def load_cookies_and_login(driver):
    """
    1순위: 프로필에 저장된 세션 확인 (전용 프로필 사용 시 주)
    2순위: naver_cookies.pkl 주입
    캡차 감지 시 즉시 False 반환
    """
    driver.get("https://www.naver.com")
    time.sleep(3)

    # 캡차 체크
    if _is_captcha_present(driver):
        print("   ⚠️ 캡차 감지됨 — 재로그인 필요 (세션이 의심받는 상태)")
        return False

    # 1순위: 프로필 세션 확인
    if _is_logged_in(driver):
        print("   프로필 세션으로 로그인 확인")
        return True

    # 2순위: 쿠키 파일 주입
    if os.path.exists(COOKIE_PATH):
        try:
            with open(COOKIE_PATH, "rb") as f:
                cookies = pickle.load(f)
            print(f"   쿠키 파일 로드 시도 ({len(cookies)}개)")
            for cookie in cookies:
                try:
                    if "sameSite" in cookie:
                        del cookie["sameSite"]
                    driver.add_cookie(cookie)
                except Exception:
                    pass
            driver.get("https://www.naver.com")
            time.sleep(3)
            if _is_logged_in(driver):
                print("   쿠키 로그인 성공")
                return True
        except Exception as e:
            print(f"   쿠키 로드 오류: {e}")

    print("   ❌ 로그인 실패 — 재로그인이 필요합니다.")
    print("   -> save_cookies.py를 실행하거나 login_profile.py로 로그인하세요.")
    return False


def save_current_cookies(driver):
    """현재 드라이버의 쿠키를 파일로 저장 (로그인 후 호출)"""
    cookies = driver.get_cookies()
    with open(COOKIE_PATH, "wb") as f:
        pickle.dump(cookies, f)
    print(f"   쿠키 저장 완료 ({len(cookies)}개)")


# ============================================================
# 이미지 업로드 (SmartEditor One — iframe 내부)
# ============================================================
def insert_image_at_cursor(driver, image_path):
    """
    SmartEditor의 '사진' 툴바 버튼을 클릭한 뒤,
    숨겨진 file input에 send_keys로 이미지를 삽입한다.
    반드시 iframe(mainFrame) 안에서 호출해야 한다.
    """
    if not os.path.exists(image_path):
        print(f"      이미지 파일 없음: {image_path}")
        return False

    abs_path = os.path.abspath(image_path).replace("/", "\\")

    # 1) '사진' 툴바 버튼 클릭
    try:
        photo_btn = driver.execute_script("""
            var btns = document.querySelectorAll('button');
            for (var i = 0; i < btns.length; i++) {
                if (btns[i].textContent.includes('사진')) return btns[i];
            }
            return null;
        """)
        if photo_btn:
            driver.execute_script("arguments[0].click();", photo_btn)
            time.sleep(2)
        else:
            print("      사진 툴바 버튼 없음")
            return False
    except Exception as e:
        print(f"      사진 버튼 클릭 실패: {e}")
        return False

    # 2) 숨겨진 file input을 강제 표시 후 send_keys
    try:
        file_input = driver.execute_script("""
            var inp = document.getElementById('hidden-file');
            if (!inp) {
                var inputs = document.querySelectorAll('input[type=file]');
                if (inputs.length > 0) inp = inputs[0];
            }
            if (inp) {
                inp.style.display = 'block';
                inp.style.visibility = 'visible';
                inp.style.opacity = '1';
                inp.style.position = 'fixed';
                inp.style.top = '0';
                inp.style.left = '0';
                inp.style.width = '200px';
                inp.style.height = '50px';
                inp.style.zIndex = '99999';
                return inp;
            }
            return null;
        """)
        if not file_input:
            print("      file input을 찾을 수 없음")
            return False

        file_input.send_keys(abs_path)
        print(f"      파일 업로드 전송: {os.path.basename(abs_path)}")
        time.sleep(5)
    except Exception as e:
        print(f"      파일 업로드 실패: {e}")
        return False

    # 3) 삽입 검증
    try:
        imgs = driver.find_elements(By.CSS_SELECTOR, "img")
        if imgs:
            print(f"      이미지 삽입 확인 (<img> {len(imgs)}개)")
            return True
        else:
            print("      ⚠️ 이미지 삽입 확인 실패 (<img> 없음)")
            return False
    except Exception:
        return True


def download_image_to_temp(url):
    """URL 이미지를 임시 파일로 다운로드 (기존 호환용)"""
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    fd, path = tempfile.mkstemp(suffix=".jpg")
    with os.fdopen(fd, "wb") as f:
        f.write(resp.content)
    return path


# ============================================================
# 텍스트 입력
# ============================================================
def type_text_slowly(element, text, min_delay=0.01, max_delay=0.05):
    """텍스트를 한 글자씩 입력 (랜덤 딜레이 → 사람처럼)"""
    for ch in text:
        element.send_keys(ch)
        time.sleep(random.uniform(min_delay, max_delay))


def safe_click(driver, element):
    if element is None:
        raise ValueError("safe_click: element is None")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    time.sleep(0.5)
    ActionChains(driver).move_to_element(element).click().perform()
    time.sleep(0.5)


# ============================================================
# 카테고리 설정 (best-effort)
# ============================================================
def _try_set_category(driver, category_name):
    """네이버 블로그 카테고리를 text로 찾아 선택.
    실패해도 발행은 계속 진행 (best-effort)."""
    try:
        cat_selector = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".category_select, .cat_select"))
        )
        safe_click(driver, cat_selector)
        time.sleep(1)
        options = driver.find_elements(By.CSS_SELECTOR, ".category_select li a, .cat_select li a")
        for opt in options:
            if category_name in opt.text:
                safe_click(driver, opt)
                print(f"   카테고리 '{category_name}' 선택")
                return True
        # 선택 실패 → ESC
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(0.3)
    except Exception:
        pass
    return False


# ============================================================
# 글 발행 (SmartEditor One — iframe 내부)
# ============================================================
def publish_to_naver_blog(driver, title, content, tags=None, main_category=None, image_paths=None):
    """
    네이버 블로그에 글을 발행한다.

    Args:
        title: 글 제목
        content: 본문 텍스트 (마크다운 없이, \n\n으로 문단 구분)
        tags: 태그 리스트
        main_category: 카테고리명 (best-effort 카테고리 설정용)
        image_paths: 로컬 이미지 파일 경로 리스트
    """
    write_url = f"https://blog.naver.com/{BLOG_ID}?Redirect=Write&"
    driver.get(write_url)
    time.sleep(6)

    if _is_captcha_present(driver):
        raise Exception("캡차 감지됨 — 발행 중단 (세션이 의심받는 상태)")

    # --- iframe 전환 (mainFrame) ---
    try:
        WebDriverWait(driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame"))
        )
        time.sleep(3)
    except Exception:
        raise Exception("mainFrame iframe을 찾을 수 없습니다.")

    # --- 임시저장 복구 다이얼로그 처리 (취소 클릭) ---
    try:
        driver.execute_script("""
            var btns = document.querySelectorAll('button');
            for (var i = 0; i < btns.length; i++) {
                if (btns[i].textContent.trim() === '취소') {
                    btns[i].click();
                    break;
                }
            }
        """)
        time.sleep(1)
    except Exception:
        pass

    # --- 제목 입력 (JavaScript 직접 조작) ---
    # SmartEditor 새 구조: .se-documentTitle 안의 <p>에 직접 innerHTML 설정
    title_result = driver.execute_script(f"""
        var titleModule = document.querySelector('.se-documentTitle .se-module-text');
        if (!titleModule) return '제목 모듈 없음';
        var p = titleModule.querySelector('p');
        if (!p) return '제목 <p> 없음';
        // 기존 내용 제거
        p.innerHTML = '';
        // 새 제목 텍스트 삽입
        var span = document.createElement('span');
        span.className = 'se-ff-nanummyeongjo se-fs32 __se-node';
        span.textContent = {repr(title)};
        p.appendChild(span);
        // SmartEditor에 변경 알림
        p.dispatchEvent(new Event('input', {{bubbles: true}}));
        p.dispatchEvent(new Event('keyup', {{bubbles: true}}));
        return '성공';
    """)
    if title_result != "성공":
        raise Exception(f"제목 입력 실패: {title_result}")
    print(f"   제목 입력 완료: {title[:30]}...")
    time.sleep(1)

    # --- 본문 입력 (JavaScript 직접 조작) ---
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    total_paras = len(paragraphs)

    # 이미지 삽입 위치 계산
    img_positions = {}
    if image_paths:
        for i in range(len(image_paths)):
            if i == 0:
                img_positions[0] = i
            else:
                pos = min(total_paras, (total_paras * (i + 1)) // (len(image_paths) + 1))
                img_positions[pos] = i

    # 본문 HTML 생성
    body_html_parts = []
    for i, para in enumerate(paragraphs):
        # 이미지 플레이스홀더 삽입
        if i in img_positions:
            img_idx = img_positions[i]
            body_html_parts.append(f'<div class="img-placeholder" data-img-idx="{img_idx}"></div>')

        seg_clean = para.replace("**", "").replace("___", "").replace("__", "")
        # H3 소제목 감지
        if seg_clean.startswith("### "):
            text = seg_clean[4:]
            body_html_parts.append(f'<h3 class="se-ff-nanummyeongjo se-fs24 __se-node">{text}</h3>')
        elif seg_clean.startswith("## "):
            text = seg_clean[3:]
            body_html_parts.append(f'<h3 class="se-ff-nanummyeongjo se-fs24 __se-node">{text}</h3>')
        elif seg_clean.startswith("# "):
            text = seg_clean[2:]
            body_html_parts.append(f'<h3 class="se-ff-nanummyeongjo se-fs24 __se-node">{text}</h3>')
        else:
            lines = seg_clean.split("\n")
            for line in lines:
                if line.strip():
                    body_html_parts.append(
                        f'<p class="se-text-paragraph se-text-paragraph-align-left">'
                        f'<span class="se-ff-nanummyeongjo se-fs30 __se-node">{line.strip()}</span></p>'
                    )

    body_html = "\n".join(body_html_parts)

    body_result = driver.execute_script(f"""
        var bodyModule = document.querySelector('.se-body .se-module-text');
        if (!bodyModule) return '본문 모듈 없음';
        var p = bodyModule.querySelector('p');
        if (!p) return '본문 <p> 없음';
        // 기존 내용 제거
        p.innerHTML = '';
        // 새 본문 HTML 삽입
        p.insertAdjacentHTML('afterend', {repr(body_html)});
        // 기존 빈 p 제거
        p.remove();
        // SmartEditor에 변경 알림
        bodyModule.dispatchEvent(new Event('input', {{bubbles: true}}));
        return '성공';
    """)
    if body_result != "성공":
        raise Exception(f"본문 입력 실패: {body_result}")

    print(f"   본문 입력 완료 ({len(paragraphs)}개 문단)")
    time.sleep(1)

    # --- 이미지 삽입 (로컬 파일 → 툴바 사진 버튼 → file input) ---
    img_count = 0
    if image_paths:
        for img_idx, img_path in enumerate(image_paths):
            print(f"   이미지 삽입 중... ({img_idx+1}/{len(image_paths)})")
            ok = insert_image_at_cursor(driver, img_path)
            if ok:
                img_count += 1
        print(f"   이미지 삽입 완료: {img_count}/{len(image_paths)}장")

    # --- 태그 입력 (iframe 안쪽) ---
    if tags:
        try:
            tag_input = None
            for sel in ["input[placeholder*='태그']", "input.tag_input", ".se-footer input"]:
                try:
                    els = driver.find_elements(By.CSS_SELECTOR, sel)
                    for el in els:
                        if el.is_displayed():
                            tag_input = el
                            break
                    if tag_input:
                        break
                except Exception:
                    continue
            if tag_input:
                for tag in tags[:10]:
                    tag_input.send_keys(tag)
                    time.sleep(0.3)
                    tag_input.send_keys(Keys.RETURN)
                    time.sleep(0.5)
                print(f"   태그 입력: {', '.join(tags[:5])}...")
        except Exception as e:
            print(f"   태그 입력 실패 (무시하고 계속): {e}")

    # --- 라이브러리/팝업 닫기 (발행 버튼 가림 방지, iframe 안) ---
    try:
        driver.execute_script("""
            // 라이브러리 패널 닫기
            var closeButtons = document.querySelectorAll('[class*="close"]');
            for (var i = 0; i < closeButtons.length; i++) {
                var btn = closeButtons[i];
                if (btn.offsetParent !== null && btn.offsetWidth > 0) {
                    btn.click();
                    break;
                }
            }
        """)
        time.sleep(1)
    except Exception:
        pass

    # --- 카테고리 설정 (best-effort, iframe 안) ---
    if main_category:
        try:
            _try_set_category(driver, main_category)
        except Exception:
            pass

    # --- 발행 버튼 클릭 (iframe 안에서 찾기) ---
    publish_btn = driver.execute_script("""
        // 방법 1: publish_btn 클래스로 찾기 (가장 안정적)
        var clsSelectors = ['button[class*="publish_btn"]', '[class*="publish_btn_area"] button', '[class*="publish_btn"]'];
        for (var s = 0; s < clsSelectors.length; s++) {
            var els = document.querySelectorAll(clsSelectors[s]);
            for (var i = 0; i < els.length; i++) {
                if (els[i].offsetParent !== null && els[i].offsetWidth > 0) return els[i];
            }
        }
        // 방법 2: 상단 영역(y<50)에서 '발행' 텍스트 버튼
        var all = document.querySelectorAll('button');
        for (var i = 0; i < all.length; i++) {
            var el = all[i];
            var rect = el.getBoundingClientRect();
            if (rect.y < 50 && el.textContent.trim().includes('발행') && el.offsetParent !== null) {
                return el;
            }
        }
        return null;
    """)

    if not publish_btn:
        driver.save_screenshot("publish_error.png")
        raise Exception("발행 버튼을 찾을 수 없습니다. (screenshot: publish_error.png)")

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", publish_btn)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", publish_btn)
    print("   발행 버튼 클릭 완료")
    time.sleep(5)

    # 스크린샷 (발행 후 상태 확인용)
    try:
        driver.save_screenshot("after_publish.png")
        print("   after_publish.png 저장")
    except Exception:
        pass

    # --- 발행 확인 대화상자 (JS 직접 클릭으로 안정적 처리) ---
    try:
        confirm_result = driver.execute_script("""
            // 방법1: 발행 설정 패널 내 확인 버튼 찾기
            // 패널 클래스: publish_layer, config_layer 등
            var panelSelectors = ['.publish_layer', '.config_layer',
                                  '[class*="publish_confirm"]', '[class*="publish_layer"]'];
            for (var p = 0; p < panelSelectors.length; p++) {
                var panels = document.querySelectorAll(panelSelectors[p]);
                for (var pi = 0; pi < panels.length; pi++) {
                    var panel = panels[pi];
                    var btns = panel.querySelectorAll('button');
                    for (var b = 0; b < btns.length; b++) {
                        if (btns[b].textContent.trim() === '발행' &&
                            btns[b].offsetParent !== null && btns[b].offsetWidth > 0) {
                            btns[b].click();
                            return 'panel_click';
                        }
                    }
                }
            }
            // 방법2: y > 300인 발행 버튼 (패널은 화면 아래에 나타남)
            var allBtns = document.querySelectorAll('button');
            var panelBtns = [];
            for (var i = 0; i < allBtns.length; i++) {
                var el = allBtns[i];
                var r = el.getBoundingClientRect();
                if (el.textContent.trim().includes('발행') && el.offsetParent !== null &&
                    el.offsetWidth > 0 && r.y > 300) {
                    panelBtns.push({el: el, y: r.y});
                }
            }
            // 가장 아래쪽(패널 확인) 버튼
            if (panelBtns.length > 0) {
                panelBtns.sort(function(a,b){ return b.y - a.y; });
                panelBtns[0].el.click();
                return 'bottom_click_y=' + panelBtns[0].y;
            }
            // 방법3: 발행 패널 확인 후 자동 저장 대기
            return 'no_panel_found';
        """)
        print(f"   패널 확인 결과: {confirm_result}")
        time.sleep(8)
    except Exception as e:
        print(f"   확인 버튼 클릭 실패: {e}")

    time.sleep(3)

    time.sleep(3)

    # URL 캡처 (발행 후 리다이렉트 대기)
    try:
        driver.switch_to.default_content()
    except Exception:
        pass
    time.sleep(2)
    current_url = driver.current_url

    # 발행 완료 확인 (URL에 PostView가 있으면 성공)
    if "PostView" in current_url or "post" in current_url.lower():
        print(f"   발행 성공 URL: {current_url}")
    else:
        print(f"   현재 URL: {current_url} (확인 필요)")

    return current_url


# ============================================================
# 전체 발행 흐름
# ============================================================
def full_publish(title, content, tags=None, headless=False, image_paths=None, main_category=None):
    """
    네이버 블로그 전체 발행 흐름.
    - image_paths: 로컬 이미지 경로 리스트 (대표+본문). 없으면 content 내 [IMG:url] 처리.
    - main_category: 카테고리 설정용 (best-effort).
    Returns: 발행된 페이지 URL
    Raises: Exception (로그인 실패, 캡차 등)
    """
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 네이버 발행 시작")
    print(f"  제목: {title[:50]}...")
    if image_paths:
        print(f"  이미지: {len(image_paths)}장 (로컬 파일)")
    print(f"{'='*60}")

    driver = create_driver(headless=headless)
    try:
        login_success = load_cookies_and_login(driver)
        if not login_success:
            raise Exception("네이버 로그인 실패 — 재로그인이 필요합니다.")

        url = publish_to_naver_blog(
            driver, title, content, tags,
            main_category=main_category,
            image_paths=image_paths,
        )

        # 발행 성공 시 쿠키 갱신
        try:
            save_current_cookies(driver)
        except Exception:
            pass

        print(f"   ✅ 발행 완료: {url}")
        return url

    except Exception as e:
        print(f"   ❌ 발행 실패: {e}")
        raise
    finally:
        driver.quit()


# ============================================================
# CLI 테스트
# ============================================================
if __name__ == "__main__":
    import json

    print("=" * 60)
    print("네이버 블로그 발행 모듈 테스트")
    print("=" * 60)

    if not os.path.exists(PROFILE_DIR):
        os.makedirs(PROFILE_DIR, exist_ok=True)
        print(f"전용 프로필 생성됨: {PROFILE_DIR}")
        print("login_profile.py로 네이버에 로그인해주세요.")

    # 드라이버 생성 테스트
    print("\n--- 드라이버 생성 테스트 ---")
    driver = create_driver(headless=False)
    try:
        driver.get("https://www.naver.com")
        print(f"네이버 접속 성공: {driver.title[:30]}")
        print(f"로그인 상태: {'예' if _is_logged_in(driver) else '아니오'}")
        print(f"캡차 감지: {'예' if _is_captcha_present(driver) else '아니오'}")
    finally:
        driver.quit()
    print("드라이버 종료 완료")
