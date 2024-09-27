#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from django.core.management.base import BaseCommand
from django.test.client import Client

from write.models import MtEntry
from write.settings import PUBLISH_DIR

APP_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', 'static', 'js', 'preflight_app.js')


def fetch(entry):
    c = Client()
    
    print "fetching", entry.title.encode('utf-8')
    response = c.get(u"/is/%s" % entry.slug)
    
    if response.status_code != 200:
        raise Exception(response.status_code)
    
    path = os.path.join(PUBLISH_DIR, '%s.html' % entry.slug)
    with open(path, 'wb') as f:
        f.write(response.content)
    
    print "generated", path


class Command(BaseCommand):
    help = 'Saves html version'

    def handle(self, *args, **options):
        """
        """
        c = Client()

        if len(args) > 1:
            print "usage: python manage.py publish               # publish all posts"
            print "usage: python manage.py publish slug-of-post  # publish one post"
        
        elif len(args) == 1:
            slug = args[0]
            try:
                entry = MtEntry.objects.get(slug=slug)
            except MtEntry.DoesNotExist:
                print "post %s not found" % slug
                return
            
            fetch(entry)
        
        else:
            for entry in MtEntry.objects.filter(published=True):
                fetch(entry)
            
            response = c.get('/is/index.php')
            path = os.path.join(PUBLISH_DIR, 'index.php')
            with open(path, 'wb') as f:
                f.write(response.content)
            
            response = c.get('/is/archives')
            path = os.path.join(PUBLISH_DIR, 'archives.html')
            with open(path, 'wb') as f:
                f.write(response.content)
            
            response = c.get('/is/feed/us/recent_entries.xml')
            path = os.path.join(PUBLISH_DIR, 'feed', 'us')
            if not os.path.exists(path):
                os.makedirs(path)
            xml_path = os.path.join(path, 'recent_entries.xml')
            with open(xml_path, 'wb') as f:
                f.write(response.content)
