import json
import os
import time

import pandas as pd
import requests

from datetime import datetime
from warnings import warn

from pyotp import TOTP
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def main():
    history_url = "https://www.amazon.co.uk/alexa-privacy/apd/rvh/customer-history-records"
    audio_url = "https://www.amazon.co.uk/alexa-privacy/apd/rvh/audio"

    if not os.path.exists('headers.json'):
        create_headers()

    history = get_history(history_url)

    print()


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
    with open('auth.json', 'r') as f:
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


def get_history(url):
    history = pd.DataFrame(
        columns=["timestamp", "transcript", "utterance_id", "device", "person", "utterance_type", "intent"])
    params = get_params()
    headers = get_headers()
    done = False
    while not done:
        r = handle_request(url, params, headers)
        d = r.json()
        if not d['encodedRequestToken']:
            done = True
        else:
            params['previousRequestToken'] = d['encodedRequestToken']
        records_df = create_records_df(d)
        history = pd.concat([history, records_df])
    return history.set_index("timestamp")


def create_records_df(d):
    records = [r['voiceHistoryRecordItems'][0] for r in d['customerHistoryRecords'] if
               r['voiceHistoryRecordItems'][0]['recordItemType'] == 'CUSTOMER_TRANSCRIPT']
    return pd.DataFrame({
        "timestamp": [r['timestamp'] for r in records],
        "transcript": [r['transcriptText'] for r in records],
        "utterance_id": [r['utteranceId'] for r in records],
        "device": [r['device']['deviceName'] for r in d['customerHistoryRecords'] if
                   r['voiceHistoryRecordItems'][0]['recordItemType'] == 'CUSTOMER_TRANSCRIPT'],
        "person": [r['personsInfo'][0]['personFirstName'] if r['personsInfo'] else '' for r in records],
        "utterance_type": [r['utteranceType'] for r in d['customerHistoryRecords'] if
                           r['voiceHistoryRecordItems'][0]['recordItemType'] == 'CUSTOMER_TRANSCRIPT'],
        "intent": [r['intent'] for r in d['customerHistoryRecords'] if
                   r['voiceHistoryRecordItems'][0]['recordItemType'] == 'CUSTOMER_TRANSCRIPT'],
    })


def download_audio(utterances, url, fp='/audio'):
    pass


def get_params(start_date="01/01/2022"):
    return {
        'startTime': 0,  # int(time.mktime(datetime.strptime(start_date, "%d/%m/%Y").timetuple())),
        'endTime': int(time.time()),
    }


def get_headers():
    with open('headers.json', 'r') as f:
        return json.load(f)


def handle_request(url, params, headers, retry_wait_time=0):
    while True:
        try:
            return requests.get(url=url, params=params, headers=headers)
        except requests.exceptions.ConnectionError as e:
            warn("Error just occurred:")
            warn(e)
            warn(f"Retrying in {retry_wait_time} second...")
            time.sleep(retry_wait_time)
            warn("Retrying...")
            continue


if __name__ == '__main__':
    main()
