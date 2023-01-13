# OTP认证因素
## 功能介绍

基于时间的一次性密码算法（英语：Time-based One-Time Password，简称：TOTP）是一种根据预共享的密钥与当前时间计算一次性密码的算法。它已被互联网工程任务组接纳为RFC 6238标准[1]，成为主动开放认证（OATH）的基石，并被用于众多多重要素验证系统当中。

TOTP是散列消息认证码（HMAC）当中的一个例子。它结合一个私钥与当前时间戳，使用一个密码散列函数来生成一次性密码。由于网络延迟与时钟不同步可能导致密码接收者不得不尝试多次遇到正确的时间来进行身份验证，时间戳通常以30秒为间隔，从而避免反复尝试。

在特定的多重因素验证应用中，用户验证步骤如下：一位用户在网站或其他服务器上输入用户名和密码，使用运行在本地的智能手机或其他设备中的TOTP生成一个一次性密码提交给服务器，并同时向服务器输入该一次性密码。服务器随即运行TOTP并验证输入的一次性密码。为此，用户设备与服务器中的时钟必须大致同步（服务器一般会接受客户端时间-1区间（也就是延迟了30秒）的时间戳生成的一次性密码）。在此之前，服务器与用户的设备必须通过一个安全的信道共享一个密钥，用于此后所有的身份验证会话。如需要执行更多步骤，用户也可以用TOTP验证服务器。

## 配置指南

=== "插件租赁"
    经由左侧菜单栏依次进入【插件管理】->【租户插件管理】，在插件租赁页面中找到OTP认证因素插件卡片，点击租赁<br/>
    [![Bhol1J.png](https://v1.ax1x.com/2022/11/07/Bhol1J.png)](https://x.imgtu.com/i/Bhol1J)

=== "认证因素配置"
    经由左侧菜单栏依次进入【认证管理】-> 【认证因素】,点击创建按钮，类型选择"OTP",填入相关信息，至此配置完成<br/>
    [![BhogKO.png](https://v1.ax1x.com/2022/11/07/BhogKO.png)](https://x.imgtu.com/i/BhogKO)

=== "打开认证管理"
    [![BbXjAq.png](https://v1.ax1x.com/2022/10/25/BbXjAq.png)](https://x.imgtu.com/i/BbXjAq)
    
=== "点击设置OTP身份认证器"

    !!! 注意
        每次设置新的OTP身份认证器都会覆盖已有的 

    [![BhohPQ.png](https://v1.ax1x.com/2022/11/07/BhohPQ.png)](https://x.imgtu.com/i/BhohPQ)


=== "扫描二维码"

    !!! 注意
        需要手机先安装谷歌Authenticator或者微软Authenticator或者FreeOTP等客户端软件, 扫码后，输入OTP代码, 点击确认

    [![Bho86f.png](https://v1.ax1x.com/2022/11/07/Bho86f.png)](https://x.imgtu.com/i/Bho86f)

=== "编辑OTP认证器，打开应用开关"
    [![BhoxNc.png](https://v1.ax1x.com/2022/11/07/BhoxNc.png)](https://x.imgtu.com/i/BhoxNc)

    [![Bho5a3.png](https://v1.ax1x.com/2022/11/07/Bho5a3.png)](https://x.imgtu.com/i/Bho5a3)


## 登录过程

=== "首先账密登录"
    [![BhoAIj.png](https://v1.ax1x.com/2022/11/07/BhoAIj.png)](https://x.imgtu.com/i/BhoAIj)

=== "输入OTP代码"

    !!! 注意
        如果操作不及时, OTP代码可能过期，重新输入新的OTP代码即可

    [![BhoW05.png](https://v1.ax1x.com/2022/11/07/BhoW05.png)](https://x.imgtu.com/i/BhoW05)
