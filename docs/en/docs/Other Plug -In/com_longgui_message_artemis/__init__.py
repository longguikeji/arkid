from typing import List
from arkid.core import actions, pages
from arkid.core.api import GlobalAuth, operation
from arkid.core.extension import create_extension_schema
from arkid.core.extension.message import MessageExtension
from arkid.extension.models import TenantExtensionConfig
from arkid.core.constants import *
from .MessageListener import MessageListener
from .schema import *
import stomp
from ninja.schema import Field
from arkid.core.translation import gettext_default as _

class MessageArtemisExtension(MessageExtension):
    
    conns = []
        
    def load(self):
        super().load()
        self.register_extension_profile_schema()
        self.listen_queue()
        
    def register_extension_profile_schema(self):
        ArtemisServerConfig = create_extension_schema(
            "ArtemisServerConfig",
            __file__,
            fields=[
                (
                    "host",
                    str,
                    Field(
                        title=_("服务地址")
                    )
                ),
                (
                    "port",
                    str,
                    Field(
                        title=_("服务端口")
                    )
                ),
                (
                    "username",
                    str,
                    Field(
                        title=_("用户名")
                    )
                ),
                (
                    "password",
                    str,
                    Field(
                        title=_("密码"),
                        type="password",
                    )
                ),
                (
                    "destination",
                    str,
                    Field(
                        title=_("队列名")
                    )
                )
            ]
        )
        self.register_profile_schema(
            ArtemisServerConfig
        )
    
    def listen_queue(self):
        item = self.model
        
        if not item.profile:
            return
        
        self.conn = stomp.Connection(
            host_and_ports=[
                (
                    item.profile.get("host","127.0.0.1"), 
                    item.profile.get("port",61616)
                )
            ],
            heartbeats=(6000, 12000)
        )
        self.conn.set_listener('', MessageListener())
        self.conn.connect(
            item.profile.get("username","artemis"), 
            item.profile.get("password","artemis"), 
            wait=True,
            headers={"client-id": "arkid"},
        )
        self.conn.subscribe(
            destination=item.profile.get("destination","arkid"),
            id=item.profile.get("destination","arkid"),
            ack="auto",
            headers={
                'subscription-type': 'ANYCAST',
                'durable-subscription-name': f'arkid.{item.profile.get("destination","arkid")}',
            },
        )
    
extension = MessageArtemisExtension()
