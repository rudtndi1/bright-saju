# -*- coding: utf-8 -*-
"""
좋은 기운 하루 — 네이버 블로그 자동화 시스템 (메인 진입점)

명령어:
  list                    전체 카테고리/주제 목록
  generate [대분류] [주제]  특정 카테고리에서 글 생성 → Notion 저장
  daily                   오늘 요일에 맞는 글 생성 → Notion 저장 (발행 안 함)
  auto                    무인 전체 자동화: 소재선택 → 생성 → 이미지 → 발행 → 기록
  schedule [회차]          설정된 회차만큼 자동 발행 (스케줄러용)
  bank                    소재 뱅크 사용 현황 보기
  bank-reset              소재 뱅크 전체 초기화 (테스트용)
  driver-test             드라이버 생성 테스트
"""
import sys
import os
import logging
from datetime import datetime

# stdout/stderr를 UTF-8로 강제 — 한국어 Windows(기본 cp949)에서도
# 이모지·한글이 포함된 print/log 출력이 깨지거나 인코딩 에러로 중단되지 않게 함.
# (run_daily.bat의 PYTHONUTF8=1 없이 직접 실행해도 동일하게 동작)
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from content_generator import CATEGORIES, WEEKDAY_MAIN_CATEGORY, generate_blog_post
from notion_manager import save_to_notion, update_status, build_publish_content
from topic_bank import TopicBank
from image_fetcher import fetch_images

# 발행 모듈: HTTP API 방식 (브라우저 조작 없이 서버에 직접 POST)
try:
    from publish_naver_api import full_publish
except ImportError:
    try:
        from publish_direct import full_publish
    except ImportError:
        from publish_approved import full_publish

# ============================================================
# 로깅 설정
# ============================================================
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
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
log = logging.getLogger("blog-automation")


def generate_and_save(main_category, subcategory=None, topic=None, log_to_db=True):
    """
    글 생성 → Notion 저장.
    - log_to_db: Notion DB에 저장 여부
    Returns: result dict or None (실패 시)
    """
    log.info(f"===== 글 생성 시작 | {main_category} / {subcategory or '(랜덤)'} / {topic or '(랜덤)'} =====")

    try:
        result = generate_blog_post(main_category, topic=topic, subcategory=subcategory)
    except Exception as e:
        log.error(f"글 생성 실패: {e}")
        return None

    log.info(f"제목: {result['title']}")
    log.info(f"태그: {result['tags']}")

    if log_to_db:
        try:
            page_id, image_urls = save_to_notion(
                title=result["title"],
                content=result["content"],
                category=result["category"],
                tags=result["tags"],
                image_prompts=[result["cover_image_prompt"]] + result["image_prompts"],
            )
            result["page_id"] = page_id
            result["notion_image_urls"] = image_urls
            log.info(f"Notion 저장 완료: {page_id}")
        except Exception as e:
            log.error(f"Notion 저장 실패: {e}")
            return None

    return result


def chrome_is_running():
    """Chrome 실행 여부 확인"""
    try:
        import subprocess
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace",
        ).stdout
        return "chrome.exe" in out
    except Exception:
        return False


