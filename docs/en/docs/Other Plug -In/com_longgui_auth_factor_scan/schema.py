from typing import Optional, List
from arkid.core.schema import ResponseSchema
from pydantic import BaseModel, Field


class QRCodeIn(BaseModel):
    qrcode_id: str = Field(
        type="text",
        title="QRCode ID",
    )


class QRCodeCreateOut(BaseModel):
    qrcode_id: str = Field(
        type="text",
        title="QRCode ID",
    )


class QRCodeStatusOut(BaseModel):
    qrcode_id: str = Field(
        type="text",
        title="QRCode ID",
    )
    expired: bool = Field(
        title="Is Expired",
    )

    status: str = Field(
        title="Status",
    )

    userinfo: Optional[dict] = Field(
        title="User Info",
    )

    token: Optional[str] = Field(
        title="token",
    )
