#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from write.models import MtEntry
from write.publish import regenerate_published_site, write_entry_html


class Command(BaseCommand):
    help = "Saves html version"

    def handle(self, *args, **options):
        if len(args) > 1:
            print("usage: python manage.py publish               # publish all posts")
            print("usage: python manage.py publish slug-of-post  # publish one post")

        elif len(args) == 1:
            slug = args[0]
            try:
                entry = MtEntry.objects.get(slug=slug)
            except MtEntry.DoesNotExist:
                print("post %s not found" % slug)
                return
            print("fetching", entry.title.encode("utf-8"))
            path = write_entry_html(entry)
            print("generated", path)

        else:
            regenerate_published_site()
