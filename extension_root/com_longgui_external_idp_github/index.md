# Github 第三方登录插件

## 功能介绍
配置Github插件后，可以点击ArkID登录页面的Github图标，跳转到Github网站完成Oauth2认证，并和ArkID的用户绑定

### 创建Github应用

=== "打开创建Github开发者设置页面"
    [![X7Ew38.png](https://s1.ax1x.com/2022/06/16/X7Ew38.png)](https://imgtu.com/i/X7Ew38)

=== "点击创建，填写表单"
    名称，主页URL和回调URL可以随意填写，回调URL后面步骤中会更改成ArkID自动生成的URL。
    [![X7E0gS.png](https://s1.ax1x.com/2022/06/16/X7E0gS.png)](https://imgtu.com/i/X7E0gS)

=== "生成Client Secret"
    [![X7EruQ.png](https://s1.ax1x.com/2022/06/16/X7EruQ.png)](https://imgtu.com/i/X7EruQ)

=== "保存Client ID和Client Secret"
    [![X7EBjg.png](https://s1.ax1x.com/2022/06/16/X7EBjg.png)](https://imgtu.com/i/X7EBjg)

### 创建ArkID第三方登录配置,获取回调URL

=== "打开第三方认证页面"
    [![X7Ef3T.png](https://s1.ax1x.com/2022/06/16/X7Ef3T.png)](https://imgtu.com/i/X7Ef3T)

=== "填写表单参数， 点击创建"
    [![X7E4vF.png](https://s1.ax1x.com/2022/06/16/X7E4vF.png)](https://imgtu.com/i/X7E4vF)

=== "点击编辑按钮，获取ArkID回调URL"
    [![X7EhgU.png](https://s1.ax1x.com/2022/06/16/X7EhgU.png)](https://imgtu.com/i/X7EhgU)

### 更新Github应用回调URL，点击登录按钮

=== "重新设置Github应用回调URL"
    [![X7EWCV.png](https://s1.ax1x.com/2022/06/16/X7EWCV.png)](https://imgtu.com/i/X7EWCV)


=== "点击登录页面Github图标"
    [![X7V4it.png](https://s1.ax1x.com/2022/06/16/X7V4it.png)](https://imgtu.com/i/X7V4it)

=== "点击认证按钮"
    [![X7VfII.png](https://s1.ax1x.com/2022/06/16/X7VfII.png)](https://imgtu.com/i/X7VfII)
    
## 实现思路
需要覆盖插件基类的抽象方法，插件基类见[arkid.core.extension.extrnal_idp.ExternalIdpExtension](/%20%20开发者指南/%20插件分类/第三方登录/)

## 抽象方法实现:
* [get_img_url](#extension_root.com_longgui_external_idp_github.ExternalIdpGithubExtension.get_img_url)
* [get_authorize_url](#extension_root.com_longgui_external_idp_github.ExternalIdpGithubExtension.get_authorize_url)
* [get_ext_token_by_code](#extension_root.com_longgui_external_idp_github.ExternalIdpGithubExtension.get_ext_token_by_code)
* [get_user_info_by_ext_token](#extension_root.com_longgui_external_idp_github.ExternalIdpGithubExtension.get_user_info_by_ext_token)
* [get_arkid_user](#extension_root.com_longgui_external_idp_github.ExternalIdpGithubExtension.get_arkid_user)


## 代码

::: extension_root.com_longgui_external_idp_github.ExternalIdpGithubExtension
    rendering:
        show_source: true