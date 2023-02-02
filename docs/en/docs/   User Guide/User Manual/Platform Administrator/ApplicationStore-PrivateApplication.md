# app Store-Private application

* app Store—Private application Click the menu "Application management>app Store>Private application"
[![BxUU4w.png](https://v1.ax1x.com/2022/11/11/BxUU4w.png)](https://zimgs.com/i/BxUU4w)

* Buy or try Click the menu "Application management>app Store>Private application>Choose a record>Buy or try"
[![BxUU4w.png](https://v1.ax1x.com/2022/11/11/BxUU4w.png)](https://zimgs.com/i/BxUU4w)

* bought Click the menu "Application management>app Store>Private application>bought>"
[![BxUaIb.png](https://v1.ax1x.com/2022/11/11/BxUaIb.png)](https://zimgs.com/i/BxUaIb)

* View default configuration Click the menu "Application management>app Store>Private application>bought>Choose a record>default allocation"
[![BxUvvt.png](https://v1.ax1x.com/2022/11/11/BxUvvt.png)](https://zimgs.com/i/BxUvvt)

* Install Click the menu "Application management>app Store>Private application>bought>Choose a record>Install"，Configure reference helm Chart's values.yaml，Can be empty
[![BxUcNB.md.png](https://v1.ax1x.com/2022/11/11/BxUcNB.md.png)](https://zimgs.com/i/BxUcNB)
<br/>
Custom configuration parameter description：Apply installation support automatic configuration OIDC to log into the application，The parameters in the table below will be sent to Helm Chart's values.Replace it with the actual OIDC address before yaml
<br/>

|  parameter   | illustrate  | example  |
|  ----  | ----  | ---  |
| $arkid_oidc_root_url  | ArkIDApplication entry address | https://1 You will add 4470 A0 D. 16 DB 459431.Ark.dev.Dragon Turtle Technology.com  |
| $arkid_oidc_client_id  | client_id | 1hQdgZJ9Gf9KhQGhL9RLmatEV1q97rp8Od9kR8n8  |
| $arkid_oidc_client_secret  | client_secret  |FT2rETrpg9tmtB0wChSBUmRLlHXNH6eesPbeRl2qHpZ1nD3fcCFlEfa3UxLRsiR5MpHvc15i6zZcwLmMtcqVy5zf7ONqSOALNRXP1bBaWALbn2nrn8BLtEuaFIZvtrEm  |
| $arkid_oidc_authorize  | authorizeaddress | https://Ark.dev.Dragon Turtle Technology.com/api/v1/tenant/49 Boss 1127-Hurt-4535-917 d-Get 024831/app/J0 d 0253 a-Accompanied-4 Slack-8506-Dam 1275573 Bear/oauth/authorize/  |
| $arkid_oidc_token  | Get the token address | https://Ark.dev.Dragon Turtle Technology.com/api/v1/tenant/49 Boss 1127-Hurt-4535-917 d-Get 024831/oauth/token/  |
| $arkid_oidc_jwks  | Get the JWKS certificate address | https://Ark.dev.Dragon Turtle Technology.com/api/v1/tenant/49 Boss 1127-Hurt-4535-917 d-Get 024831/.well-known/jwks.json  |
| $arkid_oidc_userinfo  | Get user information address | https://Ark.dev.Dragon Turtle Technology.com/api/v1/tenant/49 Boss 1127-Hurt-4535-917 d-Get 024831/oauth/userinfo/  |
| $arkid_oidc_logout  | Login address | https://Ark.dev.Dragon Turtle Technology.com/api/v1/tenant/49 Boss 1127-Hurt-4535-917 d-Get 024831/oidc/logout/  |

Example 1： Jumpserver Installation parameter
```
global:
  storageClass: standard

## Please configure your MySQL server first
## Jumpserver will not start the external MySQL server.
##
externalDatabase:
  engine: mysql
  host: jms-mysql
  port: 3306
  user: root
  password: "weakPassword"
  database: jumpserver

## Please configure your Redis server first
## Jumpserver will not start the external Redis server.
##
externalRedis:
  host: jms-redis-master
  port: 6379
  password: "weakPassword"
  
ingress:
  hosts:
    - "test.jumpserver.org"
  
core:
  config:
    # Generate a new random secret key by execute `cat /dev/urandom | tr -dc A-Za-z0-9 | head -c 50`
    secretKey: "GxrLH7rewfsRN8B9Zl6MEGD50Uou4LF6UVsEIwfsRN8B9Zl6MEGD50UouayGMhYll8dqmn"
    # Generate a new random bootstrap token by execute `cat /dev/urandom | tr -dc A-Za-z0-9 | head -c 24`
    bootstrapToken: "ilR8RvAbK7lgRTxs"
    log:
      level: DEBUG
    
  env:
    # Doc: https://docs.jumpserver.org/zh/master/admin-guide/authentication/openid/#5-jumpserver
    AUTH_OPENID: True
    BASE_SITE_URL: $arkid_oidc_root_url
    AUTH_OPENID_CLIENT_ID: $arkid_oidc_client_id
    AUTH_OPENID_CLIENT_SECRET: $arkid_oidc_client_secret
    AUTH_OPENID_PROVIDER_ENDPOINT: $arkid_oidc_client_authorize
    AUTH_OPENID_PROVIDER_AUTHORIZATION_ENDPOINT: $arkid_oidc_client_authorize
    AUTH_OPENID_PROVIDER_TOKEN_ENDPOINT: $arkid_oidc_client_token
    AUTH_OPENID_PROVIDER_JWKS_ENDPOINT: $arkid_oidc_jwks
    AUTH_OPENID_PROVIDER_USERINFO_ENDPOINT: $arkid_oidc_client_userinfo
    AUTH_OPENID_PROVIDER_END_SESSION_ENDPOINT: $arkid_oidc_logout
    AUTH_OPENID_PROVIDER_SIGNATURE_ALG: HS256
    AUTH_OPENID_PROVIDER_SIGNATURE_KEY: null
    AUTH_OPENID_SCOPES: openid profile email
    AUTH_OPENID_ID_TOKEN_MAX_AGE: 60
    AUTH_OPENID_ID_TOKEN_INCLUDE_CLAIMS: True
    AUTH_OPENID_USE_STATE: True
    AUTH_OPENID_USE_NONCE: True
    AUTH_OPENID_SHARE_SESSION: False
    AUTH_OPENID_IGNORE_SSL_VERIFICATION: True

```

Example 2： Scrape Installation parameter
```
## arkid-oidc.yaml
env: 
  GF_SERVER_ROOT_URL: $arkid_oidc_root_url
  GF_AUTH_GENERIC_OAUTH_ENABLED: "true"
  GF_AUTH_GENERIC_OAUTH_NAME: "arkid"
  GF_AUTH_GENERIC_OAUTH_CLIENT_ID: "$arkid_oidc_client_id"
  GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET: "$arkid_oidc_client_secret"
  GF_AUTH_GENERIC_OAUTH_SCOPES: "email,openid,userinfo"
  GF_AUTH_GENERIC_OAUTH_AUTH_URL: "$arkid_oidc_authorize"
  GF_AUTH_GENERIC_OAUTH_TOKEN_URL: "$arkid_oidc_token"
  GF_AUTH_GENERIC_OAUTH_API_URL: "$arkid_oidc_userinfo"
```

* If the privatization application has an entry address，After installation, automatically create the corresponding entry application in the application list
```
# Private application Chart.yaml Annotations must be added to configuration，Only then will automatically create an entry application
annotations:
  web_url_from_services: App
```
[![BxUP96.png](https://v1.ax1x.com/2022/11/11/BxUP96.png)](https://zimgs.com/i/BxUP96)

* To access the application，Click on the homepage>App，Accessable application

Example 1：Jumpserver
Homepage click JumpServer
[![BF6wpB.jpg](https://v1.ax1x.com/2023/01/15/BF6wpB.jpg)](https://zimgs.com/i/BF6wpB)
Enter JumpServer, Click Openid to log in，Start OIDC login JumpServer
[![BF2ihj.jpg](https://v1.ax1x.com/2023/01/15/BF2ihj.jpg)](https://zimgs.com/i/BF2ihj)

Example 2：Scrape
Home Click Grafana
[![BF2UVG.jpg](https://v1.ax1x.com/2023/01/15/BF2UVG.jpg)](https://zimgs.com/i/BF2UVG)
Enter Grafana，Click SIGN in with arkid，Start OIDC login Grafana
[![BF2CO6.jpg](https://v1.ax1x.com/2023/01/15/BF2CO6.jpg)](https://zimgs.com/i/BF2CO6)
