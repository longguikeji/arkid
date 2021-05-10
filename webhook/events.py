#!/usr/bin/env python3


"""User-defined webhook events."""

import logging
from operator import attrgetter
from .dispatcher import CeleryDispatcher

logger = logging.getLogger(__name__)


class Event(object):
    """Webhook Event.

    Arguments:
        name (str): Name of this event.
            Namespaces can be dot-separated, and if so subscribers can
            glob-match based on the parts in the name, e.g.
            ``"order.created"``.

    Keyword Arguments:
        timeout (float): Default request timeout for this event.
        retry (bool): Enable/disable retries when dispatching this event fails
            Disabled by default.
        retry_max (int): Max number of retries (3 by default).
        retry_delay (float): Delay between retries (60 seconds by default).
        allow_keepalive: Flag to disable HTTP connection keepalive
            for this event only.  Keepalive is enabled by default.

    """

    allow_keepalive = True

    def __init__(
        self,
        name,
        timeout=None,
        retry=None,
        retry_max=None,
        retry_delay=None,
        request_data=None,
        allow_keepalive=None,
        **kwargs
    ):
        # type: (str, float, Dispatcher, bool, int, float, App,
        #        List, Mapping, Dict, bool) -> None
        self.name = name
        self.timeout = timeout
        self.retry = retry
        self.retry_max = retry_max
        self.retry_delay = retry_delay
        if allow_keepalive is not None:
            self.allow_keepalive = allow_keepalive
        self.dispatcher = CeleryDispatcher()

    def send(self, data, sender=None, timeout=None):
        # type: (Any, Any, Callable, Callable, float, Callable) -> promise
        """Send event to all subscribers."""
        return self._send(self.name, data, sender=sender, timeout=timeout)

    def _send(self, name, data, sender=None, timeout=None):
        # type: (str, Any, Dict, Any, Callable,
        #        Callable, float, Callable, Dict) -> promise
        timeout = timeout if timeout is not None else self.timeout
        return self.dispatcher.send(
            name,
            data,
            sender,
            timeout=timeout,
            retry=self.retry,
            retry_max=self.retry_max,
            retry_delay=self.retry_delay,
            allow_keepalive=self.allow_keepalive,
        )


class ModelEvent(Event):
    """Event related to model changes.

    This event type follows a specific payload format:

    .. code-block:: json

        {"event": "(str)event_name",
         "sender": "(User pk)optional_sender",
         "data": {"event specific data": "value"}}

    """

    def __init__(self, name, model, signal, *args, **kwargs):
        super(ModelEvent, self).__init__(name, **kwargs)
        self.signal = signal
        self.model = model

    def send(self, instance, data=None, sender=None, **kwargs):
        # type: (Model, Any, Any, **Any) -> promise
        """Send event for model ``instance``.

        Keyword Arguments:
            data (Any): Event specific data.

        See Also:
            :meth:`Event.send` for more arguments supported.
        """
        return self._send(
            self.name,
            self.to_message(
                data,
                instance=instance,
                sender=sender,
            ),
            sender=sender,
            **kwargs
        )

    def send_from_instance(self, instance, **kwargs):
        # type: (Model, Mapping, **Any) -> promise
        return self.send(
            instance=instance,
            data=self.instance_data(instance),
            sender=self.instance_sender(instance),
        )

    def to_message(self, data, instance=None, sender=None):
        # type: (Any, Model, Any, str) -> Dict[str, Any]
        return {
            'event': self.name,
            'sender': sender,
            'data': data or {},
        }

    def instance_sender(self, instance):
        # type: (Model) -> Any
        """Get event ``sender`` from model instance."""
        return None

    def instance_data(self, instance):
        # type: (Model) -> Any
        """Get event data from ``instance.webhooks.payload()``."""
        return {}

    def connect_model_signal(self, **kwargs):

        signal.connect(self, sender=self.model, **kwargs)

    def should_dispatch(self, instance, **kwargs):
        # type: (Model, **Any) -> bool
        return True

    def on_signal(self, instance, **kwargs):
        try:
            return self.send_from_instance(instance, **kwargs)
        except Exception as exc:
            logger.exception('Event %s Dispatch Error %s', self.name, exc)
            raise exc

    def __call__(self, instance, **kwargs):
        if self.should_dispatch(instance, **kwargs):
            return self.on_signal(instance, **kwargs)
