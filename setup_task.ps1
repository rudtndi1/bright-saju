# ============================================================
# setup_task.ps1 - 매일 09:00 블로그 자동화 작업 등록
# 사용법: powershell -ExecutionPolicy Bypass -File setup_task.ps1
#
# 주의: Chrome이 켜져 있으면 Default 프로필이 잠겨 발행이 실패함.
#       09:00 자동 실행 시 Chrome을 닫아둔 상태여야 함.
# ============================================================
$ProjectDir = "C:\AI\bright-saju-blog"
$TaskName = "BrightSajuBlogDaily"
$BatPath = "$ProjectDir\run_daily.bat"

# 사전 검사
if (-not (Test-Path $BatPath)) {
    Write-Host "run_daily.bat 를 찾을 수 없습니다: $BatPath"
    exit 1
}
if (-not (Test-Path "$ProjectDir\venv\Scripts\python.exe")) {
    Write-Host "venv python.exe 를 찾을 수 없습니다."
    exit 1
}

# 실행 액션: run_daily.bat (내부에서 로그 리다이렉트)
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$BatPath`"" -WorkingDirectory $ProjectDir

# 트리거: 매일 09:17 (정각 피하고 자연스러운 시간)
$trigger = New-ScheduledTaskTrigger -Daily -At "09:17"

# 설정: 정각에 컴퓨터가 꺼져 있어도 켜진 뒤 실행, 최대 2시간 제한
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# 실행 주체: 현재 로그인 사용자 (로그인 상태에서만 실행)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

# 작업 등록 (동일 이름이 있으면 덮어쓰기)
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "좋은 기운 하루 블로그 자동화: 매일 09:00 글 생성 + 네이버 발행" -Force | Out-Null

Write-Host "작업 등록 완료: $TaskName (매일 09:00)"

# 등록 결과 확인
Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName, State, @{N='시작시각';E={$_.Triggers[0].StartBoundary}}
