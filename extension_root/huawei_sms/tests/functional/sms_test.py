
from extension_root.huawei_sms.provider import HuaWeiSMSProvider
from extension_root.huawei_sms.constants import KEY
import os
import django
import unittest

# 导入settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arkid.settings")
# 安装django
django.setup()


class TestDict(unittest.TestCase):

    def test_send_sms(self):
        from extension.models import Extension

        o = Extension.active_objects.filter(
            type=KEY,
        ).first()
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
        mobile = '15291584673'
        code = '1234'
        sms_provider.send_auth_code(mobile, code)
