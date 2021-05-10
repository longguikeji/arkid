#!/usr/bin/env python3


"""Default webhook dispatcher."""

from celery import group
from tasks import dispatch_requests
from .utils import chunks
from .request import Request
import json

MIME_JSON = 'application/json'
DEFAULT_CODECS = {MIME_JSON: json.dumps}
CHUNKSIZE = 10


class BaseDispatcher:
    def __init__(self, timeout=None):
        self.timeout = (
            timeout if timeout is not None else self.app.settings.THORN_EVENT_TIMEOUT
        )

    def send(self, event, payload, sender, allow_keepalive=True, **kwargs):
        pass

    def prepare_requests(self, event, payload, sender, timeout=None, **kwargs):
        # holds a cache of the payload serialized by content-type,
        # built incrementally depending on what content-types are
        # required by the subscribers.
        cache = {}
        timeout = timeout if timeout is not None else self.timeout
        context = context or {}
        return (
            Request(
                event,
                self.encode_cached(payload, cache, subscriber.content_type),
                sender,
                subscriber,
                timeout=timeout,
                **kwargs
            )
            for subscriber in self.subscribers_for_event(event, sender)
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

    def subscribers_for_event(self, name, sender=None):
        """Return a list of :class:`~thorn.django.models.Subscriber`
        subscribing to an event by name (optionally filtered by sender)."""
        pass


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

    def send(self, event, payload, sender, timeout=None, **kwargs):
        return self.as_request_group(
            self.prepare_requests(
                event,
                payload,
                sender.pk if sender else sender,
                timeout,
            )
        ).apply_async()
