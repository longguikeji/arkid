from openapi.utils import extend_schema_tags

tag = 'app'
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
                'tag': 'app.create'
            }
        },
        'item': {
            'provisioning': {
                'tag': 'app.provisioning'
            },
            'update': {
                'tag': 'app.update'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{id}/',
                'method': 'delete'
            }
        },
    }
)

app_create_tag = 'app.create'
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

app_update_tag = 'app.update'
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

app_provisioning_tag = 'app.provisioning'
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
                'tag': 'app.provisioning.create'
            }
        },
        'item': {
            'mapping': {
                'tag': 'app.provisioning.mapping'
            },
            'profile': {
                'tag': 'app.provisioning.profile'
            },
            'update': {
                'tag': 'app.provisioning.update'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{id}/',
                'method': 'delete'
            }
        },
    }
)

app_provisioning_create_tag = 'app.provisioning.create'
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

app_provisioning_update_tag = 'app.provisioning.update'
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

app_provisioning_mapping_tag = 'app.provisioning.mapping'
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
                'tag': 'app.provisioning.mapping.create'
            }
        },
        'item': {
            'update': {
                'tag': 'app.provisioning.mapping.update'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/mapping/{id}/',
                'method': 'delete'
            }
        }
    }
)

app_provisioning_mapping_create_tag = 'app.provisioning.mapping.create'
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

app_provisioning_mapping_update_tag = 'app.provisioning.mapping.update'
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

app_provisioning_profile_tag = 'app.provisioning.profile'
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
                'tag': 'app.provisioning.profile.create'
            }
        },
        'item': {
            'update': {
                'tag': 'app.provisioning.profile.update'
            },
            'delete': {
                'path': '/api/v1/tenant/{parent_lookup_tenant}/app/{parent_lookup_app}/provisioning/{parent_lookup_provisioning}/profile/{id}/',
                'method': 'delete'
            }
        }
    }
)

app_provisioning_profile_create_tag = 'app.provisioning.profile.create'
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


app_provisioning_profile_update_tag = 'app.provisioning.profile.update'
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
