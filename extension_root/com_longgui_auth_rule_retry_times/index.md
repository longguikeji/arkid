# 认证规则: 认证失败次数限制
## 功能介绍

在用户超出限制认证失败次数后，对用户认证凭证表单进行扩充，插入次级认证因素，并在用户再次发起认证请求时进行次级认证因素校验

## 配置指南

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

