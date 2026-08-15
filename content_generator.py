# -*- coding: utf-8 -*-
"""
콘텐츠 생성 모듈 (Groq API + LLaMA-3.3-70B)
- 카테고리별 톤 차등 (전문/실용/공감)
- AI 특유 표현 금지 → 사람이 쓴 것 같은 글쓰기
- FAQ, 표, 체크리스트 포함 (정보 밀도 ↑)
- 키워드 기반 발행: 소재 뱅크의 롱테일 키워드를 topic으로 받음
"""
import os
import re
import random
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# =========================================================
# 카테고리 구조 (topic_bank.py와 동일)
# =========================================================
CATEGORIES = {
    "무료운세": ["오늘의 운세", "띠별 운세", "무료 궁합"],
    "손없는날_길일": ["손없는날", "이사 날짜", "개업 날짜", "결혼 택일"],
    "작명_출산": ["작명", "이름풀이", "출산 준비"],
    "이사_생활정보": ["이사 준비 체크리스트", "집들이 선물", "신혼집 준비", "자취 필수템", "생활용품 추천"],
    "선물_경조사": ["결혼선물", "집들이선물", "부모님선물", "명절선물"],
}

WEEKDAY_MAIN_CATEGORY = [
    "무료운세",        # 월
    "손없는날_길일",   # 화
    "작명_출산",       # 수
    "이사_생활정보",   # 목
    "선물_경조사",     # 금
    "무료운세",        # 토
    "손없는날_길일",   # 일
]

# =========================================================
# 카테고리별 톤/_Invoke문 전문
# =========================================================
CATEGORY_TONES = {
    "무료운세": (
        "주제: 명리학·사주·운세 분야. 톤은 믿음 가는 전문가지만 어렵지 않게 풀어주는 설명.\n"
        "경력·실제 경험을 언급하며 신뢰감을 준다. 구체적 사례(연예인 사주, 주변 사람 에피소드)로 설명.\n"
        "전문 용어(십신, 오행, 십이지, 세운 등)를 쓸 때 반드시 쉬운 설명을 덧붙인다."
    ),
    "손없는날_길일": (
        "주제: 손없는날·길일·택일 분야. 톤은 실용 정보 가이드.\n"
        "달력/날짜 중심으로 설명. 구체적 날짜와 팁을 제공.\n"
        "이사·개업·결혼 등 중요한 일정에 대한 실질적 조언이 핵심."
    ),
    "작명_출산": (
        "주제: 작명·이름풀이·출산 준비 분야. 톤은 정서적 공감 + 전문성.\n"
        "예비 부모의 마음에 공감하며, 이름이 아이에게 미치는 영향을 따뜻하게 설명.\n"
        "성명학 용어(오행, 한자 뜻, 발음 구조 등)를 쉽게 풀어서 전달."
    ),
    "이사_생활정보": (
        "주제: 이사·생활정보 분야. 톤은 실용 체크리스트·꿀팁 위주.\n"
        "체크리스트·비교표·단계별 절차로 구성. 정보 밀도 높이기.\n"
        "실제 사용 경험에서 나오는 꿀팁을 자연스럽게 섞는다."
    ),
    "선물_경조사": (
        "주제: 선물·경조사 분야. 톤은 예산/가격 중심 실용 꿀팁.\n"
        "가격대별 추천·실속 있는 선택·센스 있는 아이디어를 제공.\n"
        "상황별(결혼·집들이·부모님·명절) 구체적 추천이 핵심."
    ),
}

# =========================================================
# AI 특유 표현 금지 목록 (조사 결과 인용)
# =========================================================
BANNED_EXPRESSIONS = (
    "아래 표현은 절대 쓰지 않는다 (AI로 판별되는 표현들):\n"
    "- '알아보도록 하겠습니다', '확인해보겠습니다', '살펴보겠습니다'\n"
    "- '결론적으로 말씀드리자면', '결론적으로 정리하자면', '정리하자면'\n"
    "- '많은 분들이 궁금해하시는', '많은 분들이 모르는'\n"
    "- '~하는 것이 좋습니다', '~하는 것이 중요합니다'\n"
    "- '~라고 할 수 있습니다', '~이라고 말할 수 있습니다'\n"
    "- '이처럼', '이에 따라', '그러므로', '따라서'\n"
    "- '최근', '요즘', '현재'로 문장 시작을 남발\n"
    "- 문장 시작에 '또한', '그리고', '더불어'를 반복 사용\n"
    "- '어떻게 하면 좋을까요?'를 2회 이상 반복\n"
    "→ 위 표현 대신 일상적인 말투로 대체한다."
)

