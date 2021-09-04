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
        'global': {
            'create': {
                'tag': 'app.create'
            }
        },
        'local': {
            'sync': {
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
        'global': {
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
        'global': {
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
        'type':'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/app/{app_uuid}/provisioning/',
            'method': 'get'
        },
        'global': {
            'mapping': {
                'tag': 'app.provisioning.mapping'
            },
            'profile': {
                'tag': 'app.provisioning.profile'
            },
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/app/{app_uuid}/provisioning/',
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
            'path': '/api/v1/tenant/{tenant_uuid}/app/{app_uuid}/provisioning/mapping/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'app.provisioning.mapping.create'
            }
        },
        'local': {
            'update': {
                'tag': 'app.provisioning.mapping.update'
            },
            'delete': {
                'path': '/api/v1/tenant/{tenant_uuid}/app/{app_uuid}/provisioning/mapping/{map_uuid}/',
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
            'path': '/api/v1/tenant/{tenant_uuid}/app/{app_uuid}/provisioning/mapping/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{tenant_uuid}/app/{app_uuid}/provisioning/mapping/',
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
            'path': '/api/v1/tenant/{tenant_uuid}/app/{app_uuid}/provisioning/mapping/{map_uuid}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/app/{app_uuid}/provisioning/mapping/{map_uuid}/',
                'method': 'put'
            }
        }
    }
)

app_provisioning_profile_tag = 'app.provisioning.profile'
app_provisioning_profile_name = '应用同步配置属性'

extend_schema_tags(
    app_provisioning_profile_tag,
    app_provisioning_profile_name,
    {
        'type':'table_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/app/{app_uuid}/provisioning/profile/',
            'method': 'get'
        },
        'global': {
            'create': {
                'tag': 'app.provisioning.profile.create'
            }
        },
        'local': {
            'update': {
                'tag': 'app.provisioning.profile.update'
            },
            'delete': {
                'path': '/api/v1/tenant/{tenant_uuid}/app/{app_uuid}/provisioning/profile/{profile_uuid}/',
                'method': 'delete'
            }
        }
    }
)

app_provisioning_profile_create_tag = 'app.provisioning.profile.create'
app_provisioning_profile_create_name = '创建应用同步配置属性'

extend_schema_tags(
    app_provisioning_profile_create_tag,
    app_provisioning_profile_create_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/app/{app_uuid}/provisioning/profile/',
            'method': 'post'
        },
        'global': {
            'create': {
                'path': '/api/v1/tenant/{tenant_uuid}/app/{app_uuid}/provisioning/profile/',
                'method': 'post'
            }
        }
    }
)


app_provisioning_profile_update_tag = 'app.provisioning.profile.update'
app_provisioning_profile_update_name = '编辑应用同步配置属性'

extend_schema_tags(
    app_provisioning_profile_update_tag,
    app_provisioning_profile_update_name,
    {
        'type': 'form_page',
        'init': {
            'path': '/api/v1/tenant/{tenant_uuid}/app/{app_uuid}/provisioning/profile/{profile_uuid}/',
            'method': 'get'
        },
        'global': {
            'update': {
                'path': '/api/v1/tenant/{tenant_uuid}/app/{app_uuid}/provisioning/profile/{profile_uuid}/',
                'method': 'put'
            }
        }
    }
)