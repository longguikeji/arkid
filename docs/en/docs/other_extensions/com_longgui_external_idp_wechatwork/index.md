# WechatWork 第三方登录插件

## 功能介绍
配置企业微信插件后，可以点击ArkID登录页面的企业微信图标，跳转到企业微信完成Oauth2认证，并和ArkID的用户绑定
对接详情见[扫码授权登录](https://developer.work.weixin.qq.com/document/path/91025)

### 创建企业微信应用

=== "打开企业微信管理后台，创建应用"
    [![vSeLYF.png](https://s1.ax1x.com/2022/07/26/vSeLYF.png)](https://imgtu.com/i/vSeLYF)

=== "填写表单"
    [![vSmESH.png](https://s1.ax1x.com/2022/07/26/vSmESH.png)](https://imgtu.com/i/vSmESH)

=== "保存Secret"
    [![vSmGlj.png](https://s1.ax1x.com/2022/07/26/vSmGlj.png)](https://imgtu.com/i/vSmGlj)

=== "保存企业ID"
    [![vSmXAf.png](https://s1.ax1x.com/2022/07/26/vSmXAf.png)](https://imgtu.com/i/vSmXAf)

### 创建ArkID第三方登录配置,获取回调URL

=== "打开第三方认证页面"
    [![X7Ef3T.png](https://s1.ax1x.com/2022/06/16/X7Ef3T.png)](https://imgtu.com/i/X7Ef3T)

=== "填写表单参数， 点击创建"
    [![vEbTyV.md.jpg](https://s1.ax1x.com/2022/08/02/vEbTyV.md.jpg)](https://imgtu.com/i/vEbTyV)

=== "点击编辑按钮，获取ArkID回调域名"
    [![vELShj.md.jpg](https://s1.ax1x.com/2022/08/02/vELShj.md.jpg)](https://imgtu.com/i/vELShj)

### 更新企业微信应用回调URL，点击登录按钮

=== "登录 企业管理端后台->进入需要开启的自建应用->点击 网页授权及JS-SDK"
    [![vELBKP.md.jpg](https://s1.ax1x.com/2022/08/02/vELBKP.md.jpg)](https://imgtu.com/i/vELBKP)

=== "设置可信域名，输入回调域名"
    [![vEL6Ug.md.jpg](https://s1.ax1x.com/2022/08/02/vEL6Ug.md.jpg)](https://imgtu.com/i/vEL6Ug)

=== "点击可信ip"
    [![vEOVMt.md.jpg](https://s1.ax1x.com/2022/08/02/vEOVMt.md.jpg)](https://imgtu.com/i/vEOVMt)

=== "配置可信ip"
    [![vEOYLV.md.jpg](https://s1.ax1x.com/2022/08/02/vEOYLV.md.jpg)](https://imgtu.com/i/vEOYLV)

=== "服务器ip可以通过使用终端ping网站的方式获得"
    [![vEORoD.md.jpg](https://s1.ax1x.com/2022/08/02/vEORoD.md.jpg)](https://imgtu.com/i/vEORoD)

=== "在企业微信中打开网页链接，点击企业微信图标按钮"
    [![vELfvq.md.jpg](https://s1.ax1x.com/2022/08/02/vELfvq.md.jpg)](https://imgtu.com/i/vELfvq)

# 统一绑定和解绑说明
请参见[三方账号绑定](/%20%20%20用户指南/用户手册/%20普通用户/认证管理/三方账号绑定/)
