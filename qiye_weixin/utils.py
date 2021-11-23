#!/usr/bin/env python3
import os
import json
import time
from .client import WeixinClient
from config import get_app_config
from common.logger import logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')
TRAINING_PIC = os.path.join(BASE_DIR, 'training.png')


def get_weixin_client():
    app_config = get_app_config()
    data = app_config.data.get('qiye_weixin')

    corpid = data.get('corpid')
    corpsecret = data.get('corpsecret')
    agentid = data.get('agentid')

    client = WeixinClient(corpid, corpsecret, agentid)
    load_access_token(client)
    return client


def init_data_file():
    if not os.path.exists(DATA_FILE):
        init_data = {
            'access_token': '',
            'textcard_url': '',
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(init_data, f)
        return init_data


def load_access_token(client):
    init_data_file()
    access_token = ''
    with open(DATA_FILE, 'r+') as f:
        data = json.load(f)

    cur_time = time.time()
    time_and_token = data.get('access_token')
    if not time_and_token:
        access_token = client.get_access_token()
        data['access_token'] = "\t".join([str(cur_time), access_token])
        client.ACCESS_TOKEN = access_token
    else:
        t, access_token = time_and_token.split()
        # 判断access_token是否有效
        if 0 < cur_time - float(t) < 7200:
            client.ACCESS_TOKEN = access_token
            return access_token
        else:
            access_token = client.get_access_token()
            data['access_token'] = "\t".join([str(cur_time), access_token])
            client.ACCESS_TOKEN = access_token

    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
    return access_token


def load_textcard_url(client):
    init_data_file()
    textcard_url = ''
    with open(DATA_FILE, "r+") as f:
        data = json.load(f)

    textcard_url = data.get('textcard_url')
    if not textcard_url:
        if not os.path.exists(TRAINING_PIC):
            return ''
        textcard_url = client.upload_picture(TRAINING_PIC)
        data['textcard_url'] = textcard_url

    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)
    return textcard_url


def send_textcard():
    client = get_weixin_client()
    textcard_url = load_textcard_url(client)
    logger.info(textcard_url)
    client.send_textcard('test', 'test', 'test1234', textcard_url, '更多内容')


if __name__ == '__main__':
    client = get_weixin_client()
    textcard_url = load_textcard_url(client)
    print(textcard_url)
    client.send_textcard('FanHe', 'test', 'test1234', textcard_url, '更多内容')
