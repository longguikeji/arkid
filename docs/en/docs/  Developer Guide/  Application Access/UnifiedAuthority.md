# Unified authority
arkidSupport third -party applications，By output your own interface document，Arkid here by reading the application itself interface document，You can flexible management authority in ARKID。

## Access step

1.Need to prepare a readable Openapi.json access address，At least Permissions nodes in JSON，Permissions contain basic role information，And interface information。Here，Can be used as a reference:

``` json
{
    "permissions":[
        {
            "name":"customer",
            "sort_id":0,
            "type":"group",
            "container":[
                3,
                6
            ]
        },
        {
            "name":"tenant-admin",
            "sort_id":1,
            "type":"group",
            "container":[
                4
            ]
        },
        {
            "name":"platform-admin",
            "sort_id":2,
            "type":"group",
            "container":[
                5
            ]
        },
        {
            "name":"appList",
            "sort_id":3,
            "type":"api",
            "container":[

            ],
            "operation_id":"api_v1_views_app_list_apps"
        },
        {
            "name":"Create an application",
            "sort_id":4,
            "type":"api",
            "container":[

            ],
            "operation_id":"api_v1_views_app_create_app"
        },
        {
            "name":"Public app list",
            "sort_id":5,
            "type":"api",
            "container":[

            ],
            "operation_id":"api_v1_views_app_list_open_apps"
        },
        {
            "name":"Get an app",
            "sort_id":6,
            "type":"api",
            "container":[

            ],
            "operation_id":"api_v1_views_app_get_app"
        }
    ]
}
```

| parameter name        | Parameter Description           |
| :---------:    | :--------------: |
| `name`    | name  |         
| `sort_id` | Sorting ID (developer generates itself) |
| `type` | Type (API or group) |
| `container` | SORT containing interfaces_ID (only value in the group type) |
| `operation_id` | Operation ID (only the API type has this field) |

2.Application lists needed under the application management menu，Create a new application

