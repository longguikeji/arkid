# Code example

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


## Java

``` java
import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.WebServlet;
import java.io.IOException;

@WebServlet(name = "OidcServlet", value = "/OidcServlet")
public class OidcLoginServlet extends HttpServlet {

    public final static String  clientId = "Y0nyNqIBsNBqYlW5ebGTRvgeNO6B0zZxvmFSCKWP";
    public final static String clientSecret = "LZHoJu7yZ5XnKR2dff4WlnD3BWcXTol2QBQX2IwboZUJYdVKmjvvEfRe002XK4nu1ujYZMdo3X4ow9CKiyVRLFRMoNEufhAeE0OgK5tVtRPRvVYAvKlIjE4QSaw6bRSB";
    public final static String authUrl = "http://localhost:9528/api/v1/tenant/4da114ce-e115-44a0-823b-d372114425d0/app/0b97eb6a-ee67-4e64-b59d-f4b49f3546ed/oauth/authorize/";
    public final static String redirectUri = "http://127.0.0.1:8080/redirect";
    public final static String getTokenUrl = "http://localhost:9528/api/v1/tenant/4da114ce-e115-44a0-823b-d372114425d0/oauth/token/";
    public final static String getUserinfoUrl = "http://localhost:9528/api/v1/tenant/4da114ce-e115-44a0-823b-d372114425d0/oauth/userinfo/";

    /**
     * Authorize
     * @param request
     * @param response
     * @throws ServletException
     * @throws IOException
     */
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        StringBuilder sb = new StringBuilder();
        sb.append(authUrl);
        sb.append("?client_id=");
        sb.append(clientId);
        sb.append("&redirect_uri=");
        sb.append(redirectUri);
        sb.append("&response_type=code");
        sb.append("&scope=userinfo");
        response.sendRedirect(sb.toString());
    }
}
```
``` java
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import org.apache.http.Consts;
import org.apache.http.HttpEntity;
import org.apache.http.HttpHeaders;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.mime.MultipartEntityBuilder;
import org.apache.http.entity.mime.content.StringBody;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import org.apache.commons.codec.binary.Base64;
import java.util.HashMap;
import java.util.Map;

@WebServlet(name = "OidcRedirectServlet", value = "/OidcRedirectServlet")
public class OidcRedirectServlet extends HttpServlet {

    /**
     * Authorize
     * @param request
     * @param response
     * @throws ServletException
     * @throws IOException
     */
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String code = request.getParameter("code");
        // Get AccessStokeen
        JSONObject accessTokenResult = requestAccessToken(code);
//        {
//            "access_token":"f9i0Jy0J7IDLHnZWbW3vMUSYI80fmw",
//            "expires_in":36000,
//            "token_type":"Bearer",
//            "scope":"userinfo",
//            "refresh_token":"gJclZjxoeRuq170HqgbDl6u3JdATcQ"
//        }
        if(accessTokenResult!=null){
            //Get UserInfo
            JSONObject userInfoResult = requestUserInfo(accessTokenResult.getString("access_token"));
//            {
//                "id":"faf5aae6-3cdf-4595-8b4a-3a06b31117c8",
//                "name":"admin",
//                "sub":"faf5aae6-3cdf-4595-8b4a-3a06b31117c8",
//                "sub_id":"faf5aae6-3cdf-4595-8b4a-3a06b31117c8",
//                "preferred_username":"admin",
//                "groups":["tenant_admin"],
//                "tenant_id":"4da114ce-e115-44a0-823b-d372114425d0",
//                "tenant_slug":""
//            }
        }else{
            System.out.println("Did not get access_token");
        }
    }

    /**
     * Get AccessStokeen
     * @param code Authorization code
     * @return JsonObject
     */
    private JSONObject requestAccessToken(String code){
        Map<String, String> params = new HashMap<>();
        params.put("code",code);
        params.put("grant_type","authorization_code");
        //Create a request object
        HttpPost httpPost = new HttpPost(OidcLoginServlet.getTokenUrl);
        // Create Auth authentication object
        String auth = OidcLoginServlet.clientId + ":" + OidcLoginServlet.clientSecret;
        byte[] encodedAuth = Base64.encodeBase64(
                auth.getBytes(StandardCharsets.UTF_8));
        String authHeader = "Basic " + new String(encodedAuth);
        //Create HTTPClient object
        CloseableHttpClient httpClient = HttpClientBuilder.create().build();
        try {
            // Put the verification information in Header
            httpPost.setHeader(HttpHeaders.AUTHORIZATION, authHeader);
            //Create a request header
            BasicResponseHandler handler = new BasicResponseHandler();
            //Set the request format
            MultipartEntityBuilder builder = MultipartEntityBuilder.create();
            if (params != null) {
                for (String key : params.keySet()) {
                    builder.addPart(key,
                            new StringBody(params.get(key), ContentType.create("text/plain", Consts.UTF_8)));
                }
            }
            HttpEntity reqEntity = builder.build();
            httpPost.setEntity(reqEntity);
            // Execute a request
            String result = httpClient.execute(httpPost, handler);
            JSONObject jsonObj = JSON.parseObject(result);
            return jsonObj;
        }catch (Exception e) {
            System.out.println(e);
        }finally {
            //Release connection
            try {
                httpClient.close();
            } catch (Exception e) {

            }
        }
        return null;
    }

    /**
     * Get user information
     * @param accessToken Request token
     * @return JsonObject
     */
    private JSONObject requestUserInfo(String accessToken){
        //Create a request object
        HttpGet httpGet = new HttpGet(OidcLoginServlet.getUserinfoUrl);
        //Create HTTPClient object
        CloseableHttpClient httpClient = HttpClientBuilder.create().build();
        try {
            //Create a request header
            BasicResponseHandler handler = new BasicResponseHandler();
            //Set the request header
            httpGet.setHeader(HttpHeaders.AUTHORIZATION, "Bearer "+accessToken);
            // Execute a request
            String result = httpClient.execute(httpGet, handler);
            System.out.println(result);
            JSONObject jsonObj = JSON.parseObject(result);
            return jsonObj;
        }catch (Exception e) {
            System.out.println(e);
        }finally {
            //Release connection
            try {
                httpClient.close();
            } catch (Exception e) {

            }
        }
        return null;
    }
}
```

