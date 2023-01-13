# Webauthn认证因素
## 功能介绍

Web Authentication API（也称作 WebAuthn）使用asymmetric (public-key) cryptography （非对称加密）替代密码或 SMS 短信在网站上注册、登录、second-factor authentication（双因素验证）。解决了 phishing（钓鱼）、data breaches（数据破坏）、SMS 文本攻击、其它双因素验证等重大安全问题，同时显著提高了易用性（因为用户不必管理许多越来越复杂的密码)。


## 配置指南

=== "插件租赁"
    经由左侧菜单栏依次进入【租户管理】->【插件管理】，在插件租赁页面中找到Webauthn认证因素插件卡片，点击租赁<br/>
    [![BbXRb4.png](https://v1.ax1x.com/2022/10/25/BbXRb4.png)](https://x.imgtu.com/i/BbXRb4)

=== "认证因素配置"
    经由左侧菜单栏依次进入【认证管理】-> 【认证因素】,点击创建按钮，类型选择"webAuthn",填入相关信息，至此配置完成<br/>
    [![BbMVm3.png](https://v1.ax1x.com/2022/10/28/BbMVm3.png)](https://x.imgtu.com/i/BbMVm3)

=== "注册界面"
    [![BbXzqY.png](https://v1.ax1x.com/2022/10/25/BbXzqY.png)](https://x.imgtu.com/i/BbXzqY)

=== "注册凭证"
    [![BbX4DH.png](https://v1.ax1x.com/2022/10/25/BbX4DH.png)](https://x.imgtu.com/i/BbX4DH)

=== "登录界面"
    [![BbXCMZ.png](https://v1.ax1x.com/2022/10/25/BbXCMZ.png)](https://x.imgtu.com/i/BbXCMZ)

=== "登录凭证"
    [![BbXX3U.png](https://v1.ax1x.com/2022/10/25/BbXX3U.png)](https://x.imgtu.com/i/BbXX3U)



## webauthn凭证管理

=== "打开认证管理"
    [![BbXjAq.png](https://v1.ax1x.com/2022/10/25/BbXjAq.png)](https://x.imgtu.com/i/BbXjAq)

=== "删除webauthn凭证"
    [![BbXnCs.png](https://v1.ax1x.com/2022/10/25/BbXnCs.png)](https://x.imgtu.com/i/BbXnCs)

=== "新增webauthn凭证"
    [![BbXMBa.png](https://v1.ax1x.com/2022/10/25/BbXMBa.png)](https://x.imgtu.com/i/BbXMBa)


!!! 注意
    WebAuthn协议不支持使用IP地址访问，部署时请配置好域名, 否则，浏览器不支持
