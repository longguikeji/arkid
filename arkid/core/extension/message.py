
from abc import abstractmethod
from arkid.common.logger import logger
from arkid.core.error import ErrorCode
from arkid.core.extension import Extension
from arkid.core.models import Tenant, User, TenantExtensionConfig,Message
from arkid.core.translation import gettext_default as _
from arkid.core.event import SEND_MESSAGE,Event

class MessageExtension(Extension):

    TYPE = "message"
    
    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'type'
    composite_model = TenantExtensionConfig
    
    @property
    def type(self):
        return MessageExtension.TYPE

    def load(self):
        super().load()
    
    def register_message_schema(self, schema, app_type):
        """
        注册消息中间件schema
        Params:
            schema: schema
            app_type: 消息中间件类型
        """
        self.register_config_schema(schema, self.package + '_' + app_type)
        self.register_composite_config_schema(schema, app_type, exclude=['extension'])
    
    @abstractmethod   
    def send_message(self, event:Event, **kwargs):
        """ 发送消息

        Args:
            event (Event): 事件
        """
        pass
    
    def save_message(self,tenant:Tenant,user:User,source:TenantExtensionConfig,title:str,content:str,**kwargs):
        """保存消息

        Args:
            tenant (Tenant): 租户
            user (User): 用户
            source (TenantExtensionConfig): 来源
            title (str): 标题
            content (str): 内容
        """
        try:
            message = Message(
                tenant=tenant,
                user=user,
                source=source,
                title=title,
                content=content
            )
            
            message.save()
        except Exception as err:
            logger.error(err)
            return False, ErrorCode.MESSAGE_SAVE_FAILED
        
        return True,None