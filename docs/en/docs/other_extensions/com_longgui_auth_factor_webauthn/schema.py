from typing import Optional, List
from arkid.core.schema import ResponseSchema
from pydantic import BaseModel, Field
from webauthn.helpers.structs import AuthenticatorTransport, CredentialDeviceType


class RegistrationOptionsRequestSchema(BaseModel):
    username: str = Field(
        type="text",
        title="用户名",
    )
    config_id: str = Field(
        type="text",
        title="配置ID",
    )


class RegistrationResponseSchema(BaseModel):
    username: str = Field(
        type="text",
        title="用户名",
    )
    config_id: str = Field(
        type="text",
        title="配置ID",
    )
    response: dict = Field(default={})


class AuthenticationOptionsRequestSchema(BaseModel):
    username: str = Field(
        default='',
        type="text",
        title="用户名",
    )
    config_id: str = Field(
        type="text",
        title="配置ID",
    )


class AuthenticationResponseSchema(BaseModel):
    username: str = Field(
        default='',
        type="text",
        title="用户名",
    )
    config_id: str = Field(
        type="text",
        title="配置ID",
    )
    response: dict = Field(default={})


class WebAuthnCredential(BaseModel):
    """
    A Pydantic class for WebAuthn credentials in Redis. Includes information py_webauthn will need
    for verifying authentication attempts after registration.

    ID and public key bytes should be **Base64URL-encoded** for ease of storing in and referencing
    from Redis
    """

    id: str
    public_key: str
    username: str
    sign_count: int
    is_discoverable_credential: bool
    device_type: CredentialDeviceType
    backed_up: bool
    transports: Optional[List[AuthenticatorTransport]]


class ListMineCredentialsOut(ResponseSchema):
    pass


class CredentialItemSchema(BaseModel):
    id: str
    cred_id: str = Field(title="凭证ID")
    sign_count: int = Field(title="认证次数")
    transports: str = Field(title="认证器通信方式")
    is_disc_cred: bool = Field(title="客户端是否存储凭证")
    device_type: str = Field(title="设备类型")
    backed_up: bool = Field(title="凭证是否已备份")
