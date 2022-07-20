
from abc import abstractmethod
from arkid.common.logger import logger
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core.event import SEND_SMS,Event

class SmsExtension(Extension):

    TYPE = "sms"

    @property
    def type(self):
        return SmsExtension.TYPE

    def load(self):
        self.listen_event(SEND_SMS, self.event_send_sms)
        super().load()
        
    def event_send_sms(self,event,**kwargs):
        """ 发送短信时间

        Args:
            event (Event): 事件
        事件数据（event.data）结构说明:
            ``` json
            {
                "config_id": "xxxx", # 必传，插件运行时配置ID
                "mobile": "xxxx", # 必传，电话号码
                "code": "xxxx", # 非必传，验证码
                "areacode": "xxxx", # 非必传，区号
                "username": "xxxx" # 非必传，用户名
                ...
            }
            
            ```

        Returns:
            发送短信结果
        """
        if event.packages == self.package or self.package in event.packages:
            return self.send_sms(event,**kwargs)
        
        
    @abstractmethod   
    def send_sms(self, event:Event, **kwargs):
        """ 发送短信

        Args:
            event (Event): 事件
        """
        pass
    