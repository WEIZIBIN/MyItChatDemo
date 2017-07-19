import requests
import time
import re
import rsa
import binascii
import json
import logging
import log
import base64
import urllib.parse
from config import WEIBO_USERNAME, WEIBO_PASSWORD

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
}
logger = logging.getLogger('MyItChatDemo')
xiaoice_uid = 5175429989
polling_wait_second = 2


class Weibo():
    def __init__(self, username, password):
        self.s = requests.session()
        self.s.headers.update(headers)
        self.username = username
        self.password = password
        self.pre_login_response = None
        self.ticket = None  # ticket to login
        self.redirect_url = None  # redirect login url
        self.jsonp = None  # handshake parameter
        self.client_id = None  # client_id to polling WeiboIM
        self.polling_id = 3  # IM polling_id start from 3

    def login(self):
        self.pre_login()
        self.post_login()
        self.get_login()
        self.redirect_login()
        logger.info('weibo login success')

    def pre_login(self):
        url = 'https://login.sina.com.cn/sso/prelogin.php'
        params = {
            'entry': 'weibo',
            'callback': 'sinaSSOController.preloginCallBack',
            'su': self.get_encrypted_username(),
            'rsakt': 'mod',
            'client': 'ssologin.js(v1.4.19)',
            '_': int(time.time() * 1000)
        }
        logger.debug('attempt to pre login url : %s params : %s' % (url, params))
        response = self.s.get(url, params=params)
        regex = r'sinaSSOController.preloginCallBack\(([\s\S]+)\)'
        response_text = re.search(regex, response.text).group(1)
        response_data = json.loads(response_text)
        logger.debug('pre login response : %s' % response_data)
        self.pre_login_response = response_data

    def post_login(self):
        url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        servertime = int(time.time())
        nonce = self.pre_login_response['nonce']
        pubkey = self.pre_login_response['pubkey']
        rsakv = self.pre_login_response['rsakv']
        params = {
            'entry': 'weibo',
            'gateway': '1',
            'from': "",
            'savestate': '7',
            'qrcode_flag': 'false',
            'userticket': '1',
            'pagerefer': "",
            'vsnf': '1',
            'su': self.get_encrypted_username(),
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'rsakv': rsakv,
            'sp': self.get_encrypted_password(servertime=servertime, nonce=nonce, pubkey=pubkey),
            'sr': '1920*1080',
            'encoding': 'UTF-8',
            'prelt': '42',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'TEXT'
        }
        logger.debug('attempt to post login url : %s params : %s' % (url, params))
        response_json = self.s.post(url, data=params).json()
        if response_json['retcode'] == '0':
            self.ticket = response_json['ticket']
            logger.debug('%s post login success ticket : %s' % (response_json['nick'], self.ticket))
        else:
            logger.error(
                'post login failed retcode : %s reason: %s' % (response_json['retcode'], response_json['reason']))
            raise ConnectionRefusedError

    def get_encrypted_password(self, servertime, nonce, pubkey):
        encypted_string = str(servertime) + '\t' + str(nonce) + '\n' + str(self.password)
        key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
        pw_encypted = rsa.encrypt(encypted_string.encode('utf-8'), key)
        pw = binascii.b2a_hex(pw_encypted)
        return pw.decode('utf-8')

    def get_encrypted_username(self):
        return base64.b64encode(urllib.parse.quote(self.username).encode('utf-8')).decode('utf-8')

    def get_login(self):
        url = 'https://passport.weibo.com/wbsso/login'
        now = time.time()
        params = {
            'ssosavestate': int(now) + 365 * 86400,
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack&sudaref=weibo.com',
            'ticket': self.ticket,
            'recode': '0'
        }
        logger.debug('attempt to get login url : %s params : %s' % (url, params))
        response = self.s.get(url, params=params)
        regex = r"sinaSSOController.feedBackUrlCallBack\(([\s\S]+)\);"
        response_text = re.search(regex, response.text).group(1)
        response_json = json.loads(response_text)
        self.redirect_url = 'https://weibo.com/%s' % response_json['userinfo']['userdomain']
        logger.debug('get login response url : %s' % self.redirect_url)

    def redirect_login(self):
        url = self.redirect_url
        logger.debug('attempt to redirect login url : %s' % url)
        response = self.s.get(self.redirect_url)
        logger.debug('redirect login success')

    def get_msg_from_xiaoice(self, msg):
        self.request_webim()
        self.handshake()
        self.subscript_msg()
        self.switch_to_xiaoice()
        self.post_msg_to_xiaoice(msg)
        return self.polling_msg_from_xiaoice()

    def request_webim(self):
        url = 'http://api.weibo.com/webim/webim_nas.json'
        params = {
            'source': '209678993',
            'returntype': 'json',
            'v': '1.1',
            'source': '209678993',
            'callback': 'angular.callbacks._2'
        }
        logger.debug('attempt to request_webim url : %s params : %s' % (url, params))
        response = self.s.get(url, params=params)
        logger.debug('request_webim success response : %s' % response.text)

    def handshake(self):
        url = 'https://web.im.weibo.com/im/handshake'
        now = int(time.time() * 1000)
        self.jsonp = 'jQuery214024520499455942235_' + str(now)
        params = {
            'jsonp': self.jsonp,
            'message': '[{"version": "1.0", "minimumVersion": "1.0", "channel": "/meta/handshake","supportedConnectionTypes": ["callback-polling"], "advice": {"timeout": 60000, "interval": 0},"id": "2"}]',
            '_': now
        }
        logger.debug('attempt to handshake url : %s params : %s' % (url, params))
        response = self.s.get(url, params=params)
        logger.debug('handshake success response : %s' % response.text)
        regex = r"\(\[([\s\S]+)\]\)"
        response_text = re.search(regex, response.text).group(1)
        response_json = json.loads(response_text)
        self.client_id = response_json['clientId']
        logger.debug('Weibo IM client id : %s' % self.client_id)

    def subscript_msg(self):
        url = 'https://web.im.weibo.com/im/'
        now = int(time.time() * 1000)
        params = {
            'jsonp': self.jsonp,
            'message': ('[{"channel":"/meta/subscribe","subscription":"/im/5908081220","id":"%s","clientId":"%s"}]'
                        % (self.polling_id, self.client_id)),
            '_': now
        }
        self.polling_id += 1
        logger.debug('attempt to subscript url : %s params : %s' % (url, params))
        response = self.s.get(url, params=params)
        logger.debug('subscript success response : %s' % response.text)

    def switch_to_xiaoice(self):
        url = 'https://web.im.weibo.com/im/'
        now = int(time.time() * 1000)
        params = {
            'jsonp': self.jsonp,
            'message': (
            '[{"channel":"/im/req","data":{"cmd":"synchroniz","type":"dmread","uid":%s},"id":"%s","clientId":"%s"}]'
            % (xiaoice_uid, self.polling_id, self.client_id)),
            '_': now
        }
        self.polling_id += 1
        logger.debug('attempt to switch to xiaoice url : %s params : %s' % (url, params))
        response = self.s.get(url, params=params)
        logger.debug('switch to xiaoice success response : %s' % response.text)

    def post_msg_to_xiaoice(self, msg):
        url = 'http://api.weibo.com/webim/2/direct_messages/new.json?source=209678993'
        self.s.headers.update({'Referer': 'http://api.weibo.com/chat/'})
        logger.info('session headers update to : %s' % self.s.headers)
        params = {
            'text': urllib.parse.quote(msg),
            'uid': xiaoice_uid
        }
        self.polling_id += 1
        logger.debug('attempt to post msg url : %s params : %s' % (url, params))
        response = self.s.post(url, data=params)
        logger.debug('post msg success response : %s' % response.text)

    def polling_msg_from_xiaoice(self):
        while True:
            url = 'https://web.im.weibo.com/im/connect'
            now = int(time.time() * 1000)
            params = {
                'jsonp': self.jsonp,
                'message': '[{"channel":"/meta/connect","connectionType":"callback-polling","id":"%s","clientId":"%s"}]'
                           % (self.polling_id, self.client_id),
                '_': now
            }
            self.polling_id += 1
            logger.debug('attempt to polling IM url : %s params : %s' % (url, params))
            response = self.s.get(url, params=params)
            print(response.status_code)
            logger.debug('polling IM success response : %s' % response.text)
            regex = r"\(\[{([\s\S]+)},{([\s\S]+)}\]\)"
            match = re.search(regex, response.text)
            if match is not None:
                match_group = match.groups()
                if match_group is not None and len(match_group) == 2:
                    im_data = json.loads("{%s}" % match_group[0])
                    if 'data' in im_data and 'type' in im_data['data'] and im_data['data']['type'] == 'msg':
                        for item in im_data['data']['items']:
                            if item[0] == xiaoice_uid:
                                print(item[1])
            time.sleep(polling_wait_second)


def main():
    log.set_logging(loggingLevel=logging.DEBUG)
    weibo = Weibo(WEIBO_USERNAME, WEIBO_PASSWORD)
    weibo.login()
    weibo.get_msg_from_xiaoice('你好')


if __name__ == '__main__':
    main()
