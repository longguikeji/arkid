from django.core.management.base import BaseCommand

from mama_cas.services import get_backend_path
from mama_cas.services import get_callbacks
from mama_cas.services import get_logout_url
from mama_cas.services import logout_allowed
from mama_cas.services import proxy_allowed
from mama_cas.services import proxy_callback_allowed
from mama_cas.services import service_allowed


class Command(BaseCommand):
    help = 'Check validity and display configuration of a service identifier'

    def add_arguments(self, parser):
        parser.add_argument(
            'service',
            help='Service identifier (e.g. https://example.com)',
        )
        parser.add_argument(
            'pgturl', nargs='?',
            help='Proxy callback identifier (e.g. https://proxy.example.com)',
        )

    def handle(self, **options):
        self.service = options['service']
        self.pgturl = options['pgturl']
        self.verbosity = options['verbosity']

        if service_allowed(self.service):
            try:
                self.stdout.write(self.style.SUCCESS("Valid service: %s" % self.service))
            except AttributeError:
                # Django 1.8 does not have the "Success" style
                self.stdout.write(self.style.SQL_FIELD("Valid service: %s" % self.service))
            if self.verbosity >= 1:
                self.format_output('Proxy allowed', proxy_allowed(self.service))
                if self.pgturl:
                    self.format_output('Proxy callback allowed', proxy_callback_allowed(self.service, self.pgturl))
                self.format_output('Logout allowed', logout_allowed(self.service))
                self.format_output('Logout URL', get_logout_url(self.service))
                self.format_output('Callbacks', ', '.join(get_callbacks(self.service)))
            if self.verbosity >= 2:
                self.format_output('Backend', get_backend_path(self.service))
        else:
            self.stdout.write(self.style.ERROR("Invalid service: %s" % self.service))

    def format_output(self, label, text):
        self.stdout.write("  %s: %s" % (self.style.MIGRATE_LABEL(label), text))
