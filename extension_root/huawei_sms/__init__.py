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
        signature = o.data.get('signature')
        sender = o.data.get('sender')

        template_code = o.data.get('template_code')
        template_register = o.data.get('template_register')
        template_reset_pwd = o.data.get('template_reset_pwd')
        template_activate = o.data.get('template_activate')
        template_reset_mobile = o.data.get('template_reset_mobile')
        template_login = o.data.get('template_login')

        template_code_i18n = o.data.get('template_code_i18n')
        template_register_i18n = o.data.get('template_register_i18n')
        template_reset_pwd_i18n = o.data.get('template_reset_pwd_i18n')
        template_activate_i18n = o.data.get('template_activate_i18n')
        template_reset_mobile_i18n = o.data.get('template_reset_mobile_i18n')
        template_login_i18n = o.data.get('template_login_i18n')

        sms_provider = HuaWeiSMSProvider(
            access_key=access_key,
            secret_key=secret_key,
            signature=signature,
            sender=sender,
            template_code=template_code,
            template_register=template_register,
            template_reset_pwd=template_reset_pwd,
            template_activate=template_activate,
            template_reset_mobile=template_reset_mobile,
            template_login=template_login,
            template_code_i18n=template_code_i18n,
            template_register_i18n=template_register_i18n,
            template_reset_pwd_i18n=template_reset_pwd_i18n,
            template_activate_i18n=template_activate_i18n,
            template_reset_mobile_i18n=template_reset_mobile_i18n,
            template_login_i18n=template_login_i18n,
        )

        runtime.register_sms_provider(sms_provider)

        super().start(runtime=runtime, *args, **kwargs)

    def teardown(self, runtime: Runtime, *args, **kwargs):

        from extension.models import Extension
        o = Extension.objects.filter(
            type=KEY,
        ).order_by('-id').first()

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

        runtime.logout_sms_provider(sms_provider)


extension = HuaWeiExtension(
    name=KEY,
    tags='sms',
    scope='global',
    type='global',
    description="""基于华为云平台的短信发送功能""",
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='insfocus@gmail.com',
    serializer=HuaWeiSMSSerializer,
)
