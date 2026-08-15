import os
import re
import random
import urllib.parse
import requests
from datetime import datetime
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

notion = Client(auth=os.getenv("NOTION_TOKEN"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")


# 최종 fallback용 (Pollinations/Unsplash 둘 다 실패했을 때만 사용)
CATEGORY_DEFAULT_IMAGES = {
    "오늘의운세": [
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
        "https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?w=800&q=80",
        "https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?w=800&q=80",
    ],
    "손없는날": [
        "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=800&q=80",
        "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800&q=80",
    ],
    "이사날짜": [
        "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800&q=80",
        "https://images.unsplash.com/photo-1484154218962-a1c002085d2f?w=800&q=80",
    ],
    "이름풀이": [
        "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=800&q=80",
        "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=800&q=80",
    ],
    "인기글": [
        "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800&q=80",
        "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800&q=80",
    ],
}


def get_image_url(query, category, index=0):
    """이미지 URL 가져오기 - 글 내용(query=AI 이미지 프롬프트)에 맞춰 매번 새로 생성"""

    # 1. Pollinations.ai로 프롬프트 기반 이미지 생성 (무료, 키 불필요)
    #    seed를 매번 랜덤으로 줘서 같은 프롬프트라도 반복되지 않게 함
    #    실제로 이미지가 다 만들어질 때까지 기다린 뒤 URL을 넘겨야
    #    노션에서 "불러올 수 없음" 오류가 안 남
    try:
        encoded = urllib.parse.quote(query)
        seed = random.randint(1, 999999)
        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=800&height=600&seed={seed}&nologo=true&model=flux"
        )
        print(f"   🎨 이미지 생성 중... (프롬프트: {query[:60]}...)")
        resp = requests.get(url, timeout=60)
        if resp.status_code == 200 and len(resp.content) > 1000:
            print(f"   ✅ 이미지 생성 완료")
            return url
        else:
            print(f"   ⚠️ 이미지 생성 실패 (status={resp.status_code}), fallback 사용")
    except Exception as e:
        print(f"   ⚠️ 이미지 생성 오류: {e}, fallback 사용")

    # 2. Unsplash API (키가 있는 경우 백업)
    if UNSPLASH_ACCESS_KEY:
        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
            params = {"query": query, "per_page": 1, "orientation": "landscape"}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            data = response.json()
            if data.get("results"):
                return data["results"][0]["urls"]["regular"]
        except:
            pass

    # 3. 카테고리별 기본 이미지 (최종 fallback, 여기까지 오면 안 됨)
    if category in CATEGORY_DEFAULT_IMAGES:
        images = CATEGORY_DEFAULT_IMAGES[category]
        return images[index % len(images)]

    return "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80"


def check_image_url(url):
    """이미지 URL 유효성 확인"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            return 'image' in content_type
        return False
    except:
        return False


def _compute_image_positions(total, img_count):
    """문단 수와 이미지 수 기준으로 이미지 삽입 위치 계산 (최대 3개)"""
    positions = []
    if img_count >= 1:
        positions.append(max(1, total // 4))
    if img_count >= 2:
        positions.append(max(2, total // 2))
    if img_count >= 3:
        positions.append(max(3, total * 3 // 4))
    return positions


def build_publish_content(content, image_urls):
    """Notion 저장과 동일한 위치에 [IMG:url] 마커를 삽입한 네이버 발행용 텍스트 생성"""
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    if not paragraphs:
        return content
    total = len(paragraphs)
    positions = _compute_image_positions(total, len(image_urls))
    out = []
    img_idx = 0
    for i, para in enumerate(paragraphs):
        if i in positions and img_idx < len(image_urls):
            out.append(f"[IMG:{image_urls[img_idx]}]")
            img_idx += 1
        out.append(para)
    return "\n\n".join(out)


def create_content_blocks(content, image_prompts, category):
    """본문 + 이미지 블록 생성. (blocks, 실제 사용된 이미지 URL 목록) 반환"""
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

    if not paragraphs:
        return [], []

    total = len(paragraphs)
    positions = _compute_image_positions(total, len(image_prompts))

    blocks = []
    used_urls = []
    img_idx = 0

    for i, para in enumerate(paragraphs):
        if i in positions and img_idx < len(image_prompts):
            img_url = get_image_url(image_prompts[img_idx], category, img_idx)
            used_urls.append(img_url)

            blocks.append({
                "object": "block",
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {"url": img_url}
                }
            })

            blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })

            img_idx += 1

        para = para.strip()
        if not para:
            continue

        if para.startswith('#'):
            level = len(para.split()[0])
            text = para.lstrip('#').strip()
            h_type = f"heading_{min(level, 3)}"
            blocks.append({
                "object": "block",
                "type": h_type,
                h_type: {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                }
            })
        elif para.startswith('>'):
            text = para.lstrip('>').strip()
            blocks.append({
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                }
            })
        elif '\n' in para and any(line.strip().startswith('- ') for line in para.split('\n')):
            for line in para.split('\n'):
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    text = line[2:].strip()
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": text}}]
                        }
                    })
        elif para.startswith('- ') or para.startswith('* '):
            text = para[2:].strip()
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                }
            })
        else:
            rich_text = []
            parts = re.split(r'(\*\*.*?\*\*)', para)
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    rich_text.append({
                        "type": "text",
                        "text": {"content": part[2:-2]},
                        "annotations": {"bold": True}
                    })
                else:
                    rich_text.append({
                        "type": "text",
                        "text": {"content": part}
                    })

            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": rich_text}
            })

    return blocks, used_urls


def save_to_notion(title, content, category, tags=None, image_prompts=None):
    """노션에 글 저장. (page_id, 실제 사용된 이미지 URL 목록) 반환"""
    print(f"\n{'='*50}")
    print(f"📝 저장 시작: {title}")

    blocks, image_urls = create_content_blocks(content, image_prompts or [], category)

    multi_select = []
    if tags:
        multi_select = [{"name": t} for t in tags[:10]]
    if category and category not in [t["name"] for t in multi_select]:
        multi_select.append({"name": category})

    properties = {
        "제목": {"title": [{"text": {"content": title}}]},
        "카테고리": {"select": {"name": category}},
        "상태": {"status": {"name": "검토대기"}},
        "생성일": {"date": {"start": datetime.now().isoformat()}},
    }
    if multi_select:
        properties["태그"] = {"multi_select": multi_select}

    new_page = notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties=properties
    )

    if blocks:
        notion.blocks.children.append(
            block_id=new_page["id"],
            children=blocks
        )

    img_count = len([b for b in blocks if b["type"] == "image"])
    print(f"✅ 저장 완료!")
    print(f"   페이지: https://notion.so/{new_page['id'].replace('-', '')}")
    print(f"   이미지: {img_count}개")
    print(f"   블록: {len(blocks)}개")
    print(f"{'='*50}")

    return new_page['id'], image_urls


def get_approved_posts():
    """승인된 글 가져오기"""
    response = notion.databases.query(
        database_id=DATABASE_ID,
        filter={"property": "상태", "status": {"equals": "승인"}}
    )

    posts = []
    for page in response["results"]:
        props = page["properties"]

        title = ""
        if props.get("제목") and props["제목"].get("title"):
            title = props["제목"]["title"][0]["text"]["content"] if props["제목"]["title"] else ""

        content = ""
        try:
            blocks = notion.blocks.children.list(block_id=page["id"])
            for block in blocks["results"]:
                bt = block["type"]
                if bt in ["paragraph", "heading_1", "heading_2", "heading_3", "quote", "bulleted_list_item"]:
                    rt = block.get(bt, {}).get("rich_text", [])
                    text = "".join([r["text"]["content"] for r in rt])
                    if text:
                        content += text + "\n\n"
                elif bt == "image":
                    img = block.get("image", {})
                    img_url = img.get("external", {}).get("url") or img.get("file", {}).get("url")
                    if img_url:
                        content += f"[IMG:{img_url}]\n\n"
        except:
            pass

        category = props.get("카테고리", {}).get("select", {}).get("name", "")
        tags = [t["name"] for t in props.get("태그", {}).get("multi_select", [])]

        posts.append({
            "id": page["id"],
            "title": title,
            "content": content.strip(),
            "category": category,
            "tags": tags
        })

    return posts


def update_status(page_id, status, blog_url=None):
    """상태 업데이트"""
    props = {"상태": {"status": {"name": status}}}
    if blog_url:
        props["블러그URL"] = {"url": blog_url}
    notion.pages.update(page_id=page_id, properties=props)
    print(f"📝 상태: {status}")


if __name__ == "__main__":
    test = {
        "title": "[테스트] 7월 21일 오늘의 운세",
        "content": "안녕하세요, 좋은 기운 하루입니다.\n\n오늘은 특별한 날입니다.\n\n**쥐띠**\n행운이 가득합니다.\n\n**소띠**\n좋은 소식이 있습니다.",
        "category": "오늘의운세",
        "tags": ["오늘의운세", "사주"],
        "image_prompts": ["korean fortune telling warm sunrise, beige tone, ivory tone, 4k"]
    }
    pid, img_urls = save_to_notion(**test)
    print(f"테스트 완료: {pid}")
    print(f"사용된 이미지: {len(img_urls)}개")