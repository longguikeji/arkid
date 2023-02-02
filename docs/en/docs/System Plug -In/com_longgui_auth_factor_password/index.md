# Password authentication factors
## Features

User table extension password field，Allow users to certify through the user name and password，register。

general user：

* exist “mine - Certification management“ The function of adding a reset password
* exist “register” Page implementation user name and password registration
* exist “Log in” Page implementation user name password login

Tenant administrator

* exist”User Management - user list“The function of adding a reset password

## Configuration guide
## Configuration guide

=== "Plug -in lease"
    Enter through the menu bar on the left【Tenant management】->【Plug -in management】，Find the password authentication factor plug -in card in the plug -in lease page，Click to rent<br/>
    [![vEoE7j.png](https://s1.ax1x.com/2022/08/02/vEoE7j.png)](https://imgtu.com/i/vEoE7j)

=== "Certification factor configuration"
    Enter through the menu bar on the left【Certification management】-> 【Authentication】,Click to create button，Type selection"password",Fill in related information，The configuration is completed<br/>
    [![vEoU9x.md.png](https://s1.ax1x.com/2022/08/02/vEoU9x.md.png)](https://imgtu.com/i/vEoU9x)

=== "login interface"
    [![vEoWgf.md.png](https://s1.ax1x.com/2022/08/02/vEoWgf.md.png)](https://imgtu.com/i/vEoWgf)

=== "Registration interface"
    [![vEoXvT.png](https://s1.ax1x.com/2022/08/02/vEoXvT.png)](https://imgtu.com/i/vEoXvT)

=== "Change the password interface"
    Enter from the user avatar menu【Certification management】interface,Choose to change the password tab page<br/>
    [![vEo6UA.md.png](https://s1.ax1x.com/2022/08/02/vEo6UA.md.png)](https://imgtu.com/i/vEo6UA)

## Implementation

general user：register/Log in：

```mermaid
sequenceDiagram
    participant D as user
    participant C as Platform core
    participant A as Password authentication factors plug -in
    
    C->>A: Loading plug -in
    A->>C: Register and monitor password certification related events（register/Register）
    D->>C: Visit Registration/log in page
    C->>A: Send Create_LOGIN_PAGE_AUTH_Factor event
    A->>C: Response event，Assemble/Login page element
    C->>D: Rendering/Log in/Reset password page
    D->>C: Enter the relevant information，Clicked【register/Log in】Button
    C->>A: Register/Login event
    A->>C: Response event，Complete registration/Login process，Return result
    C->>D: test result，Such as completing registration/Log in the relevant operation to generate token and jump to the desktop，If the registration is not completed/Login operation, it prompts an error

```

general user：reset Password：

```mermaid
sequenceDiagram
    participant D as user
    participant C as Platform core
    participant A as Password authentication factors plug -in
    
    C->>A: Loading plug -in
    A->>C: Towards“mine - Certification management“ Add reset password elements to the page，Register to reset the password interface to the core
    D->>C: access“mine - Certification management“ Reset the password function in the page，Enter the new password
    C->>A: Access reset password interface
    A->>C: Response interface，Check the input parameter，Return result
    C->>D: test result，And prompt whether to complete the change

```

Administrator user： Reset the user password

```mermaid
sequenceDiagram
    participant D as user
    participant C as Platform core
    participant A as Password authentication factors plug -in
    
    C->>A: Loading plug -in
    A->>C: Towards“user list-Edit user”Page injection password element，Inject password fields into the core user model
    D->>C: Administrator login，Visiting User List page，Edit user password，Click to save
    C->>D: Modify the password field value and save to the database
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

::: extension_root.com_longgui_auth_factor_password.PasswordAuthFactorExtension
    rendering:
        show_source: true