# =========================================================
# 이미지 스타일 (이미지 프롬프트에 붙이는 접미사)
# =========================================================
IMAGE_STYLE_SUFFIX = (
    ", real photograph, natural lighting, Korean lifestyle, "
    "authentic warm tone, 4k"
)

# =========================================================
# 참고 링크 (AI에게 부여하는 안정적인 URL)
# =========================================================
CATEGORY_REFERENCE_LINKS = {
    "무료운세": ["https://encyclopedias.naver.com/", "https://search.naver.com/search.naver?query=%EC%82%AC%EC%A3%BC%ED%8C%94%EC%9E%90"],
    "손없는날_길일": ["https://encyclopedias.naver.com/", "https://search.naver.com/search.naver?query=%EC%86%90%EC%97%86%EB%8A%94%EB%82%A0"],
    "작명_출산": ["https://encyclopedias.naver.com/", "https://search.naver.com/search.naver?query=%EC%9E%91%EB%AA%85"],
    "이사_생활정보": ["https://encyclopedias.naver.com/", "https://search.naver.com/search.naver?query=%EC%9D%B4%EC%82%AC%EC%A4%80%EB%B9%84"],
    "선물_경조사": ["https://encyclopedias.naver.com/", "https://search.naver.com/search.naver?query=%EA%B2%B0%ED%98%BC%EC%84%A0%EB%AC%BC"],
}


# =========================================================
# 시스템 프롬프트 (카테고리별 톤 + AI 특유 표현 금지)
# =========================================================
def _build_system_prompt(topic, subcategory, main_category):
    tone = CATEGORY_TONES.get(main_category, CATEGORY_TONES["이사_생활정보"])
    ref_links = CATEGORY_REFERENCE_LINKS.get(main_category, ["https://blog.naver.com/bright-saju"])
    external_link = random.choice(ref_links)

    return f'''당신은 30대 후반 여성으로, 네이버 블로그 "좋은 기운 하루"를 5년째 운영 중이다.
주제 "{topic}"(세부 카테고리: {subcategory})에 대해 이웃들에게 얘기하듯 블로그 글을 쓴다.

[블로그 성격/_Invoke문]
{tone}

[말투 - 반드시 지킬 것]
- 첫 문장 2~3개는 반드시 개인적인 일상/공감 에피소드로 시작한다.
  예: "요즘 이사 날짜 때문에 고민 많으시죠. 저도 2월에 이사하면서 하루종일 달력만 봤거든요."
- 문장 길이를 의도적으로 불규칙하게: 짧은 문장(3~8자 어절)과 긴 문장(30자 이상)을 섞는다.
  예: "진짜 힘들었어요. 주말에도 전화기만 붙들고 있었으니까요. 결국 3월 둘째 주 토요일로 잡았는데, 손없는날이라 마음이 좀 놓이더라고요."

{BANNED_EXPRESSIONS}

- 실제 사람이 친구한테 카톡 보내듯 편하게. 완벽한 문장보다 자연스러운 흐름.
- 구체적인 숫자/날짜/가격/예시를 넣는다 (정보 밀도 높이기).
- 개인 경험/일상 에피소드와 정보를 자연스럽게 섞는다.
- '채우기 문장'은 절대 금지. 정보 밀도가 낮으면 오히려 짧게 끝낸다.
- 과도하게 예의 바른 어투("도움이 되셨으면 좋겠습니다", "좋은 하루 보내세요")를 남발하지 않는다.

[구성 - 반드시 지킬 것]
- 소제목(H3) 5~7개. 딱딱한 명사형 대신 질문형/구어체.
  예: "손없는날이 대체 뭐길래?", "이사 날짜는 언제 잡아야 할까?", "진짜 필요한 것만 골랐어요"
- 표 1개 이상 포함 — 반드시 HTML <table> 태그로 직접 작성:
  예: <table><thead><tr><th>제품</th><th>가격</th><th>특징</th></tr></thead>
  <tbody><tr><td>홍삼세트</td><td>50,000원</td><td>면역력 강화</td></tr></tbody></table>
- 체크리스트 또는 번호 매긴 목록 1개 이상 — <ul><li> 또는 <ol><li> HTML로 직접 작성.
- FAQ 섹션: 글 마지막 부분에5~7개 Q&A 형식으로 포함.
  질문은 사람들이 실제로 검색할 법한 롱테일 키워드로.
- 메인 키워드 "{topic}"를 첫 문단과 중간, FAQ에 자연스럽게5회 이상 반복 (억지로 반복 말 것).
- 태그로 쓸 단어 중 최소3개는 본문에 자연스럽게 등장한다.
- 참고 링크: 본문 내용과 자연스럽게 연결해서 아래 URL을 본문에1회 언급한다:
  {external_link}
- 내부 링크: "우리 블로그에서도 관련 이야기를 다뤘어요 — 블로그 메인에서 확인: https://blog.naver.com/bright-saju" 형식으로1회 언급.
- 최소2500자 이상.

[절대 금지]
- 한자(漢字) 사용 금지. 한글과 영어만.
- 아래 출력 형식의 마커를 정확히 그대로 사용.
- 본문은 반드시 HTML 태그로 직접 작성: <p>, <h3>, <table>, <ul>, <li> 등.
- URL을 임의로 만들지 말 것. 반드시 위에 제시된 URL만 사용.

[출력 형식 - 마커를 정확히 그대로만 사용]
# SEO 제목
(제목 텍스트만 — SEO 키워드 포함,30자 이내 권장)
# 대표 이미지 프롬프트
(영문 프롬프트만, 한글 설명 금지. 예: "korean fortune telling warm beige morning light, real photograph, warm tone")
# 본문
<!--IMG:0-->
<p>첫 문단 — 개인 에피소드로 시작, 메인 키워드 포함</p>
<!--IMG:1-->
<h3>첫 번째 소제목</h3>
<p>본문 내용. HTML 태그를 직접 사용하여 구조화.</p>
<table><thead><tr><th>컬럼1</th><th>컬럼2</th></tr></thead><tbody><tr><td>값1</td><td>값2</td></tr></tbody></table>
IMAGE_PROMPT:
(영문 프롬프트만)
<h3>두 번째 소제목</h3>
<p>본문 내용.</p>
<ul><li>항목1</li><li>항목2</li><li>항목3</li></ul>
IMAGE_PROMPT:
(영문 프롬프트만)
<!--IMG:2-->
<h3>세 번째 소제목</h3>
<p>본문 내용.</p>
IMAGE_PROMPT:
(영문 프롬프트만)
<h3>네 번째 소제목</h3>
<p>본문 내용.</p>
<!--IMG:3-->
<p>마무리 + 참고 링크 언급 + 내부 링크 언급</p>
## 자주 묻는 질문
Q: (질문)
A: (답변)
... (5~7개)
# 태그
(태그10개, 쉼표로 구분)
'''


