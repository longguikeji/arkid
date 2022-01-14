"""
插件处理
"""
from enum import auto
from common.extension import InMemExtension
from runtime import Runtime
from .constants import KEY
from .listener import MessageListener
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import ExtensionBaseSerializer

class MessageExtensionConfigSerializer(serializers.Serializer):

    host = serializers.CharField(required=True, label=_('服务IP'))
    port = serializers.CharField(required=True, label=_('端口号'))
    username = serializers.CharField(required=True, label=_('用户名'))
    password = serializers.CharField(required=True, label=_('密码'))
    destination = serializers.CharField(required=True,label=_("队列名"))


class MessageExtensionSerializer(ExtensionBaseSerializer):

    data = MessageExtensionConfigSerializer(label=_('配置数据'))
    

class MessageExtension(InMemExtension):
    """
    认证规则插件
    """
    _conn = None

    def start(self, runtime: Runtime, *args, **kwargs):

        # from extension.models import Extension

        # o = Extension.active_objects.filter(
        #     type=KEY,
        # ).first()
        # print("extension start")
        # import stomp
        # self._conn = stomp.Connection(
        #     host_and_ports=[
        #         (
        #             o.data.get("host","127.0.0.1"), 
        #             o.data.get("port",61616)
        #         )
        #     ],
        #     heartbeats=(6000, 12000)
        # )
        # self._conn.set_listener('', MessageListener())

        # self._conn.connect(
        #     o.data.get("username","artemis"), 
        #     o.data.get("password","artemis"), 
        #     wait=True,
        #     headers={"client-id": "arkid"},
        # )
        # self._conn.subscribe(
        #     destination=o.data.get("destination","arkid"),
        #     id=o.data.get("destination","arkid"),
        #     ack="auto",
        #     headers={
        #         'subscription-type': 'ANYCAST',
        #         'durable-subscription-name': f'arkid.{o.data.get("destination","arkid")}',
        #     },
        # )
        return super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):  # pylint: disable=unused-argument
        # print("teardown")

        # self._conn.unsubscribe(
        #     destination="arkid",
        #     id="arkid",
        #     headers={
        #         'subscription-type': 'ANYCAST',
        #         'durable-subscription-name': f"arkid.sssarkid",
        #     },
        # )
        # self._conn.disconnect()
        return super().teardown(runtime=runtime, *args, **kwargs)


extension = MessageExtension(
    tags='message',
    name=KEY,
    scope='tenant',
    type='tenant',
    description="消息模块(artemis)",
    version="1.0",
    homepage="https://www.longguikeji.com",
    logo="",
    maintainer="北京龙归科技有限公司",
    serializer=MessageExtensionSerializer,
)
