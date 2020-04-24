import abc
import six


@six.add_metaclass(abc.ABCMeta)
class ArkIDAuthorizer(object):
    """
    授权器基类，用于生成有效的授权头部。
    支持处理无效的的授权头部。
    """

    @abc.abstractmethod
    def set_authorization_header(self, header_dict: dict):
        """
        获取 HTTP 请求头部的 dict 数据，并将 `{"Authorization": "..."}` 形式的
        授权信息加入其中。
        注意：
            若 `Authorization` 授权信息已经设置，则此方法将会覆盖原来的授权信息。
        """

    def handle_missing_authorization(self, *args, **kwargs):
        """
        若 HTTP 请求使用此授权器进行访问时出现 401 （ HTTP 请求未经授权）响应，
        若授权器可以采取某些措施补救这种情况，其将会更新状态并返回 True；
        若授权器针对这种情况无能为力，其也许会更新一些操作，但是更重要的是，会
        返回 False。

        默认情况下，总是返回 False ，不采取任何操作。
        """
        return False
