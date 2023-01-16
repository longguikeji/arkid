## Features
Application protocol，Other types of plug -in can be inherited by inherit the protocol base class，How to get a base class，Convenient plug -in load

## Implementation

first step，Create a new class，Inherit the base class

Step 2，[LOAD] (load] (load] (LOAD] (#arkid.core.extension.app_protocol.AppProtocolExtension.Load) method

* Need to use the application schema to use [register_app_protocol_schema](#arkid.core.extension.app_protocol.AppProtocolExtension.register_app_protocol_schema) method loaded in
* Optional，If the application needs to use the application import authentication method implemented by the base class，Need to call [register_enter_view](#arkid.core.extension.app_protocol.AppProtocolExtension.register_enter_View) method

third step，Implement the abstract method specified in the base class

## Abstract method
* [create_app](#arkid.core.extension.app_protocol.AppProtocolExtension.create_app)
* [update_app](#arkid.core.extension.app_protocol.AppProtocolExtension.update_app)
* [delete_app](#arkid.core.extension.app_protocol.AppProtocolExtension.delete_app)

## Foundation definition

::: arkid.core.extension.app_protocol.AppProtocolExtension
    rendering:
        show_source: true

## Exemplary

::: extension_root.com_longgui_app_protocol_oidc.OAuth2ServerExtension
    rendering:
        show_source: true
