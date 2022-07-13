# 图片验证码认证因素
## 功能介绍

对用户认证凭证表单进行扩充，插入图片验证码并实现相关验证功能

<b>注意：图片验证码认证因素不具有认证/注册/修改密码等功能，仅对其他认证因素进行凭证元素扩充</b>

普通用户：

* 在 “登录” 页面实现向指定表单插入图片验证码

## 配置指南

## 实现思路

* 普通用户：图片验证码：
```mermaid
sequenceDiagram
    participant D as 用户
    participant C as 平台核心
    participant A as 图片验证码认证因素插件
    
    C->>A: 加载插件
    A->>C: 注册并监听手机验证码相关事件（注册/登录/重置密码等）
    C->>B: 加载插件
    B->>C: 监听短信事件
    D->>C: 访问注册/登录/重置密码页面
    C->>A: 发出CREATE_LOGIN_PAGE_AUTH_FACTOR事件
    A->>C: 响应事件，组装注册/登录/重置密码页面元素
    C->>D: 渲染注册/登录/重置密码页面
    D->>A: 输入手机号码，点击【发送短信】按钮，访问短信发送接口
    A->>B: 生成短信验证码，发出SEND_SMS事件
    B->>A: 响应事件，发出短信
    A->>D: 返回短信发送结果
    D->>C: 输入相关信息，点击【注册/登录/重置密码】按钮
    C->>A: 发出注册/登录/重置密码事件
    A->>C: 响应事件，完成注册/登录/重置密码流程，返回结果
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

