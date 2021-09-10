from openapi.utils import extend_schema_tags

tag = [ 'desktop', 'notice' ]
path = 'desktop'
name = '桌面'

app_tag = 'desktop'
app_name = '应用市集'

extend_schema_tags(
    app_tag,
    app_name,
    {
        'type':'dashboard_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/user/{parent_lookup_user}/app/',
            'method': 'get'
        }
    }
)


notice_tag = 'notice'
notice_name = '通知列表'

extend_schema_tags(
    notice_tag,
    notice_name
)