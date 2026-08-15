# -*- coding: utf-8 -*-
"""
Chrome 크래시 진단 스크립트 (일회성)
- 일반 selenium vs undetected-chromedriver
- headed vs headless
- 전용 프로필 vs 실제 Default 프로필(닫혀 있을 때만)
각 조합을 순서대로 시도해서 어느 조합이 되는지 확인한다.
"""
import os
import sys
import traceback
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def ts():
    return datetime.now().strftime("%H:%M:%S")


def test_plain(headless, profile_dir, label):
    """일반 selenium으로 드라이버 생성 테스트"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--disable-dev-shm-usage")
    if profile_dir:
        opts.add_argument(f"--user-data-dir={profile_dir}")
    opts.add_argument("--lang=ko-KR,ko")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts,
    )
    driver.set_page_load_timeout(30)
    driver.get("https://www.naver.com")
    print(f"  [{ts()}] ✅ {label} — 네이버 접속 성공: {driver.title[:40]}")
    driver.quit()
    return True


def test_uc(headless, profile_dir, label):
    """undetected-chromedriver로 드라이버 생성 테스트"""
    import undetected_chromedriver as uc

    opts = uc.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--lang=ko-KR,ko")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")

    kwargs = {"options": opts}
    if profile_dir:
        kwargs["user_data_dir"] = profile_dir

    driver = uc.Chrome(**kwargs)
    driver.set_page_load_timeout(30)
    driver.get("https://www.naver.com")
    print(f"  [{ts()}] ✅ {label} — 네이버 접속 성공: {driver.title[:40]}")
    driver.quit()
    return True


def main():
    ded_profile = os.path.join(BASE_DIR, "chrome_profile")
    default_profile = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")

    tests = [
        # (func, headless, profile, label)
        (test_plain, False, ded_profile, "일반 selenium + headed + 전용 프로필"),
        (test_plain, True, ded_profile, "일반 selenium + headless + 전용 프로필"),
        (test_uc, False, ded_profile, "undetected + headed + 전용 프로필"),
        (test_uc, True, ded_profile, "undetected + headless + 전용 프로필"),
    ]

    results = []
    for func, headless, profile, label in tests:
        print(f"[{ts()}] ▶ 테스트: {label}")
        try:
            ok = func(headless, profile, label)
            results.append((label, "성공"))
        except Exception as e:
            msg = str(e)[:200].replace("\n", " ")
            print(f"  [{ts()}] ❌ {label} 실패: {msg}")
            results.append((label, f"실패: {msg}"))
        print()

    print("=" * 60)
    print("진단 결과 요약")
    for label, result in results:
        print(f"  {'✅' if result == '성공' else '❌'} {label}: {result}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
