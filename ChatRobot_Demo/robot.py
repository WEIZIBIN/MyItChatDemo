import requests
import logging
import weibo
from config import tuling_apiUrl, tuling_key, WEIBO_USERNAME, WEIBO_PASSWORD, ROBOT_TULING, ROBOT_XIAOICE

logger = logging.getLogger('MyItChatDemo.robot')
weibo_instance = None


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


def get_reply_from_xiaoice(info, userid):
    return weibo_instance.get_msg_from_xiaoice(info)


# set reply robot tuling
if ROBOT_TULING:
    get_reply_msg = get_reply_from_tuling

# set reply robot xiaoice
if ROBOT_XIAOICE:
    weibo_instance = weibo.Weibo(WEIBO_USERNAME, WEIBO_PASSWORD)
    weibo_instance.login()
    weibo_instance.im_init()
    get_reply_msg = get_reply_from_xiaoice
