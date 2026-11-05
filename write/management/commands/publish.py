#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError

from write.models import MtEntry
from write.publish import regenerate_published_site, write_entry_html


class Command(BaseCommand):
    help = "Saves html version"

    def add_arguments(self, parser):
        parser.add_argument(
            "slug",
            nargs="?",
            help="Slug of a published post. Leave it out to regenerate the whole site",
        )

    def handle(self, *args, **options):
        slug = options["slug"]
        if not slug:
            regenerate_published_site()
            return

        try:
            entry = MtEntry.objects.get(slug=slug, published=True)
        except MtEntry.DoesNotExist:
            raise CommandError("no published post with the slug %s" % slug)

        path = write_entry_html(entry)
        self.stdout.write("generated %s" % path)