USER_PROMPT_TEMPLATE = "'{topic}' 주제로 블로그 글을 작성해주세요. 반드시 HTML 태그(<p>, <h3>, <table>, <ul>)를 사용하여 본문을 구조화하고, 첫 문장은 개인 경험으로 시작하세요. 5개 이상 소제목, 표1개 이상, FAQ를 포함하세요."


def generate_blog_post(main_category, topic=None, subcategory=None):
    """
    글 생성.
    - main_category: 대분류 ("무료운세" 등)
    - topic: 소재 뱅크의 롱테일 키워드. 미지정 시 카테고리에서 랜덤 선택.
    - subcategory: 세부 카테고리. 미지정 시 topic에서 추론하거나 랜덤.
    """
    if subcategory is None:
        subcategory = random.choice(CATEGORIES[main_category])
    if topic is None:
        topic = random.choice(CATEGORIES[main_category])

    system_prompt = _build_system_prompt(topic, subcategory, main_category)
    user_prompt = USER_PROMPT_TEMPLATE.format(topic=topic)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.85,
        max_tokens=6000,
    )

    raw = response.choices[0].message.content.strip()
    return parse_seo_output(raw, main_category, topic, subcategory)


def parse_seo_output(raw, main_category, topic, subcategory=None):
    """AI 출력(raw)을 title / cover_image_prompt / content / image_prompts / tags로 분해.
    이제 본문은 HTML 태그를 포함한다."""

    # 1) SEO 제목
    title_match = re.search(r"#\s*SEO\s*제목\s*\n(.+)", raw)
    title = title_match.group(1).strip() if title_match else f"{topic} 완벽 가이드"

    # 2) 대표 이미지 프롬프트
    cover_match = re.search(r"#\s*대표\s*이미지\s*프롬프트\s*\n(.+)", raw)
    cover_prompt = cover_match.group(1).strip() if cover_match else topic
    cover_prompt = cover_prompt + IMAGE_STYLE_SUFFIX

    # 3) 본문 영역 추출 (# 본문 ~ ## 자주 묻는 질문 또는 # 태그)
    body_match = re.search(r"#\s*본문\s*\n(.+?)(?:##\s*자주 묻는 질문|#\s*태그|$)", raw, re.S)
    body = body_match.group(1).strip() if body_match else raw

    # 4) FAQ 섹션 추출
    faq_match = re.search(r"(?:##?\s*자주 묻는 질문.*?)#?\s*태그", raw, re.S)
    faq_section = faq_match.group(0).replace("# 태그", "").strip() if faq_match else ""

    # 5) 본문에서 이미지 프롬프트 추출
    image_prompts = re.findall(r"IMAGE_PROMPT:\s*\n?(.+)", body)
    image_prompts = [p.strip() + IMAGE_STYLE_SUFFIX for p in image_prompts]

    # 6) 본문에서 IMAGE_PROMPT 라인 제거, 이미지 마커는 유지
    clean_body = re.sub(r"IMAGE_PROMPT:\s*\n?.+", "", body)
    clean_body = clean_body.replace("[대표이미지]", "").strip()
    for i in range(1, 10):
        clean_body = clean_body.replace(f"[본문이미지{i}]", "")
    clean_body = re.sub(r"\n{3,}", "\n\n", clean_body).strip()

    # 7) HTML 엔티티 디코딩
    import html as html_mod
    clean_body = html_mod.unescape(clean_body)

    # 8) 한자 제거
    clean_body = re.sub(r'[一-鿿]+', '', clean_body)
    clean_body = re.sub(r'\n{3,}', '\n\n', clean_body).strip()

    # 9) 태그
    tags_match = re.search(r"#\s*태그\s*\n(.+)", raw, re.S)
    tags = []
    if tags_match:
        tag_line = tags_match.group(1).strip()
        tags = [t.strip().lstrip("#") for t in re.split(r"[,\n]", tag_line) if t.strip()]

    return {
        "title": title,
        "content": clean_body,
        "tags": tags,
        "category": main_category,
        "subcategory": subcategory,
        "topic": topic,
        "cover_image_prompt": cover_prompt,
        "image_prompts": image_prompts if image_prompts else [cover_prompt],
    }


