import json
import time

import requests

from warnings import warn


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


def get_headers():
    with open('headers.json', 'r') as f:
        return json.load(f)
