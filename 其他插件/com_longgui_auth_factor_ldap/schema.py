from logging import PlaceHolder
from typing import List, Optional
from uuid import UUID
from ninja import Field, Schema
from arkid.core.extension import create_extension_schema
from arkid.core.extension.auth_factor import BaseAuthFactorSchema
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _

UserFieldsOut = create_extension_schema(
    "UserFieldsOut",
    __file__,
    [
        (
            "data",
            List[str],
            Field(
                title=_("字段名")
            )
        )
    ],
    ResponseSchema
)

UpdateUserPasswordIn = create_extension_schema(
    "UpdateUserPasswordIn",
    __file__,
    [
        (
            "current_password",
            str,
            Field(
                type="password",
                title="原密码",
            )
        ),
        (
            "password",
            str,
            Field(
                type="password",
                title="新密码",
            )
        ),
        (
            "confirm_password",
            str,
            Field(
                type="password",
                title="确认密码",
                default=""
            )
        )
    ],
)

UpdateUserPasswordOut = create_extension_schema(
    "UpdateUserPasswordOut",
    __file__,
    [
        (
            "data",
            List[str],
            Field(
                title=_("字段名")
            )
        )
    ],
    ResponseSchema
)