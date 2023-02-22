# OIDC

OIDC是基于OAuth2和OpenID整合的新认证授权协议

## 四种授权模式

客户端必须得到用户的授权（authorization grant），才能获得令牌（access token）。[rfc 6749](https://www.rfc-editor.org/rfc/rfc6749)定义了四种授权方式。

* 授权码模式（authorization code）
* 简化模式（implicit）
* 密码模式（password）
* 客户端模式（client credentials）

### 授权码模式（authorization code）

授权码模式（authorization code）是功能最完整、流程最严密、使用最多的授权模式。它的特点就是通过客户端的后台服务器，与"服务提供商"的认证服务器进行互动。
由于这是一个基于重定向的流程，客户端必须有能力和资源拥有者的user-agent（通常为WEB浏览器）进行交互，并且有能力接收来自授权服务器的重定向请求。

[![BOwzL9.png](https://v1.ax1x.com/2022/12/12/BOwzL9.png)](https://zimgs.com/i/BOwzL9)

它的步骤如下：
```
（A）用户访问客户端，后者将前者导向认证服务器(arkid)。
（B）用户选择是否给予客户端授权。
（C）假设用户给予授权，认证服务器(arkid)将用户导向客户端事先指定的"重定向URI"（redirection URI），同时附上一个授权码。
（D）客户端收到授权码，附上早先的"重定向URI"，向认证服务器(arkid)申请令牌。这一步是在客户端的后台的服务器上完成的，对用户不可见。
（E）认证服务器(arkid)核对了授权码和重定向URI，确认无误后，向客户端发送访问令牌（access token）和更新令牌（refresh token）。
```

### 简化模式（implicit）

简化模式（implicit grant type）不通过第三方应用程序的服务器，直接在浏览器中向认证服务器申请令牌，跳过了"授权码"这个步骤，。所有步骤在浏览器中完成，令牌对访问者是可见的。

[![BOw4GY.png](https://v1.ax1x.com/2022/12/12/BOw4GY.png)](https://zimgs.com/i/BOw4GY)

它的步骤如下：
```
（A）客户端将用户导向认证服务器(arkid)。
（B）用户决定是否给于客户端授权。
（C）假设用户给予授权，认证服务器(arkid)将用户导向客户端指定的"重定向URI"，并在URI的Hash部分包含了访问令牌。
（D）浏览器向资源服务器发出请求，其中不包括上一步收到的Hash值。
（E）资源服务器返回一个网页，其中包含的代码可以获取Hash值中的令牌。
（F）浏览器执行上一步获得的脚本，提取出令牌。
（G）浏览器将令牌发给客户端。
```

### 密码模式（password）

密码模式（Resource Owner Password Credentials Grant）中，用户向客户端提供自己的用户名和密码。客户端使用这些信息，向"服务商提供商"索要授权。
在这种模式中，用户必须把自己的密码给客户端，但是客户端不得储存密码。风险很大，因此只适用于其他授权方式都无法采用的情况，而且必须是用户高度信任的应用。

[![BOwCzH.png](https://v1.ax1x.com/2022/12/12/BOwCzH.png)](https://zimgs.com/i/BOwCzH)

它的步骤如下：
```
（A）用户向客户端提供用户名和密码。
（B）客户端将用户名和密码发给认证服务器，向后者请求令牌。
（C）认证服务器(arkid)确认无误后，向客户端提供访问令牌。
```

### 客户端模式（client credentials）

客户端模式（Client Credentials Grant）指客户端以自己的名义，而不是以用户的名义，向"服务提供商(arkid)"进行认证。严格地说，客户端模式并不属于OAuth框架所要解决的问题。在这种模式中，用户直接向客户端注册，客户端以自己的名义要求"服务提供商(arkid)"提供服务。

[![BOwJoZ.png](https://v1.ax1x.com/2022/12/12/BOwJoZ.png)](https://zimgs.com/i/BOwJoZ)

它的步骤如下：
```
（A）客户端向认证服务器进行身份认证，并要求一个访问令牌。
（B）认证服务器确认无误后，向客户端提供访问令牌。
```
## 客户端类型

根据 OAuth 2.0 规范，应用程序可以分为机密的或公开的。主要区别在于应用程序是否能够安全地持有凭据（例如client ID和secret）。这会影响应用程序可以使用的身份验证类型。

* 机密（confidential）
* 公开（public）

### 机密（confidential）

机密应用程序可以以安全的方式保存secret，而不会将其暴露给未经授权的方。他们需要一个受信任的后端服务器来存储secret。可以使用HS256加密和RS256加密

### 公开（public）

公开的应用程序无法安全地持有secret，只能使用RS256加密。

## 添加OIDC应用

=== "打开应用列表"
    [![X55Ch4.md.jpg](https://s1.ax1x.com/2022/06/14/X55Ch4.md.jpg)](https://imgtu.com/i/X55Ch4)

=== "点击创建，填写表单"
    点击确认后，对话框关闭，可以看到你创建的应用。
    [![XonRpV.md.jpg](https://s1.ax1x.com/2022/06/15/XonRpV.md.jpg)](https://imgtu.com/i/XonRpV)

=== "点击协议配置"
    [![XouEjS.md.jpg](https://s1.ax1x.com/2022/06/15/XouEjS.md.jpg)](https://imgtu.com/i/XouEjS)

=== "填写配置"
    应用类型选择为OIDC，填写参数，创建完毕
    [![XoK9rF.md.jpg](https://s1.ax1x.com/2022/06/15/XoK9rF.md.jpg)](https://imgtu.com/i/XoK9rF)

=== "再次点击协议配置"
    即可查看该协议所有相关的参数。
    [![XoMPQf.md.jpg](https://s1.ax1x.com/2022/06/15/XoMPQf.md.jpg)](https://imgtu.com/i/XoMPQf)

## 如何隐藏授权页
如果打开了隐藏授权页开关，则不会让用户选择是否授权，用户已登录就直接授权成功，进入提供的重定向页
[![BOwjHU.jpg](https://v1.ax1x.com/2022/12/12/BOwjHU.jpg)](https://zimgs.com/i/BOwjHU)

## 使用OIDC应用

1.  ### 明白页面字段含义

    [![XoJCND.md.jpg](https://s1.ax1x.com/2022/06/15/XoJCND.md.jpg)](https://imgtu.com/i/XoJCND)

    | 英文参数名称        | 对应页面字段                          |
    | :---------:    | :----------------------------------: |
    | `redirect url`      | 回调地址  |
    | `client_id`      | 客户端id  |
    | `client_token`     | 客户端秘钥 |
    | `authorize url`        | 授权url |
    | `get token url` | 获取access_token地址 |
    | `userinfo url`   | 用户信息地址 |
    | `logout url`   | 退出登录地址 |


2.  ### 获取Authorization Code

    - 请求地址: `authorize url`
    - 请求方式: GET(**重定向**)
    - 请求参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `client_id`    | `client_id`  |         
    | `redirect_uri` | `redirect url` |         
    | `response_type`| 填入code |   code     
    | `scope`        | 可选 ( openid userinfo) |  如果传递openid，获取token会多一个id_token

    - 请求示例: http://authorize url/?client_id=xxxxx&redirect_uri=xxxxx&response_type=code&scope=userinfo
    - 返回参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `code`    | 授权码  |         

    - 返回示例: http://redirect_uri?code=XEV8esOvaVk9wyAuiNXpb3Nuwn5av9&token=cd34840ffc804b894ede31bc21b176ef559e137f


3.  ### 获取Access Token

    - 请求地址: `get token url`
    - 请求方式: POST
    - 请求头参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `Authorization`    | token格式为 client_id:client_secret 使用base64编码  |  Basic Token
    | `Content-Type` | 填入multipart/form-data |

    - 请求参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `code`    | 授权码  |         
    | `grant_type` | 填入authorization_code |


    - 请求示例:

    [![XoX9Z4.md.jpg](https://s1.ax1x.com/2022/06/15/XoX9Z4.md.jpg)](https://imgtu.com/i/XoX9Z4)

    - 返回参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `access_token`    | 令牌  |         
    | `expires_in` | 过期时间 |
    | `token_type` | Bearer |
    | `scope` | userinfo openid |
    | `refresh_token` | 用于更新令牌的令牌 |

    - 返回示例: 
    ``` json
    {
        "access_token": "yytknMlZC6P6cIqPnN0XPRPEBRVf2X",
        "expires_in": 36000,
        "token_type": "Bearer",
        "scope": "userinfo openid",
        "refresh_token": "2rw6Bn0BZuVjll0KKWGg7DYJTdlACC",
        "id_token": "xxxxx"
    }
    ```


4.  ### 获取用户信息

    - 请求地址: `userinfo url`
    - 请求方式: GET
    - 请求头参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `Authorization`    | Bearer access_token  |  Bearer cFcWq78HH9MKVQOFJgGPl6RFtESAc2

    - 返回参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `id`    | 用户id  |         
    | `name` | 用户名称 |
    | `sub` | 用户id |
    | `sub_id` | 用户id |
    | `preferred_username` | 用户名 |
    | `groups` | 用户分组 |
    | `tenant_id` | 租户id |
    | `tenant_slug` | 租户slug |

    - 返回示例: 
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

5.  ### 刷新token
    
    这一步是可选的如果颁发的令牌过了有效期，可以使用这个接口更换新的令牌

    - 请求地址: `get token url`
    - 请求方式: POST
    - 请求头参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `Authorization`    | 这个token由client_id和client_secret生成  |  Basic Token
    | `Content-Type` | 填入multipart/form-data |

    - 请求参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `refresh_token`    | 更新令牌  |         
    | `grant_type` | 填入refresh_token |


    - 请求示例:

    [![XozCX6.md.jpg](https://s1.ax1x.com/2022/06/15/XozCX6.md.jpg)](https://imgtu.com/i/XozCX6)

    - 返回参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `access_token`    | 令牌  |         
    | `expires_in` | 过期时间 |
    | `token_type` | Bearer |
    | `scope` | userinfo openid |
    | `refresh_token` | 用于更新令牌的令牌 |

    - 返回示例: 
    ``` json
    {
        "access_token": "51s34LPxhhKlUTP5r5mHevGW7ussXC",
        "expires_in": 36000,
        "token_type": "Bearer",
        "scope": "userinfo",
        "refresh_token": "68trmzGvLmmbjACnHFGgzoCl5LBOrJ"
    }
    ```


6.  ### 退出oidc
    
    这一步是可选的，可以退出用户登录，并跳转到指定地址

    - 请求地址: `logout url`
    - 请求方式: GET
    - 请求参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `id_token_hint`    | id_token(这个id_token需从获取AccessToken接口中获取)  |         
    | `post_logout_redirect_uri` | 退出登录后跳转的地址(可选) |

    - 请求示例: 
    ``` text
    http://logout_url?id_token_hint=xxxx&post_logout_redirect_uri=xxxxx
    ```

    - 返回参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `error_code`    | 错误码  |         
    | `error_msg` | 错误信息 |

    - 返回示例: 
    ``` json
    {
        "error_code":0,
        "error_msg":"logout success"
    }
    ```