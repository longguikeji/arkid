## Features
Display the ARKID login page (password、Before mobile phone)，The system will traverse the automatic login plug -in (such as Keberos) **authenticate** method，If one of the plug -in certification is successful，Then you can log in immediately

## Implementation
* Call the ARKID system before entering the ARKID system **/api/v1/login/** interface，In the processing function of this interface，URL Query Params and **/api/v1/login_process/** Parameter rendering **templates/login_enter.html** Template returns to the browser，JavaScript code in the browser execution template，
Judge URL Query Parmas Whether there is token， If there is，Save in LocalStorage，if there is not，Take the token in LocalStorage，At last，Reset to the browser to **/api/v1/login_process** And bring token and url Query Parmas as query parameters
* Enter **/api/v1/login_process/**After the processing function of the interface，Will determine whether there is token in the query parameter，If there is token，After verifying Token is valid，If there is NEXT in the query parameter, Direct redirection to the URL pointed by Next，If not, redirect to the front -end login page；If there is no token or token, it will fail，
Then distribute auto_Login event，And traverse the event distribution back result，If one of the automatic authentication plug -in certification is successful and returned to User，Then refresh the user token，Bring token redirection **/api/v1/login/** ，If all automatic authentication plugins have failed to authenticate，Reset to the front -end login page

## Abstract method
* [authenticate](#arkid.core.extension.auto_auth.AutoAuthExtension.authenticate)

!!! hint
    authenticate The certification should be returned to User, If it fails to return to None，If similar Kerberos certification, you need to enter Authenticate twice，The first time you should enter should be returned to httpResponse The status code is 401
## Foundation definition

::: arkid.core.extension.auto_auth.AutoAuthExtension
    rendering:
        show_source: true
    

        
