# Miniprogram 第三方登录插件

## 功能介绍
配置Miniprogram插件后，可以点击通过插件提供的登录和绑定方法，很方便的将小程序用户，和ArkID的用户绑定。可以很方便实现微信小程序的免密登录arkid

### 配置微信小程序的基本信息

=== "登录微信公众平台，进入需要配置的小程序"
    [![vnmnD1.md.jpg](https://s1.ax1x.com/2022/08/05/vnmnD1.md.jpg)](https://imgtu.com/i/vnmnD1)

=== "保存App ID和App Secret"
    [![vnmE34.md.jpg](https://s1.ax1x.com/2022/08/05/vnmE34.md.jpg)](https://imgtu.com/i/vnmE34)

### 创建ArkID第三方登录配置,获取回调URL

=== "打开第三方认证页面"
    [![jzjOud.md.jpg](https://s1.ax1x.com/2022/07/26/jzjOud.md.jpg)](https://imgtu.com/i/jzjOud)

=== "填写表单参数，点击创建"
    [![vnmIGF.md.jpg](https://s1.ax1x.com/2022/08/05/vnmIGF.md.jpg)](https://imgtu.com/i/vnmIGF)

=== "点击编辑按钮，获取登录地址、绑定地址、登录地址的域名"
    [![vnmOVx.md.jpg](https://s1.ax1x.com/2022/08/05/vnmOVx.md.jpg)](https://imgtu.com/i/vnmOVx)

### 更新微信小程序的服务器域名

=== "配置服务器域名"
    [![vnmNDI.md.jpg](https://s1.ax1x.com/2022/08/05/vnmNDI.md.jpg)](https://imgtu.com/i/vnmNDI)

### 如何使用登录接口和绑定接口

1. 登录接口

    - 请求地址: `login url`
    - 请求方式: GET
    - 请求参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `code`    | `code`  |  开发人员调用小程序提供的方法会得到一个code

    - 请求示例: http://login url/?code=xxxxx
    - 返回参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `token`    | `token`  |  用户token(只有用户已经绑定过才会有这个参数)
    | `ext_id`    | `ext_id`  |  用户id
    | `tenant_id`    | `tenant_id`  |  租户id
    | `bind`    | `bind`  |  绑定地址

    - 返回示例:
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

2. 绑定接口

    - 请求地址: `bind url`
    - 请求方式: POST
    - 请求头参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `Authorization`    | Token token  |  由arkid用户登录获取的token

    - 请求参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `ext_id`    | `ext_id`  |  在登录接口获得的绑定id

    - 请求示例: http://bind url

    - 返回示例:
    ``` json
        {
            "error": "0",
            "package": "com.longgui.external.idp.miniprogram"
        }
    ```

### 如何获取arkid用户的token

1. login_page接口

    - 请求地址: `/api/v1/tenant/{tenant_id}/login_page/`
    - 请求方式: GET
    - 返回示例:
    ``` json
        {
            "data":{
                "login":{
                    "name":"login",
                    "forms":[
                        {
                            "label":"用户名密码登录",
                            "items":[
                                {
                                    "value":null,
                                    "type":"text",
                                    "placeholder":"用户名",
                                    "name":"username",
                                    "append":null,
                                    "http":null
                                },
                                {
                                    "value":null,
                                    "type":"password",
                                    "placeholder":"密码",
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
                                "title":"登录",
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
                            "prepend":"还没有账号，",
                            "title":"立即注册",
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
                            "label":"用户名密码注册",
                            "items":[
                                {
                                    "value":null,
                                    "type":"text",
                                    "placeholder":"用户名",
                                    "name":"username",
                                    "append":null,
                                    "http":null
                                },
                                {
                                    "value":null,
                                    "type":"password",
                                    "placeholder":"密码",
                                    "name":"password",
                                    "append":null,
                                    "http":null
                                },
                                {
                                    "value":null,
                                    "type":"password",
                                    "placeholder":"密码确认",
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
                                "title":"注册",
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
                            "prepend":"已有账号，",
                            "title":"立即登录",
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
                            "prepend":"还没有账号，",
                            "title":"立即注册",
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
                            "prepend":"已有账号，",
                            "title":"立即登录",
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
                "name":"平台租户",
                "slug":"",
                "icon":null
            }
        }
    ```

    - 返回说明:
    我们需要重点关注data中的login和register对象中的forms中的第0个对象的items和submit字段，其中submit中的http地址是请求地址，items数组中为请求参数

2. 注册接口

    - 请求地址: `/api/v1/tenant/{tenant_id}/register/?event_tag=com.longgui.auth.factor.password.register`
    - 请求方式: POST
    - 请求参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `username`    | `username`  |  用户名
    | `password`    | `password`  |  密码
    | `checkpassword`    | `checkpassword`  |  重复密码
    | `config_id`    | `config_id`  |  配置id在login_page的items中已经提供了

    - 请求示例:
    ``` json
        {
            "username":"abcd",
            "password":"abcd",
            "checkpassword":"abcd",
            "config_id":"70f8d39e-30cc-40de-8a70-ec6495c21e84"
        }
    ```

    - 返回参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `user`    | `user`  |  用户对象
    | `id`    | `id`  |  用户id
    | `username`    | `username`  |  用户名
    | `token`    | `token`  |  用户token

    - 请求示例:
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

3. 登录接口

    - 请求地址: `/api/v1/tenant/{tenant_id}/auth/?event_tag=com.longgui.auth.factor.password.auth`
    - 请求方式: POST
    - 请求参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `username`    | `username`  |  用户名
    | `password`    | `password`  |  密码
    | `config_id`    | `config_id`  |  配置id在login_page的items中已经提供了

    - 请求示例:
    ``` json
        {
            "username":"abcd",
            "password":"abcd",
            "config_id":"70f8d39e-30cc-40de-8a70-ec6495c21e84"
        }
    ```

    - 返回参数:

    | 参数名称        | 参数说明           | 示例           |
    | :---------:    | :--------------: | :--------------: |
    | `user`    | `user`  |  用户对象
    | `id`    | `id`  |  用户id
    | `username`    | `username`  |  用户名
    | `token`    | `token`  |  用户token

    - 请求示例:
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
