from extension.models import Extension
import typing
import os
from pathlib import Path
from common.extension import InMemExtension
import config
import importlib
import shutil
import string
from common.logger import logger
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


def find_available_extensions() -> typing.List[InMemExtension]:
    app_config = config.get_app_config()
    from runtime import get_app_runtime

    extensions = []
    for name in os.listdir(app_config.extension.root):
        ext_dir = Path(app_config.extension.root) / name
        if not ext_dir.is_dir() or not is_valid_extension_name(name):
            continue

        ext_name = f'{ext_dir.parent}.{name}'
        ext = load_extension(get_app_runtime(), ext_name, name)
        extensions.append(ext)

    return extensions


def load_installed_extensions(runtime) -> typing.List[InMemExtension]:
    app_config = config.get_app_config()

    try:
        extensions = list(Extension.active_objects.filter())
    except Exception:
        return []

    loaded_extensions = []
    
    extension: Extension
    for extension in extensions:
        name = extension.type
        ext_dir = Path(app_config.extension.root) / name
        if not ext_dir.is_dir() or not is_valid_extension_name(name):
            continue

        ext_name = f'{ext_dir.parent}.{name}'

        ext = load_extension(runtime, ext_name, name, True)
        if ext is not None:
            logger.info(f'extension {ext.name} loaded')
            ext.start(runtime)
            loaded_extensions.append(ext)


    return loaded_extensions


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


def load_extension(runtime, ext_name: str, name: str, execute: bool=False) -> any:
    app_config = config.get_app_config()
    ext_dir = Path(app_config.extension.root) / name

    ext = importlib.import_module(ext_name)
    if not execute:
        return ext.extension

    extension_global_urls_filename = Path(ext_dir) / 'urls.py'
    if extension_global_urls_filename.exists():
        urlpatterns = [url('', include((f'{ext_name}.urls', 'extension'), namespace=f'{name}'))]
        runtime.register_route(urlpatterns)

    extension_tenant_urls_filename = Path(ext_dir) / 'tenant_urls.py'        
    if extension_tenant_urls_filename.exists():
        print('>>>', f'{ext_name}.tenant_urls')
        urlpatterns = [url(r'tenant/(?P<tenant_id>[\w-]+)/', include((f'{ext_name}.tenant_urls', 'extension'), namespace=f'{name}'))]
        print(urlpatterns)
        runtime.register_route(urlpatterns)
        
    ext.extension.start(runtime)
    return ext.extension
