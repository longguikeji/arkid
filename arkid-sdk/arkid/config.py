"""
Load config files once per interpreter invocation.
"""
import logging
import os
import pkg_resources

from six.moves.configparser import (
    ConfigParser,
    MissingSectionHeaderError,
    NoOptionError,
    NoSectionError,
)

from arkid.exceptions import ArkIDError, ArkIDSDKUsageError

logger = logging.getLogger(__name__)


# at import-time, it's None
_parser = None


def _get_lib_config_path():
    """
    获取 ArkID SDk 中默认配置文件的位置
    暂时不能处理任何专有状态，只是一个获取文件位置的助手
    """
    fname = "oneid.cfg"
    try:
        logger.debug("Attempting pkg_resources load of lib config")
        path = pkg_resources.resource_filename("arkid", fname)
        logger.debug("pkg_resources load of lib config success")
    except ImportError:
        logger.debug("pkg_resources load of lib config failed, failing over to path joining")
        pkg_path = os.path.dirname(__file__)
        path = os.path.join(pkg_path, fname)
    return path


class ArkIDConfigParser(object):
    """
    对 < ConfigParser > 对象进行封装，以修改 get() 和 配置文件的载入。
    """

    _GENERAL_CONF_SECTION = "general"

    def __init__(self):
        logger.debug("Loading SDK Config parser")
        self._parser = ConfigParser()
        self._load_config()
        logger.debug("Config load succeeded")

    def _load_config(self):
        """
        载入配置文件内容
        """
        try:
            self._parser.read(_get_lib_config_path())
        except MissingSectionHeaderError:
            logger.error(
                (
                    # TODO
                )
            )
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


        Also optionally, check for a relevant environment variable, which is
        named always as ARKID_SDK_{option.upper()}. Note that 'section'
        doesn't slot into the naming at all. Otherwise, we'd have to contend
        with ARKID_SDK_GENERAL_... for almost everything, and
        ARKID_SDK_ENVIRONMENT\ PROD_... which is awful.

        Returns None for an unfound key, rather than raising a NoOptionError.
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
            logger.debug("载入来自{}={}环境的配置".format(env_option_name, value))
            value = os.environ[env_option_name]
        else:
            try:
                value = self._parser.get(section, option)
            except (NoOptionError, NoSectionError):
                if failover_to_general:
                    logger.debug("载入配置 [{}]:{} 失败，将从[general]选项下加载配置".format(section, option))
                    value = self.get(option, section=self._GENERAL_CONF_SECTION)

        if value is not None:
            value = type_cast(value) if type_cast else str(value)
        return value


def _get_parser():
    """
    Singleton pattern implemented via a global variable and function.
    There is only ever one _parser, and it is always returned by this function.
    """
    global _parser
    if _parser is None:
        _parser = ArkIDConfigParser()
    return _parser


def get_service_url(environment, service):
    logger.debug(
        'Service URL Lookup for "{}" under env "{}"'.format(service, environment)
    )
    p = _get_parser()
    option = service + "_service"
    # TODO: validate with urlparse?
    url = p.get(option, environment=environment)
    if url is None:
        raise ArkIDSDKUsageError(
            (
                'Failed to find a url for service "{}" in environment "{}". '
                'Please double-check that ARKID_SDK_ENVIRONMENT is set correctly, or not set at all'
            ).format(service, environment)
        )
    logger.debug('Service URL Lookup Result: "{}" is at "{}"'.format(service, url))
    return url


def get_http_timeout(environment):
    p = _get_parser()
    value = p.get(
        "http_timeout",
        environment=environment,
        failover_to_general=True,
        check_env=True,
        type_cast=float,
    )
    value = 60 if value is None else value
    logger.debug("default http_timeout set to {}".format(value))
    return value


def get_ssl_verify(environment):
    p = _get_parser()
    value = p.get(
        "ssl_verify",
        environment=environment,
        failover_to_general=False,
        check_env=True,
        type_cast=_bool_cast,
    )
    if value is None:
        return True
    logger.debug("ssl_verify set to {}".format(value))
    return value


def _bool_cast(value):
    value = value.lower()
    if value in ("1", "yes", "true", "on"):
        return True
    elif value in ("0", "no", "false", "off"):
        return False
    logger.error('Value "{}" can\'t cast to bool'.format(value))
    raise ValueError("Invalid config bool")


def get_arkid_environ(input_env=None):
    """
    在配置中查找的 ArkID SDK 所需的运行环境。

    通常为 `default` ，但其可被系统环境变量 `ARKID_SDK_ENVIRONMENT` 覆盖。
    在这种情况下，若调用者未显式指定运行环境，将使用 `ARKID_SDK_ENVIRONMENT` 。
    :param input_env: An environment which was passed.
                      e.g. to a client instantiation
    """
    if input_env is None:
        env = os.environ.get("ARKID_SDK_ENVIRONMENT", "default")
    else:
        env = input_env

    if env != "default":
        logger.info(
            ("载入非默认配置环境 arkid_environment={}".format(env))
        )
    return env
