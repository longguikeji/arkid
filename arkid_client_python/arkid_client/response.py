import logging

logger = logging.getLogger(__name__)


class ArkIDResponse(object):
    """
    通用响应基类，只有一个简单的 `data` 成员。最常见的响应数据
    是 JSON 字典。为了尽可能不去处理这种类型的反应， < ArkIDResponse >
    对象支持通过字典的形式来直接访问响应内容，如果 `data` 不是字典结构，
    将会抛出 < TypeError > 异常.
    >>> print('"Response ID": response["id"]') # alias for response.data["id"]

    < ArkIDResponse > 对象封装 HTTP 响应的数据给调用者，大多数的操作都是基于
    与这些数据进行交互。
    """

    def __init__(self, data, client=None):
        # 初始化客户端类型
        self.client = client

        # 初始化响应数据
        self._data = data

    def __str__(self):
        return "{}:({})".format(self.__class__.__name__, self.data)

    def __getitem__(self, key):
        # 强制以 dict 形式获取所需信息，若捕获到 < TypeError > 异常，
        # 说明相应数据类型非 dict 。
        data = self.data
        try:
            return data[key]
        except TypeError:
            logger.error("无法基于<'{}'>类型索引响应数据".format(type(self)))
            raise TypeError('此类型的响应数据不支持索引。')

    def __contains__(self, item):
        """
        ``x in BaseResponse`` is an alias for ``x in BaseResponse.data``
        """
        return item in self.data

    @property
    def data(self):
        """
        Response data as a Python data structure. Usually a dict or list.
        """
        return self._data

    def get(self, *args, **kwargs):
        """
        ``BaseResponse.get`` is just an alias for ``BaseResponse.data.get``
        """
        return self.data.get(*args, **kwargs)


class ArkIDHTTPResponse(ArkIDResponse):
    """
    封装底层 HTTP 响应对象。如果响应数据类型是JSON，则解析后的数据将在 `data` 中，
    否则 `data` 将为 None ，并且 `text` 将被使用。

    :ivar http_status: HTTP status code returned by the server (int)
    :ivar content_type: Content-Type header returned by the server (str)
    """

    def __init__(self, http_response, client=None):
        # 初始化 HTTP 响应数据
        ArkIDResponse.__init__(self, http_response, client=client)
        self.http_status = http_response.status_code
        self.content_type = http_response.headers["Content-Type"]

    @property
    def data(self):
        try:
            return self._data.json()
        except ValueError:
            logger.warning('由于无效的JSON格式，< ArkIDHTTPResponse > 对象的 `data` 参数值为空')
            return None

    @property
    def text(self):
        """
        The raw response data as a string.
        """
        return self._data.text
