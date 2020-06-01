import requests
import time
import json



# 简单封装get请求
def get(data = None):
    if data is None:
        data = {}
    
    # 发送请求
    r = requests.get(url = data['url'],headers = data['headers'])
    # 简单的判断接口的code码 等于200进行断言
    if r.status_code == 200:
        
        content = data["assert"]        #取到断言内容，是一个列表

        for i in range(0,len(content)):
            # 列表中的每个值和接口的返回值去对比
            if content[i] in str(r.text):
                pass
                data['isok'] = 'ok'
            else:
                data['isok'] = '断言失败'
                print(content[i] + '这个断言没有通过')
    else:
        data['isok'] = r.status_code            #code 码不是200，改变字典 isok 的值，用于记录失败原因
    # 返回字典用于记录测试报告
    return data

def post(data = None):
    
    if data is None:
        data = {}
    # 发送post请求
    r = requests.post(url = data['url'], data = json.dumps(data['payload']),headers = data['headers'])
    # 简单的判断接口的code码 等于200就让它通过
    if r.status_code == 200:
        
        content = data["assert"]

        for i in range(0,len(content)):
            # 每个字段和去接口的返回值去对比
            if content[i] in str(r.text):
                pass
                data['isok'] = 'ok'
            else:
                data['isok'] = '断言失败'
                print(content[i] + '这个断言没有通过')
    else:
        data['isok'] = r.status_code
    # 返回字典用于记录测试报告
    return data
