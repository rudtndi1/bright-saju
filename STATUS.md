# 작업 진행 상태 (2026-08-01 오후 기준 — 갱신)

> 다음 세션에서 Claude에게 "STATUS.md 보고 이어서" 하면 됩니다.

## 목표
`C:\AI\bright-saju-blog` 블로그 자동화 **전체 자동화 완성**
→ 카테고리별 순환 + 소재 뱅크 기반 + 사람이 쓴 것 같은 글 + 실사 사진 + 무인 발행

---

## 완료된 변경 (2026-08-01 오후 갱신)

### 대분류 5건 발행 완료 (이미지 포함)
| 카테고리 | 제목 | logNo | 상태 |
|----------|------|-------|------|
| 무료운세 | 띠별 운세 운이 좋은 띠 순서 | 224364812750 | ✅ 발행 + 이미지4장 삽입 |
| 손없는날_길일 | 2월 이사 날짜 잡기 전 확인할 것 | 224364813421 | ✅ 발행 + 이미지4장 삽입 |
| 작명_출산 | 남자아이 이름풀이 방법 | 224364814045 | ✅ 발행 + 이미지4장 삽입 |
| 이사_생활정보 | 자취 세탁기 추천 완벽 가이드 | 224364814749 | ✅ 발행 + 이미지4장 삽입 |
| 선물_경조사 | 추천 명절선물 건강식품 세트 총정리 | 224364815385 | ✅ 발행 + 이미지4장 삽입 |

- 텍스트 발행: HTTP API (`publish_naver_api.py`)로 빠르게 발행
- 이미지 삽입: Selenium SmartEditor 편집 모드로 에디터 열어서 이미지 삽입 후 저장
- 각 글: 대표 카드뉴스 이미지1장 + 본문 실사 이미지3장 = 총4장
- 이미지 소스: Pillow 카드뉴스(대표) + Unsplash 실사(본문)

### 추가 개발 내역
| 파일 | 변경 |
|------|------|
| `publish_all_categories.py` | **신규** — 대분류5건 배치 발행 (HTTP API) |
| `add_images_to_posts.py` | **신규** — 기존 글에 Selenium으로 이미지 추가 |
| `login_fresh.py` | **신규** — 완전 새 프로필로 로그인 (stale 세션 해결) |
| `re_login.py` | **신규** — 기존 프로필 강제 재로그인 |
| `publish_naver_api.py` | `_inject_images_into_html` 추가, `upload_image`에 imageFileName 필드 추가 |

### 주요 발견
| 항목 | 내용 |
|------|------|
| HTTP 이미지 업로드 | `blog.upphoto.naver.com`이 현재 네이버 에디터 photo-infra 시스템으로 전환 → HTTP로 재현 어려움 |
| 안정적 이미지 삽입 경로 | **Selenium SmartEditor** (`publish_approved.py`의 `insert_image_at_cursor`)가 검증된 유일한 경로 |
| 세션 문제 | `login_profile.py` 프로필에 stale 세션이 남아 있어 `login_fresh.py` (새 프로필) 필요 |
| 편집 모드 에디터 | `PostWriteForm.naver?Redirect=Edit&directAccess=true` → 메인 프레임에 렌더링 (mainFrame iframe 아님) |

---

## 완료된 변경 (2026-08-01)

### 🔴 블로킹 이슈 해결
| 이슈 | 해결 |
|------|------|
| 헤드리스 Chrome 크래시 (DevToolsActivePort) | **원인: Default 프로필 사용** → 전용 프로필(`chrome_profile/`)로 전환하면 headed/headless 모두 성공 |
| Default 프로필 잠금 (Chrome 실행 시 충돌) | 전용 프로필로 완전 분리 — Chrome 실행 중에도 발행 가능 |
| undetected-chromedriver 호환 불가 (Python 3.14) | 일반 selenium + CDP stealth(navigator.webdriver 숨기기) 조합으로 대체 |

### 📁 신규/변경 파일

| 파일 | 변경 내용 |
|---|---|
| `topic_bank.py` | **신규** — 소재 뱅크 관리 모듈 (topics.json에서 미사용 키워드 선택/사용완료 표시) |
| `topics.json` | **신규** — 19개 세부 카테고리 ×45개 롱테일 키워드 = 855개 소재 |
| `build_topic_bank.py` | **신규** — 소재 뱅크 생성 스크립트 |
| `image_fetcher.py` | **신규** — 이미지 확보 모듈 (Pillow 카드뉴스 대표 이미지 + Unsplash 실사 본문 이미지) |
| `login_profile.py` | **신규** — 전용 프로필 최초 1회 로그인 헬퍼 |
| `fonts/NanumGothic-*.ttf` | **신규** — 나눔고딕 폰트 (카드뉴스 이미지용) |
| `chrome_profile/` | **신규** — 전용 Chrome 프로필 (자동 생성) |
| `content_generator.py` | **대폭 개선** — 카테고리별 톤 차등, AI 특유 표현 금지 50개, 불규칙 문장 길이, FAQ/표/체크리스트 포함, 링크 1~2개 |
| `publish_approved.py` | **리팩터링** — 전용 프로필 사용, 캡차 감지, 세션만료 감지, 이미지 로컬 파일 직접 삽입, 쿠키 갱신 |
| `main.py` | **개선** — 소재 뱅크 연동, 이미지 모듈 연동, `schedule` 명령 추가, `bank`/`bank-reset`/`driver-test` 명령 추가, UTF-8 로깅 |
| `setup_task.ps1` | 09:00 → 09:17 (정각 피하고 자연스러운 시간) |
| `run_daily.bat` | PYTHONUTF8 환경 변수 추가 |
| `벤방지_가이드.md` | **신규** — 조사 결과 기반 벤 회피 가이드 (이미 시스템에 반영된 내용 포함) |
| `매뉴얼.md` | 갱신 (아래) |

