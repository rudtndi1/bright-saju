# -*- coding: utf-8 -*-
"""
완전히 새로운 프로필로 네이버 로그인 → 쿠키 저장
- chrome_profile_login/ 폴더를 신규로 사용 (기존 stale 쿠키와 무관)
- 로그인 감지(실제 로그인) 시에만 쿠키를 pkl + json에 저장
- 이미지 업로드 세션 만료 시 사용하는 확실한 재로그인 방법
"""
import os
import sys
import json
import time
import pickle

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_COOKIE_PATH = os.path.join(PROJECT_DIR, "naver_cookies.json")
PKL_COOKIE_PATH = os.path.join(PROJECT_DIR, "naver_cookies.pkl")
LOGIN_PROFILE_DIR = os.path.join(PROJECT_DIR, "chrome_profile_login")


def _is_logged_in(driver):
    cookies = driver.get_cookies()
    names = [c["name"] for c in cookies]
    return any(n in names for n in ("NID_AUT", "NID_SES"))


def main():
    os.makedirs(LOGIN_PROFILE_DIR, exist_ok=True)
    print(f"새 전용 프로필 사용: {LOGIN_PROFILE_DIR}")

    opts = Options()
    opts.add_argument(f"--user-data-dir={LOGIN_PROFILE_DIR}")
    opts.add_argument("--profile-directory=Default")
    opts.add_argument("--window-size=1400,900")
    opts.add_argument("--lang=ko-KR,ko")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    try:
        driver.get("https://www.naver.com")
        time.sleep(4)

        print("=" * 55)
        print("새 Chrome이 열렸습니다. (완전 초기 상태)")
        print("네이버 로그인 화면에서 로그인해주세요.")
        print("실제 로그인이 감지될 때까지 대기합니다.")
        print("=" * 55)

        while not _is_logged_in(driver):
            time.sleep(2)
        time.sleep(3)  # 세션 안정화

        cookies = driver.get_cookies()
        auth = [c["name"] for c in cookies if c["name"] in ("NID_AUT", "NID_SES")]

        with open(PKL_COOKIE_PATH, "wb") as f:
            pickle.dump(cookies, f)
        with open(JSON_COOKIE_PATH, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)

        print(f"[OK] 새 로그인 감지! 쿠키 저장 완료 ({len(cookies)}개)")
        print(f"   인증 쿠키: {auth}")
        print("완료. 창을 닫습니다.")
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
