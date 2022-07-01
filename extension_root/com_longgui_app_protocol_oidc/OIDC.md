# OIDC

OIDC是基于OAuth2和OpenID整合的新认证授权协议

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
    ![XoMPQf.md.jpg](https://s1.ax1x.com/2022/06/15/XoMPQf.md.jpg)](https://imgtu.com/i/XoMPQf)


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
    - 请求方式: GET
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
    | `Authorization`    | 这个token由client_id和client_secret生成  |  Basic Token
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
        "access_token": "cFcWq78HH9MKVQOFJgGPl6RFtESAc2",
        "expires_in": 36000,
        "token_type": "Bearer",
        "scope": "userinfo",
        "refresh_token": "oRHcgoGYsL5h1UimT4rWcg93lcTyjN"
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
    | `id_token_hint`    | id_token  |         
    | `post_logout_redirect_uri` | 退出登录后跳转的地址(可选) |

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