def auto_publish(headless=False):
    """
    무인 전체 자동화:
    소재선택 → 생성 → 이미지 확보 → 네이버 발행 → 기록 → 로그
    """
    log.info("===== 무인 자동화 시작 =====")

    bank = TopicBank()

    # 1) 오늘 요일에 맞는 대분류 선택
    weekday = datetime.now().weekday()
    main_category = WEEKDAY_MAIN_CATEGORY[weekday]
    weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
    log.info(f"오늘({weekday_names[weekday]}) 대분류: {main_category}")

    # 2) 소재 뱅크에서 키워드 선택
    mc, subcategory, keyword = bank.next_topic(main_category)
    if keyword is None:
        log.info(f"{main_category}의 모든 소재가 소진되었습니다. 다음 카테고리로 시도합니다.")
        for try_cat in CATEGORIES.keys():
            mc, subcategory, keyword = bank.next_topic(try_cat)
            if keyword:
                main_category = try_cat
                break
        if keyword is None:
            log.warning("전체 소재 뱅크가 소진되었습니다.")
            return None

    log.info(f"선택된 소재: {main_category} / {subcategory} → {keyword}")

    # 3) Chrome 프로필 잠금 확인
    if not headless and chrome_is_running():
        log.warning("Chrome 실행 중 — headed 모드 사용 시 충돌 가능 (전용 프로필 사용으로 대부분 해결)")

    # 4) 글 생성
    result = generate_blog_post(main_category, subcategory=subcategory, topic=keyword)
    if not result:
        log.error("글 생성 실패")
        return None

    log.info(f"글 생성 완료: {result['title']}")

    # 5) Notion 저장 (검토대기)
    try:
        page_id, image_urls = save_to_notion(
            title=result["title"],
            content=result["content"],
            category=result["category"],
            tags=result["tags"],
            image_prompts=[result["cover_image_prompt"]] + result["image_prompts"],
        )
        log.info(f"Notion 저장 완료: {page_id}")
    except Exception as e:
        log.error(f"Notion 저장 실패: {e}")
        return None

    # 6) 이미지 확보 (로컬 파일)
    try:
        images = fetch_images(
            topic=keyword,
            main_category=main_category,
            title=result["title"],
            image_prompts=[result["cover_image_prompt"]] + result["image_prompts"],
            max_body_images=3,
        )
        image_paths = [img["local_path"] for img in images]
    except Exception as e:
        log.warning(f"이미지 확보 실패 (텍스트만 발행): {e}")
        image_paths = []

    # 7) 네이버 발행
    try:
        from publish_approved import full_publish
        url = full_publish(
            title=result["title"],
            content=result["content"],
            tags=result["tags"],
            headless=headless,
            image_paths=image_paths,
            main_category=main_category,
        )
        log.info(f"발행 완료: {url}")

        # 8) Notion 상태 갱신
        update_status(page_id, "발행완료", blog_url=url)

        # 9) 소재 뱅크 상태 갱신
        bank.mark_used(main_category, subcategory, keyword, blog_url=url)

        return {"page_id": page_id, "url": url, "title": result["title"]}

    except Exception as e:
        log.error(f"발행 실패: {e}")
        try:
            update_status(page_id, "발행실패")
        except Exception:
            pass
        return None


def schedule_run(count=1, headless=False):
    """스케줄러용: count회차 만큼 발행 (간격 랜덤 30~90초)"""
    import time
    import random
    results = []
    for i in range(count):
        log.info(f"\n===== [{i+1}/{count}] 회차 시작 =====")
        result = auto_publish(headless=headless)
        if result:
            results.append(result)
        else:
            log.info(f"회차 {i+1} 실패 — 다음 회차로")

        if i < count - 1:
            wait = random.randint(30, 90)
            log.info(f"다음 회차까지 {wait}초 대기")
            time.sleep(wait)

    log.info(f"\n===== 스케줄 완료: {len(results)}/{count}회 성공 =====")
    return results


def chrome_is_running():
    """Chrome 실행 여부 확인"""
    try:
        import subprocess
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq chrome.exe"],
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace",
        ).stdout
        return "chrome.exe" in out
    except Exception:
        return False


def driver_test():
    """드라이버 생성 + 네이버 접속 테스트"""
    from publish_approved import create_driver, _is_logged_in, _is_captcha_present
    from topic_bank import TopicBank

    print("=" * 60)
    print("드라이버 진단 테스트")
    print("=" * 60)

    profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile")
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir, exist_ok=True)
        print(f"전용 프로필 생성: {profile_dir}")

    print("\n[1] headed + 전용 프로필")
    driver = create_driver(headless=False)
    try:
        driver.get("https://www.naver.com")
        import time; time.sleep(3)
        print(f"   접속 성공: {driver.title[:30]}")
        print(f"   로그인: {'예' if _is_logged_in(driver) else '아니오'}")
        print(f"   캡차: {'감지됨' if _is_captcha_present(driver) else '없음'}")
    except Exception as e:
        print(f"   실패: {e}")
    finally:
        driver.quit()

    print("\n[2] headless + 전용 프로필")
    driver = create_driver(headless=True)
    try:
        driver.get("https://www.naver.com")
        import time; time.sleep(3)
        print(f"   접속 성공: {driver.title[:30]}")
        print(f"   로그인: {'예' if _is_logged_in(driver) else '아니오'}")
        print(f"   캡차: {'감지됨' if _is_captcha_present(driver) else '없음'}")
    except Exception as e:
        print(f"   실패: {e}")
    finally:
        driver.quit()

    print("\n[3] 소재 뱅크 현황")
    bank = TopicBank()
    print(bank.stats())

    print("\n진단 완료")


