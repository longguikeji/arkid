from typing import Optional, List
from ninja import Field, ModelSchema, Schema
from arkid.core.schema import ResponseSchema
from pydantic import UUID4
from arkid.core.translation import gettext_default as _

# class UpdateMinePasswordIn(Schema):

#     old_password: Optional[str] = Field(type="password", title="原密码", default=None)

#     password: str = Field(
#         type="password",
#         title="新密码",
#     )

#     confirm_password: str = Field(type="password", title="确认密码", default="")


class AuthenticatorsItemOut(Schema):

    id: UUID4 = Field(hidden=True)
    is_apply: bool = Field(title=_("是否应用"))
    otp_uri: str = Field(title=_("二维码URI"), format="qrcode")


class AuthenticatorDeleteOut(ResponseSchema):
    pass


class UserOTPAuthenticatorSchema(Schema):
    otp_uri: str = Field(title=_("二维码URI"), format="qrcode")
    otp_code: Optional[str] = Field(title=_("一次性密码"))


class UserOTPAuthenticatorOut(ResponseSchema):

    data: UserOTPAuthenticatorSchema


class UserOTPAuthenticatorEditSchema(Schema):
    otp_uri: str = Field(title=_("二维码URI"), readonly=True, format="qrcode")
    is_apply: bool = Field(title=_("是否应用"))


class UserOTPAuthenticatorEditOut(ResponseSchema):

    data: UserOTPAuthenticatorEditSchema
