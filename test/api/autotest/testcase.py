import json

class TestCase:
    def __init__(self,data):
        self.tittle = data.get('tittle','没有标题')
        self.condition = data.get('condition')
        self.url = data.get('url')
        self.headers = data.get('headers')
        self.payload = json.dumps(data.get('payload'))
        self.type = data.get('type')
        self.time = data.get('time',0)
        self.asserts = data.get('assert')
        self.codenum = 0   #接口返回状态码
        self.text = ''       #接口返回信息

    def InputsError(self):
        if self.url != None:
            if self.type != None:
                if self.time.isdigit():
                    self.time = self.time
                else:
                    self.time = 0
            else:
                ex = Exception('接口数据不对，没有请求类型')
                raise ex
        else:
            ex = Exception('接口数据不对，没有url')
            raise ex