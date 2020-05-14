##### 一、测试目的：
本次测试对一账通部分接口进行性能测试，以达到对接口性能进行评估和调优的目的。
##### 二、测试结论：
通过测试，发现了以下问题：       
1、CPU占用过高          
2、系统稳定性较差           
3、部分接口响应时间过长      
进行优化后，系统稳定性显著提高，CPU和内存占用大幅度降低，但仍然存在某些接口响应时间过长的问题              
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
账号：一共4033个。在通讯录中，部门分类3499个，项目组3个          
部门分类：一级分组7个，最深层次5级                
##### 七、测试结果汇总：
接口性能受数据量影响较大，如获取我的应用信息接口会受应用信息数据量影响，因此测试结果只作参考
接口|并发用户数量|运行场景/s|平均并发量（线程数/秒）|平均响应时间/s
:-----|:-----|:-----|:-----|:-----
登录（http://localhost:8989/siteapi/oneid/ucenter/login/)|750|60|12.500|6.737
获取应用信息（http://localhost:8989/siteapi/oneid/ucenter/apps/)|450|60|7.500|19.600
获取部门分类（http://localhost:8989/siteapi/oneid/meta/node/d_root/tree/?user_required=true)|6|60|0.100|40.850
获取角色分类（http://localhost:8989/siteapi/oneid/meta/node/d_role/tree/?user_required=true)|750|60|12.500|6.817
个人资料页面修改信息（http://localhost:8989/siteapi/oneid/ucenter/profile/)|1100|60|18.333|5.018
账号管理查看账号信息（http://localhost:8989/siteapi/oneid/user/?page=1&page_size=10&keyword=)|150|60|2.500|34.758
分组管理查看部门分类信息（http://localhost:8989/siteapi/oneid/node/d_root/tree/?user_required=true)|5|60|0.083|39.473
应用管理查看应用信息（http://localhost:8989/siteapi/oneid/app/?page=1&page_size=10)|150|60|2.500|29.163
配置管理查看配置信息（http://localhost:8989/siteapi/oneid/config/)|950|60|15.833|7.350
配置管理修改配置信息（http://localhost:8989/siteapi/oneid/config/)|650|60|10.833|8.267
查看子管理员信息（http://localhost:8989/siteapi/oneid/node/g_manager/node/)|150|60|2.500|41.369
查看操作日志（http://localhost:8989/siteapi/oneid/log/?page=1&page_size=10)|600|60|10.000|10.478
绑定微信（http://localhost:8989/siteapi/v1/user/admin/)|200|60|3.333|22.218
根据微信查询用户（http://localhost:8989/siteapi/v1/user/admin/)|1700|60|28.333|3.752
空白接口-性能极值（http://localhost:8989/siteapi/v1/user/admin/)|7200|60|120.000|0.722
