# Message middleware：Artemis

## Features

Message data transmitted by the third -party software through Artemis as a middleware and displayed on the Arkid platform

## Example

=== "Plug -in lease"
    Enter through the menu bar on the left【Tenant management】->【Plug -in management】，Find the message intermediate parts in the plug -in lease page：Artemis plug -in card，Click to rent<br/>
    [![vybxGd.png](https://s1.ax1x.com/2022/08/22/vybxGd.png)](https://imgse.com/i/vybxGd)<br/>

=== "Set up a platform plug -in"
    Enter through the menu bar on the left【Platform management】->【Platform plug -in】，Find the message middleware：Artemis plug -in card，Edit configuration<br/>
    [![vyqSxI.md.png](https://s1.ax1x.com/2022/08/22/vyqSxI.md.png)](https://imgse.com/i/vyqSxI)
    illustrate:In addition to the user name and password of the server address port, the configuration information，Crane name is a unified queue name of the platform，That is, all tenants on the platform shared<br/>

=== "Send message description"
The message structure is as follows：Note that the ID in the user ID list requires third -party software to obtain the platform by the OIDC protocol<br/>
```
{
    "title": "Message title",
    "content": "Message content",
    "url": "Jump link",
    "users": ["xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"], #User ID list
}
```

=== "python3+stompSend message code example"
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
        "title": "Message title",
        "content": "Message content",
        "url": "Jump link",
        "users": ["xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"], #User ID list
        "sender":"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" # Sender ID
    }
    conn.send(body=json.dumps(data), destination='your destination')
    time.sleep(2)
    conn.disconnect()
```
