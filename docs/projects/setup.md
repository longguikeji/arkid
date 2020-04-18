# 要求

## ArkID框架要求以下内容

 - python （3.6）
 - django （2.0、2.1、2.2、3.0）
 - djangorestframework （3.10.2+）
 - django-cors-headers （2.5.3+）
 - celery （4.2.1+）
 - django-celery-results （1.0.1+）
 - django-celery-beat （1.1.1+）
 - rules （2.0+）
 - passlib （*）
 - django-oauth-toolkit （1.2.0+）
 - django-cors-middleware （1.4.0+）
 - redis （3.2.0+）
 - sqlparse （*）
 - cryptography （2.8+）
 - django-redis （4.10.0+）
 - repoze-who （2.3+）
 - cherrypy （18.4.0+）
 
我们强烈建议python和Django为官方正式的最新修补版本。

## 以下软件包是可选的：

 - pyjwkest （*） -支持JWT, JWS, JWE, JWK等编码解码。
 - pysaml2 （4.9.0+） -支持构建构建SAML2服务提供者或身份提供者。
 - ldap3 （2.5.2+） -包装OpenLDAP 2.x库。
 - minio （4.0.18+） -支持访问任何与Amazon S3兼容的对象存储服务器
 - alipay-sdk-python （3.3.202+） -支持访问蚂蚁金服开放平台的官方SDK。
 - coreapi （2.3.3+） -支持模式生成。
 - pypinyin （*） -支持将汉字转为拼音，可用于汉字注音、排序、检索。
 - aliyun-python-sdk-core-v3 （2.8.6+） -Aliyun Python SDK的核心模块。
 - kubernetes （10.0.0+） -kubernetes的Python客户端
 - pyasn1 （0.4.8+） -ASN.1类型和DER / BER / CER编解码器（X.208）
 - django-simple-captcha （0.5.12+） -支持将验证码图像添加到Django表单中。
 - django-jsonfield （1.2.0+） -支持灵活查询JSONField和相关表单字段
 - mako （1.1.0+） -支持提供一种非XML语法。

# 安装

## 使用pip进行安装，包括您所需的任何可选软件包...

- pip install django-arkid
- pip install pyjwkest
- pip install ldap3

## ...或从github克隆项目.

git clone https://github.com/longguikeji/arkid-core.git

## 添加 'arkid' 到您的INSTALLED_APPS设置.

- INSTALLED_APPS = [
    ...
    'arkid',
    'arkid.oauth2_provider',
]

添加某些 app 时，可能需要在您的 django 项目的配置文件中手动添加某些参数，以保证 ArkID 可以完美的为您提供服务.
当然，这些被 ArkID 需要的参数都可以在 arkid.oneid.settings_setup.py 中找到，其中包含了默认的参数配置.
您可以参照默认配置文件来对您的项目采取相应的配置策略.

## 如果您打算使用ArkID框架的相关URL。可将以下内容添加到您的根urls.py文件中。

- urlpatterns = [
    ...
    url(r'^api-auth/', include('arkid.oauth2_provider.urls'))
]

# 注意

## 必需参数设置

### 如果您正在尝试使用 ArkID 框架来丰富您的项目，请注意以下几个问题:

- 如果您试图使用 ArkID 框架相关接口功能，请务必设置 REST_FRAMEWORK， AUTHENTICATION_BACKENDS， CELERY 组件相关的参数，可参照 arkid.oneid.settings_setup.py 中的相关说明进行操作.
- 当您在使用 ArkID 框架时遇到任何 NotConfiguredException 异常时，说明您的项目配置文件中缺少 ArkID 框架所必需的参数，请您务必参照 arkid.oneid.settings_setup.py 中的相关说明进行操作.