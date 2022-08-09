# 密码认证因素
## 功能介绍

对用户表扩展密码字段，允许用户通过用户名与密码的方式进行认证，注册。

普通用户：

* 在 “我的 - 认证管理“ 中添加重置密码的功能
* 在 “注册” 页面实现用户名密码注册
* 在 “登录” 页面实现用户名密码登录

租户管理员

* 在”用户管理 - 用户列表“中添加重置密码的功能

## 配置指南
## 配置指南

=== "插件租赁"
    经由左侧菜单栏依次进入【租户管理】->【插件管理】，在插件租赁页面中找到密码认证因素插件卡片，点击租赁
    [![vEoE7j.png](https://s1.ax1x.com/2022/08/02/vEoE7j.png)](https://imgtu.com/i/vEoE7j)

=== "认证因素配置"
    经由左侧菜单栏依次进入【认证管理】-> 【认证因素】,点击创建按钮，类型选择"password",填入相关信息，至此配置完成
    [![vEoU9x.md.png](https://s1.ax1x.com/2022/08/02/vEoU9x.md.png)](https://imgtu.com/i/vEoU9x)

=== "登录界面"
    [![vEoWgf.md.png](https://s1.ax1x.com/2022/08/02/vEoWgf.md.png)](https://imgtu.com/i/vEoWgf)

=== "注册界面"
    [![vEoXvT.png](https://s1.ax1x.com/2022/08/02/vEoXvT.png)](https://imgtu.com/i/vEoXvT)

=== "更改密码界面"
    由用户头像菜单进入【认证管理】界面,选择更改密码标签页
    [![vEo6UA.md.png](https://s1.ax1x.com/2022/08/02/vEo6UA.md.png)](https://imgtu.com/i/vEo6UA)

## 实现思路

普通用户：注册/登录：

```mermaid
sequenceDiagram
    participant D as 用户
    participant C as 平台核心
    participant A as 密码认证因素插件
    
    C->>A: 加载插件
    A->>C: 注册并监听密码认证相关事件（注册/登录等）
    D->>C: 访问注册/登录页面
    C->>A: 发出CREATE_LOGIN_PAGE_AUTH_FACTOR事件
    A->>C: 响应事件，组装注册/登录页面元素
    C->>D: 渲染注册/登录/重置密码页面
    D->>C: 输入相关信息，点击【注册/登录】按钮
    C->>A: 发出注册/登录事件
    A->>C: 响应事件，完成注册/登录流程，返回结果
    C->>D: 检查结果，如完成注册/登录相关操作则生成token并跳转至桌面，如未完成注册/登录操作则提示错误

```

普通用户：重置密码：

```mermaid
sequenceDiagram
    participant D as 用户
    participant C as 平台核心
    participant A as 密码认证因素插件
    
    C->>A: 加载插件
    A->>C: 向“我的 - 认证管理“ 页面中添加重置密码元素，向核心注册重置密码接口
    D->>C: 访问“我的 - 认证管理“ 页面中重置密码功能，录入新的密码
    C->>A: 访问重置密码接口
    A->>C: 响应接口，检查输入参数，返回结果
    C->>D: 检查结果，并提示是否完成更改

```

管理员用户： 重置用户密码

```mermaid
sequenceDiagram
    participant D as 用户
    participant C as 平台核心
    participant A as 密码认证因素插件
    
    C->>A: 加载插件
    A->>C: 向“用户列表-编辑用户”页面注入密码元素，向核心用户模型注入密码字段
    D->>C: 管理员登录，访问用户列表页面，编辑用户密码，点击保存
    C->>D: 修改密码字段值并保存至数据库
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

::: extension_root.com_longgui_auth_factor_password.PasswordAuthFactorExtension
    rendering:
        show_source: true

