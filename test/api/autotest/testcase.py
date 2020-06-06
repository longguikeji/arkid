import json
from inputs_error import InputsError

class TestCase:
    def __init__(self,data):
        self.tittle = data.get('tittle','没有标题')
        self.notSkip = data.get('notSkip')
        self.url = data.get('url')
        self.headers = data.get('headers')
        self.payload = data.get('payload')
        self.type = data.get('type')
        self.time = data.get('time',0)
        self.asserts = data.get('assert')

        request_type = ['get','post','options','head','delete','put','connect']

        if self.url != None:
            if self.type != None:
                if self.type.lower() not in request_type:
                    raise InputsError("请求类型输入不正确,输入为：" + self.type)
                else:
                    pass
            else:
                raise InputsError("接口数据不对，缺少请求类型")
        else:
            raise InputsError("接口数据不对，缺少url")

        if self.time >=0 and isinstance(self.time,int):
            pass
        else:
            raise InputsError("测试用例数据的time不对")
