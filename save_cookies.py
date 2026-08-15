import os
import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def save_cookies():
    chrome_options = Options()
    
    # ✅ 기존 Chrome 프로필 사용 (이미 로그인된 상태 그대로)
    user_data_dir = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")
    profile_dir = "Default"
    
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument(f"--profile-directory={profile_dir}")
    
    # 셀레니움 감지 우회 옵션들
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        # 네이버 메인으로 이동 (이미 로그인된 상태)
        driver.get("https://www.naver.com")
        print("네이버 메인이 열렸습니다.")
        print("로그인 상태를 확인하세요.")
        input("확인 후 Enter 키를 누르세요 >>> ")
        
        # 쿠키 저장
        cookies = driver.get_cookies()
        with open("naver_cookies.pkl", "wb") as f:
            pickle.dump(cookies, f)
        
        print(f"쿠키 저장 완료! ({len(cookies)}개)")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    save_cookies()