#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

from django.core.management.base import BaseCommand
from write.models import MtEntry

APP_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'static', 'js', 'preflight_app.js')

class Command(BaseCommand):
    help = 'Fixes up html of blog entries'

    def handle(self, *args, **options):
        """
        Process all blog HTML
        
            python manage.py preflight
        
        This will properly indent the HTML and fix op various other artefacts
        created by the Aloha Editor.
        
        In the future it will also auto-link etcetera.
        """
        for entry in MtEntry.objects.filter(entry_status = 2):
            print "performing preflight for", entry.entry_title
            pipe = subprocess.Popen(['node', APP_PATH, str(2)],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            converted = pipe.communicate(entry.entry_text.encode('utf-8'))[0]
            entry.entry_text = converted
            entry.save()
