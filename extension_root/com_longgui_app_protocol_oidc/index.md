# OAuth2与OIDC应用协议

本插件提供两类协议： **OAuth2** 与 **OIDC**

## OIDC

###一、首先在OIDC认证中心添加OIDC应用

参考：https://www.yuque.com/longguikeji/arkid2/cfykt1
![](https://cdn.nlark.com/yuque/0/2021/png/12498678/1622275083990-943e6373-0fe0-439c-b687-85c7b7c7afcb.png?x-oss-process=image%2Fresize%2Cw_750%2Climit_0)

注意：Userinfo的接口为  xxx/oauth/userinfo/ !!

###二、jenkins 安装插件，OpenId Connect Authentication
![](https://cdn.nlark.com/yuque/0/2021/png/12498678/1618989070356-17907ecd-9508-4526-87f6-2c963e267234.png?x-oss-process=image%2Fresize%2Cw_750%2Climit_0)

###三、配置jenkins安全认证
系统管理 -- 全局安全配置 -- Login with Openid Connect
![](https://cdn.nlark.com/yuque/0/2021/png/12498678/1618989322496-84a6abd1-cb25-4efe-bab1-37f6d62680a9.png?x-oss-process=image%2Fresize%2Cw_1130%2Climit_0)

自动配置
![](https://cdn.nlark.com/yuque/0/2022/png/12498678/1641353495682-fe1f4965-6b29-4f03-99a9-eee3b5ef1e4f.png?x-oss-process=image%2Fresize%2Cw_750%2Climit_0)

手动配置
![](https://cdn.nlark.com/yuque/0/2021/png/12498678/1622275020692-6a32ea82-37f9-40a7-b721-90aeeab14798.png?x-oss-process=image%2Fresize%2Cw_750%2Climit_0)

Logout from OpenID Provider 
● End session URL for OpenID Provider : 填写Logout的url
![](https://cdn.nlark.com/yuque/0/2021/png/12498678/1626364028615-c6a10c0b-34a8-4cb4-9979-fad1975d244e.png?x-oss-process=image%2Fresize%2Cw_807%2Climit_0)

● Post logout redirect URL：填jenkins的访问地址
![](https://cdn.nlark.com/yuque/0/2021/png/12498678/1626363896256-911c2344-1fe3-4ced-8f16-1337f8f699a8.png?x-oss-process=image%2Fresize%2Cw_750%2Climit_0)
![](https://cdn.nlark.com/yuque/0/2021/png/12498678/1619154921110-c03fbbdc-a4f3-4887-b022-b49cc7921827.png)

## OAuth2

### 第一步，在插件中心添加oAuth插件
![](https://cdn.nlark.com/yuque/0/2021/png/21376338/1632394737154-c1483edf-979c-4d5d-a75e-0d8a6a16927b.png)


### 第二步，在应用中心添加oAuth应用
![](https://cdn.nlark.com/yuque/0/2021/png/21376338/1632394866451-3b438edd-6b5c-45a3-9a4a-9814d645bda8.png)

### 第三步，在添加arkid第三方登录(可选，适用于需要在租户登录页显示)
![](https://cdn.nlark.com/yuque/0/2021/png/21376338/1632395118656-189b0dbe-4d9e-43db-aed6-ad9ee631a1dc.png)

可以将创建成功后的callback url填回oAuth应用界面
![](https://cdn.nlark.com/yuque/0/2021/png/21376338/1632395189651-87439d2c-c7d1-4ff4-a64a-295142788a8d.png)

## 以下为接口说明(针对不接入租户登录页的情况)

### 授权
请求地址:
https://IP:PORT/api/v1/app/APP_ID/tenant/TENANT_UUID/oauth/authorize/

请求参数:
![](https://cdn.nlark.com/yuque/0/2021/png/21376338/1634721707037-96ef1bf0-888c-44a0-a74a-1df3e1edc9d6.png)
https://IP:PORT/api/v1/app/APP_ID/tenant/TENANT_UUID/oauth/authorize/?client_id=xxxxx&redirect_uri=xxxxx&response_type=code&scope=userinfo

返回参数:
![](https://cdn.nlark.com/yuque/0/2021/png/21376338/1632396333927-63bde0bc-401d-45d2-8646-fcc72e697e71.png)
https://redirect_uri?code=XEV8esOvaVk9wyAuiNXpb3Nuwn5av9&token=cd34840ffc804b894ede31bc21b176ef559e137f

### 获取access_token
请求地址:https://IP:PORT/api/v1/tenant/TENANT_UUID/oauth/token/

请求参数:
![](https://cdn.nlark.com/yuque/0/2021/png/21376338/1632396388808-44c59859-2f36-4882-a99e-fbd625f01a4e.png)

返回参数:
![](https://cdn.nlark.com/yuque/0/2021/png/21376338/1634721748531-bd9c48a9-5030-44e5-b964-73b42b4622ed.png)

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
![](https://cdn.nlark.com/yuque/0/2021/png/21376338/1632396607862-3c639ca4-b58a-4e4f-a874-42e0c279fabd.png)

返回参数:
![](https://cdn.nlark.com/yuque/0/2021/png/21376338/1632396629837-39c05687-a769-4a1a-a476-8aa6e7e7fdd0.png)

{
"id": 1,
"name": "admin",
"email": "insfocus@gmail.com"
}

### 刷新token
请求地址:https://IP:PORT/api/v1/tenant/TENANT_UUID/oauth/token/

请求参数:
![](https://cdn.nlark.com/yuque/0/2021/png/21376338/1632396750578-a7e75191-0148-4995-bc46-68881afb0006.png)
![](https://cdn.nlark.com/yuque/0/2021/png/21376338/1632396761726-2dbc4239-bb3c-4959-ac27-fcf72284eb0d.png)

返回参数:
![](https://cdn.nlark.com/yuque/0/2021/png/21376338/1632396781925-6b0b9efe-a656-461d-a482-281b120a1384.png)

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
![](https://cdn.nlark.com/yuque/0/2021/png/21376338/1634721997464-bad9b503-eac2-49e3-bbdd-7f789a9a146a.png)

返回参数:
{
    "error_code":0,
    "error_msg":"logout success"
}
