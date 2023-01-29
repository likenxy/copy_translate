#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import sys
import os
import uuid
import requests
import hashlib
import time
import json

sys.path.append(os.path.abspath("SO_site-packages"))
import pyperclip

URL = 'https://openapi.youdao.com/api'
APP_KEY = '你的APPID'
APP_SECRET = '你的APP秘钥'

recent_value = ""

def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    q_utf8 = q #q.decode("utf-8")
    size = len(q_utf8)
    return q_utf8 if size <= 20 else q_utf8[0:10] + str(size) + q_utf8[size - 10:size]


def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(URL, data=data, headers=headers)


def show_basic(b):
    if 'phonetic' in b and 'uk-phonetic' in b:
        print('音:   (美)[{}] | (英)[{}]'.format(str(b['phonetic']), str(b['uk-phonetic'])))
    elif 'phonetic' in b:
        print('音:  [{}]'.format(str(b['phonetic'])))
    elif 'uk-phonetic' in b:
        print('音:  [{}]'.format(str(b['uk-phonetic'])))
    if 'explains' in b:
        explains = b['explains']
        for e in explains:
            print(str(e))

def show_res(r):
    print("")
    if 'errorCode' in r:
        if r['errorCode'] != '0' :
            print('\033[0;97;40m[翻译失败]\033[0m')
            return
    if 'query' in r:
        print('\033[1;97;40mquery:   {}\033[0m'.format(r['query']))
    if 'translation' in r:
        tmp = '['
        translations = r['translation']
        for i in range(len(translations)-1):
            tmp += str(translations[i]) + "| "
        tmp += translations[len(translations) - 1] + ']'
        print('\033[1;97;40mtranslation: {}\033[0m'.format(tmp))
    if 'basic' in r:
        show_basic(r['basic'])

    print("")
def connect(q):
    data = {}
    data['from'] = 'auto'
    data['to'] = 'auto'
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign

    response = do_request(data)
    contentType = response.headers['Content-Type']
    if contentType == "audio/mp3":
        millis = int(round(time.time() * 1000))
        filePath = "合成的音频存储路径" + str(millis) + ".mp3"
        fo = open(filePath, 'wb')
        fo.write(response.content)
        fo.close()
    else:
        #print response.content
        resJson = json.loads(response.content, encoding='UTF-8')
        #print(resJson)
        show_res(resJson)



while True:
	tmp_value = pyperclip.paste()
	if tmp_value != recent_value and not tmp_value is None:
		recent_value = tmp_value
		lines = [line.strip() for line in tmp_value.split()]
		q = " ".join(lines)
		connect(q)
	time.sleep(0.1)

