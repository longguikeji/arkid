# radiusClient

## Features

The plug -in supports the Radius server of the given given，Log in to user login，If the login user account exists on the Radius server，But there is no existence in Arkid，Will use a given user name and password to create new users

### Steps

=== "Find the plug -in and try"
    [![BUpkQQ.jpg](https://v1.ax1x.com/2022/12/16/BUpkQQ.jpg)](https://zimgs.com/i/BUpkQQ)

=== "Click on the tenant configuration"
    [![BUm2Gb.jpg](https://v1.ax1x.com/2022/12/16/BUm2Gb.jpg)](https://zimgs.com/i/BUm2Gb)

=== "Configure the radius server information，And save the certification address"
    [![BU0GEL.jpg](https://v1.ax1x.com/2022/12/16/BU0GEL.jpg)](https://zimgs.com/i/BU0GEL)

=== "Get the tenant ID"
    [![BnBwEc.jpg](https://v1.ax1x.com/2023/01/06/BnBwEc.jpg)](https://zimgs.com/i/BnBwEc)

### Login interface

- Request address: `/api/v1/tenant/{tenant_id}/com_Dragon turtle_app_protocol_radius_client/radius_login/`
- Way of requesting: POST
- Request parameter:

| parameter name        | Parameter Description           | Exemplary           |
| :---------:    | :--------------: | :--------------: |    
| `username` | username |
| `password` | password |

- Return sample: 
``` json
{
    "error": "0",
    "package": "com.longgui.app.protocol.radius.client",
    "data": {
        "token": "6a4473603dfae89ac9ef8e6aacdcd2369233d2a5"
    }
}
```
