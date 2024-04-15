import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import easyocr

# 브라우저 설정
chrome_options = Options()
chrome_options.add_experimental_option('detach', True)
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1200, 1000)

# 웹사이트 도메인 입력
driver.get('u want web site')

# 팝업 창 닫기
WebDriverWait(driver, 1.1).until(
EC.element_to_be_clickable((By.XPATH, '//div[@class="popupCheck"]')))
driver.find_element(By.XPATH, '//div[@class="popupCheck"]').click()

# 로그인
def login(username, password):
    driver.find_element(By.LINK_TEXT, '로그인').click()
    WebDriverWait(driver, 1.1).until(
        EC.presence_of_element_located((By.ID, "userId")))
    driver.find_element(By.ID, "userId").send_keys(username)
    driver.find_element(By.ID, "userPwd").send_keys(password + Keys.ENTER)

# 사용자 아이디 비밀번호 입력
login('user_id', 'user_pass')

# 날짜 선택
def select_date(day):
    try:
        date_xpath = f"//li[normalize-space(text())='{day}']"
        WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, date_xpath)))
        driver.find_element(By.XPATH, date_xpath).click()
    except Exception as e:
        print("Error clicking the date:", e)

# 원하는 날짜 입력
select_date(00)

button_xpath = '//a[@class="sideBtn is-primary"]'
driver.find_element(By.XPATH, button_xpath).click()

# OCR 설정 및 캡차 처리
reader = easyocr.Reader(['en'])
def handle_captcha():
    try:
        # 캡차 이미지가 화면에 보이기를 기다림
        captcha_img = WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="imgCaptcha"]')))

        # 캡차 이미지를 스크린샷으로 캡처하고 텍스트 추출
        captcha_text = reader.readtext(captcha_img.screenshot_as_png)[0][1].replace(' ', '')
        print(f"Detected CAPTCHA text: {captcha_text}")  # 추출된 텍스트 출력

        # 캡차 입력 필드 찾기, 입력하기
        captcha_input = driver.find_element(By.XPATH, '//*[@id="txtCaptcha"]')
        captcha_input.clear()
        captcha_input.send_keys(captcha_text + Keys.ENTER)
    except Exception as e:
        print(f"Error handling CAPTCHA: {e}")

# 결제 함수
def payment():
    WebDriverWait(driver, 1.1).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="NextStepImage"]')))
    driver.find_element(By.XPATH, '//*[@id="NextStepImage"]').click()


