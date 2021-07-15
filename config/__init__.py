from django.conf import settings
from pathlib import Path
from django.utils.translation import to_language
import toml
from .email_config import EmailConfig
from .extension_config import ExtensionConfig
from common.utils import deep_merge


class Config(object):

    extension: ExtensionConfig
    email: EmailConfig

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self, filename=None):
        if filename is None:
            filename = Path(settings.BASE_DIR) / settings.CONFIG_FILE

        data = toml.load(filename)

        local_filename: Path = Path(settings.BASE_DIR) / settings.CONFIG_LOCAL_FILE
        if local_filename.exists():
            local_data = toml.load(local_filename)
            data = deep_merge(data, local_data, update=False)

        self.name = data.get('name')
        self.host = data.get('host')
        self.frontend_host = data.get('frontend_host')
        self.https_enabled = data.get('https_enabled')

        self.extension = ExtensionConfig(
            root=data.get('extension').get('root'),
        )

        self.email = EmailConfig(
            host=data.get('email').get('host'),
            port=data.get('email').get('port'),
            user=data.get('email').get('user'),
            password=data.get('email').get('password'),
            nickname=data.get('email').get('nickname'),
        )

        # scan all extension configs
        for k, v in data.items():
            if k == 'extension':
                for name, vv in v.items():
                    self.extension.config[name] = vv

    def get_host(self, schema=True):
        if schema:
            return '{}://{}'.format('https' if self.https_enabled else 'http', self.host)

        return self.host

    def get_frontend_host(self, schema=True):
        if schema:
            return '{}://{}'.format('https' if self.https_enabled else 'http', self.frontend_host)

        return self.host

    def get_slug_frontend_host(self, slug, schema=True):
        if schema:
            return '{}://{}.{}'.format('https' if self.https_enabled else 'http', slug, self.frontend_host)
        return self.host


def get_app_config() -> Config:
    return Config()
