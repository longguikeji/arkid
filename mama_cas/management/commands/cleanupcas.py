from django.core.management.base import BaseCommand

from mama_cas.models import ServiceTicket
from mama_cas.models import ProxyTicket
from mama_cas.models import ProxyGrantingTicket


class Command(BaseCommand):
    """
    A management command for deleting invalid tickets from the
    database. A ticket is invalidated either by being consumed or
    by expiration. Invalid tickets are not valid for authentication
    and can be safely deleted.

    These tickets are not deleted at the moment of invalidation so
    appropriate error messages can be returned if an invalid ticket is
    validated. However, this command should be run periodically to
    prevent storage or performance problems.

    This command calls ``delete_invalid_tickets()`` for each applicable
    model, which deletes all invalid tickets of that type that are not
    referenced by other ``Ticket``s.
    """
    help = "Delete consumed or expired CAS tickets from the database"

    def handle(self, **options):
        ProxyGrantingTicket.objects.delete_invalid_tickets()
        ProxyTicket.objects.delete_invalid_tickets()
        ServiceTicket.objects.delete_invalid_tickets()
