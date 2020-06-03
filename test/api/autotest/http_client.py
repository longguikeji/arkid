import requests
import time
import json

# 简单封装get请求
def get(testcase):
    
    # 发送请求
    r = requests.get(url = testcase.url,headers = testcase.headers)
    # 简单的判断接口的code码 等于200进行断言
    if r.status_code == 200:
        
        content = testcase.asserts        #取到断言内容，是一个列表

        for i in range(0,len(content)):
            # 列表中的每个值和接口的返回值去对比
            if content[i] in str(r.text):
                pass
                testcase.isok = 'ok'
            else:
                testcase.isok = '断言失败'
                print(content[i] + '这个断言没有通过')
    else:
        testcase.isok = r.status_code            #code 码不是200，改变testcase isok 属性的值，用于记录失败原因
    
    return testcase.isok

def post(testcase):
    
    # 发送post请求
    r = requests.post(url = testcase.url, data = testcase.payload,headers = testcase.headers)
    # 简单的判断接口的code码 等于200就让它通过
    if r.status_code == 200:
        
        content = testcase.asserts

        for i in range(0,len(content)):
            # 每个字段和去接口的返回值去对比
            if content[i] in str(r.text):
                pass
                testcase.isok = 'ok'
            else:
                testcase.isok = '断言失败'
                print(content[i] + '这个断言没有通过')
    else:
        testcase.isok = r.status_code
    #code 码不是200，改变testcase isok 属性的值，用于记录失败原因
    return testcase.isok
