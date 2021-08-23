"""
自定义字段映射关系及配置
"""
attribute_mappings = {
    "people": {
        "uid": "uuid",
        "cn": "username",
        "givenName": "last_name",
        "mail": "email",
        "telephoneNumber": "mobile"
    },
    "group": {
        "id": "id",
        "cn": "name"
    }
}
