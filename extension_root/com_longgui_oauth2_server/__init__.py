from arkid.core import extension

class OAuth2ServerExtension(extension.Extension):

    def load(self):
        super().load()
        self.load_urls()
    
    def load_urls(self):
        # from django.urls import path

        # urls = [
        #     url(r'^o/', include(('oauth2_provider.urls', 'oauth2_provider'), namespace='oauth2_provider')),
        # ]

        self.register_routers(urls, True)

extension = OAuth2ServerExtension(
    package='com.longgui.oauth2_server',
    description='OAuth2认证服务',
    version='1.0',
    labels='oauth',
    homepage='https://www.longguikeji.com',
    logo='',
    author='hanbin@jinji-inc.com',
)