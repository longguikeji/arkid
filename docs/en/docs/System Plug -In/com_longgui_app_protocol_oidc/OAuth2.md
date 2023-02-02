# OAuth2

OAuth2Is an authorized open agreement

## Four authorization modes

The client must be authorized by the user（authorization grant），Only to get token（access token）。[rfc 6749](https://www.rfc-editor.org/rfc/RFC6749) Definition of four authorization methods。

* Authorization code mode（authorization code）
* Simplified mode（implicit）
* Password（password）
* Client mode（client credentials）

### Authorization code mode（authorization code）

Authorization code mode（authorization code）It is the most complete function、The strictest process、The most authorized mode of use。It is characterized by the background server of the client，and"service provider"The authentication server interacts。
Since this is a process -based process，The client must be capable and resource owner's USER-agent（Usually web browser）Interact，And have the ability to receive the redirection request from the authorized server。

[![BOwzL9.png](https://v1.ax1x.com/2022/12/12/BOwzL9.png)](https://zimgs.com/i/BOwzL9)

Its steps are as follows：
```
（A）User access client，The latter will guide the former -oriented authentication server (ARKID)。
（B）Users choose whether to give client authorization。
（C）Suppose users authorize，Certification server (ARKID) specifies the user to the client in advance"Reset to URI"（redirection URI），At the same time, an authorization code is attached。
（D）The client receives the authorization code，Earlier"Reset to URI"，Apply to the certification server (ARKID)。This step is done on the server of the client's background，No visible to users。
（E）Authentication server (ARKID) checks the authorization code and redirect to the URI，After confirmation，Send access to the client（access token）And update token（refresh token）。
```

### Simplified mode（implicit）

Simplified mode（implicit grant type）Server without third -party applications，Apply directly to the certification server to apply to the certification server in the browser，Skip"Authorization code"This step，。All steps are completed in the browser，The token is visible to the visitors。

[![BOw4GY.png](https://v1.ax1x.com/2022/12/12/BOw4GY.png)](https://zimgs.com/i/BOw4GY)

Its steps are as follows：
```
（A）The client will guide the user -oriented authentication server (ARKID)。
（B）The user decides whether to authorize the client。
（C）Suppose users authorize，Certification server (ARKID) specifies the user -oriented client"Reset to URI"，And in the Hash part of the URI, the access token is included。
（D）The browser sends a request to the resource server，It does not include the hash value received in the previous step。
（E）Resource server returns a web page，The code contains can get the token in the hash value。
（F）The browser executes the script obtained in the previous step，Extract。
（G）The browser sends the token to the client。
```

### Password（password）

Password（Resource Owner Password Credentials Grant）middle，Users provide their own username and password to the client。Use this information on the client，Towards"Service provider"Be authorized。
In this mode，Users must give their passwords to the client，But the client must not store the password。Risk，Therefore, it is only applicable to other authorization methods，And it must be a highly trusted application of users。

[![BOwCzH.png](https://v1.ax1x.com/2022/12/12/BOwCzH.png)](https://zimgs.com/i/BOwCzH)

Its steps are as follows：
```
（A）Users provide user names and passwords to the client。
（B）The client sends the username and password to the certification server，Ask the latter to token。
（C）Authentic server (ARKID) confirmed that it is correct，Provide access to the client。
```

### Client mode（client credentials）

Client mode（Client Credentials Grant）Refers to the client in its own name，Instead of the name of the user，Towards"Service provider (ARKID)"Certify。Strictly speaking，The client mode does not belong to the problem that the OAUTH framework is to solve。In this mode，Users register directly to the client，The client is in its own name"Service provider (ARKID)"Provide services。

[![BOwJoZ.png](https://v1.ax1x.com/2022/12/12/BOwJoZ.png)](https://zimgs.com/i/BOwJoZ)

Its steps are as follows：
```
（A）The client conducts identity authentication to the certification server，And ask a access token。
（B）After the authentication server is confirmed, it is correct，Provide access to the client。
```
## Client type

according to OAuth 2.0 specification，Applications can be divided into confidential or public。The main difference is whether the application can hold the credentials safely（For example client ID and secret）。This will affect the type verification type that the application can use。

* confidential（confidential）
* public（public）

### confidential（confidential）

Confidential applications can save secret in a safe way，Will not expose it to unauthorized。They need a trusted back -end server to store Secret。You can use HS256 encryption and RS256 encryption

### public（public）

Public applications cannot safely hold Secret，Can only use RS256 encryption。


## Add OAUTH2 application

=== "Open the application list"
    [![X55Ch4.md.jpg](https://s1.ax1x.com/2022/06/14/X55Ch4.md.jpg)](https://imgtu.com/i/X55Ch4)

=== "Click to create，Fill in the form"
    After clicking to confirm，Dialog box closed，You can see the application you created。
    [![XT9IET.md.jpg](https://s1.ax1x.com/2022/06/15/XT9IET.md.jpg)](https://imgtu.com/i/XT9IET)

=== "Click the protocol configuration"
    [![XT9LvR.md.jpg](https://s1.ax1x.com/2022/06/15/XT9LvR.md.jpg)](https://imgtu.com/i/XT9LvR)

=== "Fill in configuration"
    Application type selection as OIDC，Fill in the parameter，Complete
    [![XTCP8H.md.jpg](https://s1.ax1x.com/2022/06/15/XTCP8H.md.jpg)](https://imgtu.com/i/XTCP8H)

=== "Click the protocol configuration again"
    You can view all related parameters of the protocol。
    [![XTCMGQ.md.jpg](https://s1.ax1x.com/2022/06/15/XTCMGQ.md.jpg)](https://imgtu.com/i/XTCMGQ)

## How to hide the license page
If the hidden authorization page switch is turned on，It will not allow users to choose whether to authorize，The user has logged in and directly authorized successfully，Enter the redirection page provided
[![BOwjHU.jpg](https://v1.ax1x.com/2022/12/12/BOwjHU.jpg)](https://zimgs.com/i/BOwjHU)

## Use OAUTH2 Application

1.  ### Understand the meaning of the page field field

    [![XTirE6.md.jpg](https://s1.ax1x.com/2022/06/15/XTirE6.md.jpg)](https://imgtu.com/i/XTirE6)

    | English parameter name        | Corresponding page surface field                          |
    | :---------:    | :----------------------------------: |
    | `redirect url`      | Callback address  |
    | `client_id`      | Client ID  |
    | `client_token`     | Client key |
    | `authorize url`        | Authorized URL |
    | `get token url` | Get ACCESS_Token address |
    | `userinfo url`   | User information address |
    | `logout url`   | Exit login address |


2.  ### Get Authorization Code

    - Request address: `authorize url`
    - Way of requesting: GET(**Redirect**)
    - Request parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `client_id`    | `client_id`  |         
    | `redirect_uri` | `redirect url` |         
    | `response_type`| Fill in Code |   code     
    | `scope`        | Optional ( openid userinfo) |  If you pass openid，Get token more ID will_token

    - Request example: http://authorize url/?client_id=xxxxx&redirect_uri=xxxxx&response_type=code&scope=userinfo
    - Return parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `code`    | Authorization code  |         

    - Return sample: http://redirect_uri?code=As a savings, the seventh seven&token=Sadaa 4840, and I will be 04 with a 4 -wing 1 bastard 1 b 176


3.  ### Get ACCESS Token

    - Request address: `get token url`
    - Way of requesting: POST
    - Request head parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `Authorization`    | tokenFormat client_id:client_secret Use base64 encoding  |  Basic Token
    | `Content-Type` | Fill in MULTIPART/form-data |

    - Request parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `code`    | Authorization code  |         
    | `grant_type` | Fill in Authorization_code |


    - Request example:

    [![XoX9Z4.md.jpg](https://s1.ax1x.com/2022/06/15/XoX9Z4.md.jpg)](https://imgtu.com/i/XoX9Z4)

    - Return parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `access_token`    | Token  |         
    | `expires_in` | Expiration |
    | `token_type` | Bearer |
    | `scope` | userinfo openid |
    | `refresh_token` | Token to token |

    - Return sample: 
    ``` json
    {
        "access_token": "cFcWq78HH9MKVQOFJgGPl6RFtESAc2",
        "expires_in": 36000,
        "token_type": "Bearer",
        "scope": "userinfo",
        "refresh_token": "oRHcgoGYsL5h1UimT4rWcg93lcTyjN"
    }
    ```


4.  ### Get user information

    - Request address: `userinfo url`
    - Way of requesting: GET
    - Request head parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `Authorization`    | Bearer access_token  |  Bearer cFcWq78HH9MKVQOFJgGPl6RFtESAc2

    - Return parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `id`    | User ID  |         
    | `name` | user name |
    | `sub` | User ID |
    | `sub_id` | User ID |
    | `preferred_username` | username |
    | `groups` | User group |
    | `tenant_id` | Tenant ID |
    | `tenant_slug` | Practitioner Slug |

    - Return sample: 
    ``` json
    {
        "id": "faf5aae6-3cdf-4595-8b4a-3a06b31117c8",
        "name": "admin",
        "sub": "faf5aae6-3cdf-4595-8b4a-3a06b31117c8",
        "sub_id": "faf5aae6-3cdf-4595-8b4a-3a06b31117c8",
        "preferred_username": "admin",
        "groups": [
        ],
        "tenant_id": "4da114ce-e115-44a0-823b-d372114425d0",
        "tenant_slug": ""
    }
    ```

5.  ### Refresh token
    
    This step is a option.，You can use this interface to replace the new token

    - Request address: `get token url`
    - Way of requesting: POST
    - Request head parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `Authorization`    | This token is client_id and client_secret  |  Basic Token
    | `Content-Type` | Fill in MULTIPART/form-data |

    - Request parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `refresh_token`    | Update token  |         
    | `grant_type` | Fill in Refresh_token |


    - Request example:

    [![XozCX6.md.jpg](https://s1.ax1x.com/2022/06/15/XozCX6.md.jpg)](https://imgtu.com/i/XozCX6)

    - Return parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `access_token`    | Token  |         
    | `expires_in` | Expiration |
    | `token_type` | Bearer |
    | `scope` | userinfo openid |
    | `refresh_token` | Token to token |

    - Return sample: 
    ``` json
    {
        "access_token": "51s34LPxhhKlUTP5r5mHevGW7ussXC",
        "expires_in": 36000,
        "token_type": "Bearer",
        "scope": "userinfo",
        "refresh_token": "68trmzGvLmmbjACnHFGgzoCl5LBOrJ"
    }
    ```
