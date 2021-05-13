#!/usr/bin/env python3


"""Tasks used by the Celery dispatcher."""

from celery import shared_task
from celery import group
from .request import Request
from .models import WebHook
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def dispatch_requests(reqs, app=None):
    """Process a batch of HTTP requests."""
    # session = Request.Session()
    g = group(dispatch_request.s(**req) for req in reqs)
    g.delay()


@shared_task(bind=True, ignore_result=True)
def dispatch_request(self, event, data, webhook, session=None, **kwargs):
    """Process a single HTTP request."""
    webhook = WebHook(**webhook)
    request = Request(event, data, webhook, **kwargs)
    try:
        request.dispatch(session=session, propagate=request.retry)
    except request.connection_errors + request.timeout_errors as exc:
        if request.retry:
            raise self.retry(
                exc=exc, max_retries=request.retry_max, countdown=request.retry_delay
            )
        raise
