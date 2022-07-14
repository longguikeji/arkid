# 图形验证码认证因素
## 功能介绍

对用户认证凭证表单进行扩充，插入图形验证码并实现相关验证功能

<b>注意：图形验证码认证因素不具有认证/注册/修改密码等功能，仅对其他认证因素进行凭证元素扩充</b>

普通用户：

* 在 “登录” 页面实现向指定表单插入图形验证码

## 配置指南

## 实现思路

* 普通用户：图形验证码：
```mermaid
sequenceDiagram
    participant D as 用户
    participant C as 平台核心
    participant A as 图形验证码认证因素插件
    
    C->>A: 加载插件
    A->>C: 注册并监听事件[AUTHRULE_FIX_LOGIN_PAGE]('/%20%20开发者指南/参考文档/事件列表/),[AUTHRULE_CHECK_AUTH_DATA]('/%20%20开发者指南/参考文档/事件列表/)
    D->>C: 访问注册/登录/重置密码页面
    C->>A: 发出AUTHRULE_FIX_LOGIN_PAGE事件
    A->>C: 响应事件,向注册/登录/重置密码页面注入元素
    C->>D: 渲染注册/登录/重置密码页面
    D->>C: 输入认证凭证，发起认证请求
    C->>A: 触发认证凭证检查事件
    A->>C: 响应事件，完成认证凭证检查，返回结果
    C->>D: 检查结果，如完成注册/登录相关操作则生成token并跳转至桌面，如完成重置密码操作或者未完成注册/登录操作则提示错误

```
## 抽象方法实现
* [load](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.load)
* [authenticate](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.authenticate)
* [register](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.register)
* [reset_password](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.reset_password)
* [create_login_page](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.create_login_page)
* [create_register_page](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.create_register_page)
* [create_password_page](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.create_password_page)
* [create_other_page](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.create_other_page)
* [create_auth_manage_page](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.create_auth_manage_page)

## 代码

::: extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension
    rendering:
        show_source: true

