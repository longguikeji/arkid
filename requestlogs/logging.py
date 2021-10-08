import logging
import uuid
import threading

from .base import SETTINGS

local = threading.local()


def get_request_id():
    return getattr(local, SETTINGS['REQUEST_ID_ATTRIBUTE_NAME'], '')


def set_request_id(_uuid=None):
    _uuid = _uuid or uuid.uuid4().hex
    setattr(local, SETTINGS['REQUEST_ID_ATTRIBUTE_NAME'], _uuid)
    return _uuid


def validate_uuid(_uuid):
    try:
        val = uuid.UUID(_uuid, version=4)
    except (ValueError, TypeError):
        return None

    return _uuid if val.hex == _uuid else None


class RequestIdContext(logging.Filter):
    def filter(self, record):
        setattr(record, SETTINGS['REQUEST_ID_ATTRIBUTE_NAME'],
                get_request_id())
        return True
