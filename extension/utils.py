import typing
import os
from pathlib import Path
from common.extension import InMemExtension
import config
import importlib
import shutil
import string
from common.logger import logger
from config import Config
from django.conf.urls import url, include



def is_valid_extension_name(name: str) -> bool:
    name = name.strip().lower()

    valid_identifiers = string.ascii_lowercase + string.digits + '_'

    b = True

    for idx, c in enumerate(name):
        if idx == 0 and c in string.digits + '_':
            b = False
            break

        if c not in valid_identifiers:
            b = False
            break

    return b


def find_installed_extensions() -> typing.List[InMemExtension]:
    app_config = config.get_app_config()

    extensions = []
    for name in os.listdir(app_config.extension.root):
        ext_dir = Path(app_config.extension.root) / name
        if not ext_dir.is_dir() or not is_valid_extension_name(name):
            continue

        ext_name = f'{ext_dir.parent}.{name}'
        ext = load_extension(ext_name)
        extensions.append(ext)

    return extensions


def load_installed_extensions(runtime) -> typing.List[InMemExtension]:
    app_config = config.get_app_config()

    extensions = []
    for name in os.listdir(app_config.extension.root):
        ext_dir = Path(app_config.extension.root) / name
        if not ext_dir.is_dir() or not is_valid_extension_name(name):
            continue

        ext_name = f'{ext_dir.parent}.{name}'

        if app_config.extension.config.get(name, {}).get('enabled') == 0:
            logger.warning(f'skip extension: {name}, [not enabled]')
            continue

        ext = load_extension(ext_name)
        if ext is not None:
            logger.info(f'extension {ext.name} loaded')
            ext.start(runtime)
            extensions.append(ext)

        extension_global_urls_filename = Path(ext_dir) / 'urls.py'
        if extension_global_urls_filename.exists():
            print(f'>>>load extension urls: {ext_name}.urls')
            urlpatterns = [url('', include((f'{ext_name}.urls', 'extension'), namespace=f'{ext.name}'))]
            runtime.register_route(urlpatterns)

        extension_tenant_urls_filename = Path(ext_dir) / 'tenant_urls.py'
        if extension_tenant_urls_filename.exists():
            print(f'load extension urls: {ext_name}.urls')
            urlpatterns = [url(r'tenant/(?P<tenant_id>[\w-]+)/', include((f'{ext_name}.tenant_urls', 'extension'), namespace=f'{ext.name}'))]
            runtime.register_route(urlpatterns)


    return extensions


def install_extension(p: Path) -> None:
    '''
    Install an extension from various sources:

    1. local directory
    2. remote http url

    '''
    name = p.name

    if not is_valid_extension_name(name):
        return

    app_config = config.get_app_config()
    ext_dir = Path(app_config.extension.root) / name
    
    shutil.copytree(p, ext_dir)


def uninstall_extension(name: str) -> None:
    '''
    Uninstall an extension from the extension directory, this operation is non recoverable
    '''
    # TODO: 增加校验，防止部分应用中的扩展被卸载后导致无法正常工作

    if not is_valid_extension_name(name):
        return

    app_config = config.get_app_config()
    ext_dir = Path(app_config.extension.root) / name
    if ext_dir.exists():
        shutil.rmtree(ext_dir)


def load_extension(name: str) -> any:
    # if not is_valid_extension_name(name):
    #     return

    ext = importlib.import_module(name)
    return ext.extension
