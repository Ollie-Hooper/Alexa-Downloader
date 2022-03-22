from datetime import datetime
import json
import warnings

import pandas as pd
import requests
import time


# import urllib3.exceptions


def main():
    history_url = "https://www.amazon.co.uk/alexa-privacy/apd/rvh/customer-history-records"
    audio_url = "https://www.amazon.co.uk/alexa-privacy/apd/rvh/audio"

    history = get_history(history_url)


def get_history(url):
    history = pd.DataFrame(columns=["timestamp", "transcript", "utterance_id", "device", "person", "utterance_type", "intent"])
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
            warnings.warn("Error just occurred:")
            warnings.warn(e)
            warnings.warn(f"Retrying in {retry_wait_time} second...")
            time.sleep(retry_wait_time)
            warnings.warn("Retrying...")
            continue


if __name__ == '__main__':
    main()
