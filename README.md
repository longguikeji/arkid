# 一账通

**V2 版本**是我们目前主力研发的版本，请移步：https://github.com/longguikeji/arkid/tree/v2-dev

V1 为稳定版本，并处在积极维护中，定期port v2的feature到v1中

ArkID是全新一代企业单点登录解决方案, 彻底告别企业内多系统多账号的烦恼, 节省管理成本, 自带功能全面的WEB管理界面，提升管理效率。

更多细节参见 [docs.arkid.longguikeji.com](https://www.yuque.com/longguikeji/arkid/)

## 功能特性

### 兼容各种常见协议, 让每个应用都可以连接

1. LDAP
2. OAuth 2.0
3. OpenID Connect
4. SAML 2.0
5. HTTP API

### 丰富的账号与分组管理

1. 灵活高效的管理企业内部账号与分组
2. 支持一键钉钉导入

### 完备的权限管理

细粒度的权限管理，让企业没有管理不到的权限

1. 账号权限
2. 分组权限
3. 应用白名单，黑名单
4. 应用内权限

### 工作台(Workspace)

每位员工均拥有自己的工作台，一键访问业务系统

### 自定义登陆UI

名称、LOGO、主题色，让登陆页面彰显企业文化

## 项目说明

- [arkid-frontend](https://github.com/longguikeji/arkid-frontend): 前端代码
- [arkid-core](https://github.com/longguikeji/arkid-core): 后端核心以及其他
- [arkid-broker](https://github.com/longguikeji/arkid-broker): 一账通部署在ArkOS中的服务Broker

## DEMO

https://arkid.demo.longguikeji.com

```
用户名: admin
密码: longguikeji
```

## 文档

- [完整文档](https://www.yuque.com/longguikeji/arkid/)
- [接口文档](https://oneid1.docs.apiary.io/#)

## 部署

我们推荐基于Kubernetes的环境部署，官方helm charts参考: [Charts](https://github.com/longguikeji/arkid-charts)


## Issues

请通过[Github Issues](https://github.com/longguikeji/arkid-core/issues)给我们提交问题

## Changelog

[Release Notes](https://github.com/longguikeji/arkid-core/releases)


## Contact

- [Website](https://www.longguikeji.com)
- 技术交流 QQ 群 （167885406）

## License

[LGPL-3.0](https://opensource.org/licenses/LGPL-3.0)

Copyright (c) 2019-present, 北京龙归科技有限公司

正在招聘，欢迎简历： hr@longguikeji.com
