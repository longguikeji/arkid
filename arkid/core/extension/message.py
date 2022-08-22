
from abc import abstractmethod
from arkid.common.logger import logger
from arkid.core.error import ErrorCode
from arkid.core.extension import Extension
from arkid.core.models import Tenant, User, TenantExtensionConfig,Message
from arkid.core.translation import gettext_default as _
from arkid.core.event import Event

class MessageExtension(Extension):

    TYPE = "message"
    
    @property
    def type(self):
        return MessageExtension.TYPE

    def load(self):
        super().load()
    
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