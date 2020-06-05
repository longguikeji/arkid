import json
from inputs_error import InputsError

class TestCase:
    def __init__(self,data):
        self.tittle = data.get('tittle','没有标题')
        self.condition = data.get('condition')
        self.url = data.get('url')
        self.headers = data.get('headers')
        self.payload = data.get('payload')
        self.type = data.get('type')
        self.time = data.get('time',0)
        self.asserts = data.get('assert')

        if self.url != None:
            while self.type == None:
                raise InputsError("接口数据不对，缺少请求类型")
        else:
            raise InputsError("接口数据不对，缺少url")
