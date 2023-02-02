# Miniprogram Third -party login plug -in

## Features
After configuring the miniprogram plug -in，You can click the login and binding method provided by the plug -in，Very convenient to use the applet user，Binding with ARKID users。It can be very convenient to realize the secret login of WeChat applet.

### Configure the basic information of WeChat Mini Program

=== "Log in to WeChat public platform，Enter the applet that needs configuration"
    [![vnmnD1.md.jpg](https://s1.ax1x.com/2022/08/05/vnmnD1.md.jpg)](https://imgtu.com/i/vnmnD1)

=== "Save the app ID and app Secret"
    [![vnmE34.md.jpg](https://s1.ax1x.com/2022/08/05/vnmE34.md.jpg)](https://imgtu.com/i/vnmE34)

### Create Arkid third -party login configuration,Get the recovery URL

=== "Open the third -party certification page"
    [![jzjOud.md.jpg](https://s1.ax1x.com/2022/07/26/jzjOud.md.jpg)](https://imgtu.com/i/jzjOud)

=== "Fill in the form parameter，Click to create"
    [![vnmIGF.md.jpg](https://s1.ax1x.com/2022/08/05/vnmIGF.md.jpg)](https://imgtu.com/i/vnmIGF)

=== "Click the editor button，Get the login address、Binding address、Domain name of the login address"
    [![vnmOVx.md.jpg](https://s1.ax1x.com/2022/08/05/vnmOVx.md.jpg)](https://imgtu.com/i/vnmOVx)

### Update the server domain name of WeChat Mini Program

=== "Configuration server domain name"
    [![vnmNDI.md.jpg](https://s1.ax1x.com/2022/08/05/vnmNDI.md.jpg)](https://imgtu.com/i/vnmNDI)

### How to use the login interface and binding interface

1. Login interface

    - Request address: `login url`
    - Way of requesting: GET
    - Request parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `code`    | `code`  |  Developers call the method provided by the applet to get a code

    - Request example: http://login url/?code=xxxxx
    - Return parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `token`    | `token`  |  User token (only the user has already been bound to have this parameter)
    | `ext_id`    | `ext_id`  |  User ID
    | `tenant_id`    | `tenant_id`  |  Tenant ID
    | `bind`    | `bind`  |  Binding address

    - Return sample:
    ``` json
    {
        "error":"0",
        "package":"com.longgui.external.idp.miniprogram",
        "data":{
            "token":"",
            "ext_id":"o0ByU5cit-Pl3uxeXmsABV4xiRq8",
            "tenant_id":"4da114cee11544a0823bd372114425d0",
            "bind":"http://localhost:8000/api/v1/idp/com_longgui_external_idp_miniprogram/0d1183d2-46e5-409c-924c-438f722de2eb/bind"
        }
    }
    or
    {
        "error":"0",
        "package":"com.longgui.external.idp.miniprogram",
        "data":{
            "token":"f4d8a6976111f9e3cc08d17bd16154a3dba9a2d5"
        }
    }
    ```

2. Binding interface

    - Request address: `bind url`
    - Way of requesting: POST
    - Request head parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `Authorization`    | Token token  |  Token obtained by logid user login

    - Request parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `ext_id`    | `ext_id`  |  Binding ID obtained in the login interface

    - Request example: http://bind url

    - Return sample:
    ``` json
        {
            "error": "0",
            "package": "com.longgui.external.idp.miniprogram"
        }
    ```

### How to get the token of Arkid users

1. login_pageinterface

    - Request address: `/api/v1/tenant/{tenant_id}/login_page/`
    - Way of requesting: GET
    - Return sample:
    ``` json
        {
            "data":{
                "login":{
                    "name":"login",
                    "forms":[
                        {
                            "label":"Username password login",
                            "items":[
                                {
                                    "value":null,
                                    "type":"text",
                                    "placeholder":"username",
                                    "name":"username",
                                    "append":null,
                                    "http":null
                                },
                                {
                                    "value":null,
                                    "type":"password",
                                    "placeholder":"password",
                                    "name":"password",
                                    "append":null,
                                    "http":null
                                },
                                {
                                    "value":"70f8d39e-30cc-40de-8a70-ec6495c21e84",
                                    "type":"hidden",
                                    "placeholder":null,
                                    "name":"config_id",
                                    "append":null,
                                    "http":null
                                }
                            ],
                            "submit":{
                                "prepend":null,
                                "title":"Log in",
                                "tooltip":null,
                                "long":null,
                                "img":null,
                                "gopage":null,
                                "redirect":null,
                                "http":{
                                    "url":"/api/v1/tenant/tenant_id/auth/?event_tag=com.longgui.auth.factor.password.auth",
                                    "method":"post",
                                    "params":null
                                },
                                "delay":null,
                                "agreement":null
                            }
                        }
                    ],
                    "bottoms":[
                        {
                            "prepend":"No account yet，",
                            "title":"Sign up now",
                            "tooltip":null,
                            "long":null,
                            "img":null,
                            "gopage":"register",
                            "redirect":null,
                            "http":null,
                            "delay":null,
                            "agreement":null
                        }
                    ],
                    "extend":{
                        "title":null,
                        "buttons":[
                            {
                                "prepend":null,
                                "title":null,
                                "tooltip":null,
                                "long":null,
                                "img":"https://gitee.com/assets/favicon.ico",
                                "gopage":null,
                                "redirect":{
                                    "url":"http://localhost:8000/api/v1/idp/com_longgui_external_idp_gitee/8fa7fcf2-d906-4da5-a6a8-1382b70863a5/login",
                                    "params":null
                                },
                                "http":null,
                                "delay":null,
                                "agreement":null
                            },
                            {
                                "prepend":null,
                                "title":null,
                                "tooltip":null,
                                "long":null,
                                "img":"https://p6-hera.byteimg.com/tos-cn-i-jbbdkfciu3/f3de430ed2b64f90a95fb8a393dfa6bd~tplv-jbbdkfciu3-image:0:0.image",
                                "gopage":null,
                                "redirect":{
                                    "url":"http://localhost:8000/api/v1/idp/com_longgui_external_idp_feishu/a36d40d6-1374-4503-a8b9-84550d9da24b/login",
                                    "params":null
                                },
                                "http":null,
                                "delay":null,
                                "agreement":null
                            },
                            {
                                "prepend":null,
                                "title":null,
                                "tooltip":null,
                                "long":null,
                                "img":"https://img.onlinedown.net/download/202108/151913-611379f149740.jpg",
                                "gopage":null,
                                "redirect":{
                                    "url":"http://aa.loopbing.top/api/v1/idp/com_longgui_external_idp_wechatwork/5d6b5935-15bb-46b2-a9f6-aa6329e64a9d/login",
                                    "params":null
                                },
                                "http":null,
                                "delay":null,
                                "agreement":null
                            },
                            {
                                "prepend":null,
                                "title":null,
                                "tooltip":null,
                                "long":null,
                                "img":"https://src.onlinedown.net/d/file/p/2019-08-06/2dc4d1b597725835d85259829db3fcff.jpg",
                                "gopage":null,
                                "redirect":{
                                    "url":"http://localhost:8000/api/v1/idp/com_longgui_external_idp_wechatscan/5ac3dec7-44a1-4269-b450-6fe0fd0fe956/login",
                                    "params":null
                                },
                                "http":null,
                                "delay":null,
                                "agreement":null
                            }
                        ]
                    }
                },
                "register":{
                    "name":"register",
                    "forms":[
                        {
                            "label":"Username and password registration",
                            "items":[
                                {
                                    "value":null,
                                    "type":"text",
                                    "placeholder":"username",
                                    "name":"username",
                                    "append":null,
                                    "http":null
                                },
                                {
                                    "value":null,
                                    "type":"password",
                                    "placeholder":"password",
                                    "name":"password",
                                    "append":null,
                                    "http":null
                                },
                                {
                                    "value":null,
                                    "type":"password",
                                    "placeholder":"Password Confirmation",
                                    "name":"checkpassword",
                                    "append":null,
                                    "http":null
                                },
                                {
                                    "value":"70f8d39e-30cc-40de-8a70-ec6495c21e84",
                                    "type":"hidden",
                                    "placeholder":null,
                                    "name":"config_id",
                                    "append":null,
                                    "http":null
                                }
                            ],
                            "submit":{
                                "prepend":null,
                                "title":"register",
                                "tooltip":null,
                                "long":null,
                                "img":null,
                                "gopage":null,
                                "redirect":null,
                                "http":{
                                    "url":"/api/v1/tenant/tenant_id/register/?event_tag=com.longgui.auth.factor.password.register",
                                    "method":"post",
                                    "params":null
                                },
                                "delay":null,
                                "agreement":null
                            }
                        }
                    ],
                    "bottoms":[
                        {
                            "prepend":"Existing account，",
                            "title":"log in immediately",
                            "tooltip":null,
                            "long":null,
                            "img":null,
                            "gopage":"login",
                            "redirect":null,
                            "http":null,
                            "delay":null,
                            "agreement":null
                        }
                    ],
                    "extend":null
                },
                "password":{
                    "name":"password",
                    "forms":[

                    ],
                    "bottoms":[
                        {
                            "prepend":"No account yet，",
                            "title":"Sign up now",
                            "tooltip":null,
                            "long":null,
                            "img":null,
                            "gopage":"register",
                            "redirect":null,
                            "http":null,
                            "delay":null,
                            "agreement":null
                        },
                        {
                            "prepend":"Existing account，",
                            "title":"log in immediately",
                            "tooltip":null,
                            "long":null,
                            "img":null,
                            "gopage":"login",
                            "redirect":null,
                            "http":null,
                            "delay":null,
                            "agreement":null
                        }
                    ],
                    "extend":null
                }
            },
            "tenant":{
                "id":"4da114ce-e115-44a0-823b-d372114425d0",
                "name":"Platform tenant",
                "slug":"",
                "icon":null
            }
        }
    ```

    - Return instruction:
    We need to focus on the Items and submit fields of the 0 objects in the Forms in the Login and Register objects in Data，The http address in submit is the request address，Items array is the request parameter

2. Registered interface

    - Request address: `/api/v1/tenant/{tenant_id}/register/?event_tag=com.Dragon turtle.auth.factor.password.register`
    - Way of requesting: POST
    - Request parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `username`    | `username`  |  username
    | `password`    | `password`  |  password
    | `checkpassword`    | `checkpassword`  |  Repeat the password
    | `config_id`    | `config_id`  |  Configure ID in LOGIN_Page's items have been provided

    - Request example:
    ``` json
        {
            "username":"abcd",
            "password":"abcd",
            "checkpassword":"abcd",
            "config_id":"70f8d39e-30cc-40de-8a70-ec6495c21e84"
        }
    ```

    - Return parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `user`    | `user`  |  User object
    | `id`    | `id`  |  User ID
    | `username`    | `username`  |  username
    | `token`    | `token`  |  User token

    - Request example:
    ``` json
    {
        "error": "0",
        "package": "core",
        "message": "",
        "data": {
            "user": {
                "id": "3740d775-e267-49f7-b431-098ca6e65f55",
                "username": "dage"
            },
            "token": "3dde5f5272743b9c82d826be3c0b8c0df290c24b"
        }
    }
    ```

3. Login interface

    - Request address: `/api/v1/tenant/{tenant_id}/auth/?event_tag=com.Dragon turtle.auth.factor.password.auth`
    - Way of requesting: POST
    - Request parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `username`    | `username`  |  username
    | `password`    | `password`  |  password
    | `config_id`    | `config_id`  |  Configure ID in LOGIN_Page's items have been provided

    - Request example:
    ``` json
        {
            "username":"abcd",
            "password":"abcd",
            "config_id":"70f8d39e-30cc-40de-8a70-ec6495c21e84"
        }
    ```

    - Return parameter:

    | parameter name        | Parameter Description           | Exemplary           |
    | :---------:    | :--------------: | :--------------: |
    | `user`    | `user`  |  User object
    | `id`    | `id`  |  User ID
    | `username`    | `username`  |  username
    | `token`    | `token`  |  User token

    - Request example:
    ``` json
    {
        "error": "0",
        "package": "core",
        "message": "",
        "data": {
            "user": {
                "id": "3740d775-e267-49f7-b431-098ca6e65f55",
                "username": "dage"
            },
            "token": "3dde5f5272743b9c82d826be3c0b8c0df290c24b"
        }
    }
    ```
