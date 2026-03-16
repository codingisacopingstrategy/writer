#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from write.models import MtEntry
from write.screenshots import screenshot


class Command(BaseCommand):
    help = 'Takes screenshots of entries'

    def add_arguments(self, parser):
        parser.add_argument(
            "slugs",
            nargs="*",
            type=str,
            help="Optional list of entry slugs to screenshot"
        )

    def handle(self, *args, **options):
        """
        Take screenshots of pages as shown on the development server.
        
            python manage.py screenshot
        
        By default it will shoot all published entries.
        If you want to specify an entry, specify it’s slug (multiple entries allowed)
        
            python manage.py screenshot "i-guess-this-is-a-unix-sin" "robin-gareus"
        """
        slugs = options["slugs"]

        if len(slugs) == 0:
            slugs = [i.slug for i in MtEntry.objects.filter(published=True)]

        screenshot(slugs)
