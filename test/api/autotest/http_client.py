import requests
import time
import json

#封装请求
def request(testcase):
    if testcase.type == 'get':      #get请求
        r = requests.get(url = testcase.url,headers = testcase.headers)
    else:                            #post请求
        r = requests.post(url = testcase.url, data = testcase.payload,headers = testcase.headers)

    testcase.codenum = r.status_code
    testcase.text = r.text

    return testcase.codenum,testcase.text