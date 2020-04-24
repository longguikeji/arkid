"""
Define ClientLogAdapter
Define BaseClient
"""
import json
import logging
import requests

from arkid_client import config
from arkid_client.exceptions import ArkIDAPIError, ArkIDSDKUsageError, convert_request_exception
from arkid_client.response import ArkIDHTTPResponse
from arkid_client.version import __version__


class ClientLogAdapter(logging.LoggerAdapter):
    """
    Stuff in the memory location of the client to make log records unambiguous.
    """
    def process(self, msg, kwargs):
        return "[instance:{0}] {1}".format(id(self.extra["client"]), msg), kwargs


class BaseClient(object):
    """
    简单的基类客户端，可处理 ArkID REST APIs 返回的错误信息。
    封装 < requests.Session > 对象为一个简化的接口，该接口不公开来自请求
    的任何内容。

    注意：
        强烈建议您不要尝试直接实例化 < BaseClient >

    **Parameters**

        ``authorizer`` (:class:`< ArkIDAuthorizer >
          < arkid.authorizers.base.ArkIDAuthorizer >`)
          A < ArkIDAuthorizer > which will generate Authorization headers

        ``app_name`` (*str*)
          （可选的）用于标识调用方，往往指代正在使用 ArkID SDK 进行开发的项目。
          此参数与客户端的任何操作无关。仅仅作为请求头部 `User-Agent` 的一部分
          发送给 ArkID 团队，以方便调试出现的问题。

       ``http_timeout`` (*float*)
          HTTP 连接响应的等待时间（单位：s）。默认 60 。
          如果传入的值为 -1 ，代表请求发送后将无限期挂起。

    All other parameters are for internal use and should be ignored.
    所有其它的初始化参数用于子类内部使用
    """

    # 可被 < BaseClient > 子类重写，其必须为 < ArkIDError > 的子类
    error_class = ArkIDAPIError
    default_response_class = ArkIDHTTPResponse

    # 一个授权器类型集， 若其值为 None ，代表可以为任意类型的授权器
    allowed_authorizer_types = None

    # 置于请求头部，用作 `User-Agent` 属性值
    BASE_USER_AGENT = "ArkID-sdk-py-{0}".format(__version__)

    def __init__(self,
                 service: str,
                 environment: str = None,
                 base_url: str = None,
                 base_path: str = None,
                 authorizer: object = None,
                 app_name: str = None,
                 http_timeout: float = None,
                 *args,
                 **kwargs):
        self._init_logger_adapter()
        self.logger.info("正在创建访问 ArkID 官方 {} 服务的{}类型的客户端".format(service, type(self)))

        # 校验授权器
        self.check_authorizer(authorizer)

        # 若未提供 `environment` 参数值，将在配置文件中查找与 `default` 相关的章节内容
        self.environment = config.get_arkid_environ(input_env=environment)
        self.authorizer = authorizer
        self.base_url = config.get_service_url(self.environment, service) if base_url is None else base_url
        self.base_url = slash_join(self.base_url, base_path)
        self.service = service
        # 封装 < requests.Session > 对象
        self._session = requests.Session()

        # 初始化请求头部
        self._headers = {"Accept": "application/json", "User-Agent": self.BASE_USER_AGENT}

        # 是否验证 SSL，通常为 True
        self._verify = config.get_ssl_verify(self.environment)

        # 初始化 HTTP 连接超时设置
        http_timeout = config.get_http_timeout(self.environment) if http_timeout is None else http_timeout

        # 若传入的参数值为 -1 ，将其转换为 None
        self._http_timeout = http_timeout if http_timeout != -1 else None

        # 初始化调用 ArkID SDK 的项目的名称
        self.app_name = None
        if app_name is not None:
            self.set_app_name(app_name)

    def _init_logger_adapter(self):
        """
        Create & assign the self.logger LoggerAdapter.
        Used when initializing a new client.
        """
        # 获取客户端类的完全限定名， 可标识为 ArkID SDK 所有
        self.logger = ClientLogAdapter(logging.getLogger(self.__module__ + "." + self.__class__.__name__),
                                       {"client": self})

        # 初始化 console_handler ，用于在终端输出调试信息
        # 如果 console_handler 存在，则不会继续添加
        # 只在开发 SDK 期间调试使用，生产环境务必将其注释掉
        if not self.logger.logger.handlers:
            self.logger.setLevel(logging.DEBUG)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            self.logger.logger.addHandler(console_handler)

    def set_app_name(self, app_name: str):
        """
        设置一个应用名称（用户代理）并发送给 ArkID 服务端。

        注意：
            强烈建议应用开发者提供一个应用名称给 ArkID 团队，
            以便在可能的情况下促进与 ArkID 的交互问题的解决。
        :param app_name: 第三方调用者的标识名称
        :return:
        """
        self.app_name = app_name
        self._headers["User-Agent"] = "{}/{}".format(self.BASE_USER_AGENT, app_name)

    def check_authorizer(self, authorizer):
        """
        若子类重写 `allowed_authorizer_types` 参数值，需检查并确保未违背所提供的约束
        :param authorizer:
        :return:
        """
        if self.allowed_authorizer_types is not None and (authorizer is not None
                                                          and type(authorizer) not in self.allowed_authorizer_types):
            self.logger.error("'{}'客户端不支持授权器'{}'".format(type(self), type(authorizer)))
            raise ArkIDSDKUsageError("{}客户端目前仅支持'{}'中的授权器类型, 而您提供的授权器类型为{}".format(type(self),
                                                                                   self.allowed_authorizer_types,
                                                                                   type(authorizer)))

        if self.allowed_authorizer_types is not None and authorizer is None:
            self.logger.error("'{}'客户端需要有效授权器的支持".format(type(self)))
            raise ArkIDSDKUsageError("'{}'客户端需要有效授权器的支持".format(type(self)))

    def reload_service_url(self, service: str):
        """
        一些种类的客户端在有些时候调用不同的接口会使用不同的服务根
        地址，虽然这种情况出现的很少，但是仍然需要提供这样一种方式
        来方便开发者更灵活的处理服务根地址不一致的情况。

        :param service: 访问 ArkID 服务端的服务名称
        :return:
        """
        self.logger.info("{}客户端正在加载 {} 服务".format(type(self), service))
        self.base_url = config.get_service_url(self.environment, service)

    def reload_authorizer(self, authorizer):
        """
        一些种类的客户端在有些时候调用不同的接口会使用不同的授权器，
        虽然这种情况出现的很少，但是仍然需要提供这样一种方式来方便
        开发者更灵活的处理授权器不一致的情况。
        :param authorizer: 新的授权器
        :return:
        """
        self.logger.info("{}客户端正在重载加载器{} => {}".format(type(self), type(self.authorizer), type(authorizer)))
        self.check_authorizer(authorizer)
        self.authorizer = authorizer

    def get(self,
            path: str,
            params: dict = None,
            headers: dict = None,
            response_class: object = None,
            retry_401: bool = True):
        """
        Make a GET request to the specified path.
        :param path: Path for the request, with or without leading slash
        :param params: Parameters to be encoded as a query string
        :param headers: HTTP headers to add to the request
        :param response_class: Class for response object, overrides the
                client's ``default_response_class``
        :param retry_401: Retry on 401 responses with fresh Authorization
                if ``self.authorizer`` supports it
        :return: :class: < ArkIDHTTPResponse > or it's subclass object
        """
        self.logger.debug("GET to {} with params {}".format(self.base_url + path, params))
        return self._request(
            "GET",
            path,
            params=params,
            headers=headers,
            response_class=response_class,
            retry_401=retry_401,
        )

    def post(
        self,
        path: str,
        json_body: dict = None,
        params: dict = None,
        headers: dict = None,
        text_body: dict or str = None,
        response_class: object = None,
        retry_401: bool = True,
    ):
        """
        Make a POST request to the specified path.
        :param path: Path for the request, with or without leading slash
        :param json_body: Data which will be JSON encoded as the body of the request
        :param params: Parameters to be encoded as a query string
        :param headers: HTTP headers to add to the request
        :param text_body: Either a raw string that will serve as the request body, or a
                dict which will be HTTP Form encoded
        :param response_class: Class for response object, overrides the client's
                ``default_response_class``
        :param retry_401: Retry on 401 responses with fresh Authorization if
                ``self.authorizer`` supports it

        :return: :class: < ArkIDHTTPResponse > or it's subclass object
        """
        self.logger.debug("POST to {} with params {}".format(self.base_url + path, params))
        return self._request(
            "POST",
            path,
            json_body=json_body,
            params=params,
            headers=headers,
            text_body=text_body,
            response_class=response_class,
            retry_401=retry_401,
        )

    def delete(
        self,
        path: str,
        params: dict = None,
        headers: dict = None,
        response_class: object = None,
        retry_401: bool = True,
    ):
        """
        Make a DELETE request to the specified path.
        :param path: Path for the request, with or without leading slash
        :param params: Parameters to be encoded as a query string
        :param headers: HTTP headers to add to the request
        :param response_class: Class for response object, overrides the client's
                ``default_response_class``
        :param retry_401: Retry on 401 responses with fresh Authorization if
                ``self.authorizer`` supports it
        :return: :class: < ArkIDHTTPResponse > or it's subclass object
        """
        self.logger.debug("DELETE to {} with params {}".format(self.base_url + path, params))
        return self._request(
            "DELETE",
            path,
            params=params,
            headers=headers,
            response_class=response_class,
            retry_401=retry_401,
        )

    def put(
        self,
        path: str,
        json_body: dict = None,
        params: dict = None,
        headers: dict = None,
        text_body: dict or str = None,
        response_class: object = None,
        retry_401: bool = True,
    ):
        """
        Make a PUT request to the specified path.
        :param path: Path for the request, with or without leading slash
        :param json_body: Data which will be JSON encoded as the body of the request
        :param params: Parameters to be encoded as a query string
        :param headers: HTTP headers to add to the request
        :param text_body: Either a raw string that will serve as the request body, or a
                dict which will be HTTP Form encoded
        :param response_class: Class for response object, overrides the client's
                ``default_response_class``
        :param retry_401: Retry on 401 responses with fresh Authorization if
                ``self.authorizer`` supports it
        :return: :class: < ArkIDHTTPResponse > or it's subclass object
        """
        self.logger.debug("PUT to {} with params {}".format(self.base_url + path, params))
        return self._request(
            "PUT",
            path,
            json_body=json_body,
            params=params,
            headers=headers,
            text_body=text_body,
            response_class=response_class,
            retry_401=retry_401,
        )

    def patch(
        self,
        path: str,
        json_body: dict = None,
        params: dict = None,
        headers: dict = None,
        text_body: dict or str = None,
        response_class: object = None,
        retry_401: bool = True,
    ):
        """
        Make a PATCH request to the specified path.
        :param path: Path for the request, with or without leading slash
        :param json_body: Data which will be JSON encoded as the body of the request
        :param params: Parameters to be encoded as a query string
        :param headers: HTTP headers to add to the request
        :param text_body: Either a raw string that will serve as the request body, or a
                dict which will be HTTP Form encoded
        :param response_class: Class for response object, overrides the client's
                ``default_response_class``
        :param retry_401: Retry on 401 responses with fresh Authorization if
                ``self.authorizer`` supports it
        :return: :class: < ArkIDHTTPResponse > or it's subclass object
        """
        self.logger.debug("PATCH to {} with params {}".format(self.base_url + path, params))
        return self._request(
            "PATCH",
            path,
            json_body=json_body,
            params=params,
            headers=headers,
            text_body=text_body,
            response_class=response_class,
            retry_401=retry_401,
        )

    def _request(
        self,
        method: str,
        path: str,
        params: dict = None,
        headers: dict = None,
        json_body: dict = None,
        text_body: dict or str = None,
        response_class=None,
        retry_401: bool = True,
    ):
        """
        封装 requests
        :param method: HTTP request method, as an all caps string
        :param path: Path for the request, with or without leading slash
        :param params: Parameters to be encoded as a query string
        :param headers: HTTP headers to add to the request
        :param json_body: Data which will be JSON encoded as the body of the request
        :param text_body: Either a raw string that will serve as the request body, or
                a dict which will be HTTP Form encoded
        :param response_class: Class for response object, overrides the client's
                ``default_response_class``
        :param retry_401: Retry on 401 responses with fresh Authorization if
                ``self.authorizer`` supports it
        :return: :class: < ArkIDHTTPResponse > or it's subclass object
        """
        _headers = dict(self._headers)

        if headers is not None:
            _headers.update(headers)

        if json_body is not None:
            assert text_body is None
            text_body = json.dumps(json_body)
            _headers.update({"Content-Type": "application/json"})

        if self.authorizer is not None:
            self.logger.debug("正在装载'{}'类型的授权器".format(type(self.authorizer)))
            self.authorizer.set_authorization_header(_headers)

        url = slash_join(self.base_url, path)
        self.logger.debug("开始访问 URL: {}".format(url))

        # because a 401 can trigger retry, we need to wrap the retry-able thing in a method
        def send_request():
            try:
                return self._session.request(
                    method=method,
                    url=url,
                    headers=_headers,
                    params=params,
                    data=text_body,
                    verify=self._verify,
                    timeout=self._http_timeout,
                )
            except requests.RequestException as exc:
                self.logger.error("NetworkError on request")
                raise convert_request_exception(exc)

        # initial request
        response = send_request()
        self.logger.debug("收到响应 URL: {}".format(response.url))

        # potential 401 retry handling
        if response.status_code == 401 and retry_401 and self.authorizer is not None:
            self.logger.debug("request got 401, checking retry-capability")
            # note that although handle_missing_authorization returns a T/F
            # value, it may actually mutate the state of the authorizer and
            # therefore change the value set by the `set_authorization_header`
            # method
            if self.authorizer.handle_missing_authorization():
                self.logger.debug("可重新尝试访问")
                self.authorizer.set_authorization_header(_headers)
                response = send_request()

        if 200 <= response.status_code < 400:
            self.logger.debug("HTTP 请求完成 响应码: {}".format(response.status_code))
            return self.default_response_class(response, client=self) \
                if response_class is None \
                else response_class(response, client=self)

        self.logger.debug("HTTP 请求完成（错误） 响应码: {}".format(response.status_code))
        raise self.error_class(response)


def slash_join(base: str, path: str):
    """
    Join a and b with a single slash, regardless of whether they already
    contain a trailing/leading slash or neither.
    :param base: base_url
    :param path: path
    """
    if not path:    # "" or None, don't append a slash
        return base
    if base.endswith("/"):
        if path.startswith("/"):
            return base[:-1] + path
        return base + path
    if path.startswith("/"):
        return base + path
    return base + "/" + path


def reload_service(service: str):
    """
    简化客户端重载服务流程的装饰器函数
    :param service: 目标服务名称
    """
    def _wrapper(func):
        def __wrapper(*args, **kwargs):
            instance = args[0]
            _service = instance.service
            instance.reload_service_url(service)
            response = func(*args, **kwargs)
            instance.reload_service_url(_service)
            return response

        return __wrapper

    return _wrapper


def reload_authorizer(func):
    """
    简化客户端重载授权器的装饰器函数
    :param func: 客户端功能接口
    """
    def _wrapper(*args, **kwargs):
        instance = args[0]
        _authorizer = instance.authorizer
        instance.reload_authorizer(args[1])
        response = func(*args, **kwargs)
        instance.reload_authorizer(_authorizer)
        return response

    return _wrapper
