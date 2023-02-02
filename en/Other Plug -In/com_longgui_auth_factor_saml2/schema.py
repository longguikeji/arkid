from typing import List, Optional
from ninja import Field, Schema
from arkid.core.extension import create_extension_schema
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _

AttributeMapping = create_extension_schema(
    "AttributeMapping",
    __file__,
    fields=[
        (
            "key",
            str,
            Field(
                title=_("字段名")
            )
        ),
        (
            "value",
            str,
            Field(
                title=_("映射名")
            )
        )
    ]
)

class ConfigSchema(Schema):
    """
    序列器
    """
    idp_xmldata_file:Optional[str] = Field(
        title=_("IDP元数据文件"),
        required=False,
        format="binary",
    )

    attribute_mapping:Optional[List[AttributeMapping]] = Field(
        title=_("自定义属性映射"),
        required=False,
        format='dynamic',
        type="array",
    )
    
LoginOut = create_extension_schema(
    "LoginOut",
    __file__,
    fields=[
        (
            "redirect",
            str,
            Field(
                title=_("跳转链接")
            )
        )
    ],
    base_schema=ResponseSchema
)