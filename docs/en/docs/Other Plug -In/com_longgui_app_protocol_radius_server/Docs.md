# FreeRadius+RestImplement route authentication

## FreeRadiusInstall

1. Install freeradius
``` bash
sudo apt-get install freeradius freeradius-mysql
```
2. Manually close freeradius
``` bash
service freeradius stop
```
3. Give/etc/Freeradius directory authority
``` bash
sudo chmod -R 777 /etc/freeradius
```
Restart freeradius if there are prompts：
``` bash
"/etc/freeradius/" is globally writable.  Refusing to start due to insecure configuration.
```
You need to execute
``` bash
 sudo chmod -R o-w /etc/freeradius
```
4. Modify the file/etc/freeradius/3.0/Users to cancel the following code comments，As a test data
``` bash
steve        Cleartext-Password := "testing"
        Service-Type = Framed-User,
        Framed-Protocol = PPP,
        Framed-IP-Address = 172.16.3.33,
        Framed-IP-Netmask = 255.255.255.0,
        Framed-Routing = Broadcast-Listen,
        Framed-Filter-Id = "std.ppp",
        Framed-MTU = 1500,
        Framed-Compression = Van-Jacobsen-TCP-IP
```
5. Restart freeradius (-X means debugging)
``` bash
sudo freeradius -X
```
6. Open a new terminal for testing，The parameters are user names、password、IP and port、key（KEY is /etc/freeradius/3.0/clients.Secret in Conf）
``` bash
radtest steve testing localhost 1812 testing123
```
The client expects the results as follows
[![BnTOMc.png](https://v1.ax1x.com/2023/01/06/BnTOMc.png)](https://zimgs.com/i/BnTOMc)
The expected result of the server is as follows
[![BnTPC5.png](https://v1.ax1x.com/2023/01/06/BnTPC5.png)](https://zimgs.com/i/BnTPC5)
You can see the successful verification**Access**
From the above server output description, the following information can be obtained
The above is a Request，Then Radius is verified，Notice，The file he executes is/etc/freeradius/3.0/sites-enabled/default，Among them, the Authorize module is where he reads the authentication configuration information，You can see that here are all false，The description has failed，Then he prompts User-Name=notfound，Explain that the user name is not found，Then returned a information that was certified。

## FreeRadiusSupport REST login

1. Open/etc/freeradius/3.0/sites-enabled/default file
``` bash
Add Auth to Authenticate node-Type
Auth-Type rest{
    rest
}
```
2. Create soft links
``` bash
cd /etc/freeradius/3.0/mods-enabled
ln -s ../mods-available/rest .
```
3. exist/etc/freeradius/3.0/In users file，Configure identity verification type
``` bash
DEFAULT Auth-Type := rest
```
4. Revise/etc/freeradius/3.0/mods-available/rest
``` bash
Note the content of the following nodes
connect_uri
preacct
accounting
post-auth
pre-proxy
post-proxy
Edit Authorize node
authorize {
    uri = "http://loopbing.natapp1.cc/api/v1/tenant/4da114ce-e115-44a0-823b-d372114425d0/com_longgui_app_protocol_radius_server/radius_login/?action=authorize"
    method = 'post'
    body = 'json'
    data = '{ "username": "%{User-Name}", "password": "%{User-Password}" }'
}
Edit Authenticate node
authenticate {
    uri = "http://loopbing.natapp1.cc/api/v1/tenant/4da114ce-e115-44a0-823b-d372114425d0/com_longgui_app_protocol_radius_server/radius_login/?action=authenticate"
    method = 'post'
    body = 'json'
    data = '{ "username": "%{User-Name}", "password": "%{User-Password}" }'
}
```
Note that the URI in the AUTHORIZE and Authenticate nodes above needs to be replaced with the login address provided by the Radius server plug -in
5. Open the external network connection
Modify the file (/etc/freeradius/3.0/clients.conf)，The iPaddr here is the client local IP
``` bash
client test_client {
    ipaddr = 111.19.83.95
    secret = testing123
}
```
At the same time, open port 1812 of the UDP protocol of the cloud server
6. Start the radius service
``` bash
sudo freeradius -X
```
If the prompt port is occupied, you can run first
``` bash
ps aux | grep radius Find the process
sudo kill -9 3452 Kill process
```
7. Test login
``` bash
radtest admin admin localhost 1812 testing123
```
