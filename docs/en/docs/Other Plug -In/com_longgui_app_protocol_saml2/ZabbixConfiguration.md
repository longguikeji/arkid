# zabbix SSO

=== "Preparation"
    + zabbixMust be 5.0 above versions，Otherwise, the SAML2 protocol is not supported<br/>
    + Pre -configure private keys and certificates for ZABBIX，The file suffix is named.KEY and.crt，Store in the ZABBIX configuration directory，Generally/etc/zabbix/web/certs/<br/>

=== "Add application"
    Log in to the ARKID platform，Enter【Application management】-> 【Application List】, Clicked【Add to】Button, Create an application called Zabbix，Application url is <b color="red">ZABBIX_WEB_HOST/index_sso.php</b><br/>
    [![XqS3Zt.md.png](https://s1.ax1x.com/2022/06/17/XqS3Zt.md.png)](https://imgtu.com/i/XqS3Zt)
  
=== "Configuration protocol"
    After the addition is completed, click on the right on the right【Configuration protocol】The button enters the protocol configuration window，Select the protocol type <b>Gathering_CERT </b>，Fill in related data in turn<br/>
    + acs : Assertion Consumer URL It should be set to \<path_to_zabbix_ui\>/index_sso.php?acs<br/>
    + sls: Single Logout URL It should be set to \<path_to_zabbix_ui\>/index_sso.php?sls<br/>
    + entity_id: Keep it consistent with the settings of ZABBIX<br/>

=== "Download certificate"
    Click to confirm and enter the editing page，After pulling down, you can see the attribute you read only,Download IDP certificate via the link，And copy IDP SSO URL and other backup<br/>
    [![XqS8dP.md.png](https://s1.ax1x.com/2022/06/17/XqS8dP.md.png)](https://imgtu.com/i/XqS8dP)

=== "Configure ZABBIX Certificate key"
    Place the IDP certificate on the Zabbix configuration directory，Generally/etc/zabbix/web/certs/，Put with the Zabbix certificate<br/>
    【Notice】：<br/>
    need to use SAML Authentication，Zabbix The private key and certificate should be configured and stored in/etc/zabbix/web/conf/certs/（Different from the version or installation method may be different，I have the test environment here as zabbix5.4 + docker） middle，unless zabbix.conf.php It provides a custom path。<br/>
    by default，Zabbix Will find in the following position：<br/>
    + conf/certs/sp.key === "SPPrivate key file"<br/>
    + conf/certs/sp.crt === "SP Certificate file"<br/>
    + conf/certs/idp.crt === "IDP Certificate file"<br/>
    <b>The file name of the file when storing must be SP/idp.crt   sp.key</b>

=== "zabbix Certification configuration"
    Enter the zabbix page authentication configuration page，As shown in the figure below，Pay attention to replace IDP entity ID and SSO service URL<br/>
    [![XqSMMd.md.png](https://s1.ax1x.com/2022/06/17/XqSMMd.md.png)](https://imgtu.com/i/XqSMMd)

=== "Add zabbix user"
    Use users who are consistent with the user name of Arkid in ZABBIX（Such as admin，Need to distinguish writing）,And give enough permissions<br/>

=== "Log in to Zabbix"
    Enter Arkid Desktop，Click ZABBIX card，After multiple jumps, you can enter Zabbix as a configuration user.<br/>
    [![XqSGIf.md.png](https://s1.ax1x.com/2022/06/17/XqSGIf.md.png)](https://imgtu.com/i/XqSGIf)
