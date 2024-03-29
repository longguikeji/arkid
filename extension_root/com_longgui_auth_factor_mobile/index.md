# 手机验证码认证因素
## 功能介绍

对用户表扩展手机号码字段，允许用户通过手机号码与验证码的方式进行认证，注册，重置密码以及更换手机号。

普通用户：

* 在 “注册” 页面实现手机号码+验证码用户注册
* 在 “登录” 页面实现手机号码+验证码用户登录
* 在 “更改密码” 页面实现手机号码+验证码方式下密码更改
* 在 “我的 - 认证管理“ 中添加重置手机号码的功能

租户管理员

* 在”用户管理 - 用户列表“中编辑页面添加手机号码编辑功能

## 前置条件

需配合短信插件使用，系统已默认提供阿里云短信插件，如需查看配置方法请移步阿里云短信插件文档。

## 配置指南

=== "插件租赁"
    经由左侧菜单栏依次进入【租户管理】->【插件管理】，在插件租赁页面中找到手机验证码认证因素插件卡片，点击租赁
    [![vEcwwV.png](https://s1.ax1x.com/2022/08/02/vEcwwV.png)](https://imgtu.com/i/vEcwwV)

=== "认证因素配置"
    经由左侧菜单栏依次进入【认证管理】-> 【认证因素】,点击创建按钮，类型选择"mobile",短信插件运行时选择一个合适的已配置的短信插件运行时配置，至此配置完成<br/>
    [![vE2VKA.md.png](https://s1.ax1x.com/2022/08/02/vE2VKA.md.png)](https://imgtu.com/i/vE2VKA)

=== "登录界面"
    [![vE2hGD.png](https://s1.ax1x.com/2022/08/02/vE2hGD.png)](https://imgtu.com/i/vE2hGD)

=== "注册界面"
    [![vE25xH.md.png](https://s1.ax1x.com/2022/08/02/vE25xH.md.png)](https://imgtu.com/i/vE25xH)

=== "密码修改界面"
    [![vE2TsA.png](https://s1.ax1x.com/2022/08/02/vE2TsA.png)](https://imgtu.com/i/vE2TsA)

=== "更换手机号码界面"
    由用户头像菜单进入【认证管理】界面,选择更改手机号码标签页<br/>
    [![vE20GF.md.png](https://s1.ax1x.com/2022/08/02/vE20GF.md.png)](https://imgtu.com/i/vE20GF)

## 实现思路

* 普通用户：手机号码+验证码用户注册/登录/重置密码：

```mermaid
sequenceDiagram
    participant D as 用户
    participant C as 平台核心
    participant A as 手机验证码认证因素插件
    participant B as 短信插件
    
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

* 普通用户：重置手机号码：

```mermaid
sequenceDiagram
    participant D as 用户
    participant C as 平台核心
    participant A as 手机验证码认证因素插件
    participant B as 短信插件
    
    C->>A: 加载插件
    A->>C: 向“我的 - 认证管理“ 页面中添加重置手机号码元素，向核心注册重置手机号码接口
    C->>B: 加载插件
    B->>C: 监听短信事件
    D->>C: 访问“我的 - 认证管理“ 页面中重置手机号码功能
    D->>A: 输入手机号码，点击【发送短信】按钮，访问短信发送接口
    A->>B: 生成短信验证码，发出SEND_SMS事件
    B->>A: 响应事件，发出短信
    A->>D: 返回短信发送结果
    D->>C: 输入验证码信息，点击【确认】按钮
    C->>A: 访问重置手机号码接口
    A->>C: 响应接口，检查输入参数，返回结果
    C->>D: 检查结果，并提示是否完成更改

```

* 管理员用户： 更换用户手机号码

```mermaid
sequenceDiagram
    participant D as 用户
    participant C as 平台核心
    participant A as 手机验证码认证因素插件
    
    C->>A: 加载插件
    A->>C: 向“用户列表-编辑用户”页面注入手机号码元素
    D->>C: 管理员登录，访问用户列表页面，编辑用户手机号码并保存
    C->>D: 写入数据至数据库

```

## 抽象方法实现
* [load](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.load)
* [authenticate](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.authenticate)
* [register](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.register)
* [reset_password](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.reset_password)
* [create_login_page](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.create_login_page)
* [create_register_page](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.create_register_page)
* [create_password_page](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.create_password_page)
* [create_other_page](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.create_other_page)
* [create_auth_manage_page](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.create_auth_manage_page)
* [check_auth_data](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.check_auth_data)
* [fix_login_page](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.fix_login_page)

## 代码

::: extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension
    rendering:
        show_source: true

::: extension_root.com_longgui_auth_factor_mobile.sms
    rendering:
        show_source: true


