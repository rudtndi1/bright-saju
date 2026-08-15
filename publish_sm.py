# -*- coding: utf-8 -*-
"""
SmartEditor 발행 모듈 (ActionChains 기반 — JS 조작 최소화)
- iframe 내부에서 ActionChains로만 요소 조작
- JS DOM 조작 없이 자연스러운 사용자 시뮬레이션
"""
import os
import re
import time
import random
import pickle
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


def create_driver(headless=False):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument(f"--user-data-dir={PROFILE_DIR}")
    opts.add_argument("--profile-directory=Default")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--lang=ko-KR,ko")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.set_page_load_timeout(30)
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        })
    except Exception:
        pass
    return driver


def _is_logged_in(driver):
    cookies = driver.get_cookies()
    names = [c["name"] for c in cookies]
    return any(n in names for n in ("NID_AUT", "NID_SES"))


def _is_captcha_present(driver):
    try:
        page = driver.page_source.lower()
        if any(kw in page for kw in ["captcha", "캡차", "로봇이 아닙니다", "recaptcha"]):
            return True
    except Exception:
        pass
    return False


def load_cookies_and_login(driver):
    driver.get("https://www.naver.com")
    time.sleep(3)
    if _is_captcha_present(driver):
        return False
    if _is_logged_in(driver):
        return True
    if os.path.exists(COOKIE_PATH):
        try:
            with open(COOKIE_PATH, "rb") as f:
                cookies = pickle.load(f)
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
                return True
        except Exception:
            pass
    return False


def type_slowly(element, text, min_d=0.01, max_d=0.05):
    for ch in text:
        element.send_keys(ch)
        time.sleep(random.uniform(min_d, max_d))


