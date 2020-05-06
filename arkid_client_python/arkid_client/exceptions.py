"""
Define ArkIDError & it's Subclass
"""
import logging
import requests

LOGGER = logging.getLogger(__name__)


class ArkIDError(Exception):
    """
    ArkID Client 错误的基类
    """


class ArkIDSDKUsageError(ArkIDError, ValueError):
    """
    当 ArkID Client 检测到它被不正确的使用时会抛出 ``ArkIDSDKUsageError`` 异常，
    这些错误通常表示某些关于 ArkID Client 使用的规范(例如所需的操作顺序)已被违反。
    """


class ArkIDAPIError(ArkIDError):
    """
    封装 REST API 的响应信息

    :ivar http_status: HTTP 响应的状态码 (int)
    :ivar message: 来自 API 的错误信息。一般来说，其对开发人员是有用的，
            但在某些情况下它也许适合显示给终端用户。
    """
    def __init__(self, response, *args):
        self._underlying_response = response
        self.http_status = response.status_code
        if "Content-Type" in response.headers and ("application/json" in response.headers["Content-Type"]):
            LOGGER.debug("响应对象的 Content-Type 为 `application/json`。 " "正在以 JSON 格式载入错误信息。")
            try:
                self._load_from_json(response.json())
            except (KeyError, ValueError):
                LOGGER.error("无法对错误信息进行 JSON 格式解析，" "响应对象的 Content-Type 参数值使用错误，" "或者响应消息体不符合规范。")
                self._load_from_text(response.text)
        else:
            LOGGER.debug("暂不支持响应对象的 Content-Type 类型， " "正在以文本格式加载错误信息（默认）。")
            # fallback to using the entire body as the message for all other types
            self._load_from_text(response.text)
        args = self._get_args()
        ArkIDError.__init__(self, *args)

    @property
    def raw_json(self) -> dict or None:
        """
        获取从 ArkID API 接收到的响应信息，尝试以 JSON 格式解析数据，
        并转化为 dict 。

        如果响应信息无法通过 JSON 格式加载， 则返回 None 。
        """
        response = self._underlying_response
        if "Content-Type" in response.headers and ("application/json" in response.headers["Content-Type"]):
            try:
                return response.json()
            except ValueError:
                LOGGER.error("无法对错误信息进行 JSON 格式解析，" "响应对象的 Content-Type 参数值使用错误，" "或者响应消息体不符合规范。")
                return None
        else:
            return None

    @property
    def raw_text(self) -> str:
        """
        以 string 形式获取响应信息。
        """
        return self._underlying_response.text

    def _get_args(self):
        """
        传入给 < Exception > 对象的参数，显示在堆栈跟踪中。
        """
        return self.http_status, self.message

    def _load_from_json(self, data: dict):
        """
        从 JSON 格式的信息中加载错误数据。需根据 ArkID 服务端的
        响应体结构来规划具体实现。
        # TODO
        """
        self.message = data

    def _load_from_text(self, text: str):
        """
        从 text 格式的信息中加载错误数据。需根据 ArkID 服务端的
        响应体结构来规划具体实现。
        # TODO
        """
        self.message = text


class UserAPIError(ArkIDAPIError):
    """
    用户服务客户端的错误类型，继承了 ``message`` 变量
    """
    def __init__(self, response):
        self.error_data = None
        ArkIDAPIError.__init__(self, response)

    def _get_args(self):
        return self.http_status, self.message


class OrgAPIError(ArkIDAPIError):
    """
    组织服务客户端的错误类型，继承了 ``message`` 变量
    """
    def __init__(self, response):
        self.error_data = None
        ArkIDAPIError.__init__(self, response)

    def _get_args(self):
        return self.http_status, self.message


class NodeAPIError(ArkIDAPIError):
    """
    节点服务客户端的错误类型，继承了 ``message`` 变量
    """
    def __init__(self, response):
        self.error_data = None
        ArkIDAPIError.__init__(self, response)

    def _get_args(self):
        return self.http_status, self.message


class InfrastructureAPIError(ArkIDAPIError):
    """
    基础设施服务客户端的错误类型，继承了 ``message`` 变量
    """
    def __init__(self, response):
        self.error_data = None
        ArkIDAPIError.__init__(self, response)

    def _get_args(self):
        return self.http_status, self.message


class UsercenterAPIError(ArkIDAPIError):
    """
    个人中心服务客户端的错误类型，继承了 ``message`` 变量
    """
    def __init__(self, response):
        self.error_data = None
        ArkIDAPIError.__init__(self, response)

    def _get_args(self):
        return self.http_status, self.message


class AuthAPIError(ArkIDAPIError):
    """
    认证服务客户端的错误类型，继承了 ``message`` 变量
    """


# Wrappers around requests exceptions, so the SDK is API independent.
class NetworkError(ArkIDError):
    """
    当与 ArkID 服务通信发生错误时会抛出 ``NetworkError`` 错误，
    其为通信方面出现的错误的基类。
    其在保留原始异常数据的基础上，也可以接受其他一些有用的消息，
    方便用户明确错误所在。
    """
    def __init__(self, message, exception):
        super(NetworkError, self).__init__(message)
        self.underlying_exception = exception


class ArkIDTimeoutError(NetworkError):
    """REST API 请求超时"""


class ArkIDConnectionTimeoutError(ArkIDTimeoutError):
    """请求在连接建立期间超时，这些错误可以进行安全地重试。"""


class ArkIDConnectionError(NetworkError):
    """在发出 REST 请求时发生连接错误。"""


def convert_request_exception(exception):
    """将 ``requests.Exception`` 转化为 ArkID Client 的 ``NetworkError``"""

    if isinstance(exception, requests.ConnectTimeout):
        return ArkIDConnectionTimeoutError("Connection Timeout Error on request", exception)

    if isinstance(exception, requests.Timeout):
        return ArkIDTimeoutError("Timeout Error on request", exception)

    if isinstance(exception, requests.ConnectionError):
        return ArkIDConnectionError("Connection Error on request", exception)

    return NetworkError("Network Error on request", exception)
