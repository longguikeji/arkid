from openapi.utils import extend_schema_tags

tag = 'app_list'
path = tag
name = '应用管理'

extend_schema_tags(
    tag,
    name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/',
            'method': 'get'
        },
        'page': {
            'create': {
                'tag': 'app_create'
            }
        },
        'item': {
            'provisioning': {
                'tag': 'app_provisioning'
            },
            'update': {
                'tag': 'app_update'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{id}/',
                'method': 'delete'
            }
        },
    }
)

app_create_tag = 'app_create'
app_create_name = '创建应用'

extend_schema_tags(
    app_create_tag,
    app_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/',
            'method': 'post'
        },
        'page': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/',
                'method': 'post'
            }
        }
    }
)

app_update_tag = 'app_update'
app_update_name = '编辑应用'

extend_schema_tags(
    app_update_tag,
    app_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{id}/',
            'method': 'get'
        },
        'page': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{id}/',
                'method': 'put'
            }
        }
    }
)

app_provisioning_tag = 'app_provisioning'
app_provisioning_name = '应用同步配置'

extend_schema_tags(
    app_provisioning_tag,
    app_provisioning_name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/',
            'method': 'get'
        },
        'page': {
            'create': {
                'tag': 'app_provisioning_create'
            }
        },
        'item': {
            'mapping': {
                'tag': 'app_provisioning_mapping'
            },
            'profile': {
                'tag': 'app_provisioning_profile'
            },
            'update': {
                'tag': 'app_provisioning_update'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{id}/',
                'method': 'delete'
            }
        },
    }
)

app_provisioning_create_tag = 'app_provisioning_create'
app_provisioning_create_name = '创建应用同步配置'

extend_schema_tags(
    app_provisioning_create_tag,
    app_provisioning_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/',
            'method': 'post'
        },
        'page': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/',
                'method': 'post'
            }
        }
    }
)

app_provisioning_update_tag = 'app_provisioning_update'
app_provisioning_update_name = '编辑应用同步配置'

extend_schema_tags(
    app_provisioning_update_tag,
    app_provisioning_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{id}/',
            'method': 'get'
        },
        'page': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{id}/',
                'method': 'put'
            }
        }
    }
)

app_provisioning_mapping_tag = 'app_provisioning_mapping'
app_provisioning_mapping_name = '应用同步配置映射'

extend_schema_tags(
    app_provisioning_mapping_tag,
    app_provisioning_mapping_name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/mapping/',
            'method': 'get'
        },
        'page': {
            'create': {
                'tag': 'app_provisioning_mapping_create'
            }
        },
        'item': {
            'update': {
                'tag': 'app_provisioning_mapping_update'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/mapping/{id}/',
                'method': 'delete'
            }
        }
    }
)

app_provisioning_mapping_create_tag = 'app_provisioning_mapping_create'
app_provisioning_mapping_create_name = '创建应用同步配置映射'

extend_schema_tags(
    app_provisioning_mapping_create_tag,
    app_provisioning_mapping_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/mapping/',
            'method': 'post'
        },
        'page': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/mapping/',
                'method': 'post'
            }
        }
    }
)

app_provisioning_mapping_update_tag = 'app_provisioning_mapping_update'
app_provisioning_mapping_update_name = '编辑应用同步配置映射'

extend_schema_tags(
    app_provisioning_mapping_update_tag,
    app_provisioning_mapping_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/mapping/{id}/',
            'method': 'get'
        },
        'page': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/mapping/{id}/',
                'method': 'put'
            }
        }
    }
)

app_provisioning_profile_tag = 'app_provisioning_profile'
app_provisioning_profile_name = '应用同步配置概述'

extend_schema_tags(
    app_provisioning_profile_tag,
    app_provisioning_profile_name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/profile/',
            'method': 'get'
        },
        'page': {
            'create': {
                'tag': 'app_provisioning_profile_create'
            }
        },
        'item': {
            'update': {
                'tag': 'app_provisioning_profile_update'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/profile/{id}/',
                'method': 'delete'
            }
        }
    }
)

app_provisioning_profile_create_tag = 'app_provisioning_profile_create'
app_provisioning_profile_create_name = '创建应用同步配置概述'

extend_schema_tags(
    app_provisioning_profile_create_tag,
    app_provisioning_profile_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/profile/',
            'method': 'post'
        },
        'page': {
            'create': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/profile/',
                'method': 'post'
            }
        }
    }
)


app_provisioning_profile_update_tag = 'app_provisioning_profile_update'
app_provisioning_profile_update_name = '编辑应用同步配置概述'

extend_schema_tags(
    app_provisioning_profile_update_tag,
    app_provisioning_profile_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/profile/{id}/',
            'method': 'get'
        },
        'page': {
            'update': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/profile/{id}/',
                'method': 'put'
            }
        }
    }
)
