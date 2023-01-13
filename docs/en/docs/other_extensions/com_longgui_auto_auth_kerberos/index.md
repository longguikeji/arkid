# Kerberos自动登录插件

## 功能介绍
通过此插件，可以用AD域中的账号自动登录到ArkID, 前提企业已经配置好AD域环境，员工电脑也在域管理之下
有关如何配置AD域的详情，参见[AD域下配置kerberos认证文档](https://www.yuque.com/longguikeji/arkid2/lr1i83)

### AD域上创建ArkID服务账户

=== "AD上创建ArkID服务账户"
    [![vCtbjI.png](https://s1.ax1x.com/2022/07/28/vCtbjI.png)](https://imgtu.com/i/vCtbjI)

=== "配置服务账户属性"
    [![vCtz4g.png](https://s1.ax1x.com/2022/07/28/vCtz4g.png)](https://imgtu.com/i/vCtz4g)

### 在AD中导出ArkID服务对应的keytab文件 

=== "AD所在Windows Server上执行命令"
    [![vCNZUU.png](https://s1.ax1x.com/2022/07/28/vCNZUU.png)](https://imgtu.com/i/vCNZUU)


### 配置ArkID Server

=== "Server上安装Kerberos客户端"

    centos上执行命令:  yum install krb5-workstation krb5-libs krb5-devel

    !!! attention "注意"
        其他的linux发行版安装的客户端软件可能不一样

=== "修改kerberos客户端配置文件"

    [![vCdFKA.png](https://s1.ax1x.com/2022/07/28/vCdFKA.png)](https://imgtu.com/i/vCdFKA)
    

=== "AD中导出的krb5.keytab放到/etc目录下"

    [![vCdhMd.png](https://s1.ax1x.com/2022/07/28/vCdhMd.png)](https://imgtu.com/i/vCdhMd)

### 配置ArkID kerberos插件

=== "创建自动登录插件配置"

    [![vCdbi8.png](https://s1.ax1x.com/2022/07/28/vCdbi8.png)](https://imgtu.com/i/vCdbi8)
    
### 配置浏览器

=== "打开浏览器本地站点"

    [![vCwiJU.png](https://s1.ax1x.com/2022/07/28/vCwiJU.png)](https://imgtu.com/i/vCwiJU)

=== "打开高级设置"

    [![vCwUTP.png](https://s1.ax1x.com/2022/07/28/vCwUTP.png)](https://imgtu.com/i/vCwUTP)
    
=== "添加ArkID站点"

    [![vCwwY8.png](https://s1.ax1x.com/2022/07/28/vCwwY8.png)](https://imgtu.com/i/vCwwY8)

!!! attention "注意"
    edge和chrome共用这个设置, firefox需要另外的配置方法, </br>
    另外也可以通过AD下发组策略设置域中的计算机
    参考：[通过组策略实现IE自动以当前域账号登录SP站点]("https://www.cnblogs.com/love007/p/4082875.html")

### 测试自动登录效果
    浏览器打开ArkID地址，不需要输入密码，以当前PC域账号登录到ArkID
