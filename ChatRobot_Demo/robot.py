import requests
import logging
import weibo
from config import tuling_apiUrl, tuling_key, weibo_username, weibo_password, robot_tuling, robot_xiaoice

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
if robot_tuling:
    get_reply_msg = get_reply_from_tuling

# set reply robot xiaoice
if robot_xiaoice:
    weibo_instance = weibo.Weibo(weibo_username, weibo_password)
    weibo_instance.login()
    weibo_instance.im_init()
    get_reply_msg = get_reply_from_xiaoice
