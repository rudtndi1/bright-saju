import os
import time
import pyperclip
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()


def create_driver(headless=False):
    """Chrome WebDriver 생성"""
    chrome_options = Options()

    if headless:
        chrome_options.add_argument("--headless")

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver


def naver_login(driver):
    """네이버 로그인"""
    driver.get("https://nid.naver.com/nidlogin.login")
    time.sleep(3)

    # ID 입력
    id_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "id"))
    )
    id_input.click()
    pyperclip.copy(os.getenv("NAVER_ID"))
    id_input.send_keys(pyperclip.paste())
    time.sleep(1)

    # PW 입력
    pw_input = driver.find_element(By.ID, "pw")
    pw_input.click()
    pyperclip.copy(os.getenv("NAVER_PW"))
    pw_input.send_keys(pyperclip.paste())
    time.sleep(1)

    # 로그인 버튼 클릭 (여러 방식 시도)
    try:
        # 방법 1: id="log.login"
        login_btn = driver.find_element(By.ID, "log.login")
        login_btn.click()
    except:
        try:
            # 방법 2: class로 찾기
            login_btn = driver.find_element(By.CLASS_NAME, "btn_login")
            login_btn.click()
        except:
            try:
                # 방법 3: button 태그 + type="submit"
                login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_btn.click()
            except:
                # 방법 4: JavaScript로 클릭
                driver.execute_script("document.querySelector('.btn_login').click()")

    time.sleep(3)
    print("✅ 네이버 로그인 완료")


def publish_to_naver_blog(driver, title, content, tags=None):
    """네이버 블로그에 글 발행"""
    driver.get("https://blog.naver.com/bright-saju?Redirect=Write&")
    time.sleep(4)

    # iframe으로 전환
    try:
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame"))
        )
        time.sleep(2)
    except:
        print("⚠️ mainFrame 전환 실패, 계속 진행")

    # 작성 중인 글 팝업 처리
    try:
        cancel_btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '취소')]"))
        )
        cancel_btn.click()
        time.sleep(1)
    except:
        pass

    # 제목 입력 (여러 방식 시도)
    try:
        title_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[@class='se-placeholder__label' and contains(text(), '제목')]/ancestor::div[contains(@class,'se-module')]//p"))
        )
    except:
        try:
            title_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".se-title-text[contenteditable='true']"))
            )
        except:
            title_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true']"))
            )

    title_field.click()
    pyperclip.copy(title)
    title_field.send_keys(pyperclip.paste())
    time.sleep(1)

    # 본문 입력
    content_plain = content.replace('#', '').replace('**', '').replace('*', '')

    try:
        content_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'se-text')]//p"))
        )
    except:
        content_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true'][2]"))
        )

    content_field.click()
    pyperclip.copy(content_plain)
    content_field.send_keys(pyperclip.paste())
    time.sleep(1)

    # 태그 입력
    if tags:
        try:
            tag_btn = driver.find_element(By.XPATH, "//button[contains(text(), '태그')]")
            tag_btn.click()
            time.sleep(1)

            tag_input = driver.find_element(By.XPATH, "//input[@placeholder='태그 입력']")
            for tag in tags[:5]:
                tag_input.send_keys(tag)
                tag_input.send_keys("\n")
                time.sleep(0.3)
        except:
            pass

    # 발행 버튼 클릭
    try:
        publish_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '발행')]"))
        )
        publish_btn.click()
    except:
        try:
            publish_btn = driver.find_element(By.CSS_SELECTOR, ".publish_btn")
            publish_btn.click()
        except:
            driver.execute_script("document.querySelector('.publish_btn').click()")

    time.sleep(2)

    # 최종 발행 확인
    try:
        confirm_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '확인') or contains(text(), '발행')]"))
        )
        confirm_btn.click()
        time.sleep(3)
    except:
        pass

    return driver.current_url


def full_publish(title, content, tags=None, headless=False):
    """전체 발행 프로세스"""
    driver = create_driver(headless=headless)

    try:
        naver_login(driver)
        url = publish_to_naver_blog(driver, title, content, tags)
        print(f"✅ 발행 완료: {url}")
        return url
    except Exception as e:
        print(f"❌ 발행 실패: {e}")
        raise
    finally:
        driver.quit()


if __name__ == "__main__":
    print("⚠️ 테스트 시 실제 네이버 블로그에 글이 발행됩니다!")