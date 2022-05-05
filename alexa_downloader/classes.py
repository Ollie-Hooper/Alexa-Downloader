import json
import os
import time

import pandas as pd

from alexa_downloader.authentication import create_headers
from alexa_downloader.history import create_records_df
from alexa_downloader.request_handler import handle_request


class AlexaDownloader:
    def __init__(self):
        self.history_url = "https://www.amazon.co.uk/alexa-privacy/apd/rvh/customer-history-records"
        self.audio_url = "https://www.amazon.co.uk/alexa-privacy/apd/rvh/audio"
        self.login_url = "https://www.amazon.co.uk/alexa-privacy/apd/rvh"

        self.headers = {}
        self.history = pd.DataFrame(
            columns=["timestamp", "transcript", "utterance_id", "device", "person", "utterance_type", "intent"])

    def login(self):
        if not os.path.exists('./headers.json'):
            self.headers = create_headers(self.login_url)
        else:
            with open("./headers.json", "r") as f:
                self.headers = json.load(f)

    def get_history(self):
        history = pd.DataFrame(
            columns=["timestamp", "transcript", "utterance_id", "device", "person", "utterance_type", "intent"])
        params = {
            'startTime': 0,
            'endTime': int(time.time()),
        }
        done = False
        while not done:
            r = handle_request(self.history_url, params, self.headers)
            d = r.json()
            if not d['encodedRequestToken']:
                done = True
            else:
                params['previousRequestToken'] = d['encodedRequestToken']
            records_df = create_records_df(d)
            history = pd.concat([history, records_df])
        self.history = history.set_index("timestamp")
        return history.set_index("timestamp")
