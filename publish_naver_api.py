# -*- coding: utf-8 -*-
"""
네이버 블로그 발행 모듈 — 순수 HTTP API 방식
- 브라우저 UI 조작 없이 서버에 직접 POST
- 로그인만 Selenium, 발행은 순수 requests
- 참고: greekr4/viruagent-cli/src/services/naverApiClient.js
"""
import os, re, time, json, pickle, uuid, base64, hashlib
from datetime import datetime
from urllib.parse import urlencode, quote
from dotenv import load_dotenv
import requests as req
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
COOKIE_PATH = os.path.join(PROJECT_DIR, "naver_cookies.json")
BLOG_ID = "bright-saju"
BLOG_HOST = "https://blog.naver.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"


# ============================================================
# 1. 로그인 (Selenium — 쿠키 저장용)
# ============================================================
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


def login_and_save_cookies():
    """Selenium으로 로그인하고 쿠키를 JSON 파일로 저장"""
    driver = create_driver()
    try:
        driver.get("https://www.naver.com")
        time.sleep(3)

        # 프로필 세션 확인
        cookies = driver.get_cookies()
        naver_names = [c["name"] for c in cookies]
        if any(n in naver_names for n in ("NID_AUT", "NID_SES")):
            print("   프로필 세션으로 로그인 확인")
        else:
            # 쿠키 파일에서 로드 시도
            pkl_path = os.path.join(PROJECT_DIR, "naver_cookies.pkl")
            if os.path.exists(pkl_path):
                with open(pkl_path, "rb") as f:
                    old_cookies = pickle.load(f)
                for cookie in old_cookies:
                    try:
                        if "sameSite" in cookie:
                            del cookie["sameSite"]
                        driver.add_cookie(cookie)
                    except Exception:
                        pass
                driver.get("https://www.naver.com")
                time.sleep(3)
                cookies = driver.get_cookies()
                naver_names = [c["name"] for c in cookies]
                if any(n in naver_names for n in ("NID_AUT", "NID_SES")):
                    print("   쿠키 로드로 로그인 확인")
                else:
                    print("   ❌ 로그인 실패 — login_profile.py를 먼저 실행하세요")
                    return False

        # 쿠키를 JSON으로 저장
        cookies = driver.get_cookies()
        with open(COOKIE_PATH, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print(f"   쿠키 저장 완료 ({len(cookies)}개)")
        return True
    finally:
        driver.quit()


def _load_cookies():
    """JSON 쿠키 파일에서 세션 쿠키 로드"""
    if not os.path.exists(COOKIE_PATH):
        # pkl 파일에서 변환 시도
        pkl_path = os.path.join(PROJECT_DIR, "naver_cookies.pkl")
        if os.path.exists(pkl_path):
            with open(pkl_path, "rb") as f:
                old_cookies = pickle.load(f)
            with open(COOKIE_PATH, "w", encoding="utf-8") as f:
                json.dump(old_cookies, f, ensure_ascii=False, indent=2)
        else:
            raise FileNotFoundError(f"쿠키 파일 없음: {COOKIE_PATH} — login_profile.py를 먼저 실행하세요")

    with open(COOKIE_PATH, "r", encoding="utf-8") as f:
        cookies = json.load(f)

    naver_cookies = [c for c in cookies if "naver" in c.get("domain", "")]
    cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in naver_cookies if c.get("name") and c.get("value"))
    if not cookie_str:
        raise ValueError("유효한 네이버 쿠키 없음 — 재로그인 필요")
    return cookie_str


def _headers(extra=None):
    """기본 HTTP 헤더"""
    h = {
        "User-Agent": USER_AGENT,
        "Cookie": _load_cookies(),
        "Accept": "application/json, text/plain, */*",
    }
    if extra:
        h.update(extra)
    return h


def _get(url, extra_headers=None, timeout=20):
    """GET 요청"""
    resp = req.get(url, headers=_headers(extra_headers), timeout=timeout, allow_redirects=True)
    resp.raise_for_status()
    return resp


def _post_form(url, data, extra_headers=None, timeout=20):
    """POST form-urlencoded"""
    resp = req.post(url, headers=_headers(extra_headers), data=data, timeout=timeout)
    resp.raise_for_status()
    return resp