def validate_post(result):
    """생성된 글의 품질 검증. 문제 있으면 (False, [문제목록]) 반환."""
    issues = []
    content = result.get("content", "")

    # 길이 검증
    text_only = re.sub(r'<[^>]+>', '', content)
    if len(text_only) < 2000:
        issues.append(f"본문이 너무 짧음 ({len(text_only)}자, 최소2000자)")

    # H3 소제목 검증
    h3_count = len(re.findall(r'<h3[^>]*>', content))
    if h3_count < 3:
        issues.append(f"H3 소제목 부족 ({h3_count}개, 최소3개)")

    # 표 검증
    table_count = len(re.findall(r'<table[^>]*>', content))
    if table_count < 1:
        issues.append("표(<table>) 없음")

    # 이미지 마커 검증
    img_markers = len(re.findall(r'<!--IMG:\d+-->', content))
    if img_markers < 1:
        issues.append("이미지 마커(<!--IMG:N-->) 없음")

    # 금지 표현 검증
    for expr in ["알아보도록 하겠습니다", "확인해보겠습니다", "살펴보겠습니다",
                 "결론적으로 말씀드리자면", "결론적으로 정리하자면",
                 "많은 분들이 궁금해하시는"]:
        if expr in content:
            issues.append(f"금지 표현 발견: {expr}")

    return (len(issues) == 0, issues)


if __name__ == "__main__":
    print("=" * 50)
    print("[테스트] 글 생성 중...")
    print("=" * 50)
    try:
        result = generate_blog_post("무료운세")
        print(f"\n제목: {result['title']}")
        print(f"대분류: {result['category']} / 세부: {result.get('subcategory', '-')}")
        print(f"주제: {result['topic']}")
        print(f"대표이미지: {result['cover_image_prompt'][:60]}...")
        print(f"본문이미지 프롬프트: {len(result['image_prompts'])}개")
        print(f"태그: {result['tags']}")
        print(f"\n--- 본문 미리보기 (첫 600자) ---\n{result['content'][:600]}...")
    except Exception as e:
        print(f"오류: {e}")
