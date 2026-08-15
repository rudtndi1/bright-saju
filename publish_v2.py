# -*- coding: utf-8 -*-
"""
네이버 블로그 발행 모듈 v2 (ActionChains + pyautogui)
- JS DOM 조작 없이 ActionChains로 제목/본문 입력 (chromedriver 크래시 방지)
- pyautogui로 발행 확인 버튼 클릭 (Selenium 클릭 실패 우회)
- 이미지: toolbar 사진 버튼 → file input send_keys
"""
import os, re, time, random, pickle, requests
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
    opts.add_argument("--window-position=0,0")
    opts.add_argument("--lang=ko-KR,ko")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    driver.set_page_load_timeout(30)
    return driver


def _is_logged_in(driver):
    cookies = driver.get_cookies()
    names = [c["name"] for c in cookies]
    return any(n in names for n in ("NID_AUT", "NID_SES"))


def load_cookies_and_login(driver):
    driver.get("https://www.naver.com")
    time.sleep(3)
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


def _click_publish_settings_confirm(driver):
    """발행 설정 패널의 ✓ 발행 버튼 클릭 (Selenium + Tab/Enter 키)"""
    time.sleep(4)

    # 방법 1: 설정 패널 안의 ✓ 발행 버튼을 Selenium으로 직접 클릭
    try:
        btn = driver.execute_script("""
            var btns = document.querySelectorAll('button');
            var publishBtns = [];
            for (var i = 0; i < btns.length; i++) {
                if (btns[i].textContent.trim() === '발행' && btns[i].offsetParent !== null && btns[i].offsetWidth > 0) {
                    publishBtns.push(btns[i]);
                }
            }
            if (publishBtns.length >= 2) return publishBtns[publishBtns.length - 1];
            if (publishBtns.length === 1) return publishBtns[0];
            return null;
        """)
        if btn:
            driver.execute_script("arguments[0].focus();", btn)
            time.sleep(0.5)
            # mousedown/mouseup/click 순차 이벤트
            driver.execute_script("""
                var el = arguments[0];
                el.dispatchEvent(new PointerEvent('pointerdown', {bubbles:true}));
                el.dispatchEvent(new MouseEvent('mousedown', {bubbles:true}));
                el.dispatchEvent(new PointerEvent('pointerup', {bubbles:true}));
                el.dispatchEvent(new MouseEvent('mouseup', {bubbles:true}));
                el.dispatchEvent(new MouseEvent('click', {bubbles:true}));
            """, btn)
            print("   ✓ 발행 버튼 클릭 (Selenium 이벤트)")
            time.sleep(8)
            return True
    except Exception as e:
        print(f"   Selenium 클릭 실패: {e}")

    # 방법 2: Tab으로 탐색 후 Enter
    try:
        print("   Tab+Enter 시도...")
        ActionChains(driver).send_keys(Keys.TAB).pause(0.3).send_keys(Keys.TAB).pause(0.3).send_keys(Keys.ENTER).perform()
        time.sleep(8)
        return True
    except Exception as e:
        print(f"   Tab+Enter 실패: {e}")

    return False


def full_publish(title, content, tags=None, headless=False, image_paths=None, main_category=None):
    """
    네이버 블로그 발행 (v2 — ActionChains + pyautogui)
    """
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 네이버 발행 v2 시작")
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

        # 2) 글쓰기 페이지
        driver.get(f"https://blog.naver.com/{BLOG_ID}?Redirect=Write&")
        time.sleep(8)

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

        # 5) 제목 입력 (ActionChains — JS 조작 없음)
        print("   제목 입력 중...")
        title_el = driver.find_element(By.CSS_SELECTOR, ".se-documentTitle .se-module-text")
        ActionChains(driver).click(title_el).pause(1).send_keys(title).perform()
        time.sleep(1)
        print(f"   제목: {title[:30]}...")

        # 6) 본문 입력 (ActionChains — JS 조작 없음)
        print("   본문 입력 중...")
        body_el = driver.find_element(By.CSS_SELECTOR, ".se-body .se-module-text")
        ActionChains(driver).click(body_el).pause(1).perform()
        time.sleep(0.5)

        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        for para in paragraphs:
            seg = para.replace("**", "").replace("___", "").replace("__", "")
            for line in seg.split("\n"):
                if line.strip():
                    ActionChains(driver).send_keys(line.strip()).perform()
                    time.sleep(0.05)
                ActionChains(driver).send_keys(Keys.RETURN).perform()
                time.sleep(0.1)
            ActionChains(driver).send_keys(Keys.RETURN).perform()
        print(f"   본문: {len(paragraphs)}개 문단")

        # 7) 이미지 삽입 (toolbar 사진 버튼 → file input)
        img_count = 0
        if image_paths:
            for idx, img_path in enumerate(image_paths):
                if not os.path.exists(img_path):
                    continue
                abs_path = os.path.abspath(img_path).replace("/", "\\")
                try:
                    # 사진 버튼 클릭
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

        # 8) 상단 발행 버튼 클릭 (iframe 안)
        print("   상단 발행 버튼 클릭...")
        try:
            pub_btn = driver.find_element(By.CSS_SELECTOR, "button[class*='publish_btn']")
            driver.execute_script("arguments[0].click();", pub_btn)
        except Exception:
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            raise Exception("발행 버튼 못 찾음")

        # 9) 설정 패널의 ✓ 발행 버튼 클릭 (pyautogui)
        print("   ✓ 발행 확인 클릭 (pyautogui)...")
        _click_publish_settings_confirm(driver)
        time.sleep(8)

        # 10) 결과 확인
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
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
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    print("=== 발행 모듈 v2 테스트 ===")
    url = full_publish(
        title="테스트 발행 v2",
        content="이것은 v2 발행 테스트입니다.\n\nActionChains로 입력한 본문입니다.\n\n마무리합니다.",
        tags=["테스트"],
    )
    print(f"결과: {url}")
