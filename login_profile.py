# -*- coding: utf-8 -*-
"""
최초 1회용 네이버 로그인 헬퍼
- 전용 프로필(chrome_profile/)로 Chrome을 열어
  사용자가 수동으로 네이버에 로그인한다.
- 로그인 후 세션이 프로필에 저장되므로,
  자동화 시 별도 쿠키 주입 없이 바로 사용 가능.

사용법:
  venv\\Scripts\\python.exe login_profile.py

실행하면 Chrome이 열리고, 네이버 로그인 화면이 표시됩니다.
로그인 후 Enter를 누르면 종료됩니다.
"""
import os
import time
from publish_approved import create_driver, _is_logged_in, save_current_cookies

PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile")


def main():
    if not os.path.exists(PROFILE_DIR):
        os.makedirs(PROFILE_DIR, exist_ok=True)
        print(f"전용 프로필 생성: {PROFILE_DIR}")

    print("=" * 60)
    print("네이버 로그인 (전용 프로필)")
    print("=" * 60)
    print()
    print("Chrome이 열리면 네이버에 로그인하세요.")
    print("⚠️ '로그인 상태 유지(다음에도 자동 로그인)'를 체크하면")
    print("   ~30일간 재로그인 없이 자동 발행이 유지됩니다.")
    print("로그인 성공 후 이 창에서 Enter를 누르세요.")
    print()

    driver = create_driver(headless=False)
    try:
        driver.get("https://www.naver.com")
        print("네이버가 열렸습니다. 로그인해주세요.")

        while True:
            if _is_logged_in(driver):
                print("\n[OK] 로그인 성공!")
                save_current_cookies(driver)
                break
            time.sleep(2)

        input("\n아무 키나 누르면 종료합니다 >>> ")

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    print("종료. 이제 자동화를 실행할 수 있습니다.")


if __name__ == "__main__":
    main()
