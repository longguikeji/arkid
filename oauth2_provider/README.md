# OneID OAuth2.0 接入指南

## 1.认证身份
接入时注册应用需要admin权限(`system_oneid_all`)
在初始情况下，使用 admin / admin 即可

```
>> res = requests.post('https//{oneid}/siteapi/v1/admin/login/', json={'username': 'admin', 'password': 'admin'})
>> res.json()['token']
'e82179089ba85bfcbaa821d3a71eee085047b3a8'
```

## 2.注册应用
在OneID中OAuth2.0 APP 必须要属于某一应用，纳入OneID的应用管理。  
创建OAuth2.0 APP，即创建OneID APP，并为该APP分配OAuth2.0 APP。  

```
>> res = requests.post('http://{oneid}/siteapi/v1/app/',
    json={
        'name': 'demo',
        'oauth_app': {
            'redirect_uris': 'http://demo/callback/'
        }
    }
    headers={'AUTHORIZATION': 'Token e82179089ba85bfcbaa821d3a71eee085047b3a8'}
)
>> res.json()
>> {
    'app_id': 2,
    'uid': 'demo',
    'name': 'demo',
    'remark': '',
    'oauth_app': {
        'client_id': '02DnhbcRvC0ogKC41lxbTpF4mK0gFPRhWx42kCvU',
        'client_secret': 'KHzsR85aIt1oQu0Y3OdruVvCiT5z5FhqPY...EGw5PRsWz3TK2FOnbAIyPuS3P7ke',
        'redirect_uris': 'http://demo/callback/',
        'client_type': 'confidential',
        'authorization_grant_type': 'authorization-code'
    }
}
```

`oauth_app` 中即为配置OAuth2.0需要的信息

建议按照步骤2中的参数进行配置，仅指定`redirect_uris`，其他均使用默认配置。  
更多定制化的参数可参考[API文档](https://github.com/rockl2e/oneid/blob/master/siteapi/v1/blueprint.md)APP部分

## 3.客户端配置
- ClientID - 来自步骤2，由OneID生成
- ClientSecret - 来自步骤2，由OneID生成
- Scopes - read，write，选填，默认申请两者
- RedirectURL - 需与步骤2中相同
- AuthURL:  "http://{oneid}/oauth/authorize/", 采用OneID域名，后面的相对url为固定写法，下同
- TokenURL: "http://{oneid}/oauth/token"

## 4.分配用户权限
应用对接到OneID后，并不是所有人都有权限通过OneID单点登录到该应用。
步骤2中创建应用时会自动创建一条名为 `app_{app_uid}_access`的权限，拿到该项权限才能真正登录。
```
> requests.patch(
    'http://{oneid}/siteapi/v1/perm/user/{username}/',
    json={
        'perm_statuses':[{
            'uid': 'app_{app_uid}_access',
            'status': 1,  # 显式授权
        }]
    }
)
```
