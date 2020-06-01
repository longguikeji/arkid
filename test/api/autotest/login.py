import requests,json
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

    data = json.dumps(payload)

    r = requests.post(url = url, data = data, headers = headers)

    token = r.json()['token']                     

    return token