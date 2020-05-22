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
应用：9个            
账号：一共4250个         
在通讯录中，部门分类账号3453个，角色分类账号1091个，标签分类账号2563个，性别分类账号377个    
在分组管理中，部门分类一级分组7个，最深层级5级；角色分类一级分组4个；标签分类一级分组1个，二级分组6个；性别分类一级分组2个                       
##### 七、测试结果汇总：
接口性能受数据量影响较大，如获取我的应用信息接口会受应用信息数据量影响，因此测试结果只作参考
接口|并发用户数量|运行场景/s|平均并发量（线程数/秒）|平均响应时间/s
:-----|:-----|:-----|:-----|:-----
登录（http://localhost:8989/siteapi/oneid/ucenter/login/)|650|60|10.833|2.346
获取应用信息（http://localhost:8989/siteapi/oneid/ucenter/apps/)|450|60|7.500|15.484
获取部门分类（http://localhost:8989/siteapi/oneid/meta/node/d_root/tree/?user_required=true)|2|60|0.033|52.408
获取角色分类（http://localhost:8989/siteapi/oneid/meta/node/d_role/tree/?user_required=true)|25|60|0.417|29.791      
获取性别分类（http://localhost:8989/siteapi/oneid/meta/node/g_xingbie/tree/?user_required=true)|60|60|1.000|20.172     
个人资料页面修改信息（http://localhost:8989/siteapi/oneid/ucenter/profile/)|1100|60|18.333|4.962
账号管理查看账号信息（http://localhost:8989/siteapi/oneid/user/?page=1&page_size=10&keyword=)|80|60|1.333|25.529
分组管理查看部门分类信息（http://localhost:8989/siteapi/oneid/node/d_root/tree/?user_required=true)|2|60|0.033|36.806
应用管理查看应用信息（http://localhost:8989/siteapi/oneid/app/?page=1&page_size=10)|200|60|3.333|29.178
配置管理查看配置信息（http://localhost:8989/siteapi/oneid/config/)|900|60|15.000|5.473
配置管理修改配置信息（http://localhost:8989/siteapi/oneid/config/)|700|60|10.833|10.699
查看子管理员信息（http://localhost:8989/siteapi/oneid/node/g_manager/node/)|200|60|3.333|21.161
查看操作日志（http://localhost:8989/siteapi/oneid/log/?page=1&page_size=10)|600|60|10.000|7.953
绑定微信（http://localhost:8989/siteapi/v1/user/admin/)|250|60|4.167|24.161
根据微信查询用户（http://localhost:8989/siteapi/v1/user/admin/)|1800|60|30.000|2.866
空白接口-性能极值（http://localhost:8989/siteapi/v1/user/admin/)|7100|60|118.333|1.088
