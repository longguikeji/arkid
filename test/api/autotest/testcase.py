import login
from config import base_url

token = login.login()            

httpurl_data = [                   #存放所有测试用例的列表，每一条字典类型数据是一个测试用例
    # 1.登录接口 第一条用例
    {'title': '登录接口',  # 用例的名称
     'condition': '',  # 前置条件 写skip 跳过这个用例，不写则正常执行
     'url': '{}siteapi/oneid/ucenter/login/'.format(base_url),
     'headers':{
         'Content-Type': 'application/json;charset=UTF-8'    
     },
     'payload': {
         'password': 'admin',
         'username': 'admin'
     },
     'type': 'post',  # 请求的类型 get 或者post，这条是 post 类型
     'isok': '',  # 用例是否通过，通过是ok 不通过则为失败原因
     'time': '1' , # 用例等待的时间 秒 1就是等待1秒后执行
     'assert':['admin']     #断言，列表类型，可添加多个判断条件，与接口返回值对比
     },
    {'title': '应用信息接口',  # 用例的名称
     'condition': '',  # 前置条件 写skip 跳过这个用例
     'url': '{}siteapi/oneid/ucenter/apps/'.format(base_url),
     'headers':{
         'Content-Type': 'application/json',
         'Authorization': 'token ' + token
     },
     'type': 'get',  # 请求的类型 get 或者post，这条是 get 类型
     'isok': '',  # 用例是否通过，通过是ok 不通过记录失败原因
     'time': '1' , # 用例等待的时间 秒 1就是等待1秒后执行
     'assert':['百度', '12306']   #断言内容，与接口返回值对比
     },
     {'title': '节点信息接口',  # 用例的名称
     'condition': '',  # 前置条件 写skip 跳过这个用例
     'url': '{}siteapi/oneid/meta/node/'.format(base_url),
     'headers':{
         'Authorization': 'token ' + token
     },
     'type': 'get',  # 请求的类型 get 或者post，这条是 get 类型
     'isok': '',  # 用例是否通过，通过是ok 不通过是 failure
     'time': '1' , # 用例等待的时间 秒 1就是等待1秒后执行
     'assert':['部门']   #断言内容，与接口返回值对比
     }
]
