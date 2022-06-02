# Github 第三方登录插件

## 功能介绍
配置Github插件后，可以点击ArkID登录页面的Github图标，跳转到Github网站完成Oauth2认证，并和ArkID的用户绑定

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