import time

import pandas as pd


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
