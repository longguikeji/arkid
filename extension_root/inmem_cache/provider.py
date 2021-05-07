import typing
from common.provider import CacheProvider


class InMemCacheProvider(CacheProvider):

    _data: typing.Dict[str, bytes] 

    def __init__(self) -> None:
        self._data = {}

    def set(self, key: str, value: any, expired: typing.Optional[int]=None):
        self._data[key] = value

    def get(self, key: str) -> typing.Optional[bytes]:
        return self._data.get(key, None)