"""
Load config files once per interpreter invocation.
"""
import logging
import os

from six.moves.configparser import (
    ConfigParser,
    MissingSectionHeaderError,
    NoOptionError,
    NoSectionError,
)

from arkid_client.exceptions import ArkIDError, ArkIDSDKUsageError

LOGGER = logging.getLogger(__name__)

# at import-time, they're None
_PARSER = None
_CONFIG_PATH = None

# def _get_lib_config_path():
#     """
#     获取 ArkID SDk 中默认配置文件的位置
#     暂时不能处理任何专有状态，只是一个获取文件位置的助手
#     """
#     fname = "oneid.cfg"
#     try:
#         LOGGER.debug("Attempting pkg_resources load of lib config")
#         path = pkg_resources.resource_filename("arkid", fname)
#         LOGGER.debug("pkg_resources load of lib config success")
#     except ImportError:
#         print('failed')
#         LOGGER.debug("pkg_resources load of lib config failed, failing over to path joining")
#         pkg_path = os.path.dirname(__file__)
#         path = os.path.join(pkg_path, fname)
#     return path


def set_config_path(path):
    """
    设置全局配置文件的路径
    :param path: 配置文件的绝对路径
    :return:
    """
    global _CONFIG_PATH
    if not os.path.exists(path):
        raise FileNotFoundError('无法找到 ArkID SDK 配置文件')
    _CONFIG_PATH = path


class ArkIDConfigParser(object):
    """
    对 < ConfigParser > 对象进行封装，以修改 get() 和 配置文件的载入。
    """

    _GENERAL_CONF_SECTION = "general"

    def __init__(self):
        LOGGER.debug("Loading SDK Config parser")
        self._parser = ConfigParser()
        self._load_config()
        LOGGER.debug("Config load succeeded")

    def _load_config(self):
        """
        载入配置文件内容
        """
        if not _CONFIG_PATH:
            raise ArkIDSDKUsageError('请先导入 ARKID SDK 所需的配置文件来使其正常工作')
        try:
            self._parser.read(_CONFIG_PATH)
        except MissingSectionHeaderError:
            LOGGER.error((
            # TODO
            ))
            raise ArkIDError(
            # TODO
            )

    def get(
        self,
        option,
        section=None,
        environment=None,
        failover_to_general=False,
        check_env=False,
        type_cast=None,
    ):
        r"""
        尝试在配置文件中查找一个选项， 若没有找到该选项，则进入 `general` 部分。
        """
        # environment is just a name for sections that start with 'environment '
        if environment:
            section = '{}{}{}'.format('environment', ' ', environment)

        # 若未指定环境名称， 将载入 `general` 选项下的内容
        if section is None:
            section = self._GENERAL_CONF_SECTION

        # 若传入 `option` 参数值，则会首先在环境变量中检索相关配置
        env_option_name = "ARKID_SDK_{}".format(option.upper())
        value = None
        if check_env and env_option_name in os.environ:
            LOGGER.debug("载入来自{}={}环境的配置".format(env_option_name, value))
            value = os.environ[env_option_name]
        else:
            try:
                value = self._parser.get(section, option)
            except (NoOptionError, NoSectionError):
                if failover_to_general:
                    LOGGER.debug("载入配置 [{}]:{} 失败，将从[general]选项下加载配置".format(section, option))
                    value = self.get(option, section=self._GENERAL_CONF_SECTION)

        if value is not None:
            value = type_cast(value) if type_cast else str(value)
        return value


def _get_parser():
    """
    获取 config parser 全局唯一
    """
    global _PARSER
    if _PARSER is None:
        _PARSER = ArkIDConfigParser()
    return _PARSER


def get_service_url(environment: str, service: str):
    """
    获取服务的根 URL
    """
    LOGGER.debug('Service URL Lookup for "{}" under env "{}"'.format(service, environment))
    _parser = _get_parser()
    option = service + "_service"
    # TODO: validate with urlparse?
    url = _parser.get(option, environment=environment)
    if url is None:
        raise ArkIDSDKUsageError(
            ('Failed to find a url for service "{}" in environment "{}". '
             'Please double-check that ARKID_SDK_ENVIRONMENT is set correctly, or not set at all').format(
                 service, environment))
    LOGGER.debug('Service URL Lookup Result: "{}" is at "{}"'.format(service, url))
    return url


def get_http_timeout(environment: str):
    """
    获取 HTTP 超时设置
    """
    _parser = _get_parser()
    value = _parser.get(
        "http_timeout",
        environment=environment,
        failover_to_general=True,
        check_env=True,
        type_cast=float,
    )
    value = 60 if value is None else value
    LOGGER.debug("default http_timeout set to {}".format(value))
    return value


def get_ssl_verify(environment: str):
    """
    获取 HTTP SSL 设置
    """
    _parser = _get_parser()
    value = _parser.get(
        "ssl_verify",
        environment=environment,
        failover_to_general=False,
        check_env=True,
        type_cast=_bool_cast,
    )
    if value is None:
        return True
    LOGGER.debug("ssl_verify set to {}".format(value))
    return value


def _bool_cast(value: str):
    """
    布尔类型转换
    """
    value = value.lower()
    if value in ("1", "yes", "true", "on"):
        return True
    if value in ("0", "no", "false", "off"):
        return False
    LOGGER.error('Value "{}" can\'t cast to bool'.format(value))
    raise ValueError("Invalid config bool")


def get_arkid_environ(input_env=None):
    """
    在配置中查找的 ArkID SDK 所需的运行环境。
    通常为 `default` ，但其可被系统环境变量 `ARKID_SDK_ENVIRONMENT` 覆盖。
    在这种情况下，若调用者未显式指定运行环境，将使用 `ARKID_SDK_ENVIRONMENT` 。
    """
    if input_env is None:
        env = os.environ.get("ARKID_SDK_ENVIRONMENT", "default")
    else:
        env = input_env

    if env != "default":
        LOGGER.info(("载入非默认配置环境 arkid_environment={}".format(env)))
    return env