# ============================================================
# 2. 네이버 API 유틸리티
# ============================================================
def init_blog():
    """블로그 ID 확인 (MyBlog에서 추출)"""
    resp = _get(f"{BLOG_HOST}/MyBlog.naver", extra_headers={"Referer": BLOG_HOST})
    match = re.search(r"blogId\s*=\s*'([^']+)'", resp.text)
    if not match:
        if "로그인" in resp.text or "login" in resp.text.lower():
            raise ValueError("세션 만료 — 재로그인 필요")
        raise ValueError("MyBlog에서 blogId 추출 실패")
    return match.group(1)


def get_token(blog_id, category_no="0"):
    """Se-Authorization 토큰 획득"""
    url = f"{BLOG_HOST}/PostWriteFormSeOptions.naver?blogId={quote(blog_id)}&categoryNo={quote(category_no)}"
    referer = f"{BLOG_HOST}/PostWriteForm.naver?blogId={quote(blog_id)}&categoryNo={quote(category_no)}&Redirect=Write"
    resp = _get(url, extra_headers={"Referer": referer})
    data = resp.json()
    token = data.get("result", {}).get("token")
    if not token:
        raise ValueError("Se-Authorization 토큰 획득 실패")
    return token


def get_editor_info(blog_id, category_no="0"):
    """에디터 ID와 editorSource 획득"""
    token = get_token(blog_id, category_no)

    # 에디터 설정
    resp = _get(
        "https://platform.editor.naver.com/api/blogpc001/v1/service_config",
        extra_headers={
            "Referer": f"{BLOG_HOST}/PostWriteForm.naver?blogId={quote(blog_id)}&categoryNo={quote(category_no)}&Redirect=Write",
            "Se-Authorization": token,
        }
    )
    config = resp.json()
    editor_id = config.get("editorInfo", {}).get("id")
    if not editor_id:
        raise ValueError("에디터 ID 획득 실패")

    # 매니저 옵션
    resp2 = _get(
        f"{BLOG_HOST}/PostWriteFormManagerOptions.naver?blogId={quote(blog_id)}&categoryNo={quote(category_no)}",
        extra_headers={"Referer": f"{BLOG_HOST}/PostWriteForm.naver?blogId={quote(blog_id)}&categoryNo={quote(category_no)}&Redirect=Write"}
    )
    mgr = resp2.json()
    editor_source = mgr.get("result", {}).get("formView", {}).get("editorSource", "blogpc001")

    return {"editorId": editor_id, "editorSource": editor_source, "token": token}


def get_categories(blog_id):
    """카테고리 목록 반환 {이름: ID}"""
    resp = _get(
        f"{BLOG_HOST}/PostWriteFormManagerOptions.naver?blogId={quote(blog_id)}&categoryNo=0",
        extra_headers={"Referer": f"{BLOG_HOST}/PostWriteForm.naver?blogId={quote(blog_id)}&Redirect=Write"}
    )
    data = resp.json()
    cat_list = data.get("result", {}).get("formView", {}).get("categoryListFormView", {}).get("categoryFormViewList", [])
    result = {}
    for cat in cat_list:
        name = cat.get("categoryName", "")
        no = cat.get("categoryNo")
        if name and no is not None:
            result[name] = int(no)
    return result


def get_upload_session_key(token, blog_id):
    """이미지 업로드 세션 키 획득"""
    resp = _get(
        "https://platform.editor.naver.com/api/blogpc001/v1/photo-uploader/session-key",
        extra_headers={
            "Referer": f"{BLOG_HOST}/PostWriteForm.naver?blogId={quote(blog_id)}&Redirect=Write",
            "Se-Authorization": token,
        }
    )
    return resp.json().get("sessionKey")


