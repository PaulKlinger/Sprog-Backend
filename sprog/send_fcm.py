import requests
import json
from typing import List

import sprog_auth
from .utility import datetime_to_timestamp
from .poems import Poem


def send_fcm(poems: List[Poem]):
    last_poems = [datetime_to_timestamp(p.datetime) for p in poems[:15]]
    jsondata = json.dumps(
        {"to": "/topics/PoemUpdates",
         "data": {"last_poems": last_poems}
         })
    response = requests.post(url="https://fcm.googleapis.com/fcm/send",
                             data=jsondata,
                             headers={
                                 "Content-type": "application/json",
                                 "Authorization": "key=" + sprog_auth.passwords["FCM_KEY"],
                              })
    response.raise_for_status()
