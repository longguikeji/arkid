import requests
import time
import json

#封装请求
def request(testcase):
    if testcase.type == 'get':      #get请求
        r = requests.get(url = testcase.url,headers = testcase.headers)
    elif testcase.type == 'post':                            #post请求
        r = requests.post(url = testcase.url, json = testcase.payload, headers = testcase.headers)
    return r