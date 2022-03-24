import json
import os

from warnings import warn

from pyotp import TOTP
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def login():
    if not os.path.exists('./headers.json'):
        create_headers()


def create_headers():
    login_url = "https://www.amazon.co.uk/alexa-privacy/apd/rvh"
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s)
    driver.get(login_url)
    if os.path.exists('auth.json'):
        auto_login(driver)
    try:
        r = driver.wait_for_request('/alexa-privacy/apd/rvh/customer-history-records', timeout=300)
        with open("./headers.json", "w") as f:
            json.dump(dict(r.headers), f)
    except TimeoutError:
        warn("Timed out trying to login and get request... quitting")
        quit()
    finally:
        driver.quit()


def auto_login(driver):
    with open('./auth.json', 'r') as f:
        auth = json.load(f)
    e_username = driver.find_element(By.ID, "ap_email")
    e_password = driver.find_element(By.ID, "ap_password")
    e_submit = driver.find_element(By.ID, "signInSubmit")
    e_username.send_keys(auth['email'])
    e_password.send_keys(auth['password'])
    e_submit.click()
    if e_totp := driver.find_element(By.ID, "auth-mfa-otpcode"):
        totp = TOTP(auth['secret'])
        e_totp.send_keys(totp.now())
        e_signin = driver.find_element(By.ID, "auth-signin-button")
        e_signin.click()
