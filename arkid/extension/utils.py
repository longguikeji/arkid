import typing
import os
from pathlib import Path
import importlib
import shutil
import string
import sys

from django.apps import apps
from django.conf import settings
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
    for ext_root_path in app_config.extension.root:
        for name in os.listdir(ext_root_path):
            ext_dir = Path(ext_root_path) / name
            if not ext_dir.is_dir() or not is_valid_extension_name(name):
                continue

            # ext_name = f'{ext_dir.parent}.{name}'
            ext = import_extension(ext_dir)
            if ext:
                extensions.append(ext)

    return extensions


# def load_active_extensions() -> typing.List[core.extension.Extension]:
def load_active_extensions():
    app_config = config.get_app_config()

    try:
        extensions = list(Extension.valid_objects.filter())
    except Exception:
        return []

    load_extension_apps(extensions)

    loaded_extensions = []

    extension: Extension
    for extension in extensions:
        if not extension.is_active:
            continue
        package = extension.package
        name = package.replace('.', '_')
        ext_dir = Path(extension.ext_dir)
        if not ext_dir.is_dir() or not is_valid_extension_name(name):
            continue

        ext = load_extension(extension.ext_dir)
        if ext:
            loaded_extensions.append(ext)

    return loaded_extensions

def load_extension_apps(extensions):

    for extension in extensions:
        name = extension.package.replace('.', '_')
        extension_models= Path(extension.ext_dir) / 'models.py'
        if not extension_models.exists():
            continue

        app_name = str(extension.ext_dir).replace('/','.')
        if app_name in settings.INSTALLED_APPS:
            continue
        settings.INSTALLED_APPS += (app_name,)

    apps.app_configs = typing.OrderedDict()
    apps.apps_ready = apps.models_ready = apps.loading = apps.ready = False
    apps.clear_cache()
    apps.populate(settings.INSTALLED_APPS)


def delete_extension_folder(extension) -> None:
    '''
    Uninstall an extension from the extension directory, this operation is non recoverable
    '''
    # TODO: 增加校验，防止部分应用中的扩展被卸载后导致无法正常工作

    name = extension.name
    if not is_valid_extension_name(name):
        return

    ext_dir = Path(extension.ext_dir)
    if ext_dir.exists():
        shutil.rmtree(ext_dir)


def import_extension(ext_dir: str) -> any:
    logger.info(f"Importing  {ext_dir}")
    ext_name = str(ext_dir).replace('/','.')
    from pip._internal import main
    requirements = str(ext_dir)+'/'+'requirements.txt'
    main(['install', '-r', requirements])
    
    ext = importlib.import_module(ext_name)
    logger.info(f"Imported  {ext}")
    if ext and hasattr(ext, 'extension'):
        ext.extension.ext_dir = ext_dir
        logger.info(f'{ext_name} import success')
        return ext.extension
    else:
        logger.info(f'{ext_name} import fail')
        return None


def load_extension(ext_dir: str) -> any:
    ext_name = str(ext_dir).replace('/','.')
    ext = importlib.import_module(ext_name)
    if not hasattr(ext, 'extension'):
        ext = importlib.import_module(ext_name+'.main')
    if ext and hasattr(ext, 'extension'):
        ext.extension.ext_dir = ext_dir
        ext.extension.start()
        logger.info(f'{ext_name} load success')
        return ext.extension
    else:
        logger.info(f'{ext_name} load fail')
        return None


def unload_extension(ext_dir: str) -> any:
    if not Path(ext_dir).exists():
        return
    ext_name = f'{Path(ext_dir).parent}.{Path(ext_dir).name}'
    ext = importlib.import_module(ext_name)
    if ext:
        ext.extension.stop()
    sys.modules.pop(ext_name, None)


def reload_extension(ext_dir: str) -> None:
    from django.urls import clear_url_caches
    from importlib import reload
    import api.v1.urls
    import arkid.urls
    # 清理url缓存
    clear_url_caches()
    
    unload_extension(ext_dir)
    load_extension(ext_dir)

    # 重新加载相应的url
    reload(api.v1.urls)
    reload(arkid.urls)
