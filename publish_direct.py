# -*- coding: utf-8 -*-
"""
네이버 블로그 발행 모듈 — 직접 POST 방식
- SmartEditor UI 조작 없이 /RabbitWrite.naver에 직접 POST
- chromedriver 크래시 없음, pyautogui 불필요
- 문서: https://dbhyeong.github.io/blog/naver-blog-smarteditor-rabbitwrite-image-upload-automation
"""
import os, re, time, json, pickle, base64, requests
from datetime import datetime
from urllib.parse import urlencode
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(PROJECT_DIR, "chrome_profile")
COOKIE_PATH = os.path.join(PROJECT_DIR, "naver_cookies.pkl")
BLOG_ID = "bright-saju"


def create_driver():
    opts = Options()
    opts.add_argument(f"--user-data-dir={PROFILE_DIR}")
    opts.add_argument("--profile-directory=Default")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--lang=ko-KR,ko")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--disable-dev-shm-usage")
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


def _wait_for_smart_editor(driver, timeout=30):
    """SmartEditor._editors.blogpc001 객체가 생길 때까지 대기
    상위 프레임에서 iframe의 contentWindow에 접근"""
    for _ in range(timeout):
        try:
            # 상위 프레임에서 SmartEditor 접근
            ready = driver.execute_script("""
                var f = document.querySelector('iframe#mainFrame');
                if (!f) return false;
                try {
                    var w = f.contentWindow;
                    if (!w) return false;
                    if (w.SmartEditor && w.SmartEditor._editors) return true;
                    // blogpc001 외 다른 에디터 이름도 확인
                    var keys = Object.keys(w.SmartEditor._editors || {});
                    return keys.length > 0;
                } catch(e) { return false; }
            """)
            if ready:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def _upload_image_via_editor(driver, image_path):
    """SmartEditor 내부 이미지 업로드 서비스로 이미지 업로드 → resource 반환"""
    abs_path = os.path.abspath(image_path).replace("/", "\\")
    with open(image_path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode()

    # 확장자/Content-Type 결정
    ext = os.path.splitext(image_path)[1].lower()
    ct = {"jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
          ".gif": "image/gif", ".webp": "image/webp"}.get(ext, "image/jpeg")

    result = driver.execute_script(f"""
        var f = document.querySelector('iframe#mainFrame');
        if (!f || !f.contentWindow.SmartEditor) return null;
        var w = f.contentWindow;
        var editor = w.SmartEditor._editors.blogpc001;

        // base64 → File
        var b64 = "{img_data}";
        var bin = atob(b64);
        var arr = new Uint8Array(bin.length);
        for (var i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
        var blob = new Blob([arr], {{type: "{ct}"}});
        var file = new File([blob], "image_{Date.now()}{ext}", {{
            type: "{ct}", lastModified: Date.now()
        }});

        // SmartEditor 이미지 업로드 서비스 호출
        var service = editor._videoUploadService._imageUploadService;
        var sourceList = service.createSourceList(["codex-" + Date.now()], [file]);

        return service.uploadImagesFromFiles(sourceList).then(function(result) {{
            return JSON.stringify(result);
        }});
    """)
    return result


def _build_document_model(title, paragraphs, image_resources=None):
    """SmartEditor documentModel JSON 구성"""
    components = []

    # 제목
    components.append({
        "@ctype": "documentTitle",
        "content": [{"@ctype": "text", "text": title}]
    })

    # 본문 문단 + 이미지
    img_idx = 0
    for para in paragraphs:
        seg = para.replace("**", "").replace("___", "").replace("__", "").strip()
        if not seg:
            continue

        # 이미지 삽입 위치 확인
        if image_resources and img_idx < len(image_resources):
            img = image_resources[img_idx]
            width_pct = min(96.0, float(img.get("widthPercentage", 100)))
            components.append({
                "@ctype": "image",
                "src": img.get("src", ""),
                "represent": img_idx == 0,
                "widthPercentage": width_pct,
                "origin": {"srcFrom": "local", "@ctype": "imageOrigin"}
            })
            img_idx += 1

        # 텍스트 문단
        components.append({
            "@ctype": "text",
            "content": [{"@ctype": "paragraph", "text": seg}]
        })

    # 남은 이미지
    if image_resources:
        for i in range(img_idx, len(image_resources)):
            img = image_resources[i]
            components.append({
                "@ctype": "image",
                "src": img.get("src", ""),
                "represent": False,
                "widthPercentage": float(img.get("widthPercentage", 100)),
                "origin": {"srcFrom": "local", "@ctype": "imageOrigin"}
            })

    return {"components": components}


def _get_category_id(driver, category_name):
    """카테고리 이름으로 ID 찾기"""
    try:
        result = driver.execute_script("""
            var f = document.querySelector('iframe#mainFrame');
            if (!f) return null;
            var w = f.contentWindow;
            // SmartEditor에서 카테고리 목록 가져오기
            var editor = w.SmartEditor._editors.blogpc001;
            if (editor && editor.getCategories) {
                return JSON.stringify(editor.getCategories());
            }
            return null;
        """)
        if result:
            cats = json.loads(result)
            for cat in cats:
                if category_name in cat.get("name", ""):
                    return cat.get("id", 0)
    except Exception:
        pass
    return 0


def _publish_post(driver, blog_id, document_model, category_id=0, tags=None,
                   post_write_time_type="now", pre_post=None):
    """네이버 서버에 직접 POST 발행"""
    population_meta = {
        "categoryId": category_id,
        "postWriteTimeType": post_write_time_type,
        "autoSaveNo": 0,
    }
    if tags:
        population_meta["tags"] = ",".join(tags)
    if pre_post:
        population_meta["prePostYear"] = pre_post.get("year", 2026)
        population_meta["prePostMonth"] = pre_post.get("month", 1)
        population_meta["prePostDate"] = pre_post.get("date", 1)
        population_meta["prePostHour"] = pre_post.get("hour", 9)
        population_meta["prePostMinute"] = pre_post.get("minute", 0)

    population_params = {
        "populationMeta": json.dumps(population_meta),
        "editorSource": "smarteditor",
    }

    # POST 데이터 구성
    post_data = {
        "blogId": blog_id,
        "documentModel": json.dumps(document_model),
        "mediaResources": json.dumps({"image": [], "video": [], "file": []}),
        "populationParams": json.dumps(population_params),
        "productApiVersion": "v1",
    }

    # CDP로 직접 POST (쿠키 포함)
    result = driver.execute_script(f"""
        var postData = {json.dumps(post_data)};
        var params = new URLSearchParams();
        for (var key in postData) {{
            params.append(key, postData[key]);
        }}

        return fetch("/RabbitWrite.naver", {{
            method: "POST",
            headers: {{
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
            }},
            body: params.toString(),
            credentials: "same-origin"
        }}).then(function(r) {{
            return r.text().then(function(t) {{
                return {{status: r.status, body: t}};
            }});
        }}).catch(function(e) {{
            return {{error: e.message}};
        }});
    """)
    return result


def _extract_log_no(response_text):
    """응답에서 logNo 추출"""
    try:
        data = json.loads(response_text)
        if data.get("isSuccess"):
            return data.get("logNo")
        # redirectUrl에서 추출
        url = data.get("redirectUrl", "")
        match = re.search(r"logNo=(\d+)", url)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None


def full_publish(title, content, tags=None, headless=False, image_paths=None, main_category=None):
    """
    네이버 블로그 발행 — 직접 POST 방식
    1. 브라우저에서 로그인 + SmartEditor 로드
    2. 이미지 업로드 (SmartEditor 서비스 사용)
    3. documentModel JSON 구성
    4. /RabbitWrite.naver에 직접 POST
    """
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 네이버 발행 (직접 POST)")
    print(f"  제목: {title[:40]}")
    if image_paths:
        print(f"  이미지: {len(image_paths)}장")
    print(f"{'='*60}")

    driver = create_driver()
    try:
        # 1) 로그인
        if not load_cookies_and_login(driver):
            raise Exception("네이버 로그인 실패")
        print("   로그인 성공")

        # 2) 글쓰기 페이지 로드 (SmartEditor 초기화 대기)
        driver.get(f"https://blog.naver.com/{BLOG_ID}?Redirect=Write&")
        time.sleep(5)

        # iframe 전환
        WebDriverWait(driver, 15).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "mainFrame"))
        )
        time.sleep(3)

        # SmartEditor 초기화 대기
        if not _wait_for_smart_editor(driver, timeout=20):
            raise Exception("SmartEditor 초기화 실패")
        print("   SmartEditor 준비 완료")

        # 3) 이미지 업로드
        image_resources = []
        if image_paths:
            for idx, img_path in enumerate(image_paths):
                if not os.path.exists(img_path):
                    continue
                print(f"   이미지 {idx+1}/{len(image_paths)} 업로드 중...")
                try:
                    result = _upload_image_via_editor(driver, img_path)
                    if result:
                        data = json.loads(result) if isinstance(result, str) else result
                        if isinstance(data, list) and len(data) > 0:
                            resource = data[0]
                            resource["widthPercentage"] = 96.0
                            image_resources.append(resource)
                            print(f"   ✅ 이미지 {idx+1} 업로드 완료")
                        else:
                            print(f"   ⚠️ 이미지 {idx+1} 업로드 결과 이상: {result}")
                    else:
                        print(f"   ⚠️ 이미지 {idx+1} 업로드 실패")
                except Exception as e:
                    print(f"   ⚠️ 이미지 {idx+1} 업로드 오류: {e}")

        # 4) documentModel 구성
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        doc_model = _build_document_model(title, paragraphs, image_resources)
        print(f"   문서 모델 구성: {len(doc_model['components'])}개 컴포넌트")

        # 5) 카테고리 ID
        category_id = _get_category_id(driver, main_category or "")
        print(f"   카테고리 ID: {category_id}")

        # 6) iframe에서 빠져나와서 POST
        driver.switch_to.default_content()
        time.sleep(1)

        # 7) 직접 POST 발행
        print("   /RabbitWrite.naver POST 발행 중...")
        result = _publish_post(
            driver, BLOG_ID, doc_model,
            category_id=category_id,
            tags=tags,
        )

        if result and not result.get("error"):
            status = result.get("status")
            body = result.get("body", "")
            log_no = _extract_log_no(body)
            if log_no:
                post_url = f"https://blog.naver.com/{BLOG_ID}/{log_no}"
                print(f"   ✅ 발행 성공! logNo={log_no}")
                print(f"   URL: {post_url}")

                # 쿠키 갱신
                try:
                    with open(COOKIE_PATH, "wb") as f:
                        pickle.dump(driver.get_cookies(), f)
                except Exception:
                    pass

                return post_url
            else:
                print(f"   ⚠️ 발행 응답 (status={status}): {body[:200]}")
                # 임시저장으로 대체 시도
                print("   임시저장 시도...")
                return _try_temp_save(driver, BLOG_ID, doc_model, category_id, tags)
        else:
            print(f"   ❌ 발행 실패: {result}")
            return None

    except Exception as e:
        print(f"   ❌ 발행 실패: {e}")
        raise
    finally:
        try:
            driver.quit()
        except Exception:
            pass


