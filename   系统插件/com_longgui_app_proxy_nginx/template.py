from string import Template


class MyTemplate(Template):
    delimiter = "%"


NginxConfTemplate = MyTemplate(
    """
server {
    listen           %{port};
    server_name      %{app_server_name};
    set_real_ip_from 172.0.0.0/8;
    real_ip_header   X-Real-IP;

    location = /app_proxy_auth {
        internal;
        set $query '';
        if ($request_uri ~* "[^\?]+\?(.*)$") {
              set $query $1;
        }
        proxy_pass              %{nginx_auth_url}?$query;
        proxy_pass_request_body off;
        proxy_set_header        Content-Length "";
        proxy_set_header        X-Original-URI $request_uri;
    }

    location / {
        auth_request    /app_proxy_auth;
        auth_request_set $arkid_token $sent_http_set_cookie;
        add_header X-COOKIE-TEST $arkid_token;
        proxy_pass %{app_proxy_url};
        proxy_set_header Host $host;
        proxy_set_header Arker portal;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

}
"""
)
