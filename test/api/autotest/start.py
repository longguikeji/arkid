# 引入testcase里面的用例
from apidata import httpurl_data
# 引入请求
#import http_client
# time在这里的作用主要是等待的操作
import time
from datetime import datetime
# 引入junt
from junit import Junit
from testcase import TestCase
import requests
from inputs_error import InputsError

def createxml():

    # 获得junit实例
    junit = Junit(datetime.now())

    # 开始执行用例
    for data in httpurl_data:
        #testcase = TestCase(data)
        try:
            testcase = TestCase(data)
        except InputsError as ex:
            print(ex)
            junit.case(data.get('tittle','没有标题'), datetime.now())
            junit.error_data(str(ex))
            junit.settime()
            continue

        # 判断需要跳过的用例
        if testcase.skip:
            # 写入跳过用例标题名
            junit.case(testcase.tittle, datetime.now())
            # 跳过用例的信息
            junit.skip_case('This testcase is skipped')
            junit.settime()
            # continue 跳出本次循环不会结束循环
            continue

        # 这条用例开始执行的时间
        case_time = datetime.now()

        # 获取等待时间
        sltime = testcase.time
        # 判断时间有值在进行等待
        if sltime:
            # 使用sleep进行等待
            time.sleep(sltime)

        # 使用getattr函数进行反射调用接口 参数1：请求的对象，参数2：请求类型 get post 后面的小括号是进行传参
        #getattr(http_client, 'http_client')(testcase)
        r = requests.request(testcase.type, url = testcase.url, json = testcase.payload, headers = testcase.headers)

        # 用例通过
        reason = ''       #失败用例失败原因
        result = True       #测试结果
        if r.status_code == 200:

            for asserts in testcase.asserts:
                # 每个字段和去接口的返回值去对比
                if asserts not in str(r.text):
                    result = False
                    reason = asserts + '断言失败'
        else:
            result = False
            reason = '状态码为 ' + str(r.status_code)

        # 用例通过
        if result:
            # 写入xml测试报告
            junit.case(testcase.tittle, case_time)
            junit.settime()
        # 用例不通过
        else:
            junit.case(testcase.tittle, case_time)
            junit.failure('标题：' + testcase.tittle + '  请求类型：' + testcase.type +'   失败原因：' + reason)
            junit.settime()

    # 生成xml数据源 提供给allure
    # 生成测试套件 参数为用例的总数int类型，测试项目名称string类型
    junit.set_suite(len(httpurl_data),'一账通接口测试')
    junit.settime()
    # 生成xml
    junit.write_toxml()

if __name__ == '__main__':
    createxml()