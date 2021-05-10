#!/usr/bin/env python3


"""Tasks used by the Celery dispatcher."""

from celery import shared_task
from celery.utils.functional import memoize
from .request import Request


@shared_task(ignore_result=True)
def dispatch_requests(reqs, app=None):
    # type: (Sequence[Dict], App) -> None
    """Process a batch of HTTP requests."""
    session = Request.Session()
    [dispatch_request(session=session, **req) for req in reqs]


@shared_task(bind=True, ignore_result=True)
def dispatch_request(self, event, data, sender, subscriber, session=None, **kwargs):
    # type: (str, Dict, Any, Dict, requests.Session, App, **Any) -> None
    """Process a single HTTP request."""
    request = Request(event, data, sender, subscriber, **kwargs)
    try:
        request.dispatch(session=session, propagate=request.retry)
    except request.connection_errors + request.timeout_errors as exc:
        if request.retry:
            raise self.retry(
                exc=exc, max_retries=request.retry_max, countdown=request.retry_delay
            )
        raise
