# MultiOTPSecond factor certification
## Features
By deploying Multiotp on the server side Server，User Windows System Install MultiotPCREDENTIALPROVIDER, Implement the user's local login or log in to Windows through remote desktop，<br/>
In addition to providing user passwords (local account passwords or AD account passwords in the domain environment)，Still need to provide OTP dynamic password，In order to log in to Windows。

## Configuration guide

### Install Multiotp Server

=== "Download Multotp installation package"

    Download link：https://download.multiotp.net/

    [![BDncWZ.png](https://v1.ax1x.com/2022/12/09/BDncWZ.png)](https://zimgs.com/i/BDncWZ)

=== "Install WebService service"

    In Windows SEVER decompression compression，The administrator executes the webservice in the Windows directory_Install script

    [![BDnRUV.png](https://v1.ax1x.com/2022/12/09/BDnRUV.png)](https://zimgs.com/i/BDnRUV)

=== "Confirm that the service has been installed"

    Use Chrome to open the Multiotp address：http://localhost:8112/

    [![BDnY2L.png](https://v1.ax1x.com/2022/12/09/BDnY2L.png)](https://zimgs.com/i/BDnY2L)

### Windows ServerUsers who need to be synchronized on the upper configuration
    
=== "Create safety group"
    [![BDntEJ.png](https://v1.ax1x.com/2022/12/09/BDntEJ.png)](https://zimgs.com/i/BDntEJ)

=== "Safety group adds synchronization users"
    [![BDnjte.png](https://v1.ax1x.com/2022/12/09/BDnjte.png)](https://zimgs.com/i/BDnjte)

### Synchronize AD user to Multiotp

=== "Configure the MultiOTP server and client certification password"

    Open Powershell terminal, Enter the Windows directory under the MultiotP decompression directory to execute the following command</br>

    .\multiotp -config server-secret=secret2OTP


=== "Configure Multiotp synchronization parameters and synchronize"

    Open Powershell terminal, Enter the Windows directory under the MultiotP decompression directory to execute the following command，Pay attention to changing the address of AD，port，Usernames and password parameters</br>

    .\multiotp -config default-request-prefix-pin=0 </br>
    .\multiotp -config default-request-ldap-pwd=0 </br>
    .\multiotp -config ldap-server-type=1 </br>
    .\multiotp -config ldap-cn-identifier="sAMAccountName" </br>
    .\multiotp -config ldap-group-cn-identifier="sAMAccountName"</br>
    .\multiotp -config ldap-group-attribute="memberOf"</br>
    .\multiotp -config ldap-ssl=0</br>
    .\multiotp -config ldap-port=389</br>
    .\multiotp -config ldap-domain-controllers=DC.dragon.com</br>
    .\multiotp -config ldap-base-dn="DC=dragon,DC=com"</br>
    .\multiotp -config ldap-bind-dn="CN=Administrator,CN=Users,DC=dragon,DC=com"</br>
    .\multiotp -config ldap-server-password="2wsx@WSX"</br>
    .\multiotp -config ldap-in-group="2FAVPNUsers"</br>
    .\multiotp -config ldap-network-timeout=10</br>
    .\multiotp -config ldap-time-limit=30</br>
    .\multiotp -config ldap-activated=1</br>
    .\multiotp -debug -display-log -ldap-users-sync</br>

    [![BDnnoP.png](https://v1.ax1x.com/2022/12/09/BDnnoP.png)](https://zimgs.com/i/BDnnoP)
    
    
=== "Check the user that has been synchronized"

    [![BDnMHw.png](https://v1.ax1x.com/2022/12/09/BDnMHw.png)](https://zimgs.com/i/BDnMHw)

=== "Click the print button"

    [![BDnfU6.png](https://v1.ax1x.com/2022/12/09/BDnfU6.png)](https://zimgs.com/i/BDnfU6)

=== "Binding mobile phone authentication software"

    Use Microsoft Authenticator Or Google Authenticator scan QR code

    [![BDni2O.png](https://v1.ax1x.com/2022/12/09/BDni2O.png)](https://zimgs.com/i/BDni2O)

=== "Mobile phone authentication software display dynamic code"
    
    Dynamic code is updated every 30 seconds

    [![BDn2QQ.png](https://v1.ax1x.com/2022/12/09/BDn2QQ.png)](https://zimgs.com/i/BDn2QQ)

### User computer installation MultiotPCREDENTIALPRovider 

=== "Open the download page"

    Open https://download.multiotp.net/, Click Credential-provider link

    [![BDn6cf.png](https://v1.ax1x.com/2022/12/09/BDn6cf.png)](https://zimgs.com/i/BDn6cf)

=== "Click to download the link"

    [![BDnFnc.png](https://v1.ax1x.com/2022/12/09/BDnFnc.png)](https://zimgs.com/i/BDnFnc)

=== "Decompress installation"

    [![BDndL3.png](https://v1.ax1x.com/2022/12/09/BDndL3.png)](https://zimgs.com/i/BDndL3)

=== "Set Multiotp Server URL and password"

    Fill in the URL and Secret of Multiotp，Secret and Multiotp configured above The server password remains the same

    [![BDneGj.png](https://v1.ax1x.com/2022/12/09/BDneGj.png)](https://zimgs.com/i/BDneGj)

=== "Click Next"

    Fill in the URL and Secret of Multiotp，Secret and Multiotp configured above The server password remains the same

    [![BDnoz5.png](https://v1.ax1x.com/2022/12/09/BDnoz5.png)](https://zimgs.com/i/BDnoz5)

=== "Configure local login and remote login whether a dynamic code requires"

    [![BDIk9m.png](https://v1.ax1x.com/2022/12/09/BDIk9m.png)](https://zimgs.com/i/BDIk9m)

=== "Click to install"

    [![BDIBH4.png](https://v1.ax1x.com/2022/12/09/BDIBH4.png)](https://zimgs.com/i/BDIBH4)


### Restart the computer，Verify OTP dynamic code

=== "Enter the user password"

    [![BDIT1h.png](https://v1.ax1x.com/2022/12/09/BDIT1h.png)](https://zimgs.com/i/BDIT1h)

=== "Enter the mobile phone dynamic code"

    [![BDIm69.png](https://v1.ax1x.com/2022/12/09/BDIm69.png)](https://zimgs.com/i/BDIm69)
