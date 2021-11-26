#!/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError
from app.models import App
from tenant.models import Tenant
from runtime import get_app_runtime


class Command(BaseCommand):
    help = 'Create OIDC App'

    def add_arguments(self, parser):
        parser.add_argument('name')
        parser.add_argument('url')
        parser.add_argument('description')
        parser.add_argument('redirect_uris')
        parser.add_argument(
            '--skip_authorization', choices=['true', 'false'], default='false'
        )
        parser.add_argument(
            '--client_type', choices=['public', 'confidential'], default='public'
        )
        parser.add_argument(
            '--grant_type',
            choices=[
                'authorization-code',
                'implicit',
                'password',
                'client_credentials',
                'openid-hybrid',
            ],
            default='authorization-code',
        )
        parser.add_argument(
            '--algorithm',
            choices=[
                'RS256',
                'HS256',
            ],
            default='RS256',
        )

    def handle(self, *args, **options):
        name = options['name']
        url = options['url']
        description = options['description']
        redirect_uris = options['redirect_uris']
        skip_authorization = options['skip_authorization']
        if skip_authorization == 'true':
            skip_authorization = True
        elif skip_authorization == 'false':
            skip_authorization = False
        client_type = options['client_type']
        grant_type = options['grant_type']
        algorithm = options['algorithm']
        protocol_type = 'OIDC'
        protocol_data = {
            "skip_authorization": skip_authorization,
            "redirect_uris": redirect_uris,
            "client_type": client_type,
            "grant_type": grant_type,
            "algorithm": algorithm,
        }

        tenant = Tenant.objects.filter(id=1).first()
        app = App.objects.create(
            tenant=tenant,
            name=name,
            type=protocol_type,
            url=url,
            description=description,
        )
        r = get_app_runtime()
        provider_cls: AppTypeProvider = r.app_type_providers.get(protocol_type, None)
        assert provider_cls is not None
        provider = provider_cls()
        data = provider.create(app=app, data=protocol_data)
        if data is not None:
            app.data = data
            app.save()

        self.stdout.write(f'uuid:{app.uuid.hex}')
        self.stdout.write(f'name:{app.name}')
        self.stdout.write(f'url:{app.url}')
        self.stdout.write(f'description:{app.description}')
        for key, value in app.data.items():
            self.stdout.write(f'{key}:{value}')