def upload_image(image_path, token, blog_id):
    """이미지를blog.upphoto.naver.com에 업로드 → resource 반환"""
    session_key = get_upload_session_key(token, blog_id)
    if not session_key:
        raise ValueError("이미지 업로드 세션 키 획득 실패")

    upload_url = (
        f"https://blog.upphoto.naver.com/{session_key}/simpleUpload/0"
        f"?userId={quote(blog_id)}&extractExif=true&extractAnimatedCnt=true"
        f"&autorotate=true&extractDominantColor=false&denyAnimatedImage=false&skipXcamFiltering=false"
    )

    with open(image_path, "rb") as f:
        img_data = f.read()

    filename = os.path.basename(image_path)
    resp = req.post(
        upload_url,
        headers={
            "Cookie": _load_cookies(),
            "User-Agent": USER_AGENT,
            "Referer": f"{BLOG_HOST}/{quote(blog_id)}",
        },
        files={
            "image": (filename, img_data, "image/jpeg"),
            "imageFileName": (None, filename),  # 에디터가 보내는 필수 필드
        },
        timeout=60,
    )
    resp.raise_for_status()

    # XML 응답 파싱
    text = resp.text
    if "<url>" not in text:
        raise ValueError(f"이미지 업로드 실패: {text[:200]}")

    def extract(tag):
        m = re.search(f"<{tag}>([^<]*)</{tag}>", text)
        return m.group(1) if m else None

    return {
        "url": extract("url"),
        "width": int(extract("width") or "600"),
        "height": int(extract("height") or "400"),
        "fileName": extract("fileName") or filename,
        "fileSize": int(extract("fileSize") or "0"),
    }


def _inject_images_into_html(html, image_resources):
    """업로드한 이미지 resource를 HTML에 <img> 태그로 삽입한다.
    첫 이미지(대표 카드뉴스)는 첫 문단 뒤, 나머지는 소제목(H3) 앞에 배치.
    네이버 upconvert가 <img>를 이미지 컴포넌트로 변환하므로 본문에 이미지가 들어간다."""
    if not image_resources:
        return html

    img_tags = [
        f'<img src="{r["url"]}" width="{r.get("width", 600)}" height="{r.get("height", 400)}" />'
        for r in image_resources
    ]

    # 소제목 기준으로 분리: [텍스트, <h3>..</h3>, 텍스트, <h3>..</h3>, ...]
    parts = re.split(r"(<h3>.*?</h3>)", html, flags=re.S)

    # 1) 대표 이미지 = 첫 문단 뒤
    if parts:
        parts[0] = parts[0] + img_tags[0]

    # 2) 나머지 본문 이미지 = 소제목 앞에 고르게 배치
    rest = img_tags[1:]
    if rest:
        idx = 0
        for i in range(1, len(parts), 2):
            if parts[i].startswith("<h3>") and idx < len(rest):
                parts[i] = rest[idx] + parts[i]
                idx += 1

    return "".join(parts)


def convert_html_to_components(html, blog_id):
    """HTML을 SmartEditor 컴포넌트로 변환 (Naver API 활용)"""
    wrapped = f"<html>\n<body>\n<!--StartFragment-->\n{html}\n<!--EndFragment-->\n</body>\n</html>"
    resp = req.post(
        f"https://upconvert.editor.naver.com/blog/html/components?documentWidth=886&userId={quote(blog_id)}",
        headers={
            "Content-Type": "text/html; charset=utf-8",
            "User-Agent": USER_AGENT,
            "Cookie": _load_cookies(),
        },
        data=wrapped.encode("utf-8"),
        timeout=20,
    )
    if resp.status_code == 200:
        try:
            components = resp.json()
            if isinstance(components, list) and len(components) > 0:
                return components
        except Exception:
            pass
    return []


# ============================================================
# 3. 컴포넌트 빌더 (HTML 변환 실패 시 수동 구성)
# ============================================================
def _se_id():
    return f"SE-{uuid.uuid4()}"


def _text_component(text, font_size="fs16", bold="false", align="left", ctype="text"):
    return {
        "id": _se_id(),
        "layout": "default",
        "value": [{
            "id": _se_id(),
            "nodes": [{
                "id": _se_id(),
                "value": text,
                "style": {
                    "fontColor": "#333333",
                    "fontSizeCode": font_size,
                    "bold": bold,
                    "@ctype": "nodeStyle",
                },
                "@ctype": "textNode",
            }],
            "style": {
                "align": align,
                "lineHeight": "1.8",
                "@ctype": "paragraphStyle",
            },
            "@ctype": "paragraph",
        }],
        "@ctype": ctype,
    }


def _image_component(img_resource):
    return {
        "id": _se_id(),
        "layout": "default",
        "align": "center",
        "src": img_resource.get("url", ""),
        "internalResource": "true",
        "represent": "false",
        "path": img_resource.get("url", "").replace("https://blogfiles.pstatic.net/", ""),
        "domain": "https://blogfiles.pstatic.net",
        "fileSize": img_resource.get("fileSize", 0),
        "width": img_resource.get("width", 600),
        "widthPercentage": 0,
        "height": img_resource.get("height", 400),
        "originalWidth": img_resource.get("width", 600),
        "originalHeight": img_resource.get("height", 400),
        "fileName": img_resource.get("fileName", "image.jpg"),
        "caption": None,
        "format": "normal",
        "displayFormat": "normal",
        "imageLoaded": "true",
        "contentMode": "normal",
        "origin": {"srcFrom": "local", "@ctype": "imageOrigin"},
        "ai": "false",
        "@ctype": "image",
    }


def _build_components_from_content(title, content, image_resources):
    """HTML 변환 실패 시 수동으로 컴포넌트 구성"""
    components = []

    # 제목 컴포넌트
    components.append({
        "id": _se_id(),
        "layout": "default",
        "title": [{
            "id": _se_id(),
            "nodes": [{
                "id": _se_id(),
                "value": title,
                "@ctype": "textNode",
            }],
            "@ctype": "paragraph",
        }],
        "subTitle": None,
        "align": "left",
        "@ctype": "documentTitle",
    })

    # 이미지 컴포넌트 (상단에 배치)
    for img in image_resources:
        components.append(_image_component(img))

    # 본문 컴포넌트
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    for para in paragraphs:
        seg = para.replace("**", "").replace("___", "").replace("__", "").strip()
        if not seg:
            continue
        # H3 소제목
        if seg.startswith("### ") or seg.startswith("## ") or seg.startswith("# "):
            text = re.sub(r"^#{1,3}\s*", "", seg)
            components.append(_text_component(text, font_size="fs24", bold="true", align="center", ctype="quotation"))
        else:
            components.append(_text_component(seg))

    return components


# ============================================================
# 4. 발행
# ============================================================
def publish_post(blog_id, title, content_components, category_no="0", tags="", open_type=2):
    """RabbitWrite.naver에 직접 POST 발행"""
    editor_info = get_editor_info(blog_id, category_no)
    token = editor_info["token"]
    editor_id = editor_info["editorId"]
    editor_source = editor_info["editorSource"]

    # 제목 컴포넌트
    title_component = {
        "id": _se_id(),
        "layout": "default",
        "title": [{
            "id": _se_id(),
            "nodes": [{
                "id": _se_id(),
                "value": title,
                "@ctype": "textNode",
            }],
            "@ctype": "paragraph",
        }],
        "subTitle": None,
        "align": "left",
        "@ctype": "documentTitle",
    }

    # documentModel
    document_model = {
        "documentId": "",
        "document": {
            "version": "2.9.0",
            "theme": "default",
            "language": "ko-KR",
            "id": editor_id,
            "components": [title_component] + content_components,
        },
    }

    # populationParams
    population_params = {
        "configuration": {
            "openType": open_type,
            "commentYn": True,
            "searchYn": True,
            "sympathyYn": True,
            "scrapType": 2,
            "outSideAllowYn": True,
            "twitterPostingYn": False,
            "facebookPostingYn": False,
            "cclYn": False,
        },
        "populationMeta": {
            "categoryId": str(category_no),
            "logNo": None,
            "directorySeq": 0,
            "directoryDetail": None,
            "mrBlogTalkCode": None,
            "postWriteTimeType": "now",
            "tags": tags,
            "moviePanelParticipation": False,
            "greenReviewBannerYn": False,
            "continueSaved": False,
            "noticePostYn": False,
            "autoByCategoryYn": False,
            "postLocationSupportYn": False,
            "postLocationJson": None,
            "prePostDate": None,
            "thisDayPostInfo": None,
            "scrapYn": False,
        },
        "editorSource": editor_source,
    }

    # POST
    data = {
        "blogId": blog_id,
        "documentModel": json.dumps(document_model),
        "populationParams": json.dumps(population_params),
        "productApiVersion": "v1",
    }

    resp = _post_form(
        f"{BLOG_HOST}/RabbitWrite.naver",
        data=data,
        extra_headers={
            "Referer": f"{BLOG_HOST}/PostWriteForm.naver?blogId={quote(blog_id)}&categoryNo={quote(category_no)}&Redirect=Write",
        },
    )

    result = resp.json()
    if not result.get("isSuccess"):
        raise ValueError(f"발행 실패: {json.dumps(result, ensure_ascii=False)[:300]}")

    redirect_url = result.get("result", {}).get("redirectUrl", "")
    log_no_match = re.search(r"logNo=(\d+)", redirect_url)
    log_no = log_no_match.group(1) if log_no_match else None

    return {
        "success": True,
        "entryUrl": f"{BLOG_HOST}/{blog_id}/{log_no}" if log_no else None,
        "logNo": log_no,
        "raw": result,
    }


