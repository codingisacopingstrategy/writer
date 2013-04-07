from django.core.management.base import BaseCommand
from write.models import MtEntry
from write.screenshots import screenshot

class Command(BaseCommand):
    help = 'Takes screenshots of unpublished entries'

    def handle(self, *args, **options):
        local_drafts = [i.entry_slug() for i in MtEntry.objects.filter(entry_status = 1)]
        screenshot(local_drafts)
        self.stdout.write('Created screenshots of unpublished entries')
