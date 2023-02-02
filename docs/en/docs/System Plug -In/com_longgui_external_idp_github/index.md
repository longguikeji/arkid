# Github Third -party login plug -in

## Features
After configured GitHub plug -in，You can click the github icon on the Arkid login page，Jump to GitHub website to complete OAATH2 certification，And bind to the user of Arkid

### Create GitHub applications

=== "Open the setting page to create GitHub developers"
    [![X7Ew38.png](https://s1.ax1x.com/2022/06/16/X7Ew38.png)](https://imgtu.com/i/X7Ew38)

=== "Click to create，Fill in the form"
    name，The homepage URL and callback URL can be filled in freely，The steps will be changed to ARKID automatic URL after the step back the URL。
    [![X7E0gS.png](https://s1.ax1x.com/2022/06/16/X7E0gS.png)](https://imgtu.com/i/X7E0gS)

=== "Generate client Secret"
    [![X7EruQ.png](https://s1.ax1x.com/2022/06/16/X7EruQ.png)](https://imgtu.com/i/X7EruQ)

=== "Save client Id and client Secret"
    [![X7EBjg.png](https://s1.ax1x.com/2022/06/16/X7EBjg.png)](https://imgtu.com/i/X7EBjg)

### Create Arkid third -party login configuration,Get the recovery URL

=== "Open the third -party certification page"
    [![X7Ef3T.png](https://s1.ax1x.com/2022/06/16/X7Ef3T.png)](https://imgtu.com/i/X7Ef3T)

=== "Fill in the form parameter， Click to create"
    [![X7E4vF.png](https://s1.ax1x.com/2022/06/16/X7E4vF.png)](https://imgtu.com/i/X7E4vF)

=== "Click the editor button，Get ARKID callback URL"
    [![X7EhgU.png](https://s1.ax1x.com/2022/06/16/X7EhgU.png)](https://imgtu.com/i/X7EhgU)

### Update github application callback URL，Click the login button

=== "Re -set up GitHub application callback URL"
    [![X7EWCV.png](https://s1.ax1x.com/2022/06/16/X7EWCV.png)](https://imgtu.com/i/X7EWCV)


=== "Click GitHub icon on the login page"
    [![X7V4it.png](https://s1.ax1x.com/2022/06/16/X7V4it.png)](https://imgtu.com/i/X7V4it)

=== "Click the certification button"
    [![X7VfII.png](https://s1.ax1x.com/2022/06/16/X7VfII.png)](https://imgtu.com/i/X7VfII)
    
## Implementation
Abstract methods to cover the base class of plug -in，See [ARKID.core.extension.external_idp.ExternalIdpExtension](../../%20%20 Developer Guide/%20 plug -in classification/worth mentioning/)

# Unified binding and unbinding instructions
See [three -party account binding] (../../%20%20%20UserGuide/User Manual/%20 ordinary users/Certification management/Three -party account binding/)
## Abstract method implementation:
* [get_img_url](#extension_root.com_longgui_external_idp_github.ExternalIdpGithubExtension.get_img_url)
* [get_authorize_url](#extension_root.com_longgui_external_idp_github.ExternalIdpGithubExtension.get_authorize_url)
* [get_ext_token_by_code](#extension_root.com_longgui_external_idp_github.ExternalIdpGithubExtension.get_ext_token_by_code)
* [get_user_info_by_ext_token](#extension_root.com_longgui_external_idp_github.ExternalIdpGithubExtension.get_user_info_by_ext_token)
* [get_arkid_user](#extension_root.com_longgui_external_idp_github.ExternalIdpGithubExtension.get_arkid_user)


## Code

::: extension_root.com_longgui_external_idp_github.ExternalIdpGithubExtension
    rendering:
        show_source: true
