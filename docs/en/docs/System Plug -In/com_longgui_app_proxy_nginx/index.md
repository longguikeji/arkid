# Application URL proxy plug -in

## Features
When creating an application, you can set an application access URL as the internal address (such as：http://192.168.1.100:8000), The URL of the desktop access application will be automatically changed to</br>
http(s)://{Application ID}.{frontend_host}, Then click this link，Will be jumped by the Nginx agent to the internal URL of the application

### Configuration method

=== "Create proxy URL application"
    [![vhNtIK.png](https://s1.ax1x.com/2022/08/30/vhNtIK.png)](https://imgse.com/i/vhNtIK)

!!! Notice
    URLFormat satisfaction http://xxxx, Can't be https


=== "Confirm that the desktop application URL changes"
    [![vhNRJS.png](https://s1.ax1x.com/2022/08/30/vhNRJS.png)](https://imgse.com/i/vhNRJS)


!!! Notice
    After creating a proxy URL application，Will automatically generate nginx configuration files，After deploying Arkid，Nginx will jump to the internal address according to the content of the configuration file，Configuration file content is as follows：

[![vhUNmn.png](https://s1.ax1x.com/2022/08/30/vhUNmn.png)](https://imgse.com/i/vhUNmn)