def full_publish(title, content, tags=None, headless=False, image_paths=None, main_category=None):
    """SmartEditor One 발행 (ActionChains 기반)"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 네이버 발행 시작")
    print(f"  제목: {title[:40]}")
    if image_paths:
        print(f"  이미지: {len(image_paths)}장")
    print(f"{'='*60}")

    driver = create_driver(headless=headless)
    try:
        # 1) 로그인
        if not load_cookies_and_login(driver):
            raise Exception("네이버 로그인 실패")
        print("   로그인 성공")

        # 2) 글쓰기 페이지 이동
        driver.get(f"https://blog.naver.com/{BLOG_ID}?Redirect=Write&")
        time.sleep(8)

        if _is_captcha_present(driver):
            raise Exception("캡차 감지")

        # 3) iframe 전환
        WebDriverWait(driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame"))
        )
        time.sleep(3)

        # 4) 임시저장 다이얼로그 닫기
        try:
            cancel = driver.find_elements(By.XPATH, "//button[contains(text(), '취소')]")
            for c in cancel:
                if c.is_displayed():
                    c.click()
                    time.sleep(1)
                    break
        except Exception:
            pass

        # 5) 제목 입력 — 제목 영역 클릭 후 타이핑
        print("   제목 입력 중...")
        title_area = driver.find_element(By.CSS_SELECTOR, ".se-documentTitle .se-module-text")
        ActionChains(driver).click(title_area).perform()
        time.sleep(1)
        # SmartEditor가 contenteditable로 전환할 때까지 대기
        try:
            editable = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".se-documentTitle [contenteditable=true]"))
            )
            editable.send_keys(Keys.CONTROL + "a")
            time.sleep(0.2)
            editable.send_keys(Keys.DELETE)
            time.sleep(0.2)
            type_slowly(editable, title)
        except Exception:
            # fallback: 직접 send_keys on the module
            type_slowly(title_area, title)
        print(f"   제목: {title[:30]}...")
        time.sleep(1)

        # 6) 본문 입력 — 본문 영역 클릭 후 타이핑
        print("   본문 입력 중...")
        body_area = driver.find_element(By.CSS_SELECTOR, ".se-body .se-module-text")
        ActionChains(driver).click(body_area).perform()
        time.sleep(1)
        try:
            body_editable = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".se-body [contenteditable=true]"))
            )
        except Exception:
            body_editable = body_area

        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        for para in paragraphs:
            seg = para.replace("**", "").replace("___", "").replace("__", "")
            for line in seg.split("\n"):
                if line.strip():
                    type_slowly(body_editable, line.strip(), 0.005, 0.03)
                body_editable.send_keys(Keys.RETURN)
                time.sleep(0.15)
            body_editable.send_keys(Keys.RETURN)
        print(f"   본문: {len(paragraphs)}개 문단")
        time.sleep(1)

        # 7) 이미지 삽입 (투표 사진 버튼 → file input)
        img_count = 0
        if image_paths:
            for idx, img_path in enumerate(image_paths):
                if not os.path.exists(img_path):
                    continue
                abs_path = os.path.abspath(img_path).replace("/", "\\")
                # 사진 버튼 클릭
                try:
                    photo_btn = driver.find_elements(By.CSS_SELECTOR, "button.se-image-toolbar-button")
                    if photo_btn:
                        photo_btn[0].click()
                        time.sleep(2)
                    # file input 찾아서 업로드
                    fi = driver.execute_script("""
                        var inp = document.getElementById('hidden-file');
                        if (!inp) {
                            var inputs = document.querySelectorAll('input[type=file]');
                            if (inputs.length > 0) inp = inputs[0];
                        }
                        if (inp) {
                            inp.style.display='block'; inp.style.visibility='visible';
                            inp.style.opacity='1'; inp.style.position='fixed';
                            inp.style.top='0'; inp.style.left='0';
                            inp.style.width='200px'; inp.style.height='50px';
                            inp.style.zIndex='99999';
                            return inp;
                        }
                        return null;
                    """)
                    if fi:
                        fi.send_keys(abs_path)
                        time.sleep(5)
                        img_count += 1
                        print(f"   이미지 {idx+1}/{len(image_paths)} 삽입")
                except Exception as e:
                    print(f"   이미지 {idx+1} 실패: {e}")

        print(f"   이미지: {img_count}/{len(image_paths or [])}장")
        time.sleep(1)

        # 8) 발행 버튼 클릭 — 가장 안정적인 방법
        print("   발행 버튼 클릭 중...")
        try:
            pub_btn = driver.find_element(By.CSS_SELECTOR, "button[class*='publish_btn']")
            driver.execute_script("arguments[0].click();", pub_btn)
        except Exception:
            # fallback: ActionChains
            try:
                pub_area = driver.find_element(By.CSS_SELECTOR, "[class*='publish_btn_area']")
                ActionChains(driver).click(pub_area).perform()
            except Exception:
                raise Exception("발행 버튼 못 찾음")

        print("   발행 중... (5초 대기)")
        time.sleep(5)

        # 9) 확인 버튼 클릭
        try:
            confirm = driver.find_elements(By.CSS_SELECTOR, "button[class*='confirm'], button[class*='ok']")
            for c in confirm:
                if c.is_displayed():
                    driver.execute_script("arguments[0].click();", c)
                    print("   확인 버튼 클릭")
                    break
            else:
                # 텍스트로 찾기
                all_btns = driver.find_elements(By.TAG_NAME, "button")
                for b in all_btns:
                    if b.is_displayed() and b.text.strip() in ("확인", "발행"):
                        driver.execute_script("arguments[0].click();", b)
                        print(f"   확인/발행 버튼 클릭: {b.text.strip()}")
                        break
        except Exception:
            pass

        time.sleep(5)

        # 10) URL 확인
        driver.switch_to.default_content()
        time.sleep(2)
        url = driver.current_url

        # 쿠키 갱신
        try:
            with open(COOKIE_PATH, "wb") as f:
                pickle.dump(driver.get_cookies(), f)
        except Exception:
            pass

        print(f"   결과 URL: {url}")
        return url

    except Exception as e:
        print(f"   발행 실패: {e}")
        raise
    finally:
        driver.quit()


if __name__ == "__main__":
    print("SmartEditor 발행 모듈 테스트")
    url = full_publish(
        title="테스트 발행 글입니다",
        content="이것은 자동화 테스트입니다.\n\n두 번째 문단입니다.\n\n세 번째 문단에서 마무리합니다.",
        tags=["테스트", "자동화"],
    )
    print(f"결과: {url}")
