from arkid.core.extension.app_protocol import AppProtocolExtension
from arkid.core.extension import create_extension_schema
from arkid.core.translation import gettext_default as _
from .constants import package
from .schemas import Saml2SPCertConfigSchema

class Saml2Extension(AppProtocolExtension):
    def load(self):
        # 加载相应的配置文件
        super().load()
        self.register_app_protocol_schema(Saml2SPCertConfigSchema, 'Saml2SP_CERT')

    def create_app(self, event, **kwargs):
        if event.data["package"] == package:
            config = event.data["config"]
            return self.update_app_data(event, config, True)

    def update_app(self, event, **kwargs):
        if event.data["package"] == package:
            config = event.data["config"]
            return self.update_app_data(event, config, False)

    def delete_app(self, event, **kwargs):
        pass

extension = Saml2Extension(
    package=package,
    name='Saml2.0协议',
    version='1.0',
    labels=['saml2.0'],
    homepage='https://www.longguikeji.com',
    logo='',
    author='guancyxx@guancyxx.cn',
)
