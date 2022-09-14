# 代码示例

## FastAPI

``` py
from fastapi import FastAPI
from starlette.responses import RedirectResponse
import requests
import json

app = FastAPI()


client_id = 'KHvanrQlNIBMZj9owre9ZZ6oc8AjWNdPHYUO2rwH'
client_secret = 'ywZCKjSzxiWfgiaoEYAmloQ0greaLxLtTv6TnOyRtsgjvR7xAiTwpY0H5A46ZSSYz3x5laxHXQSlpjamnih3aQlYqS7Eq6oiSXsjiGNXnnf750i8WbbWAVAZdEaiivas'
auth_url = 'http://localhost:9528/api/v1/tenant/bf3511e2-07b3-459f-829e-17a349602531/app/10e82a7d-b7fd-45e0-976b-885859066508/oauth/authorize/'
redirect_uri = 'http://127.0.0.1:8001/redirect'
get_token_url = 'http://localhost:9528/api/v1/tenant/bf3511e2-07b3-459f-829e-17a349602531/oauth/token/'
get_userinfo_url = 'http://localhost:9528/api/v1/tenant/bf3511e2-07b3-459f-829e-17a349602531/oauth/userinfo/'

@app.get("/auth")
def oidc_auth():
    response = RedirectResponse(
        url=auth_url+'?client_id='+client_id+'&redirect_uri='+redirect_uri+'&response_type=code&scope=userinfo')
    return response


@app.get("/redirect")
def oidc_redirect(code:str):
    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    response = requests.post(
        url=get_token_url,
        auth=auth,
        data={'code':code, 'grant_type':'authorization_code'}
    )
    
    response = json.loads(response.content)
    access_token = response["access_token"]

    return requests.get(
        url=get_userinfo_url,
        headers={
            'Authorization': 'Bearer ' + access_token
        }
    ).content
```