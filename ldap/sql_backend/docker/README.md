# OneID LDAP

## Quick Start
>docker run --name ldap -d ldap  

-> admin dn='cn=admin,dc=example,dc=com';password=admin  
-> ldap:389; ldaps:636  
默认生成root：dn='cn=admin,dc=example,dc=com'; password=admin  
容器对外开放389、636端口，分别对应ldap与ldaps

## Admin
>docker run -d --env LDAP_DOMAIN='longguikeji.com' --env LDAP_PASSWORD=yourpwd ldap

-> amdin dn='cn=admin,dc=longguikeji,dc=com';passowrd=yourpwd  
根据提供的domain生成rootdn 'cn=admin,dc=longguikeji,dc=com'  
LDAP_PASSWORD则是设置root密码

## backend
* #### hdb (default) 
>docker run -d -v /your/data:/var/lib/ldap ldap

* #### sql(MySQL)
>docker run -d --env BACKEND=sql --link mysql:mysql ldap  
默认mysql地址为"mysql"  

>docker run -d --env BACKEND=sql --env SQL_HOST=localhost ldap  

或者通过SQL_HOST参数指定。其余参数如下：  
ENV about sql_backend:

|ENV|meaning|default|
|---|-------|-------|
|SQL_HOST|-|mysql|
|SQL_PORT|-|3306|
|SQL_DB|-|oneid|
|SQL_USER|-|root|
|SQL_PWD|-|root|


## TLS
* #### use auto-generated certificate:
    default

* #### user your own certificate:
>docker run -v /your/certs:/etc/openldap/assets/certs \  
>--env TLS_CRT_FILENAME=ldap.crt \  
>--env TLS_KEY_FILENAME=ldap.key \  
>--env TLS_CA_FILENAME=ca.crt \  
>ldap

## LOG

### log_level

docker run -d --env LDAP_DEBUG=1 ldap 

默认LDAP_DEBUG为32，具体log_level参数如下  
Any (-1, 0xffffffff) //开启所有的dug 信息  
Trace (1, 0x1) //跟踪trace 函数调用  
Packets (2, 0x2) //与软件包的处理相关的dug 信息  
Args (4, 0x4) //全面的debug 信息  
Conns (8, 0x8) //链接数管理的相关信息  
BER (16, 0x10) //记录包发送和接收的信息  
Filter (32, 0x20) //记录过滤处理的过程  
Config (64, 0x40) //记录配置文件的相关信息  
ACL (128, 0x80) //记录访问控制列表的相关信息  
Stats (256, 0x100) //记录链接、操作以及统计信息  
Stats2 (512, 0x200) //记录向客户端响应的统计信息  
Shell (1024, 0x400) //记录与shell 后端的通信信息  
Parse (2048, 0x800) //记录条目的分析结果信息  
Sync (16384, 0x4000) //记录数据同步资源消耗的信息  
None (32768, 0x8000) //不记录  
各level之间可以叠加，如loglevel为255则表示包括(1, 2, 4, 8, 16, 32, 64 and 128)

### log_file

日志文件位于/var/log/openldap.log

查看日志时可以通过docker直接查看
>docker logs ldap_container_name

或者
>docker exec -t tail -f /var/log/openldap.log

也可以启动时挂载到本地
>docker run -d -v /path/to/your/log:/var/log/openldap.log ldap

或者启动后拷贝
>docker cp ldap_container_name:/var/log/openldap.log /path/to/save

