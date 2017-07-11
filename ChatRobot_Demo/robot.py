import requests
import logging
from config import tuling_apiUrl, tuling_key

logger = logging.getLogger('MyItChatDemo.robot')


def get_reply_msg(info, userid):
    raise NotImplementedError()


def get_reply_from_tuling(info, userid):
    apiUrl = tuling_apiUrl
    data = {
        'key': tuling_key,
        'info': info,
        'userid': userid,
    }
    return requests.post(apiUrl, data=data).json()['text']

get_reply_msg = get_reply_from_tuling