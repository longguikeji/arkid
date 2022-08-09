# 认证规则: 认证失败次数限制
## 功能介绍

在用户超出限制认证失败次数后，对用户认证凭证表单进行扩充，插入次级认证因素，并在用户再次发起认证请求时进行次级认证因素校验

## 前置条件

认证失败次数限制规则插件中需要至少一个主认证因素插件和一个次认证因素插件支持，主认证因素即为拥有登录/注册/重置密码等主要功能的认证因素，次认证因素为主认证因素通过认证规则限制对认证过程进行补充，此处以用户名密码认证因素与图形验证码认证因素为例。

## 配置指南

=== "插件租赁"
    经由左侧菜单栏依次进入【租户管理】->【插件管理】，在插件租赁页面中找到认证次数限制规则插件卡片，点击租赁
    [![vEbUde.png](https://s1.ax1x.com/2022/08/02/vEbUde.png)](https://imgtu.com/i/vEbUde)

=== "认证规则配置"
    经由左侧菜单栏依次进入【认证管理】-> 【认证规则】,点击创建按钮，类型选择"retry_times",主认证因素选择默认密码认证因素，次认证因素选择默认的图形验证码认证因素，至此配置完成
    [![vEb7LT.md.png](https://s1.ax1x.com/2022/08/02/vEb7LT.md.png)](https://imgtu.com/i/vEb7LT)

=== "登陆界面"
    配置完成后，当用户进入登陆界面并重复失败三次后，页面会刷新并启用图形验证码
    [![vEqeSI.png](https://s1.ax1x.com/2022/08/02/vEqeSI.png)](https://imgtu.com/i/vEqeSI)

## 实现思路

* 认证规则: 认证失败次数限制：

```mermaid
sequenceDiagram
    participant D as 用户
    participant C as 平台核心
    participant A as 认证失败次数限制规则插件
    
    C->>A: 加载插件
    A->>C: 注册并监听事件CREATE_LOGIN_PAGE_RULES,AUTH_FAIL,BEFORE_AUTH
    D->>C: 访问注册/登录/重置密码页面
    C->>A: 发出CREATE_LOGIN_PAGE_RULES事件
    A->>C: 响应事件,判断是否满足规则,如满足规则即触发AUTHRULE_FIX_LOGIN_PAGE事件
    C->>D: 渲染注册/登录/重置密码页面
    D->>C: 输入认证凭证，发起认证请求
    C->>A: 触发BEFORE_AUTH事件
    A->>C: 响应事件,判断是否满足规则，如满足规则即触发AUTHRULE_CHECK_AUTH_DATA事件，检查并返回结果
    C->>A: 检查结果,如未完成认证，触发AUTH_FAIL事件
    A->>C: 响应事件,记录失败次数并判断是否刷新页面
    C->>D: 根据返回结果渲染或刷新页面

```

## 抽象方法实现

* [load](#extension_root.com_longgui_auth_rule_retry_times.AuthRuleRetryTimesExtension.load)
* [check_rule](#extension_root.com_longgui_auth_rule_retry_times.AuthRuleRetryTimesExtension.authenticate)

## 代码

::: extension_root.com_longgui_auth_rule_retry_times.AuthRuleRetryTimesExtension
    rendering:
        show_source: true

