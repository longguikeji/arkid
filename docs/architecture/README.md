# 架构设计

ArkID 后端整体基于 Django 开发。异步任务通过 celery 实现。
接口绝大部分基于 django-rest-framework 实现。

## 核心数据模型

用户(`oneid_meta.models.User`)对应一个账号。

部门(`oneid_meta.models.Dept`), 组(`oneid_meta.models.Group`)都是节点的一种特化，在抽象层面完全一致。

节点是树状结构，可以包含 0 至多个子节点。除根节点无父节点外，其他所有节点都有一个父节点。
用户可以属于 0 至多个任意节点。

ArkID 管理的核心内容就是用户与节点之间、节点与节点之间的关系。

## 应用

应用(`oneid_meta.models.APP`)一方面可以作为各种认证协议的客户端，是各种认证方式的载体。

另一方面也是权限的载体。所谓权限，是应用内的权限。

## 权限

权限(`oneid_meta.models.Perm`)可以分发给节点、个人。个人可以从所在节点继承权限。

## 认证

1. 其他应用如何通过 ArkID 登陆

ArkID 作为 ID Provider，除基本的HTTP认证方式外，可以通过以下认证方式向其他应用提供自己维护的账号信息：

- LDAP (`ldap`)
- SAML (`djangosaml2idp`)
- OAuth2.0, OIDC (`oauth2_provider`)

2. ArkID 如何通过其他应用登陆 (`siteapi/v1/views/qr.py`)

在登录 ArkID 时，除了基本的输入 ArkID 账号密码外，可以通过向以下 ID Provider 请求授权进而登陆：

- QQ
- 微信
- 企业微信
- 钉钉
- 支付宝
