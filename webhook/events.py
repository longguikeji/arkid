#!/usr/bin/env python3


"""User-defined webhook events."""

import logging
from operator import attrgetter
from .dispatcher import CeleryDispatcher
from inventory.models import User, Group
from app.models import App
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

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
        self.name = name
        self.timeout = timeout
        self.retry = retry
        self.retry_max = retry_max
        self.retry_delay = retry_delay
        self.allow_keepalive = allow_keepalive

    def send(self, data, tenants=None, timeout=None):
        """Send event to all subscribers."""
        return self._send(self.name, data, tenants=tenants, timeout=timeout)

    def _send(self, name, data, tenants=None, timeout=None):
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

    def __init__(self, name, model, tenant_field=None, **kwargs):
        super(ModelEvent, self).__init__(name, **kwargs)
        self.tenant_field = tenant_field
        self.model = model
        self.signals = self.setup_signals()
        self.connect_signal_receiver(model)

    def setup_signals(self):
        return {}

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
        value = attrgetter(self.tenant_field)(instance)
        if not value:
            return []
        elif isinstance(value, models.ManyToManyField):
            return value.all()
        else:
            return [value]

    def instance_data(self, instance):
        """Get event data from ``instance.webhooks.payload()``."""
        return instance.as_dict()

    def prepare_sender(self, sender):
        return sender

    def connect_signal_receiver(self, sender=None, weak=False, **kwargs):
        for signal, handler in self.signals.items():
            signal.connect(
                handler, sender=self.prepare_sender(sender), weak=weak, **kwargs
            )

    def should_dispatch(self, instance, **kwargs):
        raise NotImplementedError('Method Not Implemented!')

    def on_signal(self, instance, **kwargs):
        try:
            return self.send_from_instance(instance, **kwargs)
        except Exception as exc:
            logger.exception('Event %s Dispatch Error %s', self.name, exc)
            raise exc

    def __call__(self, instance, **kwargs):
        if self.should_dispatch(instance, **kwargs):
            return self.on_signal(instance, **kwargs)


class CreateModelEvent(ModelEvent):
    def should_dispatch(self, instance, raw=False, created=False, **kwargs):
        return not raw and created

    def setup_signals(self):
        from django.db.models.signals import post_save

        return {post_save: self}


class UpdateModelEvent(ModelEvent):
    def should_dispatch(self, instance, created=False, raw=False, **kwargs):
        if instance.is_del:
            return False

        return not raw and not created

    def setup_signals(self):
        from django.db.models.signals import post_save

        return {post_save: self}


class DeleteModelEvent(ModelEvent):
    def should_dispatch(self, instance, created=False, raw=False, **kwargs):
        if not instance.is_del:
            return False
        if not hasattr(instance, '_previous_version'):
            return False
        if instance._previous_version.is_del:
            return False
        return not raw and not created

    def setup_signals(self):
        from django.db.models.signals import post_save, pre_save

        return {
            post_save: self,
            pre_save: self.on_pre_save,
        }

    def on_pre_save(self, instance, sender, raw=False, **kwargs):
        if not raw and instance.pk and instance.is_del:
            try:
                instance._previous_version = sender.objects.get(pk=instance.pk)
            except ObjectDoesNotExist:
                pass


user_created_event = CreateModelEvent(
    'event.user.created', User, tenant_field='tenants'
)
user_updated_event = UpdateModelEvent(
    'event.user.updated', User, tenant_field='tenants'
)
user_deleted_event = DeleteModelEvent(
    'event.user.deleted', User, tenant_field='tenants'
)

group_created_event = CreateModelEvent(
    'event.group.created', Group, tenant_field='tenant'
)
group_updated_event = UpdateModelEvent(
    'event.group.updated', Group, tenant_field='tenant'
)
group_deleted_event = DeleteModelEvent(
    'event.group.deleted', Group, tenant_field='tenant'
)

app_created_event = CreateModelEvent('event.app.created', App, tenant_field='tenant')
app_updated_event = UpdateModelEvent('event.app.updated', App, tenant_field='tenant')
app_deleted_event = DeleteModelEvent('event.app.deleted', App, tenant_field='tenant')
