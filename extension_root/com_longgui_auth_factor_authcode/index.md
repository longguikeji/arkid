# 图形验证码认证因素
## 功能介绍

对用户认证凭证表单进行扩充，插入图形验证码并实现相关验证功能

<b>注意：图形验证码认证因素不具有认证/注册/修改密码等功能，仅对其他认证因素进行凭证元素扩充</b>

普通用户：

* 在 “登录” 页面实现向指定表单插入图形验证码

## 配置指南

=== "插件租赁"
    经由左侧菜单栏依次进入【租户管理】->【插件管理】，在插件租赁页面中找到图形验证码认证因素插件卡片，点击租赁
    [![vEHa3q.png](https://s1.ax1x.com/2022/08/02/vEHa3q.png)](https://imgtu.com/i/vEHa3q)

=== "租户配置"
    租赁完成后，进入已租赁列表，找到图形验证码认证因素插件卡片，点击租户配置，配置相关数据
    [![vEbAx0.md.png](https://s1.ax1x.com/2022/08/02/vEbAx0.md.png)](https://imgtu.com/i/vEbAx0)
    
=== "认证因素配置"
    经由左侧菜单栏依次进入【认证管理】-> 【认证因素】,点击创建按钮，类型选择"authcode"， 无须配置相关参数，至此配置完成
    [![vEbpVg.md.png](https://s1.ax1x.com/2022/08/02/vEbpVg.md.png)](https://imgtu.com/i/vEbpVg)

## 实现思路

* 普通用户：图形验证码：

```mermaid
sequenceDiagram
    participant D as 用户
    participant C as 平台核心
    participant A as 图形验证码认证因素插件
    
    C->>A: 加载插件
    A->>C: 注册并监听事件AUTHRULE_FIX_LOGIN_PAGE,AUTHRULE_CHECK_AUTH_DATA
    D->>C: 访问注册/登录/重置密码页面
    C->>A: 发出AUTHRULE_FIX_LOGIN_PAGE事件
    A->>C: 响应事件,向注册/登录/重置密码页面注入元素
    C->>D: 渲染注册/登录/重置密码页面
    D->>C: 输入认证凭证，发起认证请求
    C->>A: 触发认证凭证检查事件AUTHRULE_CHECK_AUTH_DATA
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
* [check_auth_data](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.check_auth_data)
* [fix_login_page](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.fix_login_page)

## 代码

::: extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension
    rendering:
        show_source: true