def session_check(headless=False):
    """네이버 로그인 세션 상태 확인 (발행 없이, 쿠키 만료 여부 포함)"""
    from publish_approved import create_driver, _is_logged_in, _is_captcha_present, COOKIE_PATH
    import pickle
    import time

    print("=" * 60)
    print("네이버 로그인 세션 확인")
    print("=" * 60)

    driver = create_driver(headless=headless)
    try:
        driver.get("https://www.naver.com")
        time.sleep(3)
        captcha = _is_captcha_present(driver)
        logged_in = _is_logged_in(driver)
        print(f"   캡차: {'감지됨' if captcha else '없음'}")
        print(f"   프로필 세션 로그인: {'예' if logged_in else '아니오'}")

        # 쿠키 파일의 인증 쿠키 만료 확인
        try:
            with open(COOKIE_PATH, "rb") as f:
                cookies = pickle.load(f)
            auth = [c for c in cookies if c["name"] in ("NID_AUT", "NID_SES")]
            print(f"   저장된 인증 쿠키: {len(auth)}개")
            for c in auth:
                exp = c.get("expiry") or c.get("expirationDate")
                if exp:
                    print(f"     {c['name']}: 만료 {time.strftime('%Y-%m-%d %H:%M', time.localtime(exp))}")
                else:
                    print(f"     {c['name']}: 세션쿠키(만료일 없음) — 로그인 유지 미체크 시 수명이 짧음")
        except Exception as e:
            print(f"   쿠키 파일 확인 실패: {e}")

        if logged_in and not captcha:
            print("\n   ✅ 세션 정상 — 발행 가능")
        else:
            print("\n   ❌ 재로그인 필요 → venv\\Scripts\\python.exe login_profile.py")
    finally:
        driver.quit()


if __name__ == "__main__":
    print("=" * 60)
    print("  [좋은 기운 하루] 블로그 자동화 시스템")
    print("=" * 60)

    command = sys.argv[1] if len(sys.argv) > 1 else ""

    if command == "list":
        for cat, topics in CATEGORIES.items():
            print(f"- {cat}: {', '.join(topics)}")

    elif command == "generate":
        if len(sys.argv) < 3:
            print("사용법: python main.py generate [대분류] [주제(선택)]")
            print(f"  사용 가능한 대분류: {list(CATEGORIES.keys())}")
            sys.exit(1)
        main_cat = sys.argv[2]
        if main_cat not in CATEGORIES:
            print(f"알 수 없는 대분류: {main_cat}")
            print(f"  사용 가능한 대분류: {list(CATEGORIES.keys())}")
            sys.exit(1)
        topic_arg = sys.argv[3] if len(sys.argv) > 3 else None
        result = generate_and_save(main_cat, topic=topic_arg)
        if result:
            print(f"\n제목: {result['title']}")

    elif command == "daily":
        weekday = datetime.now().weekday()
        main_category = WEEKDAY_MAIN_CATEGORY[weekday]
        weekday_names = ["월", "화", "수", "목", "금", "토", "일"]
        print(f"오늘({weekday_names[weekday]}) 대분류: {main_category}")
        generate_and_save(main_category)

    elif command == "auto":
        auto_publish()

    elif command == "schedule":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        schedule_run(count=count)

    elif command == "bank":
        bank = TopicBank()
        print(bank.stats())

    elif command == "bank-reset":
        bank = TopicBank()
        bank.reset_all()
        print("소재 뱅크 전체 초기화 완료")

    elif command == "driver-test":
        driver_test()

    elif command == "session-check":
        session_check()

    elif command == "all":
        total = sum(len(v) for v in CATEGORIES.values())
        done = 0
        for main_cat, topics in CATEGORIES.items():
            for topic in topics:
                done += 1
                log.info(f"\n[{done}/{total}] 진행 중...")
                try:
                    generate_and_save(main_cat, topic=topic)
                except Exception as e:
                    log.error(f"실패 ({main_cat}/{topic}): {e}")
        log.info(f"전체 완료: {done}/{total}")

    else:
        print("\n사용법:")
        print("  python main.py list                         전체 카테고리 목록")
        print("  python main.py generate 무료운세             해당 대분류에서 랜덤 생성")
        print("  python main.py generate 무료운세 띠별운세    특정 주제 지정 생성")
        print("  python main.py daily                        오늘 요일에 맞는 글 생성")
        print("  python main.py auto                         무인 자동화 (생성+발행)")
        print("  python main.py schedule 3                   3회차 연속 자동 발행")
        print("  python main.py bank                         소재 뱅크 현황")
        print("  python main.py bank-reset                   소재 뱅크 초기화")
        print("  python main.py driver-test                  드라이버 진단 테스트")
        print("  python main.py all                          전체 19개 주제 한번에 생성")
