#!/usr/bin/env python3


"""Default webhook dispatcher."""

from celery import group
from .tasks import dispatch_requests
from .utils import chunks
from .request import Request
from .models import WebHook
import json

MIME_JSON = 'application/json'
DEFAULT_CODECS = {MIME_JSON: json.dumps}
CHUNKSIZE = 10
EVENT_TIMEOUT = 3.0


class BaseDispatcher:
    def __init__(self):
        self.timeout = EVENT_TIMEOUT

    def send(self, event, payload, sender, allow_keepalive=True, **kwargs):
        pass

    def prepare_requests(self, event, payload, tenants, timeout=None, **kwargs):
        # holds a cache of the payload serialized by content-type,
        # built incrementally depending on what content-types are
        # required by the subscribers.
        cache = {}
        timeout = timeout if timeout is not None else self.timeout
        return (
            Request(
                event,
                self.encode_cached(payload, cache, webhook.content_type),
                webhook,
                timeout=timeout,
                **kwargs
            )
            for webhook in self.webhooks_for_event(event, tenants)
        )

    def encode_cached(self, payload, cache, ctype):
        try:
            return cache[ctype]
        except KeyError:
            value = cache[ctype] = self.encode_payload(payload, ctype)
            return value

    def encode_payload(self, data, content_type):
        try:
            encode = DEFAULT_CODECS[content_type]
        except KeyError:
            return data
        else:
            return encode(data)

    def webhooks_for_event(self, name, tenants=None):
        assert tenants.count() >= 1
        hooks = WebHook.objects.filter(events__contains=name, tenant__in=tenants)
        return hooks


class CeleryDispatcher(BaseDispatcher):
    """Dispatcher using Celery tasks to dispatch events."""

    def as_request_group(self, requests):
        return group(
            dispatch_requests.s([req.as_dict() for req in chunk])
            for chunk in self.group_requests(requests)
        )

    def group_requests(self, requests):
        """Group requests by keep-alive host/port/scheme ident."""
        return chunks(iter(requests), CHUNKSIZE)

    def send(self, event, payload, tenants, timeout=None, **kwargs):
        return self.as_request_group(
            self.prepare_requests(
                event,
                payload,
                tenants,
                timeout,
            )
        ).apply_async()
