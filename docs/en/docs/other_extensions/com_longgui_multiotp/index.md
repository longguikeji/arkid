# MultiOTP第二因素认证
## 功能介绍
通过在服务器端部署MultiOTP Server，用户Windows系统安装multiOTPCredentialProvider, 实现用户本地登录或者通过远程桌面登录Windows时，<br/>
除了需要提供用户的密码(本地账户密码或者域环境下的AD账户密码)外，仍然需要提供OTP动态密码，才能登陆Windows。

## 配置指南

### 安装MultiOTP Server

=== "下载MultOTP安装包"

    下载链接：https://download.multiotp.net/

    [![BDncWZ.png](https://v1.ax1x.com/2022/12/09/BDncWZ.png)](https://zimgs.com/i/BDncWZ)

=== "安装webservice服务"

    在windows server上解压缩，管理员执行windows目录下的webservice_install脚本

    [![BDnRUV.png](https://v1.ax1x.com/2022/12/09/BDnRUV.png)](https://zimgs.com/i/BDnRUV)

=== "确认服务已经安装"

    用chrome打开multiotp地址：http://localhost:8112/

    [![BDnY2L.png](https://v1.ax1x.com/2022/12/09/BDnY2L.png)](https://zimgs.com/i/BDnY2L)

### Windows Server上配置需要同步的用户
    
=== "创建安全组"
    [![BDntEJ.png](https://v1.ax1x.com/2022/12/09/BDntEJ.png)](https://zimgs.com/i/BDntEJ)

=== "安全组添加同步用户"
    [![BDnjte.png](https://v1.ax1x.com/2022/12/09/BDnjte.png)](https://zimgs.com/i/BDnjte)

### 同步AD用户到multiOTP

=== "配置multiOTP服务端和客户端认证密码"

    打开Powershell终端, 进入multiOTP解压目录下的windows目录执行如下命令</br>

    .\multiotp -config server-secret=secret2OTP


=== "配置multiOTP同步参数并同步"

    打开Powershell终端, 进入multiOTP解压目录下的windows目录执行如下命令，注意更改AD的地址，端口，用户名和密码等参数</br>

    .\multiotp -config default-request-prefix-pin=0 </br>
    .\multiotp -config default-request-ldap-pwd=0 </br>
    .\multiotp -config ldap-server-type=1 </br>
    .\multiotp -config ldap-cn-identifier="sAMAccountName" </br>
    .\multiotp -config ldap-group-cn-identifier="sAMAccountName"</br>
    .\multiotp -config ldap-group-attribute="memberOf"</br>
    .\multiotp -config ldap-ssl=0</br>
    .\multiotp -config ldap-port=389</br>
    .\multiotp -config ldap-domain-controllers=DC.dragon.com</br>
    .\multiotp -config ldap-base-dn="DC=dragon,DC=com"</br>
    .\multiotp -config ldap-bind-dn="CN=Administrator,CN=Users,DC=dragon,DC=com"</br>
    .\multiotp -config ldap-server-password="2wsx@WSX"</br>
    .\multiotp -config ldap-in-group="2FAVPNUsers"</br>
    .\multiotp -config ldap-network-timeout=10</br>
    .\multiotp -config ldap-time-limit=30</br>
    .\multiotp -config ldap-activated=1</br>
    .\multiotp -debug -display-log -ldap-users-sync</br>

    [![BDnnoP.png](https://v1.ax1x.com/2022/12/09/BDnnoP.png)](https://zimgs.com/i/BDnnoP)
    
    
=== "查看已同步用户"

    [![BDnMHw.png](https://v1.ax1x.com/2022/12/09/BDnMHw.png)](https://zimgs.com/i/BDnMHw)

=== "点击打印按钮"

    [![BDnfU6.png](https://v1.ax1x.com/2022/12/09/BDnfU6.png)](https://zimgs.com/i/BDnfU6)

=== "绑定手机认证软件"

    使用Microsoft Authenticator 或者Google Authenticator扫描二维码

    [![BDni2O.png](https://v1.ax1x.com/2022/12/09/BDni2O.png)](https://zimgs.com/i/BDni2O)

=== "手机认证软件显示动态码"
    
    动态码每30秒更新一次

    [![BDn2QQ.png](https://v1.ax1x.com/2022/12/09/BDn2QQ.png)](https://zimgs.com/i/BDn2QQ)

### 用户电脑安装multiOTPCredentialProvider 

=== "打开下载页面"

    打开 https://download.multiotp.net/, 点击credential-provider链接

    [![BDn6cf.png](https://v1.ax1x.com/2022/12/09/BDn6cf.png)](https://zimgs.com/i/BDn6cf)

=== "点击下载链接"

    [![BDnFnc.png](https://v1.ax1x.com/2022/12/09/BDnFnc.png)](https://zimgs.com/i/BDnFnc)

=== "解压安装"

    [![BDndL3.png](https://v1.ax1x.com/2022/12/09/BDndL3.png)](https://zimgs.com/i/BDndL3)

=== "设置multiOTP Server URL和密码"

    填写multiOTP的URL和secret，secret和上面配置的multiOTP Server密码保持相同

    [![BDneGj.png](https://v1.ax1x.com/2022/12/09/BDneGj.png)](https://zimgs.com/i/BDneGj)

=== "点击next"

    填写multiOTP的URL和secret，secret和上面配置的multiOTP Server密码保持相同

    [![BDnoz5.png](https://v1.ax1x.com/2022/12/09/BDnoz5.png)](https://zimgs.com/i/BDnoz5)

=== "配置本地登录和远程登录是否需要动态码"

    [![BDIk9m.png](https://v1.ax1x.com/2022/12/09/BDIk9m.png)](https://zimgs.com/i/BDIk9m)

=== "点击安装"

    [![BDIBH4.png](https://v1.ax1x.com/2022/12/09/BDIBH4.png)](https://zimgs.com/i/BDIBH4)


### 重启电脑，验证OTP动态码

=== "输入用户密码"

    [![BDIT1h.png](https://v1.ax1x.com/2022/12/09/BDIT1h.png)](https://zimgs.com/i/BDIT1h)

=== "输入手机动态码"

    [![BDIm69.png](https://v1.ax1x.com/2022/12/09/BDIm69.png)](https://zimgs.com/i/BDIm69)
