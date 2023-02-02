# SMS plugin：Alibaba Cloud SMS

## Features

Provide SMS service support for the platform，SMS service provider is Alibaba Cloud SMS。

## Configuration guide

=== "Plug -in lease"
    Enter through the menu bar on the left【Tenant management】->【Plug -in management】，Find the Alibaba Cloud SMS plug -in card in the plug -in lease page，Click to rent<br/>
    [![Plug -in rental] (https://S1.ax1x.com/2022/08/02/lose.png)](https://imgtu.com/i/to lose)

=== "Plug -in tenant configuration"
    After the lease is completed，Enter the lease list，Find Alibaba Cloud SMS plug -in card，Click on the tenant configuration，Configure related data<br/>
    * Domain name default.aliyuncs.com<br/>
    [![Plug -in tenant configuration] (https://S1.ax1x.com/2022/08/02/vEsDFe.md.png)](https://imgtu.com/i/vEsDFe)

=== "Configuration of the plug -in"
    After the tenant configuration is completed, return to the rental page，Click on Run on the Alibaba Cloud SMS plug -in card，Click new in the pop -up window，Enter the corresponding SMS template configuration<br/>
    [![Configuration during the plug -in] (https://S1.ax1x.com/2022/08/02/vEyZkD.md.png)](https://imgtu.com/i/vEyZkD)<br/>
    [![Configuration during the plug -in] (https://S1.ax1x.com/2022/08/02/Make sure.md.png)](https://imgtu.com/i/So make sure)<br/>
    * Notice： If you do not fill in the template parameter, the default is ["code"]，Applicable to SMS verification code

## Abstract method implementation
* [load](#extension_root.com_longgui_sms_aliyun.AliyunSMSExtension.load)
* [send_sms](#extension_root.com_longgui_sms_aliyun.AliyunSMSExtension.send_sms)

## Code

::: extension_root.com_longgui_sms_aliyun.AliyunSMSExtension
    rendering:
        show_source: true
