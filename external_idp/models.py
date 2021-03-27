from typing import Optional
from common.provider import ExternalIdpProvider


class ExternalIdp:

    id: str
    name: str
    description: str

    provider: ExternalIdpProvider
    source: any

    def __init__(self, id: str, name: str, description: str, provider: ExternalIdpProvider, source: any) -> None:
        self.id = id
        self.name = name
        self.description = description
        self.provider = provider
        self.source = source