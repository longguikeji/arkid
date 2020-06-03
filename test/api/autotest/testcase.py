import json

class TestCase:
    def __init__(self,data):
        self.tittle = data.get('tittle', '没有标题')
        self.condition = data.get('condition')
        self.url = data['url']
        self.headers = data.get('headers')
        self.payload = json.dumps(data.get('payload'))
        self.type = data['type']
        self.isok = ''                     #用于记录测试结果，初始值为''，通过为ok，不通过显示失败原因
        self.time = data.get('time',0)
        self.asserts = data.get('assert')
