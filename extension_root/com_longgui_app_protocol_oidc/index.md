# OAuth2与OIDC应用协议

本插件提供两类协议： **OAuth2** 与 **OIDC**

## OIDC

###一、首先在OIDC认证中心添加OIDC应用

参考：https://www.yuque.com/longguikeji/arkid2/cfykt1

注意：Userinfo的接口为  xxx/oauth/userinfo/ !!

###二、jenkins 安装插件，OpenId Connect Authentication

###三、配置jenkins安全认证
系统管理 -- 全局安全配置 -- Login with Openid Connect

自动配置

手动配置

Logout from OpenID Provider 
● End session URL for OpenID Provider : 填写Logout的url

● Post logout redirect URL：填jenkins的访问地址

## OAuth2

### 第一步，在插件中心添加oAuth插件

### 第二步，在应用中心添加oAuth应用

### 第三步，在添加arkid第三方登录(可选，适用于需要在租户登录页显示)

可以将创建成功后的callback url填回oAuth应用界面

## 以下为接口说明(针对不接入租户登录页的情况)

### 授权
请求地址:
https://IP:PORT/api/v1/app/APP_ID/tenant/TENANT_UUID/oauth/authorize/

请求参数:

返回参数:

### 获取access_token
请求地址:https://IP:PORT/api/v1/tenant/TENANT_UUID/oauth/token/

请求参数:

返回参数:

{
    "access_token":"n6mxPgxuU81EzgtGDaWid1KSsMpFcO",
    "expires_in":36000,
    "token_type":"Bearer",
    "scope":"openid userinfo",
    "refresh_token":"EqDjsYxbOHVrk0jL24jeTKvlziN7or",
    "id_token":"eyJhbGciOiAiUlMyNTYifQ.eyJhdWQiOiAiYW1tQjFWblVNSExsNmt2QkJCa1pOWGlRa3lSOHVYeVlSNHF6WGhPVSIsICJpYXQiOiAxNjM0NzE5OTA4LCAiYXRfaGFzaCI6ICI1WWRuS3BqeTBqcnJpSGdYN1VZVWVnIiwgInN1YiI6ICIxIiwgImlzcyI6ICJodHRwOi8vbG9jYWxob3N0OjgwMDAvYXBpL3YxL3RlbmFudC8zZWZlZDRkOS1mMmVlLTQ1NWUtYjg2OC02ZjYwZWE4ZmRmZjYiLCAiZXhwIjogMTYzNDc1NTkwOCwgImF1dGhfdGltZSI6IDE2MzQ3MTk5MDd9.KrrptiXZ_yE7_Uvpp4TWUe-Oi_i2CH_JWxUJ2U1_rCYKYcwcynz0QwxoLbRZWkkYxpjyFwOpOADWY_AHOyU26L76k2lJDJznrwsvotP-HnWfI_TNWctEXUWx-e7vVu8uGID9PWuxu2WPm028gdPHFlPONnU8NIFiSRIV3u70O4w"
}

### 获取用户信息
请求地址:https://IP:PORT/api/v1/tenant/TENANT_UUID/oauth/userinfo/

请求参数:

返回参数:

{
"id": 1,
"name": "admin",
"email": "insfocus@gmail.com"
}

### 刷新token
请求地址:https://IP:PORT/api/v1/tenant/TENANT_UUID/oauth/token/

请求参数:

返回参数:

{
	"access_token":"NlFFWj0g4e9tpsDGrQ56LJRimSSay0",
       "expires_in":36000,
       "token_type":"Bearer",
       "scope":"userinfo",
       "refresh_token":"pZ9QPc4DNE5F84wmSg3KgkDxmzFPuN"
}

### 退出oidc
请求地址:https://IP:PORT/api/v1/tenant/TENANT_UUID/oidc/logout/

请求参数:

返回参数:
{
    "error_code":0,
    "error_msg":"logout success"
}
