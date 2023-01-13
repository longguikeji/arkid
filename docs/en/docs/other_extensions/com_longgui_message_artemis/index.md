# 消息中间件：Artemis

## 功能介绍

通过Artemis作为中间件接收第三方软件传输的消息数据并展示于Arkid平台

## 使用示例

=== "插件租赁"
    经由左侧菜单栏依次进入【租户管理】->【插件管理】，在插件租赁页面中找到消息中间件：Artemis插件卡片，点击租赁<br/>
    [![vybxGd.png](https://s1.ax1x.com/2022/08/22/vybxGd.png)](https://imgse.com/i/vybxGd)<br/>

=== "设置平台插件"
    经由左侧菜单栏依次进入【平台管理】->【平台插件】，找到消息中间件：Artemis插件卡片，编辑配置<br/>
    [![vyqSxI.md.png](https://s1.ax1x.com/2022/08/22/vyqSxI.md.png)](https://imgse.com/i/vyqSxI)
    说明:配置信息除了服务器地址端口用户名密码而外，队列名为平台统一队列名，即平台上所有租户共用<br/>

=== "发送消息说明"
消息结构如下：注意用户ID列表中的ID需第三方软件以OIDC协议等方式向平台获取<br/>
```
{
    "title": "消息标题",
    "content": "消息内容",
    "url": "跳转链接",
    "users": ["xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"], #用户ID列表
}
```

=== "python3+stomp发送消息代码示例"
```
    import time
    import sys
    import json
    import stomp
    class MyListener(stomp.ConnectionListener):
        def on_error(self,message):
            print('received an error "%s"' % message)
        def on_message(self, message):
            print('received a message "%s"' % message)
    hosts = [('your host', 61616)]
    conn = stomp.Connection(host_and_ports=hosts)
    conn.set_listener('', MyListener())
    conn.connect('artemis', 'artemis', wait=True, headers={"client-id":"arkid"})
    data = {
        "title": "消息标题",
        "content": "消息内容",
        "url": "跳转链接",
        "users": ["xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"], #用户ID列表
        "sender":"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" # 发送者ID
    }
    conn.send(body=json.dumps(data), destination='your destination')
    time.sleep(2)
    conn.disconnect()
```
