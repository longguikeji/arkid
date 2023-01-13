# WechatScan 第三方登录插件

## 功能介绍
配置微信扫码登录插件后，可以点击ArkID登录页面的微信图标，跳转到微信完成Oauth2认证，并和ArkID的用户绑定
对接详情见[扫码授权登录](https://developers.weixin.qq.com/doc/oplatform/Website_App/WeChat_Login/Wechat_Login.html)

### 创建微信应用

=== "打开微信开放平台，创建网站应用"
    [![vZkldJ.md.jpg](https://s1.ax1x.com/2022/08/03/vZkldJ.md.jpg)](https://imgtu.com/i/vZkldJ)

=== "保存AppID和AppSecret"
    [![vZkNQK.md.jpg](https://s1.ax1x.com/2022/08/03/vZkNQK.md.jpg)](https://imgtu.com/i/vZkNQK)

### 创建ArkID第三方登录配置,获取回调URL

=== "打开第三方认证页面"
    [![X7Ef3T.png](https://s1.ax1x.com/2022/06/16/X7Ef3T.png)](https://imgtu.com/i/X7Ef3T)

=== "填写表单参数， 点击创建"
    [![vZkblV.md.jpg](https://s1.ax1x.com/2022/08/03/vZkblV.md.jpg)](https://imgtu.com/i/vZkblV)

=== "点击编辑按钮，获取ArkID回调域名"
    [![vZACSx.md.jpg](https://s1.ax1x.com/2022/08/03/vZACSx.md.jpg)](https://imgtu.com/i/vZACSx)

### 更新微信应用回调域名，点击登录按钮

=== "登录 微信开放平台->进入创建的网页应用"
    [![vZAW1x.md.jpg](https://s1.ax1x.com/2022/08/03/vZAW1x.md.jpg)](https://imgtu.com/i/vZAW1x)

=== "到登录页面点击微信图标按钮"
    [![vZAjjf.md.jpg](https://s1.ax1x.com/2022/08/03/vZAjjf.md.jpg)](https://imgtu.com/i/vZAjjf)

=== "扫码登录"
    [![vZE8v6.md.jpg](https://s1.ax1x.com/2022/08/03/vZE8v6.md.jpg)](https://imgtu.com/i/vZE8v6)

# 统一绑定和解绑说明
请参见[三方账号绑定](/%20%20%20用户指南/用户手册/%20普通用户/认证管理/三方账号绑定/)