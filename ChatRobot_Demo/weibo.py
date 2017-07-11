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

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
}
logger = logging.getLogger('MyItChatDemo')


class Weibo():

    def __init__(self, username, password):
        self.s = requests.session()
        self.s.headers.update(HEADERS)
        self.username = username
        self.password = password
        self.pre_login_response = None
        self.ticket = None
        self.redirect_url = None

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
            '_': int(time.time()*1000)
        }
        response = self.s.get(url, params=params)
        regex = r'sinaSSOController.preloginCallBack\((\S+)\)'
        response_text = re.search(regex,response.text).group(1)
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
        logger.debug('attempt to post login url : %s params : %s' % (url,params))
        response_json = self.s.post(url, data=params).json()
        if response_json['retcode'] == '0':
            self.ticket = response_json['ticket']
            logger.debug('%s post login success ticket : %s' % (response_json['nick'], self.ticket))
        else:
            logger.error('post login failed retcode : %s reason: %s' % (response_json['retcode'], response_json['reason']))
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
            'ssosavestate': int(now) + 7 * 365 * 86400,
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack&sudaref=weibo.com',
            'ticket': self.ticket,
            'recode': '0'
        }
        logger.debug('attempt to get login url : %s params : %s' % (url,params))
        response = self.s.get(url,params=params)
        regex = r"sinaSSOController.feedBackUrlCallBack\((\S+)\);"
        response_text = re.search(regex, response.text).group(1)
        response_json = json.loads(response_text)
        self.redirect_url = 'https://weibo.com/%s' % response_json['userinfo']['userdomain']
        logger.debug('get login response url : %s' % self.redirect_url)

    def redirect_login(self):
        url = self.redirect_url
        logger.debug('attempt to redirect login url : %s' % url)
        response = self.s.get(self.redirect_url)
        logger.debug('redirect login success')


def main():
    log.set_logging(loggingLevel=logging.DEBUG)
    weibo = Weibo(WEIBO_USERNAME,WEIBO_PASSWORD)
    weibo.login()

if __name__ == '__main__':
    main()