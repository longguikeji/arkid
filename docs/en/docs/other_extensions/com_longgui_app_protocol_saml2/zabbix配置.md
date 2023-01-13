# zabbix SSO

=== "准备工作"
    + zabbix必须为5.0以上版本，否则不支持saml2协议<br/>
    + 预先需为zabbix配置私钥和证书，文件后缀名为.key和.crt，存放在zabbix配置目录下，一般为/etc/zabbix/web/certs/<br/>

=== "添加应用"
    登录arkid平台，进入【应用管理】-> 【应用列表】, 点击【添加】按钮, 创建一个名为zabbix的应用，应用URL为 <b color="red">ZABBIX_WEB_HOST/index_sso.php</b><br/>
    [![XqS3Zt.md.png](https://s1.ax1x.com/2022/06/17/XqS3Zt.md.png)](https://imgtu.com/i/XqS3Zt)
  
=== "配置协议"
    添加完成后在右侧操作栏点击【配置协议】按钮进入协议配置窗口，选择协议类型为 <b>Saml2SP_CERT </b>，依次填入相关数据<br/>
    + acs : Assertion Consumer URL 应该设置为 \<path_to_zabbix_ui\>/index_sso.php?acs<br/>
    + sls: Single Logout URL 应设置为 \<path_to_zabbix_ui\>/index_sso.php?sls<br/>
    + entity_id: 与zabbix设置保持一致<br/>

=== "下载证书"
    点击确认后进入编辑页面，下拉后即可看到只读的属性,通过链接下载IDP证书，并拷贝IDP SSO URL等备用<br/>
    [![XqS8dP.md.png](https://s1.ax1x.com/2022/06/17/XqS8dP.md.png)](https://imgtu.com/i/XqS8dP)

=== "配置zabbix 证书密钥"
    将IDP证书上传存放在zabbix配置目录下，一般为/etc/zabbix/web/certs/，与zabbix证书放在一起<br/>
    【注意】：<br/>
    要使用 SAML 身份验证，Zabbix 应配置私钥和证书应存储在/etc/zabbix/web/conf/certs/（根据版本或安装方式不一样可能有所不同，笔者此处测试环境为zabbix5.4 + docker） 中，除非 zabbix.conf.php 中提供了自定义路径。<br/>
    默认情况下，Zabbix 将在以下位置查找：<br/>
    + conf/certs/sp.key === "SP私钥文件"<br/>
    + conf/certs/sp.crt === "SP 证书文件"<br/>
    + conf/certs/idp.crt === "IDP 证书文件"<br/>
    <b>存储时文件名称务必为sp/idp.crt   sp.key</b>

=== "zabbix 认证配置"
    进入zabbix页面Authentication配置页面，如下图配置，注意替换IDP entity id以及SSO service URL<br/>
    [![XqSMMd.md.png](https://s1.ax1x.com/2022/06/17/XqSMMd.md.png)](https://imgtu.com/i/XqSMMd)

=== "添加zabbix用户"
    在zabbix中添加与arkid用户名一致的用户（比如admin，需区分大小写）,并赋予足够权限<br/>

=== "登录至zabbix"
    进入arkid桌面，点击zabbix卡片，经多次跳转后以配置用户身份即可进入zabbix<br/>
    [![XqSGIf.md.png](https://s1.ax1x.com/2022/06/17/XqSGIf.md.png)](https://imgtu.com/i/XqSGIf)