[![vlq2Ct.md.jpg](https://s1.ax1x.com/2022/08/09/vlq2Ct.md.jpg)](https://imgtu.com/i/vlq2Ct)

3.Need to configure the application，Here we take the application of OIDC type as an example

[![vlL1RP.md.jpg](https://s1.ax1x.com/2022/08/09/vlL1RP.md.jpg)](https://imgtu.com/i/vlL1RP)

``` title="Replenishment"
Currently only supports OIDC type，Or OAUTH2 type application。Other types of applications cannot use the function of obtaining right -limited string
```

4.You need to open an open API configuration

[![vlLysU.md.jpg](https://s1.ax1x.com/2022/08/09/vlLysU.md.jpg)](https://imgtu.com/i/vlLysU)

``` title="Replenishment"
If the contents content in the interface document is changed，Need to change the application version，Except for the first configuration
```
## how to use

1.Can be under the authority management menu，All of the application pages under the authorization management menu，Pay the authorized permissions，Authorized to other tenants to use。

[![vljsQP.md.jpg](https://s1.ax1x.com/2022/08/09/vljsQP.md.jpg)](https://imgtu.com/i/vljsQP)

``` title="Replenishment"
The distribution of permissions is step by step downward，When the general authorization is opened，Except for the permissions to be opened，Will open the application entry permissions，Prevent users from other tenants from logging in
Authorize:This permission is authorized to use it for other tenants，Other tenants administrators have the permissions first，Other tenant administrators can allocate their own permissions secondary allocation。
Authorize:If this permissions switch from the opening state to the closed state，The permissions that have been assigned to other tenants，Will be retracted，Including the secondary distribution of other tenants。
```

2.Except for authorization to other tenants，Can also be in the tenant，Perform user permissions

[![vlvrtJ.md.jpg](https://s1.ax1x.com/2022/08/09/vlvrtJ.md.jpg)](https://imgtu.com/i/vlvrtJ)

## How to obtain the user's permissions string

1.Access application list，Edit application，Get parameter information

[![v3A13T.md.jpg](https://s1.ax1x.com/2022/08/10/v3A13T.md.jpg)](https://imgtu.com/i/v3A13T)

| English parameter name        | Corresponding page surface field                          |
| :---------:    | :----------------------------------: |
| `redirect url`      | Callback address  |
| `client_id`      | Client ID  |
| `client_token`     | Client key |
| `authorize url`        | Authorized URL |
| `get token url` | Get ACCESS_Token address |
| `userinfo url`   | User information address |
| `logout url`   | Exit login address |

2.Get Authorization Code

- Request address: `authorize url`
- Way of requesting: GET
- Request parameter:

| parameter name        | Parameter Description           | Exemplary           |
| :---------:    | :--------------: | :--------------: |
| `client_id`    | `client_id`  |         
| `redirect_uri` | `redirect url` |         
| `response_type`| Fill in Code |   code     
| `scope`        | Fill in (openid userinfo) |

- Request example: http://authorize url/?client_id=xxxxx&redirect_uri=xxxxx&response_type=code&scope=userinfo
- Return parameter:

| parameter name        | Parameter Description           | Exemplary           |
| :---------:    | :--------------: | :--------------: |
| `code`    | Authorization code  |         

- Return sample: http://redirect_uri?code=As a savings, the seventh seven&token=Sadaa 4840, and I will be 04 with a 4 -wing 1 bastard 1 b 176

3.Get ACCESS Token

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
| `id_token` | id_token |

- Return sample: 
``` json
{
    "access_token": "nRmo1Ko5UbStrtBNtySnUi8Ezw9YBm",
    "expires_in": 36000,
    "token_type": "Bearer",
    "scope": "openid userinfo",
    "refresh_token": "na3bP6WX3JzZynqLSJS8wI4m6zWiC9",
    "id_token": "eyJhbGciOiAiUlMyNTYiLCAidXNlIjogInNpZyIsICJraWQiOiAiRjlYSlg3N0VkTjVnNnA5Q3ZnS1NnTW9GRTh4cjNJeWp6aUNLTnR3enhWTSIsICJlIjogIkFRQUIiLCAia3R5IjogIlJTQSIsICJuIjogImlFNFkyMDhLV0x1QzhLcWZLQU96NmctaUlfeHNLU3hTYmoyMWxXbmdnMmwtay01b2ZKaVRDQklKZjFTR1dyQ3hfRXNGT1ptZUxEM29xcE96WUNhdFZ3NlBlNnVacFJhRFZSekFoOV9Da00waUFWclc2bHB4QkowSFlxZ1d3cHBpSG15M2VEbkg2V3lGVkNQUFhKd3F1MU5ETlludENqcUtWa2gxamotdjktVSJ9.eyJhdWQiOiAiQXJkeHJwajVVb0JmUUNiN1F4TDE1RG9YR2ozcHpOeHFkeFl2U1YxeCIsICJpYXQiOiAxNjYwMTE1MDU4LCAiYXRfaGFzaCI6ICJqa19ET1M0MFNnT3Fubk91QzhjeHdnIiwgInN1YiI6ICJmYWY1YWFlNi0zY2RmLTQ1OTUtOGI0YS0zYTA2YjMxMTE3YzgiLCAic3ViX2lkIjogImZhZjVhYWU2LTNjZGYtNDU5NS04YjRhLTNhMDZiMzExMTdjOCIsICJwcmVmZXJyZWRfdXNlcm5hbWUiOiAiYWRtaW4iLCAiZ3JvdXBzIjogWyJ0ZW5hbnRfYWRtaW4iXSwgInRlbmFudF9pZCI6ICI0ZGExMTRjZS1lMTE1LTQ0YTAtODIzYi1kMzcyMTE0NDI1ZDAiLCAidGVuYW50X3NsdWciOiAiIiwgImlzcyI6ICJodHRwOi8vbG9jYWxob3N0OjgwMDAvYXBpL3YxL3RlbmFudC80ZGExMTRjZS1lMTE1LTQ0YTAtODIzYi1kMzcyMTE0NDI1ZDAiLCAiZXhwIjogMTY2MDE1MTA1OCwgImF1dGhfdGltZSI6IDE2NjAxMTUwNTh9.Xcz9d79UdPAVtiObwkauIPVodQtDK8ZX9zYBhTgmjs5_lQhlgzCeUZPeUJCsIb_3AR9BChDw_EDYzwFhg1h4vYofYlRk4V9wHZypbRoDFopm343h78JbzGeexFiRhE_e4zIPmVsQj925TpMuMOP4zLKX3U6pTPJETflrvblXcUs"
}
```

4.Getting rights string

- Request address: `/api/v1/app/permission_result`
- Way of requesting: GET
- Request head parameter:

| parameter name        | Parameter Description           | Exemplary           |
| :---------:    | :--------------: | :--------------: |
| `ID-TOKEN`  | Get ACCESS_The ID returned to the token interface_token  |  xxxxx

- Return parameter:

| parameter name        | Parameter Description           | Exemplary           |
| :---------:    | :--------------: | :--------------: |
| `result`    | User permissions string (1 is a permissions，0 is no authority，Each with sort in the interface document_ID corresponds)  |

- Return sample: 
``` json
{
    "result":"11111"
}
```