---

## 현재 시스템 아키텍처

```
[소재 뱅크 topics.json] → 소재 선택 (미사용 키워드)
          ↓
[Groq LLaMA-3.3-70B] → 사람이 쓴 것 같은 글 생성 (카테고리별 톤)
          ↓
[Notion DB] → 검토대기 상태로 저장 (외부 이미지 URL 포함)
          ↓
[image_fetcher] → 대표 카드뉴스(Pillow) + 본문 실사(Unsplash/풀) 로컬 저장
          ↓
[Selenium] → 전용 프로필 + headed 모드로 네이버 SmartEditor 자동 입력
          ↓
[Notion] → 발행완료 + URL 기록 | [소재 뱅크] → 사용완료 표시
```

## 핵심 설계 결정

| 항목 | 결정 | 이유 |
|------|------|------|
| Chrome 프로필 | 전용 (`chrome_profile/`) 사용 | Default 프로필과 분리 → Chrome 실행 중에도 무력 충돌 없음 |
| 발행 모드 | headed (기본) | 봇 탐지 회피 + 가장 안정적 (1건당 1~2분) |
| 이미지 소스 | 카드뉴스 대표 + Unsplash 실사 본문 | AI 이미지(스톡)는 저품질 신호 → 실사 사진이 안전 |
| 발행 시간 | 09:17 | 정각 자동 발행은 자동화 의심 신호 |
| 로그인 | 전용 프로필 세션 유지 | 쿠키 주입보다 프로필 영속 세션이 가장 안정적 |

---

## 최초 셋업 (사용자가 해야 할 일)

### 1회만:
```powershell
cd C:\AI\bright-saju-blog

:: 1) 전용 프로필로 네이버 로그인 (Chrome 창이 열리면 로그인 후 Enter)
venv\Scripts\python.exe login_profile.py

:: 2) API 키 확인 (.env 파일)
::    GROQ_API_KEY (있음), NOTION_TOKEN (있음), NOTION_DATABASE_ID (있음)
::    UNSPLASH_ACCESS_KEY (선택: 있으면 Unsplash 사진 검색, 없으면 카테고리 사진 풀 사용)
::    PEXELS_API_KEY (선택: 있으면 Pexels 사진 검색)
```

### 반복:
```powershell
:: 자동 발행 1건
venv\Scripts\python.exe main.py auto

:: 소재 뱅크 현황
venv\Scripts\python.exe main.py bank

:: 드라이버 진단
venv\Scripts\python.exe main.py driver-test
```

### 스케줄러 재등록:
```powershell
powershell -ExecutionPolicy Bypass -File setup_task.ps1
```

---

## 벤(저품질) 방지 조치 현황

| 조치 | 상태 | 상세 |
|------|------|------|
| AI 특유 표현 금지 | ✅ 반영 | 프롬프트에 50개+ 금지 표현 명시 |
| 불규칙 문장 길이 | ✅ 반영 | 짧은 문장+긴 문장 섞기 지시 |
| 개인 경험 에피소드 | ✅ 반영 | 첫 문단 에피소드 필수 |
| 소제목·표·체크리스트 | ✅ 반영 | H3 4~5개 + 표 1개 + 체크리스트 |
| FAQ 섹션 | ✅ 반영 | 5~7개 Q&A |
| 링크 포함 | ✅ 반영 | 내부 링크 1개 포함 |
| 태그-본문 일치 | ✅ 반영 | 태그 3개 이상 본문 등장 |
| 실사 사진 사용 | ✅ 반영 | Unsplash/풀 이미지 (AI 생성 이미지 미사용) |
| 발행 시간 분산 | ✅ 반영 | 정각(09:00) 피하고 09:17 사용 |
| 정각 발행 회피 | ✅ 반영 | setup_task.ps1 09:17로 변경 |
| navigator.webdriver 숨기기 | ✅ 반영 | CDP 스크립트 적용 |
| 하루 발행량 1건 | ✅ 반영 | auto=1건, schedule=다수 가능 |
| 캡차 감지 | ✅ 반영 | 발행 중 캡차 발견 시 즉시 중단 |
| 세션 만료 감지 | ✅ 반영 | NID_AUT/NID_SES 쿠키 존재 확인 |

---

## 참고 문서

| 문서 | 설명 |
|------|------|
| `매뉴얼.md` | 전체 시스템 매뉴얼 |
| `벤방지_가이드.md` | 조사 결과 기반 벤 회피 가이드 (자세한 분석) |
| `README.md` | 빠른 시작 가이드 |

---

## 주의사항
- `.env`에 실키(API 키/네이버 계정)가 들어 있음. 절대 공개/커밋 금지.
- 발행은 검토 없이 즉시 나가는 방식 — 테스트 시 실제 네이버 블로그에 글이 올라감.
- **전용 프로필 사용**: `chrome_profile/` 폴더. 자동으로 생성되며, 최초 1회 login_profile.py로 로그인 필요.
- Default 프로필과 완전 분리 — 다른 Chrome과 충돌 없음.
- 이미지는 `images/` 폴더에 로컬 저장됨. 주기적으로 정리해도 발행에는 영향 없음.
