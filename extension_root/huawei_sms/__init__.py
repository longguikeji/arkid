
from runtime import Runtime
from common.extension import InMemExtension
from .constants import KEY
from .serializers import HuaWeiSMSSerializer
from .provider import HuaWeiSMSProvider


class HuaWeiExtension(InMemExtension):

    def start(self, runtime: Runtime, *args, **kwargs):

        from extension.models import Extension
        o = Extension.active_objects.filter(
            type=KEY,
        ).first()

        assert o is not None
        access_key = o.data.get('access_key')
        secret_key = o.data.get('secret_key')
        template = o.data.get('template')
        signature = o.data.get('signature')
        sender = o.data.get('sender')

        sms_provider = HuaWeiSMSProvider(
            access_key=access_key,
            secret_key=secret_key,
            template=template,
            signature=signature,
            sender=sender,
        )

        runtime.register_sms_provider(sms_provider)

        super().start(runtime=runtime, *args, **kwargs)


extension = HuaWeiExtension(
    name=KEY,
    description="""基于华为云平台的短信发送功能""",
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='insfocus@gmail.com',
    serializer=HuaWeiSMSSerializer,
)
