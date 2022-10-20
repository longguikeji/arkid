import logging

from django.contrib import messages
from django.contrib.auth import logout
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from arkid.core.models import User
from .exceptions import InvalidTicketSpec
from ..models import ServiceTicket
from ..models import ProxyTicket
from ..models import ProxyGrantingTicket
from .services import get_callbacks

logger = logging.getLogger(__name__)


def validate_service_ticket(service, ticket, pgturl=None, renew=False, require_https=False):
    """
    Validate a service ticket string. Return a triplet containing a
    ``ServiceTicket`` and an optional ``ProxyGrantingTicket``, or a
    ``ValidationError`` if ticket validation failed.
    """
    logger.debug("Service validation request received for %s" % ticket)

    # Check for proxy tickets passed to /serviceValidate
    if ticket and ticket.startswith(ProxyTicket.TICKET_PREFIX):
        raise InvalidTicketSpec('Proxy tickets cannot be validated with /serviceValidate')

    st = ServiceTicket.objects.validate_ticket(ticket, service, renew=renew, require_https=require_https)
    attributes = get_attributes(st.user, st.service)

    if pgturl is not None:
        logger.debug("Proxy-granting ticket request received for %s" % pgturl)
        pgt = ProxyGrantingTicket.objects.create_ticket(service, pgturl, user=st.user, granted_by_st=st)
    else:
        pgt = None
    return st, attributes, pgt


def validate_proxy_ticket(service, ticket, pgturl=None):
    """
    Validate a proxy ticket string. Return a 4-tuple containing a
    ``ProxyTicket``, an optional ``ProxyGrantingTicket`` and a list
    of proxies through which authentication proceeded, or a
    ``ValidationError`` if ticket validation failed.
    """
    logger.debug("Proxy validation request received for %s" % ticket)

    pt = ProxyTicket.objects.validate_ticket(ticket, service)
    attributes = get_attributes(pt.user, pt.service)

    # Build a list of all services that proxied authentication,
    # in reverse order of which they were traversed
    proxies = [pt.service]
    prior_pt = pt.granted_by_pgt.granted_by_pt
    while prior_pt:
        proxies.append(prior_pt.service)
        prior_pt = prior_pt.granted_by_pgt.granted_by_pt

    if pgturl is not None:
        logger.debug("Proxy-granting ticket request received for %s" % pgturl)
        pgt = ProxyGrantingTicket.objects.create_ticket(service, pgturl, user=pt.user, granted_by_pt=pt)
    else:
        pgt = None
    return pt, attributes, pgt, proxies


def validate_proxy_granting_ticket(pgt, target_service):
    """
    Validate a proxy granting ticket string. Return an ordered pair
    containing a ``ProxyTicket``, or a ``ValidationError`` if ticket
    validation failed.
    """
    logger.debug("Proxy ticket request received for %s using %s" % (target_service, pgt))

    pgt = ProxyGrantingTicket.objects.validate_ticket(pgt, target_service)
    pt = ProxyTicket.objects.create_ticket(service=target_service, user=pgt.user, granted_by_pgt=pgt)
    return pt


def get_attributes(user, service):
    """
    Return a dictionary of user attributes from the set of configured
    callback functions.
    """
    attributes = {}
    for path in get_callbacks(service):
        callback = import_string(path)
        attributes.update(callback(user, service))
    # 补充扩展字段
    user = User.expand_objects.filter(id=user.id).first()
    if 'mobile' in user:
        attributes['mobile'] = user.get('mobile')
    if 'nickname' in user:
        attributes['nickname'] = user.get('nickname')
    return attributes


def logout_user(request):
    """End a single sign-on session for the current user."""
    logger.debug("Logout request received for %s" % request.user)
    if request.user:
        ServiceTicket.objects.consume_tickets(request.user)
        ProxyTicket.objects.consume_tickets(request.user)
        ProxyGrantingTicket.objects.consume_tickets(request.user)

        ServiceTicket.objects.request_sign_out(request.user)

        logger.info("Single sign-on session ended for %s" % request.user)
        logout(request)
        messages.success(request, _('You have been successfully logged out'))
