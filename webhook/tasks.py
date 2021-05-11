#!/usr/bin/env python3


"""Tasks used by the Celery dispatcher."""

from celery import shared_task
from .request import Request
from .models import WebHook


@shared_task(ignore_result=True)
def dispatch_requests(reqs, app=None):
    # type: (Sequence[Dict], App) -> None
    """Process a batch of HTTP requests."""
    session = Request.Session()
    [dispatch_request(session=session, **req) for req in reqs]


@shared_task(bind=True, ignore_result=True)
def dispatch_request(self, event, data, webhook, session=None, **kwargs):
    # type: (str, Dict, Any, Dict, requests.Session, App, **Any) -> None
    """Process a single HTTP request."""
    webhook = WebHook(**webhook)
    request = Request(event, data, webhook, **kwargs)
    try:
        request.dispatch(session=session)
    except request.connection_errors + request.timeout_errors as exc:
        if request.retry:
            raise self.retry(
                exc=exc, max_retries=request.retry_max, countdown=request.retry_delay
            )
        raise
