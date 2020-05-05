.. _authorization:

API 认证
==========

针对 ArkID Client 的授权操作，目前仅支持 ``用户名`` + ``密码`` 的形式，
但是这样的授权流程对于用户的隐私信息是不安全的，
所以在后续的 ArkID Client开发中，
我们也许会引入 oauth2.0 或者 OIDC 相关的授权协议来加固 ArkID Client。

授权器基类
------------

``ArkIDAuthorizer`` 为一个授权器的抽象基类

.. autoclass:: arkid_client.authorizers.base.ArkIDAuthorizer
    :members:
    :member-order: bysource

授权器类型
------------

以下所有类型的授权器均可从 ``arkid_client.authorizers`` 导入

.. autoclass:: arkid_client.NullAuthorizer
    :members:
    :member-order: bysource
    :show-inheritance:

.. autoclass:: arkid_client.BasicAuthorizer
    :members:
    :member-order: bysource
    :show-inheritance:
