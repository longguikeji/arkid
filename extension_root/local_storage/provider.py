from typing import Any
from common.provider import StorageProvider
from pathlib import Path
from django.urls import reverse
from .constants import KEY


class LocalStorageProvider(StorageProvider):

    data_path: str

    def __init__(self) -> None:
        super().__init__()

    def upload(self, file: Any) -> str:
        key = self.generate_key(file)

        p = Path(self.data_path) / key

        if not p.parent.exists():
            p.parent.mkdir(parents=True)

        with open(p, 'wb') as fp:
            for chunk in file.chunks():
                fp.write(chunk)

        return key

    def resolve(self, key):
        return reverse("api:local_storage:render", args=[key, ])
