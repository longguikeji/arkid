##### 一、测试目的：
本次测试对一账通部分接口进行性能测试，以达到对接口性能进行评估和调优的目的。
##### 二、测试结论：
通过测试，发现了以下问题：       
1、CPU占用过高          
2、系统稳定性较差           
3、部分接口响应时间过长             
##### 三、测试工具：
Jmeter、截图工具
##### 四、测试环境：
1、软件
终端|操作系统
-----|-----
服务器|Centos 7
客户端|Windows 10家庭版

2、硬件
终端|配置
-----|-----
服务器|4核8G
客户端|4核8G
##### 五、测试策略：
在特定环境下对接口进行压力测试，找到被测接口的负载最大值
##### 六、测试数据规模：
本次测试数据包括：         
应用：10个     
账号：3998个   
部门分类：一级分组7个，最深层次6级       
##### 七、测试结果汇总：
接口性能受数据量影响较大，如获取我的应用信息接口会受应用信息数据量影响，因此测试结果只作参考
接口|并发用户数量|运行场景/s|平均并发量（线程数/秒）|平均响应时间/s
:-----|:-----|:-----|:-----|:-----
登录（http://localhost:8989/siteapi/oneid/ucenter/login/)|350|60|5.833|11.209
获取应用信息（http://localhost:8989/siteapi/oneid/ucenter/apps/)|400|60|6.667|15.281
获取部门分类（http://localhost:8989/siteapi/oneid/meta/node/d_root/tree/?user_required=true)|2|60|0.033|44.193
获取角色分类（http://localhost:8989/siteapi/oneid/meta/node/d_role/tree/?user_required=true)|250|60|4.167|15.362
个人资料页面修改信息（http://localhost:8989/siteapi/oneid/ucenter/profile/)|800|60|13.333|4.583
账号管理查看账号信息（http://localhost:8989/siteapi/oneid/user/?page=1&page_size=10&keyword=)|80|60|1.333|16.546
分组管理查看部门分类信息（http://localhost:8989/siteapi/oneid/node/d_root/tree/?user_required=true)|1|60|0.167|44.991
应用管理查看应用信息（http://localhost:8989/siteapi/oneid/app/?page=1&page_size=10)|100|60|1.667|18.993
配置管理查看配置信息（http://localhost:8989/siteapi/oneid/config/)|600|60|10|2.132
配置管理修改配置信息（http://localhost:8989/siteapi/oneid/config/)|500|60|8.333|10.56
查看子管理员信息（http://localhost:8989/siteapi/oneid/node/g_manager/node/)|150|60|2.5|33.651
查看操作日志（http://localhost:8989/siteapi/oneid/log/?page=1&page_size=10)|550|60|9.167|10.85
