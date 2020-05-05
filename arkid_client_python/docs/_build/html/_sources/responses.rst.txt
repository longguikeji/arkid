.. _responses:

接口响应
===========

如果没有另作说明，ArkID SDk 客户端的所有方法的返回值都是 ``ArkIDResponse`` 对象。
一些 ``ArkIDResponse`` 对象是可迭代的，在这些情况下，
它们的内容也是 ``ArkIDResponse`` 对象。

在调用ArkID 服务的接口时，使用的返回对象为 ``ArkIDResponse`` 的子类型 ``ArkIDHTTPResponse``，
它丰富了一些自定义数据信息的细节。

泛型响应类
-------------

.. autoclass:: arkid_client.response.ArkIDResponse
   :members:

.. autoclass:: arkid_client.response.ArkIDHTTPResponse
   :members:
   :show-inheritance:
