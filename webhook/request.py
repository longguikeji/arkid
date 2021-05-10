#!/usr/bin/env python3


"""Webhook HTTP requests."""
import requests
import logging
from contextlib import contextmanager

import uuid
from requests.exceptions import ConnectionError, Timeout

logger = logging.getLogger(__name__)


class Request(ThenableProxy):
    """Webhook HTTP request.

    Arguments:
        event (str): Name of event.
        data (Any): Event payload.
        sender (Any): Sender of event (or :const:`None`).
        subscriber (~thorn.generic.models.Subscriber): Subscriber to
            dispatch the request for.

    Keyword Arguments:
        on_success (Callable): Optional callback called if
            the HTTP request succeeds.  Must take single argument: ``request``.
        on_timeout (Callable): Optional callback called if the HTTP request
            times out. Must have signature: ``(request, exc)``.
        on_error (Callable): Optional callback called if the HTTP request
            fails.  Must have signature: ``(request, exc)``.
        headers (Mapping): Additional HTTP headers to send with the request.
        user_agent (str): Set custom HTTP user agent.
        recipient_validators (Sequence): List of serialized recipient
            validators.
        allow_keepalive (bool): Allow reusing session for this HTTP request.
            Enabled by default.

        retry (bool): Retry in the event of timeout/failure?
            Disabled by default.
        retry_max (int): Maximum number of times to retry before giving up.
            Default is 3.
        retry_delay (float): Delay between retries in seconds int/float.
            Default is 60 seconds.
    """

    Session = requests.Session

    #: Holds the response after the HTTP request is performed.
    response = None

    #: Tuple of exceptions considered a connection error.
    connection_errors = (ConnectionError,)

    #: Tuple of exceptions considered a timeout error.
    timeout_errors = (Timeout,)

    def __init__(
        self,
        event,
        data,
        sender,
        subscriber,
        id=None,
        timeout=None,
        retry=None,
        retry_max=None,
        retry_delay=None,
        headers=None,
        allow_keepalive=True,
        allow_redirects=None,
    ):
        # type: (str, Dict, Any, Subscriber, str, Callable,
        #        Callable, float, Callable, bool, int,
        #        float, Mapping, str, App, Sequence[Callable],
        #        bool, bool) -> None
        self.id = id or uuid()
        self.event = event
        self.data = data
        self.sender = sender
        self.subscriber = subscriber
        self.timeout = timeout
        self.retry = self.app.settings.THORN_RETRY if retry is None else retry
        self.retry_max = (
            self.app.settings.THORN_RETRY_MAX if retry_max is None else retry_max
        )
        self.retry_delay = (
            self.app.settings.THORN_RETRY_DELAY if retry_delay is None else retry_delay
        )
        self.allow_keepalive = allow_keepalive
        if allow_redirects is None:
            allow_redirects = self.app.settings.THORN_ALLOW_REDIRECTS
        self.allow_redirects = allow_redirects
        self.response = None
        self._headers = headers

    def annotate_headers(self, extra_headers):
        # type: (Dict[str, Any]) -> Dict[str, Any]
        return dict(self.headers, **extra_headers)

    def validate_recipient(self, url):
        # type: (str) -> None
        return True

    def sign_request(self, subscriber, data):
        # type: (Subscriber, str) -> str
        return subscriber.sign(data)

    def dispatch(self, session=None):
        # type: (requests.Session, bool) -> 'Request'
        if not self.cancelled:
            self.validate_recipient(self.subscriber.url)
            with self._finalize_unless_request_error():
                self.response = self.post(session=session)
                return self

    @contextmanager
    def _finalize_unless_request_error(self):
        # type: (bool) -> Any
        try:
            yield
        except self.timeout_errors as exc:
            self.handle_timeout_error(exc)
        except self.connection_errors as exc:
            self.handle_connection_error(exc)
        else:
            pass

    @contextmanager
    def session_or_acquire(self, session=None, close_session=False):
        # type: (requests.Session, bool) -> Any
        if session is None or not self.allow_keepalive:
            session, close_session = self.Session(), True
        try:
            yield session
        finally:
            if close_session and session is not None:
                session.close()

    def post(self, session=None):
        # type: (requests.Session) -> requests.Response
        url = self.subscriber.url
        with self.session_or_acquire(session) as session:
            return session.post(
                url=url,
                data=self.data,
                allow_redirects=self.allow_redirects,
                timeout=self.timeout,
                headers=self.annotate_headers(
                    {
                        'Hook-HMAC': self.sign_request(self.subscriber, self.data),
                        'Hook-Subscription': str(self.subscriber.uuid),
                    }
                ),
                verify=False,
            )

    def handle_timeout_error(self, exc, propagate=False):
        # type: (Exception, bool) -> Any
        logger.info(
            'Timed out while dispatching webhook request: %r',
            exc,
            exc_info=1,
            extra={'data': self.as_dict()},
        )
        if self.on_timeout:
            return self.on_timeout(self, exc)

    def handle_connection_error(self, exc, propagate=False):
        # type: (Exception, bool) -> None
        logger.error(
            'Error dispatching webhook request: %r',
            exc,
            exc_info=1,
            extra={'data': self.as_dict()},
        )

    def as_dict(self):
        # type: () -> Dict[str, Any]
        """Return dictionary representation of this request.

        Note:
            All values must be json serializable.
        """
        return {
            'id': self.id,
            'event': self.event,
            'sender': self.sender,
            'subscriber': self.subscriber.as_dict(),
            'data': self.data,
            'timeout': self.timeout,
            'retry': self.retry,
            'retry_max': self.retry_max,
            'retry_delay': self.retry_delay,
            'allow_keepalive': self.allow_keepalive,
        }

    @property
    def headers(self):
        # type: () -> Dict[str, Any]
        return dict(self.default_headers, **self._headers or {})

    @property
    def default_headers(self):
        # type: () -> Dict[str, Any]
        return {
            'Content-Type': self.subscriber.content_type,
            'Hook-Event': self.event,
            'Hook-Delivery': self.id,
        }
