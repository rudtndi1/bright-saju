@echo off
REM ============================================================
REM 매일 09:00 블로그 자동화 실행 진입점 (Windows 작업 스케줄러용)
REM 생성 -> Notion 저장 -> 네이버 발행 -> 상태 갱신
REM 로그는 logs\daily.log 에 누적 기록
REM ============================================================
cd /d C:\AI\bright-saju-blog
if not exist logs mkdir logs
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
C:\AI\bright-saju-blog\venv\Scripts\python.exe C:\AI\bright-saju-blog\main.py auto >> C:\AI\bright-saju-blog\logs\daily.log 2>&1
