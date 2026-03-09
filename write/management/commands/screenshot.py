#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from write.models import MtEntry
from write.screenshots import screenshot


class Command(BaseCommand):
    help = 'Takes screenshots of entries'

    def handle(self, *args, **options):
        """
        Take screenshots of pages as shown on the development server.
        
            python manage.py screenshot
        
        By default it will shoot all published entries.
        If you want to specify an entry, specify it’s slug (multiple entries allowed)
        
            python manage.py screenshot "i-guess-this-is-a-unix-sin" "robin-gareus"
        """
        if len(args) == 0:
            args = [i.slug for i in MtEntry.objects.filter(published=True)]
        screenshot(args)
