from pydantic import BaseModel, HttpUrl
from enum import Enum
from typing import Optional

class AuthTypeEnum(str, Enum):
    oauth = "oauth"
    oauth2 = "oauth2"
    oauthbearertoken = "oauthbearertoken"
    httpbasic = "httpbasic"
    httpdigest = "httpdigest"

class AuthenticationScheme(BaseModel):
    type: AuthTypeEnum
    name: str
    description: str
    specUri: Optional[HttpUrl] 
    documentationUri: Optional[HttpUrl]  