import json
# 引入config里面的用例
from config import httpurl_data
# 引入请求
import poshttp
# time在这里的作用主要是等待的操作
import time
from datetime import datetime
# 引入junt
from junit import Junit
from pathlib import Path

files = ('junit',)
# 创建文件夹
for k in files:
    path = Path(k)
    # 如果文件不存在 则创建
    if not path.is_dir():
        path.mkdir()

# 获取程序执行的时间
start_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())

# 获得junit实例
junit = Junit(datetime.now())

# 开始执行测试，并记录结果数据
result = []

# 开始执行用例
for data in httpurl_data:
    # 判断需要跳过的用例
    if data['condition'] == 'skip':
        # 写入跳过用例标题名
        junit.case(data['title'], datetime.now())
        # 跳过用例的信息
        junit.skip_case('This use case is skipped')
        junit.settime()
        # 跳过的用例也添加到结果里面
        result.append(data)
        # continue 跳出本次循环不会结束循环
        continue

    # 这条用例开始执行的时间
    case_time = datetime.now()

    # 首先判断此用例是否需要执行

    # 获取等待时间 没有的话就是0
    sltime = data.get('time', 0)
    # 判断时间有值在进行等待
    if sltime:
        # 使用sleep进行等待
        time.sleep(float(sltime))

    # 使用getattr函数进行反射调用接口 参数1：请求的对象，参数2：请求类型 get post 后面的小括号是进行传参
    case = getattr(poshttp, data['type'])(data)
    # 看结果里 接口是否为通过
    is_pass = case.get('isok', '')
    # 用例通过
    if is_pass == 'ok':
        # 写入xml测试报告
        junit.case(case['title'], case_time)
        junit.settime()
    # 用例不通过
    else:
        junit.case(case['title'], case_time)
        junit.failure('标题：' + case['title'] + '  请求类型：' + case['type'] +'   失败原因：' + str(is_pass))
        junit.settime()

    # 测试结果数据添加到list中
    result.append(case)
# 生成xml数据源 提供给allure
# 生成测试套件 参数为用例的总数
junit.suite(len(httpurl_data))
junit.settime()
# 生成xml
junit.write_toxml()
