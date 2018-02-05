import requests
import json
from typing import List
from datetime import datetime

import sprog_auth
from .utility import datetime_to_timestamp
from .poems import Poem


def send_fcm(topic, data, collapse_key):
    jsondata = json.dumps(
        {"to": topic,
         "data": data,
         "collapse_key": collapse_key,
         })
    response = requests.post(url="https://fcm.googleapis.com/fcm/send",
                             data=jsondata,
                             headers={
                                 "Content-type": "application/json",
                                 "Authorization": "key=" + sprog_auth.passwords["FCM_KEY"],
                             })
    response.raise_for_status()


def send_last_poems_fcm(poems: List[Poem]):
    last_poems = [datetime_to_timestamp(p.datetime) for p in poems[:15]]
    send_fcm(topic="/topics/PoemUpdates",
             data={"last_poems": last_poems},
             collapse_key="poem_update")


def _force_update(debug: bool = True):
    """
    Send a FCM message showing >10 available poems, i.e. force a poem update for all users.

    CAREFUL!!
    """
    now_timestamp = datetime_to_timestamp(datetime.now())
    topic = "/topics/testPoemUpdates" if debug else "/topics/PoemUpdates"
    send_fcm(topic=topic,
             data={"last_poems": [now_timestamp] * 12},
             collapse_key="poem_update")
