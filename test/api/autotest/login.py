import requests
import config

base_url = config.base_url

def login():            #login函数用来提取登录后的token，用于后续测试
    url = base_url + 'siteapi/oneid/ucenter/login/'
    
    headers = {
        "content-type": "application/json;charset=UTF-8"
    }

    payload = {
        "password": config.password,
        "username": config.username
    }

    r = requests.post(url = url, json = payload, headers = headers)

    assert r.status_code == 200 ,'登录失败'

    token = r.json()['token']
    return token