# Certification rules: Limited number of certification failure
## Features

After the number of failures of the user exceeds the limit of authentication，Expand the user certification voucher form，Insert secondary authentication factors，And when the user initiates the certification request again, the subordinate authentication factors are verified

## precondition

The number of certification failure limit rules plug -in require，The main authentication factor is to have login/register/Authentic factors for reset passwords and other main functions，The primary authentication factors are mainly authentication factors to supplement the authentication process through authentication rules，Taking the user name and password authentication factors and graphic verification code authentication factors as an example。

## Configuration guide

=== "Plug -in lease"
    Enter through the menu bar on the left【Tenant management】->【Plug -in management】，Find the number of authentication times in the plug -in lease page to limit the rules of the plug -in card，Click to rent<br/>
    [![vEbUde.png](https://s1.ax1x.com/2022/08/02/vEbUde.png)](https://imgtu.com/i/vEbUde)

=== "Certification rules configuration"
    Enter through the menu bar on the left【Certification management】-> 【Certification rules】,Click to create button，Type selection"retry_times",Choose the default password authentication factor of the main authentication factors，Select the default graphic verification code authentication factors for sub -authentication factors，The configuration is completed<br/>
    [![vEb7LT.md.png](https://s1.ax1x.com/2022/08/02/vEb7LT.md.png)](https://imgtu.com/i/vEb7LT)

=== "Login interface"
    After the configuration is complete，When the user enters the login interface and repeats three times，The page will refresh and enable the graphics verification code<br/>
    [![vEqeSI.png](https://s1.ax1x.com/2022/08/02/vEqeSI.png)](https://imgtu.com/i/vEqeSI)

## Implementation

* Certification rules: Limited number of certification failure：

```mermaid
sequenceDiagram
    participant D as user
    participant C as Platform core
    participant A as Certification failure number limit rules plugin
    
    C->>A: Loading plug -in
    A->>C: Register and monitor the incident Create_LOGIN_PAGE_RULES,AUTH_FAIL,BEFORE_AUTH
    D->>C: Visit Registration/Log in/Reset password page
    C->>A: Send Create_LOGIN_PAGE_Rules event
    A->>C: Response event,Determine whether to meet the rules,If the rules are satisfied, it will trigger Authrule_FIX_LOGIN_Page event
    C->>D: Rendering/Log in/Reset password page
    D->>C: Enter certification voucher，Initiate certification requests
    C->>A: Triggering before_Auth event
    A->>C: Response event,Determine whether to meet the rules，If the rules are satisfied, it will trigger Authrule_CHECK_AUTH_Data event，Check and return the result
    C->>A: test result,If the certification is not completed，Trigger amh_Fail event
    A->>C: Response event,Record the number of failures and determine whether to refresh the page
    C->>D: By rendering or refresh the page according to the return result

```

## Abstract method implementation

* [load](#extension_root.com_longgui_auth_rule_retry_times.AuthRuleRetryTimesExtension.load)
* [check_rule](#extension_root.com_longgui_auth_rule_retry_times.AuthRuleRetryTimesExtension.authenticate)

## Code

::: extension_root.com_longgui_auth_rule_retry_times.AuthRuleRetryTimesExtension
    rendering:
        show_source: true

