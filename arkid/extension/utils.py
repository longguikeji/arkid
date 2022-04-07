import typing
import os
from pathlib import Path
import importlib
import shutil
import string
import sys
from arkid import core
from arkid.common.logger import logger
from arkid.extension.models import Extension
from arkid import config


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


# def find_available_extensions() -> typing.List[core.extension.Extension]:
def find_available_extensions():
    app_config = config.get_app_config()
    
    extensions = []
    for name in os.listdir(app_config.extension.root):
        ext_dir = Path(app_config.extension.root) / name
        if not ext_dir.is_dir() or not is_valid_extension_name(name):
            continue

        ext_name = f'{ext_dir.parent}.{name}'
        ext = import_extension(ext_name)
        if ext:
            extensions.append(ext)

    return extensions


# def load_active_extensions() -> typing.List[core.extension.Extension]:
def load_active_extensions():
    app_config = config.get_app_config()

    try:
        extensions = list(Extension.active_objects.filter())
    except Exception:
        return []

    loaded_extensions = []

    extension: Extension
    for extension in extensions:
        package = extension.package
        name = package.replace('.', '_')
        ext_dir = Path(app_config.extension.root) / name
        if not ext_dir.is_dir() or not is_valid_extension_name(name):
            continue

        ext_package_path = f'{ext_dir.parent}.{name}'

        ext = load_extension(ext_package_path)
        if ext:
            loaded_extensions.append(ext)

    return loaded_extensions


def delete_extension_folder(name: str) -> None:
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


def import_extension(ext_name: str) -> any:
    ext = importlib.import_module(ext_name)
    if ext:
        logger.info(f'{ext_name} import success')
        return ext.extension
    else:
        logger.info(f'{ext_name} import fail')
        return None


def load_extension(ext_name: str) -> any:
    ext = importlib.import_module(ext_name)
    if ext:
        ext.extension.load()
        logger.info(f'{ext_name} load success')
        return ext.extension
    else:
        logger.info(f'{ext_name} load fail')
        return None


def unload_extension(ext_name: str) -> any:
    ext = importlib.import_module(ext_name)
    if ext:
        ext.extension.unload()
    sys.modules.pop(ext_name, None)


def reload_extension(ext_name: str) -> None:
    from django.urls import clear_url_caches
    from importlib import reload
    import api.v1.urls
    import arkid.urls
    # 清理url缓存
    clear_url_caches()

    unload_extension(ext_name)
    load_extension(ext_name)

    # 重新加载相应的url
    reload(api.v1.urls)
    reload(arkid.urls)
