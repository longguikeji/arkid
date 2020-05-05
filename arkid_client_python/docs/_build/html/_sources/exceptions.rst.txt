异常处理
==========

所有的 ARKID Client 错误都继承自 ``ArkIDError``，
所有 SDK 错误类型均可从 ``arkid_client`` 导入。
因此，您可以通过 ``ArkIDError`` 来捕获 ARKID Client 抛出的*所有*错误,
例如 ::

    import logging
    from arkid_client import UserClient, ArkIDError

    try:
        uc = UserClient(...)
        # create with no parameters will throw an exception
        user = uc.create_user()
    except ArkIDError:
        logging.exception("ArkID Error!")
        raise

在大多数情况下，最好查找 ``ArkIDError`` 的特定子类。
比如，想要区分网络故障和意外的 API 条件，
您需要通过 ``NetworkError`` 和 ``ArkIDAPIError`` 来定位问题所在::

    import logging
    from arkid_client import (UserClient,
                              ArkIDError, ArkIDAPIError, NetworkError)

    try:
        uc = UserClient(...)
        users = uc.query_user()

        for user in users:
            print(user['name'])

        ...
    except ArkIDAPIError as e:
        # Error response from the REST service, check the code and message for details.
        logging.error(("Got a ArkID API Error\n"
                       "Error Code: {}\n"
                       "Error Message: {}").format(e.code, e.message))
        raise e
    except NetworkError:
        logging.error(("Network Failure. "
                       "Possibly a firewall or connectivity issue"))
        raise
    except ArkIDError:
        logging.exception("Totally unexpected ArkIDError!")
        raise
    else:
        ...

当然，如果您想要了解更多关于响应的信息，您要做的不仅仅只有这些。

由 ArkID SDK 引起的所有错误都应该是 ``ArkIDError`` 的实例。
对 ArkID Client 方法的错误调用通常会引发 ``ArkIDSDKUsageError`` ，
但是，在极少数情况下，可能会引发标准的 python 异常( ``ValueError`` , ``OSError`` 等)


错误类型
-----------

.. autoclass:: arkid_client.ArkIDError
   :members:
   :show-inheritance:

.. autoclass:: arkid_client.ArkIDSDKUsageError
   :members:
   :show-inheritance:

.. autoclass:: arkid_client.ArkIDAPIError
   :members:
   :show-inheritance:

.. autoclass:: arkid_client.AuthAPIError
   :members:
   :show-inheritance:

.. autoclass:: arkid_client.exceptions.UserAPIError
   :members:
   :show-inheritance:

.. autoclass:: arkid_client.exceptions.OrgAPIError
   :members:
   :show-inheritance:

.. autoclass:: arkid_client.exceptions.NodeAPIError
   :members:
   :show-inheritance:

.. autoclass:: arkid_client.NetworkError
   :members:
   :show-inheritance:

.. autoclass:: arkid_client.ArkIDConnectionError
   :members:
   :show-inheritance:

.. autoclass:: arkid_client.ArkIDTimeoutError
   :members:
   :show-inheritance:

.. autoclass:: arkid_client.ArkIDConnectionTimeoutError
   :members:
   :show-inheritance:
