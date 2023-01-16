## Features
worth mentioning，In fact, log in with other IDP system accounts，The process of binding the account of ARKID。

Classic：WeChat login，Login，Flying Book Login and so on。

## Implementation

Because most of the third -party login schemes are derivatives based on the OAUTH2 protocol，Therefore, the process of the tripartite certification is based。

first,Create a third -party certification entrance on the login page，Dedication of this entrance:

* icon: [get_img_url](#arkid.core.extension.external_idp.ExternalIdpExtension.get_img_url)
* Third -party login request [Arkid.core.extension.external_idp.ExternalIdpExtension.login](#arkid.core.extension.external_idp.ExternalIdpExtension.login), The request will redirect the entrance address of the third party login, The entrance address is [get_authorize_url](#arkid.core.extension.external_idp.ExternalIdpExtension.get_authorize_URL)

When the user clicks the icon，After initiating a third -party certification request， Will return to [Arkid.core.extension.external_idp.ExternalIdpExtension.callback](#arkid.core.extension.external_idp.ExternalIdpExtension.callback) interface，And Code

In callback，Code call [get_ext_token_by_code](#arkid.core.extension.external_idp.ExternalIdpExtension.get_ext_token_by_code) method，Get ACCESS_token， Then via access_token call [get_user_info_by_ext_token](#arkid.core.extension.external_idp.ExternalIdpExtension.get_user_info_by_ext_Token) method to get user information

* If the third party certification returns EXT_ID is not bound to users in Arkid，The front end will jump to the binding page，Call [Arkid.core.extension.external_idp.ExternalIdpExtension.bind](#arkid.core.extension.external_idp.ExternalIdpExtension.bind) interface, This interface will call [bind_arkid_user](#arkid.core.extension.external_idp.ExternalIdpExtension.bind_arkid_User) Method binds EXT_ID to Arkid users

* If the third party certification returns EXT_ID has been bound to users in Arkid，Call [get_arkid_user](#arkid.core.extension.external_idp.ExternalIdpExtension.get_arkid_User) Method obtain an arkid user that has been bound

To complete the login at this point

## Abstract method
* [get_img_url](#arkid.core.extension.external_idp.ExternalIdpExtension.get_img_url)
* [get_authorize_url](#arkid.core.extension.external_idp.ExternalIdpExtension.get_authorize_url)
* [get_ext_token_by_code](#arkid.core.extension.external_idp.ExternalIdpExtension.get_ext_token_by_code)
* [get_user_info_by_ext_token](#arkid.core.extension.external_idp.ExternalIdpExtension.get_user_info_by_ext_token)
* [get_arkid_user](#arkid.core.extension.external_idp.ExternalIdpExtension.get_arkid_user)
## Foundation definition

::: arkid.core.extension.external_idp.ExternalIdpExtension
    rendering:
        show_source: true
    
## Exemplary

::: extension_root.com_longgui_external_idp_github.ExternalIdpGithubExtension
    rendering:
        show_source: true
        
