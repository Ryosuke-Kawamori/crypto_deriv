import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import time
import os
import hmac
import hashlib
import json


class Bybit():

    # 定数
    TIMEOUT = 3600               # タイムアウト
    EXTEND_TOKEN_TIME = 3000     # アクセストークン延長までの時間
    SYMBOL = 'BTCUSD'            # シンボル[BTCUSD]

    URLS = {'REST': 'https://api.bybit.com',
            #'WebSocket': 'wss://stream.api.com/realtime',
            }

    def __init__(self, api_key: str, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def create_request(self, method, access_modifiers, target_path, params):

        if access_modifiers == 'public':
            url = ''.join([self.URLS['REST'], target_path])
            if method == 'GET':
                return {'method': method,
                        'access_modifiers': access_modifiers,
                        'target_path': target_path, 'url': url,
                        'params': params,
                        'headers':{}}

            if method == 'POST':
                headers = {'Content-Type': 'application/json'}
                return {'method': method,
                        'access_modifiers': access_modifiers,
                        'target_path': target_path,
                        'url': url,
                        'params': params,
                        'headers':headers}

        if access_modifiers == 'private':
            url = ''.join([self.URLS['REST'], target_path])
            timestamp = int((time.time()) * 1000)

            if method == 'GET':
                params['api_key'] = self.api_key
                params['timestamp'] = timestamp
                sign = ''
                for key in sorted(params.keys()):
                    v = params[key]
                    if isinstance(params[key], bool):
                        if params[key]:
                            v = 'true'
                        else :
                            v = 'false'
                    sign += key + '=' + str(v) + '&'
                sign = sign[:-1]
                params['sign'] = self.sign(sign)
                return {'url': url,
                        'method': method,
                        'headers': '',
                        'params': params,
                        }


            if method == 'POST':
                params['api_key'] = self.api_key
                params['timestamp'] = timestamp
                sign = ''
                for key in sorted(params.keys()):
                    v = params[key]
                    if isinstance(params[key], bool):
                        if params[key]:
                            v = 'true'
                        else :
                            v = 'false'
                    sign += key + '=' + str(v) + '&'
                sign = sign[:-1]
                signature = self.sign(sign)
                signature_real = {'sign': signature}
                body = json.dumps(dict(params,**signature_real))
                return {'url': url,
                        'method': method,
                        'headers': {'Content-Type': 'application/json'},
                        'params': body,
                        }

    def sign(self, sign):
        return hmac.new(self.api_secret.encode('utf-8'), sign.encode('utf-8'), hashlib.sha256).hexdigest()

    def fetch(self, request):
        if request['method'] == 'GET':
            response = requests.get(url=request['url'], params=request['params'])

        elif request['method'] == 'POST':
            response = requests.post(url=request['url'], data=request['params'], headers=request['headers'])

        return response

    def send_request(self, method: str, access_modifiers: str, target_path: str, params: dict):
        return self.fetch(self.create_request(method = method, access_modifiers=access_modifiers,
                                              target_path = target_path, params=params))


