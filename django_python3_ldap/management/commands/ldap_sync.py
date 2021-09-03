import json
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from inventory.models import Tenant
from django_python3_ldap.ldap import LDAPConnection
from .conf import load_config, get_ldap_settings_from_config


class Command(BaseCommand):

    help = "Creates local user models for all users found in the remote LDAP authentication server."

    def add_arguments(self, parser):
        parser.add_argument(
            '--sync_type',
            dest='sync_type',
            type=str,
            choices=['user', 'group', 'all'],
            help='user : only sync user from ldap, group : sync group from ldap, all: sync user and group')
        parser.add_argument('--tenant_uuid', dest='tenant_uuid', type=str, help='tennat_uuid')
        parser.add_argument('--direction',
                            dest='direction',
                            type=str,
                            choices=['upstream', 'downstream'],
                            help='downstream: sync from arkid to ldap, upstream: sync from ldap to arkid')
        parser.add_argument('--add_relation',
                            action='store_true',
                            dest='add_relation',
                            default=False,
                            help='add user and group relation')

    @transaction.atomic()
    def handle(self, *args, **options):
        verbosity = options["verbosity"]
        sync_type = options["sync_type"]
        tenant_uuid = options["tenant_uuid"]
        direction = options["direction"]
        add_relation = options["add_relation"]
        self.stdout.write(f"verbosity: {verbosity}, sync_type: {sync_type}, " +
                          f"tenant_uuid: {tenant_uuid}, direction: {direction}, " + f"add_relation: {add_relation}")

        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        if not tenant:
            raise CommandError(f"{tenant_uuid} does not exist")

        data = load_config(tenant_uuid)
        if not data:
            raise CommandError(f"{tenant_uuid} config data does not exist")
        if verbosity >= 1:
            self.stdout.write(f"ldap settings: {json.dumps(data)}")

        settings = get_ldap_settings_from_config(**data)
        ldap_conn = LDAPConnection(settings=settings, tenant=tenant)

        if sync_type == "user" or sync_type == "all":
            if direction == "upstream":
                ldap_conn.add_users_from_ldap()
            else:
                ldap_conn.add_users_to_ldap()

        if sync_type == "group" or sync_type == "all":
            if direction == "upstream":
                ldap_conn.add_groups_from_ldap()
            else:
                ldap_conn.add_groups_to_ldap()

        if add_relation:
            if direction == "upstream":
                ldap_conn.add_group_user_relation_from_ldap()
            else:
                ldap_conn.add_group_user_relation_to_ldap()

        self.stdout.write("Sync completed!")
