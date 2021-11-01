from django.core.management.base import BaseCommand, CommandError

from sync_client.sync import sync


class Command(BaseCommand):

    help = "Sync from scim server to active directory."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.stdout.write("Sync started!")
        sync()
        self.stdout.write("Sync completed!")
