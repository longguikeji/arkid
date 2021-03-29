from typing import Any
from common.provider import StorageProvider
from pathlib import Path
import uuid
import oss2
import os


class OSSStorageProvider(StorageProvider):

    endpoint: str
    domain: str
    bucket: str
    access_key: str
    secret_key: str

    def __init__(self) -> None:
        super().__init__()
        self.endpoint = None
        self.domain = None
        self.bucket = None
        self.access_key = None
        self.secret_key = None

    def upload(self, file: Any) -> str:
        key = self.generate_key(file)

        auth = oss2.Auth(self.access_key, self.secret_key)
        bucket = oss2.Bucket(auth, self.endpoint, self.bucket)
        bucket.put_object(key, file)

        return key

    def resolve(self, key):
        return os.path.join(self.domain, key)