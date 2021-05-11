#!/usr/bin/env python3


"""User-defined webhook events."""

import logging
from operator import attrgetter
from .dispatcher import CeleryDispatcher
from inventory.models import User, Group
from app.models import App
from django.db.models.signals import post_save, post_delete

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
    dispatcher = CeleryDispatcher()

    def __init__(
        self,
        name,
        timeout=None,
        retry=None,
        retry_max=None,
        retry_delay=None,
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

    def send(self, data, tenants=None, timeout=None):
        # type: (Any, Any, Callable, Callable, float, Callable) -> promise
        """Send event to all subscribers."""
        return self._send(self.name, data, tenants=tenants, timeout=timeout)

    def _send(self, name, data, tenants=None, timeout=None):
        # type: (str, Any, Dict, Any, Callable,
        #        Callable, float, Callable, Dict) -> promise
        timeout = timeout if timeout is not None else self.timeout
        return self.dispatcher.send(
            name,
            data,
            tenants,
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

    def __init__(self, name, model, signal, tenant_field=None, **kwargs):
        super(ModelEvent, self).__init__(name, **kwargs)
        self.signal = signal
        self.model = model
        self.tenant_field = tenant_field
        self.connect_model_signal()

    def send(self, instance, data=None, tenants=None, **kwargs):
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
            ),
            tenants=tenants,
            **kwargs
        )

    def send_from_instance(self, instance, **kwargs):
        # type: (Model, Mapping, **Any) -> promise
        return self.send(
            instance=instance,
            data=self.instance_data(instance),
            tenants=self.instance_tenants(instance),
        )

    def to_message(self, data, instance=None):
        # type: (Any, Model, Any, str) -> Dict[str, Any]
        return {
            'event': self.name,
            'data': data or {},
        }

    def instance_tenants(self, instance):
        # type: (Model) -> Any
        """Get tenants send to from model instance."""
        return attrgetter(self.tenant_field)(instance).all()

    def instance_data(self, instance):
        # type: (Model) -> Any
        """Get event data from ``instance.webhooks.payload()``."""
        return {}

    def connect_model_signal(self, **kwargs):

        self.signal.connect(self, sender=self.model, **kwargs)

    def should_dispatch(self, instance, **kwargs):
        # type: (Model, **Any) -> bool
        if attrgetter(self.tenant_field)(instance):
            return True
        else:
            return False

    def on_signal(self, instance, **kwargs):
        try:
            return self.send_from_instance(instance, **kwargs)
        except Exception as exc:
            logger.exception('Event %s Dispatch Error %s', self.name, exc)
            raise exc

    def __call__(self, instance, **kwargs):
        if self.should_dispatch(instance, **kwargs):
            return self.on_signal(instance, **kwargs)


user_created_event = ModelEvent(
    'event.user.created', User, post_save, tenant_field='tenants'
)
user_updated_event = ModelEvent(
    'event.user.updated', User, post_save, tenant_field='tenants'
)
user_deleted_event = ModelEvent(
    'event.user.deleted', User, post_delete, tenant_field='tenants'
)

group_created_event = ModelEvent(
    'event.group.created', Group, post_save, tenant_field='tenant'
)
group_updated_event = ModelEvent(
    'event.group.updated', Group, post_save, tenant_field='tenant'
)
group_deleted_event = ModelEvent(
    'event.group.deleted', Group, post_delete, tenant_field='tenant'
)

app_created_event = ModelEvent(
    'event.app.created', App, post_save, tenant_field='tenant'
)
app_updated_event = ModelEvent(
    'event.app.updated', App, post_save, tenant_field='tenant'
)
app_deleted_event = ModelEvent(
    'event.app.deleted', App, post_delete, tenant_field='tenant'
)
