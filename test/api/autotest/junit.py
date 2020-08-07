from xml.dom.minidom import Document
from pathlib import Path
import time
from datetime import datetime

class Junit:
    def __init__(self, pstarttime):
        # 创建DOM文档对象
        self.doc = Document()
        self.pstarttime = pstarttime
        # 创建用例套件集
        self.testsuites = self.doc.createElement('testsuites')
        self.doc.appendChild(self.testsuites)
        # 当前时间
        self.nowtime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        # 创建用例套件
        self.testsuite = self.doc.createElement('testsuite')

    # 测试用例套件
    def set_suite(self, num, name):

        # 用例数量
        self.testsuite.setAttribute('tests', str(num))
        # 项目名称
        self.testsuite.setAttribute('name', name)
        # 时间
        self.testsuite.setAttribute('timestamp', str(datetime.isoformat(self.pstarttime)))

    # 每条用例是一个case
    def case(self, title, time):
        # 创建case标签
        self.testcase = self.doc.createElement('testcase')
        # 用例的名称
        self.testcase.setAttribute('name', str(title))
        self.case_timer = time
    # 跳过用例的case
    def skip_case(self, message):
        skip = self.doc.createElement('skipped')
        skip.setAttribute('message', message)
        self.testcase.appendChild(skip)
    #接口数据错误
    def error_data(self,message):
        errordata = self.doc.createElement('skipped')
        errordata.setAttribute('message', message)
        errordata.setAttribute('type', 'errordata')
        self.testcase.appendChild(errordata)
    # 设置时间
    def settime(self):
        endtime = datetime.now()
        # 单个用例的执行时间
        td = endtime - self.case_timer
        time = float(
            (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6)) / 10 ** 6
        self.testcase.setAttribute('time', str(time))
        self.testcase.setAttribute('priority', 'M')
        self.testsuite.appendChild(self.testcase)

    # 失败的用例
    def failure(self, message):
        # 创建失败用例的标签
        failure = self.doc.createElement('failure')
        # 为什么失败了这个用例
        failure.setAttribute('message', str(message))
        # 类型为失败
        failure.setAttribute('type', 'Failure')
        # 添加到testcase下
        self.testcase.appendChild(failure)

    # 生成xml  是allure的数据源
    def write_toxml(self):
        # 计算执行的时间， 用当前时间-开始时间 是总耗时
        td = datetime.now() - self.pstarttime
        td_time = float(
            (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10 ** 6)) / 10 ** 6
        self.testsuite.setAttribute('time', '%s' % td_time)
        self.testsuites.appendChild(self.testsuite)

        files = ('junit',)
    # 创建文件夹
        for k in files:
            path = Path(k)

            if path.is_file():
                index = '(0)'
                for i in range(1,10):
                    index = '('+str(i)+')'
                    path = Path(k+index)
                    if not path.is_file():
                        break

            if not path.is_dir():
                path.mkdir()

        file = path / ('API' + '-' + 'ReportJunit@' + self.nowtime + '.xml')   #xml文件名
        f = open(file, 'w')
        self.doc.writexml(f, indent='\t', newl='\n', addindent='\t', encoding='gbk')
        f.close()
