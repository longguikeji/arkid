# Mobile phone verification code authentication factors
## Features

User table extension mobile phone number field，Allows users to certify through the mobile phone number and verification code，register，Reset the password and replace the mobile phone number。

general user：

* exist “register” Page implementation mobile phone number+Verification code user registration
* exist “Log in” Page implementation mobile phone number+Verification code user login
* exist “change password” Page implementation mobile phone number+The password changes at the verification code method
* exist “mine - Certification management“ Add the function of resetting the mobile phone number

Tenant administrator

* exist”User Management - user list“In the editor page adds mobile phone number editing function

## precondition

Need to be used with SMS plug -in，The system has default to provide Alibaba Cloud SMS plug -in，If you need to view the configuration method, please move the Alibaba Cloud SMS plug -in documentation。

## Configuration guide

=== "Plug -in lease"
    Enter through the menu bar on the left【Tenant management】->【Plug -in management】，Find the mobile phone verification code authentication factor plug -in card in the plug -in lease page，Click to rent
    [![vEcwwV.png](https://s1.ax1x.com/2022/08/02/vEcwwV.png)](https://imgtu.com/i/vEcwwV)

=== "Certification factor configuration"
    Enter through the menu bar on the left【Certification management】-> 【Authentication】,Click to create button，Type selection"mobile",Select a suitable configuration SMS plug -in when runtime.，The configuration is completed<br/>
    [![vE2VKA.md.png](https://s1.ax1x.com/2022/08/02/vE2VKA.md.png)](https://imgtu.com/i/vE2VKA)

=== "login interface"
    [![vE2hGD.png](https://s1.ax1x.com/2022/08/02/vE2hGD.png)](https://imgtu.com/i/vE2hGD)

=== "Registration interface"
    [![vE25xH.md.png](https://s1.ax1x.com/2022/08/02/vE25xH.md.png)](https://imgtu.com/i/vE25xH)

=== "Password modification interface"
    [![vE2TsA.png](https://s1.ax1x.com/2022/08/02/vE2TsA.png)](https://imgtu.com/i/vE2TsA)

=== "Replace the mobile phone number interface"
    Enter from the user avatar menu【Certification management】interface,Select the mobile phone number tab page<br/>
    [![vE20GF.md.png](https://s1.ax1x.com/2022/08/02/vE20GF.md.png)](https://imgtu.com/i/vE20GF)

## Implementation

* general user：mobile phone number+Verification code user registration/Log in/reset Password：

```mermaid
sequenceDiagram
    participant D as user
    participant C as Platform core
    participant A as Mobile phone verification code authentication factors plugin
    participant B as SMS plugin
    
    C->>A: Loading plug -in
    A->>C: Register and monitor the related events of the mobile phone verification code（register/Log in/Reset password, etc.）
    C->>B: Loading plug -in
    B->>C: SMS event
    D->>C: Visit Registration/Log in/Reset password page
    C->>A: Send Create_LOGIN_PAGE_AUTH_Factor event
    A->>C: Response event，Assemble/Log in/Reset the password page element
    C->>D: Rendering/Log in/Reset password page
    D->>A: Enter the mobile phone number，Clicked【send messages】Button，Access SMS sending interface
    A->>B: Generate SMS verification code，Send and_SMS event
    B->>A: Response event，Send a text message
    A->>D: Return to SMS sending results
    D->>C: Enter the relevant information，Clicked【register/Log in/reset Password】Button
    C->>A: Register/Log in/Reset password event
    A->>C: Response event，Complete registration/Log in/Reset password process，Return result
    C->>D: test result，Such as completing registration/Log in the relevant operation to generate token and jump to the desktop，If you complete the reset password operation or not complete the registration/Login operation, it prompts an error

```

* general user：Reset the mobile phone number：

```mermaid
sequenceDiagram
    participant D as user
    participant C as Platform core
    participant A as Mobile phone verification code authentication factors plugin
    participant B as SMS plugin
    
    C->>A: Loading plug -in
    A->>C: Towards“mine - Certification management“ Add a reset mobile phone number element to the page，Register to reset the mobile phone number interface from the core
    C->>B: Loading plug -in
    B->>C: SMS event
    D->>C: access“mine - Certification management“ Reset the mobile phone number function in the page
    D->>A: Enter the mobile phone number，Clicked【send messages】Button，Access SMS sending interface
    A->>B: Generate SMS verification code，Send and_SMS event
    B->>A: Response event，Send a text message
    A->>D: Return to SMS sending results
    D->>C: Enter the verification code information，Clicked【confirm】Button
    C->>A: Access reset mobile phone number interface
    A->>C: Response interface，Check the input parameter，Return result
    C->>D: test result，And prompt whether to complete the change

```

* Administrator user： Replace the user's mobile phone number

```mermaid
sequenceDiagram
    participant D as user
    participant C as Platform core
    participant A as Mobile phone verification code authentication factors plugin
    
    C->>A: Loading plug -in
    A->>C: Towards“user list-Edit user”Page injection of mobile phone number elements
    D->>C: Administrator login，Visiting User List page，Edit the user's mobile phone number and save
    C->>D: Write data to database

```

## Abstract method implementation
* [load](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.load)
* [authenticate](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.authenticate)
* [register](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.register)
* [reset_password](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.reset_password)
* [create_login_page](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.create_login_page)
* [create_register_page](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.create_register_page)
* [create_password_page](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.create_password_page)
* [create_other_page](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.create_other_page)
* [create_auth_manage_page](#extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension.create_auth_manage_page)
* [check_auth_data](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.check_auth_data)
* [fix_login_page](#extension_root.com_longgui_auth_factor_authcode.AuthCodeAuthFactorExtension.fix_login_page)

## Code

::: extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension
    rendering:
        show_source: true

::: extension_root.com_longgui_auth_factor_mobile.sms
    rendering:
        show_source: true


