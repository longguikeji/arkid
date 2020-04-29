.. _clients:

服务客户端
=========

ArkID Client 提供了一个封装了 ArkID 所有的 API 接口的客户端类。您无需进行任何配置，
只需要在初始化客户端实例的时候，
向其添加 ArkID 服务的根地址以及必要的认证授权器 :ref:`ArkIDAuthorizers <authorization>` ；
在客户端创建成功之后，您就可以使用顶层的接口来调用 ArkID 的各项服务而无需知道
ArkID 的各端点地址或者详细的参数。

.. rubric:: 客户端类型

.. toctree::
   clients/auth
   clients/user
   clients/org
   clients/node
   clients/arkid
   clients/base


