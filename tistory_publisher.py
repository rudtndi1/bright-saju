# tistory_publisher.py - 이미지 포함 발행

import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

TISTORY_ACCESS_TOKEN = os.getenv("TISTORY_ACCESS_TOKEN")
TISTORY_BLOG_NAME = os.getenv("TISTORY_BLOG_NAME", "your-blog-name")

def upload_image_to_tistory(image_url):
    """
    외부 이미지 URL을 티스토리에 업로드하고 티스토리 URL로 변환
    """
    # 이미지 다운로드
    img_response = requests.get(image_url, timeout=30)
    if img_response.status_code != 200:
        return None
    
    # 임시 파일 저장
    temp_path = "temp_image.jpg"
    with open(temp_path, "wb") as f:
        f.write(img_response.content)
    
    # 티스토리 파일 업로드 API
    upload_url = "https://www.tistory.com/apis/post/attach"
    
    with open(temp_path, "rb") as f:
        files = {"uploadedfile": f}
        params = {
            "access_token": TISTORY_ACCESS_TOKEN,
            "output": "json",
            "blogName": TISTORY_BLOG_NAME
        }
        
        response = requests.post(upload_url, params=params, files=files)
    
    # 임시 파일 삭제
    os.remove(temp_path)
    
    result = response.json()
    if result.get("tistory", {}).get("status") == "200":
        return result["tistory"]["url"]
    
    return None


def publish_to_tistory(title, content_html, tags=None, category_id=None):
    """
    티스토리에 글 발행 (이미지 포함)
    """
    
    # HTML 내의 외부 이미지 URL을 티스토리 URL로 교체
    img_pattern = r'src="(https://image\.pollinations\.ai/[^"]+)"'
    img_urls = re.findall(img_pattern, content_html)
    
    print(f"🖼️ {len(img_urls)}개의 이미지 업로드 중...")
    
    for i, img_url in enumerate(img_urls):
        tistory_img_url = upload_image_to_tistory(img_url)
        if tistory_img_url:
            content_html = content_html.replace(img_url, tistory_img_url, 1)
            print(f"  ✅ 이미지 {i+1} 업로드 완료")
        else:
            print(f"  ⚠️ 이미지 {i+1} 업로드 실패, 원본 URL 유지")
    
    # API 발행
    url = "https://www.tistory.com/apis/post/write"
    params = {
        "access_token": TISTORY_ACCESS_TOKEN,
        "output": "json",
        "blogName": TISTORY_BLOG_NAME,
        "title": title,
        "content": content_html,
        "visibility": 3,  # 발행
        "category": category_id or 0,
        "tag": ",".join(tags) if tags else "",
        "acceptComment": 1,
    }
    
    response = requests.post(url, params=params)
    result = response.json()
    
    if result.get("tistory", {}).get("status") == "200":
        post_id = result["tistory"]["postId"]
        post_url = result["tistory"]["url"]
        print(f"✅ 티스토리 발행 완료!")
        print(f"   URL: {post_url}")
        return {"postId": post_id, "url": post_url}
    else:
        error_msg = result.get("tistory", {}).get("error_message", "Unknown error")
        raise Exception(f"티스토리 발행 실패: {error_msg}")


if __name__ == "__main__":
    # 테스트
    test_html = """
    <div style="text-align:center;">
        <img src="https://image.pollinations.ai/prompt/Korean%20traditional%20fortune%20telling%20illustration?width=800&height=500" style="max-width:100%;">
    </div>
    <p>테스트 본문입니다.</p>
    """
    
    result = publish_to_tistory("테스트 글", test_html, tags=["테스트"])