## .NET

``` C#
public partial class AutoLogin_Qywx3 : System.Web.UI.Page
{
    string clientId = "----------------------------------";//Create a new application，Provide the following information
    string clientSecret = "---------------------";
    string myurl = "--------------------------;
    string URL_Authorize = "--------------------oauth/authorize/";
    string URL_Token = "---------------------------/oauth/token/";
    string URL_Userinfo = "------------------------/oauth/userinfo/";//User information address

    protected void Page_Load(object sender, EventArgs e)
    {
        string code = Request.QueryString["code"];
        if (string.IsNullOrEmpty(code))
        {
            //Code Code
            string return_url = Server.UrlEncode(myurl);
            string url = "";
            url = URL_Authorize + "?client_id=" + clientId + "&redirect_uri=" + return_url + "&response_type=code&scope=userinfo";
            Response.Redirect(url);
            return;
        }
        else
        {
            string json = sendMessage(URL_Token, code); 
            DataContractJsonSerializer serializer = new DataContractJsonSerializer(typeof(AccessToken));
            var mStream = new MemoryStream(Encoding.Default.GetBytes(json));
            AccessToken token = (AccessToken)serializer.ReadObject(mStream);
            string access_token=token.access_token;
string url = "----------------/oauth/userinfo/"; //User information address
                string R = SendGetHttpRequest(url, access_token);
                Response.Write(R);
                return;
        }
    }

    public string SendGetHttpRequest(string url, string requestData)
    {
        WebRequest request = (WebRequest)HttpWebRequest.Create(url);  
        request.Method = "Get"; 
        request.Headers["Authorization"] = "Bearer " + requestData;
        string result = string.Empty;
        using (WebResponse response = request.GetResponse())
        {
            if (response != null)
            {
                using (Stream stream = response.GetResponseStream())
                {
                    using (StreamReader reader = new StreamReader(stream, Encoding.UTF8))
                    {
                        result = reader.ReadToEnd();
                    }
                }

            }
        }
        return result;
    }

    public string sendMessage(string strUrl, string code)
    {
        ServicePointManager.Expect100Continue = true;
        ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12 | SecurityProtocolType.Tls11 | SecurityProtocolType.Tls;
        ServicePointManager.ServerCertificateValidationCallback = (sender, certificate, chain, errors) => true;
        //1.Set the message header
        HttpWebRequest request = (HttpWebRequest)WebRequest.Create(strUrl);
        request.Method = "Post";
        string a = clientId + ":" + clientSecret;
        var b = Encoding.UTF8.GetBytes(a);
        var base64 = Convert.ToBase64String(b);
        request.Headers.Add("Authorization", "Basic " + base64);
        request.UserAgent = "Apifox/1.0.0 (https://www.apifox.cn)";
        request.ContentType = "application/x-www-form-urlencoded";
        request.Accept = "*/*";
        request.Host = "-------";//ssoDomain name and port
        request.AllowAutoRedirect = true;
        request.Headers.Add("accept-encoding", "gzip, deflate, br");
        string param = "grant_type=authorization_code&code=" + HttpUtility.UrlEncode(code);
        byte[] byteData = Encoding.ASCII.GetBytes(param);
        request.ContentLength = byteData.Length;

        using (Stream reqStream = request.GetRequestStream())
        {
            reqStream.Write(byteData, 0, byteData.Length);
        }
        //ResponseAnswer flow obtain data
        string strResponse = "";
        using (HttpWebResponse res = (HttpWebResponse)request.GetResponse())
        {
            using (Stream resStream = res.GetResponseStream())
            {
                using (StreamReader sr = new StreamReader(resStream, Encoding.UTF8)) //UTF8
                {
                    strResponse = sr.ReadToEnd();
                }
            }
            // res.Close();
        }
        return strResponse;
    }
}
```
