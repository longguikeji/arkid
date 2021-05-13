#!/usr/bin/env python3


"""Webhook HTTP requests."""
import requests
import logging
from contextlib import contextmanager
from vine.abstract import Thenable, ThenableProxy
from vine import maybe_promise, promise

import uuid
from requests.exceptions import ConnectionError, Timeout, ProxyError

logger = logging.getLogger(__name__)
RETRY = True
RETRY_MAX = 10
RETRY_DELAY = 60.0
ALLOW_REDIRECTS = False


@Thenable.register
class Request(ThenableProxy):
    """Webhook HTTP request.

    Arguments:
        event (str): Name of event.
        data (Any): Event payload.
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
    connection_errors = (ConnectionError, ProxyError)

    #: Tuple of exceptions considered a timeout error.
    timeout_errors = (Timeout,)

    def __init__(
        self,
        event,
        data,
        webhook,
        id=None,
        on_timeout=None,
        timeout=None,
        on_success=None,
        on_error=None,
        retry=None,
        retry_max=None,
        retry_delay=None,
        headers=None,
        allow_keepalive=True,
        allow_redirects=None,
    ):
        self.id = id or uuid.uuid4()
        self.event = event
        self.data = data
        self.webhook = webhook
        self.timeout = timeout
        self.on_success = on_success
        self.on_timeout = maybe_promise(on_timeout)
        self.on_error = on_error
        self.retry = RETRY if retry is None else retry
        self.retry_max = RETRY_MAX if retry_max is None else retry_max
        self.retry_delay = RETRY_DELAY if retry_delay is None else retry_delay
        self.allow_keepalive = allow_keepalive
        self.allow_redirects = (
            ALLOW_REDIRECTS if allow_redirects is None else allow_redirects
        )
        self.response = None
        self._headers = headers
        self._set_promise_target(
            promise(
                args=(self,),
                callback=self.on_success,
                on_error=self.on_error,
            )
        )

    def annotate_headers(self, extra_headers):
        # type: (Dict[str, Any]) -> Dict[str, Any]
        return dict(self.headers, **extra_headers)

    def validate_recipient(self, url):
        # type: (str) -> None
        return True

    def sign_request(self, webhook, data):
        # type: (Subscriber, str) -> str
        return webhook.sign(data)

    def dispatch(self, session=None, propagate=False):
        if not self.cancelled:
            self.validate_recipient(self.webhook.url)
            with self._finalize_unless_request_error(propagate):
                self.response = self.post(session=session)
                return self

    @contextmanager
    def _finalize_unless_request_error(self, propagate=False):
        # type: (bool) -> Any
        try:
            yield
        except self.timeout_errors as exc:
            self.handle_timeout_error(exc, propagate=propagate)
        except self.connection_errors as exc:
            self.handle_connection_error(exc, propagate=propagate)
        else:
            self._p()

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
        url = self.webhook.url
        with self.session_or_acquire(session) as session:
            return session.post(
                url=url,
                data=self.data,
                allow_redirects=self.allow_redirects,
                timeout=self.timeout,
                headers=self.annotate_headers(
                    {
                        'Arkid-Signature-256': self.sign_request(
                            self.webhook, self.data
                        ),
                        'Arkid-Hook-UUID': str(self.webhook.uuid),
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
        return self._p.throw(exc, propagate=propagate)

    def handle_connection_error(self, exc, propagate=False):
        # type: (Exception, bool) -> None
        logger.error(
            'Error dispatching webhook request: %r',
            exc,
            exc_info=1,
            extra={'data': self.as_dict()},
        )
        self._p.throw(exc, propagate=propagate)

    def as_dict(self):
        """Return dictionary representation of this request.

        Note:
            All values must be json serializable.
        """
        return {
            'id': self.id,
            'event': self.event,
            'webhook': self.webhook.as_dict(),
            'data': self.data,
            'timeout': self.timeout,
            'retry': self.retry,
            'retry_max': self.retry_max,
            'retry_delay': self.retry_delay,
            'allow_keepalive': self.allow_keepalive,
        }

    @property
    def headers(self):
        return dict(self.default_headers, **self._headers or {})

    @property
    def default_headers(self):
        return {
            'Content-Type': self.webhook.content_type,
            'Arkid-Hook-Event': self.event,
            'Arkid-Hook-Delivery': self.id,
        }
