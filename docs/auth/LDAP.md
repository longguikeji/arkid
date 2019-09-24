# LDAP

ArkID 支持 LDAP 协议。

无论使用何种后端，目前均只支持 ArkID 提供的 LDAP server。
强烈建议以 [arkid-charts](https://github.com/longguikeji/arkid-charts) 部署。

base_dn 目前不支持自定义。
限定如下：
LDAP_ADMIN = 'cn=admin,dc=example,dc=org'
LDAP_USER_BASE = 'ou=people,dc=example,dc=org'
LDAP_DEPT_BASE = 'ou=dept,dc=example,dc=org'
LDAP_GROUP_BASE = 'cn=intra,ou=group,dc=example,dc=org'

### Native
不建议使用

使用 hdb 为数据后端，LDAP、ArkID 各维护一份数据，并由 ArkID 向 LDAP 同步。

将 `oneid/settings.py` 中 `EXECUTERS` 的 'executer.LDAP.LDAPExecuter' 取消注释，  
并配置 LDAP 相关参数（`LDAP_`前缀），即可开启同步。
LDAP数据存在一定延迟，约 5~10 分钟。

### SQL

> docker pull longguikeji/ark-sql-ldap:1.0.0

使用ArkID DB 为数据后端，只维护一份数据。LDAP server 读取 ArkID DB 后以 LDAP 协议暴露。
将 `oneid/settings.py` 中 `INSTALLED_APPS` 的 'ldap.sql_backend' 取消注释。
取消注释后需重新运行 `python manage.py migrate`。
另需 celery 配合。
LDAP 数据存在一定延迟，不超过 10 分钟。
