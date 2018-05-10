#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import codecs

from django.core.management.base import BaseCommand
from write.models import MtEntry

APP_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'static', 'js', 'checkout_app.js')


class Command(BaseCommand):
    help = 'Fixes up html of blog entries'

    def handle(self, *args, **options):
        """
        Checkout html from the latest git version, and pass it through preflight
        
        This works for all archived posts.
        
            python manage.py checkout
        """
        for entry in MtEntry.objects.filter(entry_status = 2):
            print "performing checkout for", entry.entry_title
            entry_git_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', '..', '..', 'I-like-tight-pants-and-mathematics', entry.entry_slug() + '.html')
            with codecs.open(entry_git_path, 'r', 'utf-8') as entry_git_file:
                entry_git_text = entry_git_file.read()
            pipe = subprocess.Popen(['node', APP_PATH, str(2)],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            converted = pipe.communicate(entry_git_text.encode('utf-8'))[0]
            entry.entry_text = converted
            entry.save()
