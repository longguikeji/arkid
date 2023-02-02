## Features

Authentication：Including mobile phone SMS verification code，Username Password，A series of plug -in with graphics verification code, etc.，Used to identify user identity or improve system security。

## Implementation

When developers create a new authentication factors，You need to inherit the AuthFactorextension base class and implement all abstract methods，The data process of the certification factor plug -in during operation is shown in the figure below：

```mermaid
sequenceDiagram
    participant U as Client
    participant C as Platform core
    participant B as Certification factors plugin
    
    C->>B: Loading plug -in
    B->>C: Registration monitoring custom event：Certification，register，reset Password，Create_LOGIN_PAGE_AUTH_FACTOR
    U->>C: Request to get the login page
    C->>B: Trigger Create_LOGIN_PAGE_AUTH_Factor event
    B->>C: Response event，Traversing all running configuration，Configure Login according to the configuration of running_pages
    C->>U: Rendering login page
    U->>C: Enter user voucher，Click the button，Enter the certification/register/Reset password and other processes
    C->>B: Trigger certification registration/Reset password and other events
    B->>C: Response certification registration/Reset password and other events，Complete the corresponding process，Return result
    C->>U: Return to execution results
```

## Abstract method

* [authenticate](#arkid.core.extension.auth_factor.AuthFactorExtension.authenticate)
* [register](#arkid.core.extension.auth_factor.AuthFactorExtension.register)
* [reset_password](#arkid.core.extension.auth_factor.AuthFactorExtension.reset_password)
* [create_login_page](#arkid.core.extension.auth_factor.AuthFactorExtension.create_login_page)
* [create_register_page](#arkid.core.extension.auth_factor.AuthFactorExtension.create_register_page)
* [create_password_page](#arkid.core.extension.auth_factor.AuthFactorExtension.create_password_page)
* [create_other_page](#arkid.core.extension.auth_factor.AuthFactorExtension.create_other_page)
* [create_auth_manage_page](#arkid.core.extension.auth_factor.AuthFactorExtension.create_auth_manage_page)

## Foundation definition

::: arkid.core.extension.auth_factor.AuthFactorExtension
    rendering:
        show_source: true
    
## Exemplary

::: extension_root.com_longgui_auth_factor_mobile.MobileAuthFactorExtension
    rendering:
        show_source: true

::: extension_root.com_longgui_auth_factor_password.PasswordAuthFactorExtension
    rendering:
        show_source: true
