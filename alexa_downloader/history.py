import time

import pandas as pd

from alexa_downloader.request_handler import handle_request


def get_history(url):
    history = pd.DataFrame(
        columns=["timestamp", "transcript", "utterance_id", "device", "person", "utterance_type", "intent"])
    params = get_params()
    done = False
    while not done:
        r = handle_request(url, params)
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


def get_params(start_date="01/01/2022"):
    return {
        'startTime': 0,  # int(time.mktime(datetime.strptime(start_date, "%d/%m/%Y").timetuple())),
        'endTime': int(time.time()),
    }
