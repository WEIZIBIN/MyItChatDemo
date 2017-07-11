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

logger = logging.getLogger('MyItChatDemo')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
}


class Weibo():

    def __init__(self, username, password):
        self.s = requests.session()
        self.s.headers.update(HEADERS)
        self.username = username
        self.password = password
        self.pre_login_response = None

    def login(self):
        self.pre_login()
        self.post_login()

    def pre_login(self):
        url = 'https://login.sina.com.cn/sso/prelogin.php'
        params = {
            'entry': 'weibo',
            'callback': 'sinaSSOController.preloginCallBack',
            'su': self.get_encrypted_username(),
            'rsakt': 'mod',
            'client': 'ssologin.js(v1.4.19)',
            '_': int(time.time()*1000)
        }
        response = self.s.get(url, params=params)
        regx = r'sinaSSOController.preloginCallBack\((\S+)\)'
        response_text = re.search(regx,response.text).group(1)
        response_data = json.loads(response_text)
        logger.debug('pre login response : %s' % response_data)
        self.pre_login_response = response_data

    def post_login(self):
        url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        servertime = self.pre_login_response['servertime']
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
            # 'returntype': 'TEXT'
            'returntype': 'META'
        }
        response = self.s.post(url, data=params)
        response.encoding = 'gbk'
        print(response.text)
        print(response.status_code)
        # self.post_login_response = self.s.post(url, data=params).json()
        # logger.debug('post login response : %s' % self.post_login_response)

    def get_encrypted_password(self, servertime, nonce, pubkey):
        pw_string = str(servertime) + '\t' + str(nonce) + '\n' + str(self.password)
        key = rsa.PublicKey(int(pubkey, 16), int('10001', 16))
        pw_encypted = rsa.encrypt(pw_string.encode('utf-8'), key)
        pw = binascii.b2a_hex(pw_encypted)
        return pw.decode('utf-8')

    def get_encrypted_username(self):
        return base64.b64encode(urllib.parse.quote(self.username).encode('utf-8')).decode('utf-8')


def main():
    log.set_logging(loggingLevel=logging.DEBUG)
    weibo = Weibo(WEIBO_USERNAME,WEIBO_PASSWORD)
    weibo.login()

if __name__ == '__main__':
    main()