# ============================================================
# 5. 전체 발행 흐름
# ============================================================
def full_publish(title, content, tags=None, headless=False, image_paths=None, main_category=None):
    """네이버 블로그 발행 — 순수 HTTP API 방식"""
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 네이버 발행 (HTTP API)")
    print(f"  제목: {title[:40]}")
    if image_paths:
        print(f"  이미지: {len(image_paths)}장")
    print(f"{'='*60}")

    # 1) 블로그 ID 확인
    try:
        blog_id = init_blog()
        print(f"   블로그 ID: {blog_id}")
    except Exception as e:
        print(f"   ❌ 블로그 ID 확인 실패: {e}")
        print("   쿠키 갱신 시도...")
        if not login_and_save_cookies():
            raise Exception("로그인 실패")
        blog_id = init_blog()
        print(f"   블로그 ID: {blog_id}")

    # 2) 카테고리 확인
    categories = get_categories(blog_id)
    print(f"   카테고리: {list(categories.keys())[:5]}")

    category_no = "0"
    if main_category:
        for name, cat_id in categories.items():
            if main_category in name or name in main_category:
                category_no = str(cat_id)
                break
    if category_no == "0" and categories:
        category_no = str(min(categories.values()))
    print(f"   선택 카테고리: {category_no}")

    # 3) 토큰 획득
    token = get_token(blog_id, category_no)
    print(f"   토큰 획득 완료")

    # 4) 이미지 업로드
    image_resources = []
    if image_paths:
        for idx, img_path in enumerate(image_paths):
            if not os.path.exists(img_path):
                continue
            try:
                resource = upload_image(img_path, token, blog_id)
                image_resources.append(resource)
                print(f"   ✅ 이미지 {idx+1}/{len(image_paths)} 업로드")
            except Exception as e:
                print(f"   ⚠️ 이미지 {idx+1} 실패: {e}")

    # 5) HTML → 컴포넌트 변환
    # HTML 구조로 변환
    html_parts = []
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    for para in paragraphs:
        seg = para.replace("**", "").replace("___", "").replace("__", "").strip()
        if not seg:
            continue
        if seg.startswith("### ") or seg.startswith("## ") or seg.startswith("# "):
            text = re.sub(r"^#{1,3}\s*", "", seg)
            html_parts.append(f"<h3>{text}</h3>")
        else:
            html_parts.append(f"<p>{seg}</p>")
    html_content = "\n".join(html_parts)

    # 업로드한 이미지를 HTML에 <img>로 주입 (변환기가 이미지 컴포넌트로 처리)
    if image_resources:
        html_content = _inject_images_into_html(html_content, image_resources)

    # Naver API로 변환 시도
    content_components = convert_html_to_components(html_content, blog_id)
    if not content_components:
        print("   HTML 변환 실패 — 수동 컴포넌트 구성")
        content_components = _build_components_from_content(title, content, image_resources)

    print(f"   컴포넌트: {len(content_components)}개")

    # 6) 발행
    tag_str = ",".join(tags) if tags else ""
    result = publish_post(blog_id, title, content_components, category_no, tag_str)

    if result.get("success"):
        url = result.get("entryUrl")
        print(f"   ✅ 발행 성공!")
        print(f"   URL: {url}")

        # 쿠키 갱신
        try:
            driver = create_driver()
            try:
                driver.get("https://www.naver.com")
                time.sleep(2)
                cookies = driver.get_cookies()
                with open(COOKIE_PATH, "w", encoding="utf-8") as f:
                    json.dump(cookies, f, ensure_ascii=False, indent=2)
            finally:
                driver.quit()
        except Exception:
            pass

        return url
    else:
        raise Exception(f"발행 실패: {result}")


if __name__ == "__main__":
    print("=== 네이버 발행 모듈 (HTTP API) 테스트 ===")
    url = full_publish(
        title="테스트 발행 HTTP API",
        content="이것은 순수 HTTP API 방식 테스트입니다.\n\n브라우저 조작 없이 서버에 직접 요청을 보냅니다.\n\n성공하면 완전 자동화가 가능합니다.",
        tags=["테스트"],
        main_category="무료운세",
    )
    print(f"결과: {url}")
