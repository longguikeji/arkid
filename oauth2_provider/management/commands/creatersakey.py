from Cryptodome.PublicKey import RSA
from django.core.management.base import BaseCommand
from ...models import OidcRsaKey


class Command(BaseCommand):
    help = 'Randomly generate a new RSA key for the OpenID server'

    def handle(self, *args, **options):
        try:
            key = RSA.generate(2048)
            rsa_key = OidcRsaKey(key=key.exportKey('PEM').decode('utf8'))
            rsa_key.save()
            self.stdout.write(u'RSA key successfully created with kid: {0}'.format(rsa_key.kid))
        except Exception as e:
            self.stdout.write('Something goes wrong: {0}'.format(e))
