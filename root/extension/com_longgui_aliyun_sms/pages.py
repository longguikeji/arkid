from openapi.utils import extend_schema_tags

extend_schema_tags(
    name='config',
    description='短信配置',
    page={
            'type':'form_page',
            'router':'/system/extension/aliyun/config',
            'init': {
                'path': '/api/v1/extension/aliyun/config',
                'method': 'get'
            },
            'page': {
                'update': {
                    'path': '/api/v1/extension/aliyun/config',
                    'method': 'put'
                }
            }
        }
)

extend_schema_tags(
    name='send_sms',
    description='发送短信',
    page={
            'type':'form_page',
            'router':'/system/extension/aliyun/send_sms',
            'init': {
                'path': '/api/v1/extension/aliyun/send_sms',
                'method': 'post'
            }
        }
)