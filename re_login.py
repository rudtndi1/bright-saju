# -*- coding: utf-8 -*-
"""
전용 프로필 강제 재로그인
- 기존 세션 쿠키를 전부 삭제해 로그아웃 상태로 만든 뒤
- 사용자가 네이버에 새로 로그인하면
- 쿠키를 pkl + naver_cookies.json 양쪽에 저장한다.
- 이미지 업로드(blog.upphoto.naver.com)가 세션 만료로 실패할 때 사용.
"""
import os
import sys
import json
import time
import pickle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from publish_approved import create_driver, _is_logged_in, save_current_cookies

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_COOKIE_PATH = os.path.join(PROJECT_DIR, "naver_cookies.json")


def main():
    print("Chrome을 열어 네이버 세션을 초기화합니다...")
    driver = create_driver(headless=False)
    try:
        driver.get("https://www.naver.com")
        time.sleep(3)

        # 기존 세션 쿠키 전부 삭제 → 확실히 로그아웃 상태로
        driver.delete_all_cookies()
        time.sleep(1)
        driver.get("https://www.naver.com")
        time.sleep(3)

        print("=" * 55)
        print("로그아웃 상태입니다.")
        print("Chrome에서 네이버에 로그인해주세요.")
        print("로그인 감지 시 쿠키를 저장하고 자동으로 종료합니다.")
        print("=" * 55)

        # 실제 새 로그인이 감지될 때까지 대기
        while not _is_logged_in(driver):
            time.sleep(2)
        print("\n[OK] 새 로그인 감지!")

        save_current_cookies(driver)  # pkl 저장

        # JSON도 함께 저장 (publish_naver_api용)
        cookies = driver.get_cookies()
        with open(JSON_COOKIE_PATH, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print(f"   JSON 쿠키 저장 완료 ({len(cookies)}개)")

        auth = [c["name"] for c in cookies if c["name"] in ("NID_AUT", "NID_SES")]
        print(f"   인증 쿠키: {auth}")
        print("\n완료. 창을 닫습니다.")
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