def _try_temp_save(driver, blog_id, doc_model, category_id, tags):
    """임시저장 (RabbitTempPostWrite.naver) — tokenId 불필요"""
    population_meta = {
        "categoryId": category_id,
        "postWriteTimeType": "now",
        "autoSaveNo": 0,
    }
    if tags:
        population_meta["tags"] = ",".join(tags)

    post_data = {
        "blogId": blog_id,
        "documentModel": json.dumps(doc_model),
        "mediaResources": json.dumps({"image": [], "video": [], "file": []}),
        "populationParams": json.dumps({"populationMeta": json.dumps(population_meta)}),
        "productApiVersion": "v1",
    }

    result = driver.execute_script(f"""
        var postData = {json.dumps(post_data)};
        var params = new URLSearchParams();
        for (var key in postData) {{
            params.append(key, postData[key]);
        }}
        return fetch("/RabbitTempPostWrite.naver", {{
            method: "POST",
            headers: {{"Content-Type": "application/x-www-form-urlencoded"}},
            body: params.toString(),
            credentials: "same-origin"
        }}).then(r => r.text()).catch(e => e.message);
    """)
    print(f"   임시저장 결과: {str(result)[:200]}")
    return None


if __name__ == "__main__":
    print("=== 발행 모듈 (직접 POST) 테스트 ===")
    url = full_publish(
        title="테스트 발행 직접POST",
        content="이것은 직접 POST 방식 테스트입니다.\n\n서버에 직접 요청을 보내는 방식으로 발행합니다.\n\n마무리합니다.",
        tags=["테스트"],
        main_category="무료운세",
    )
    print(f"결과: {url}")
