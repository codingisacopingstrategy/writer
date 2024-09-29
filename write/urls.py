#!/usr/bin/env
# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.views.generic import RedirectView
from django.contrib import admin

import django.contrib.auth.views

from write.api import MtEntryResource, MtCommentResource
import write.views

admin.autodiscover()

entry_resource = MtEntryResource()
comment_resource = MtCommentResource()

"""
I like tight pants
  /and/ -> The final website urls. These are static files
  /or/ -> These urls point to the editable version. You need to be logged to access those.
  /is/ -> These files are the live views from which Django will generate the static files
          Some of these (i.e. the post views) have a corresponding edit page,
          but others, like the RSS feed  
"""
urlpatterns = [
    # /or/ -> These urls point to the editable version. You need to be logged to access those.
    url(r'^or/login$', django.contrib.auth.views.login,  {'template_name': 'login.html'}, name='login'),
    url(r'^or/logout$', django.contrib.auth.views.logout, {'template_name': 'logout.html'}, name='logout'),
    
    url(r'^$', RedirectView.as_view(url='/or/', permanent=False)),
    url(r'^or/$', write.views.latest_entry_write, name='latest-entry-write'),
    url(r'^or/archives$', write.views.wall, name='wall'),
    url(r'^or/links.json$', write.views.links, name='links-json'),
    url(r'^or/(?P<slug>[\w-]+)$', write.views.entry_write, name='entry-write'),

    # /is/ -> These files are the live views from which Django will generate the static files
    #          Some of these (i.e. the post views) have a corresponding edit page,
    #          but others, like the RSS feed, are read only
    url(r'^is/(?P<slug>[\w-]+)$', write.views.entry_read, name='entry-read'),
    url(r'^is/index.php$', write.views.index_php, name='index-php'),
    url(r'^is/$', write.views.latest_entry_read, name='latest-entry-read'),
    url(r'^is/about$', write.views.about, name='about'),
    url(r'^is/feed/us/recent_entries.xml$', write.views.feed, name='feed'),
    url(r'^is/archives$', write.views.archives, name='archives'),

    # handle the comments (the URL is a shout out to Movable Type / Melody — from the generated HTML you would not
    # know we moved on from this system)
    url(r'^comments.cgi$', write.views.handle_comment, name='comments'),

    # Django Admin useful for some tasks where no frontend was developed
    url(r'^admin/', admin.site.urls),

    # The API (using TastyPie) is necessary to allow the WYSIWYG editing to work
    url(r'^api/', include(entry_resource.urls)),
    url(r'^api/', include(comment_resource.urls)),

    # This serves up the generated static files. In production the webserver should take care of it
    url(r'^and/(?P<file_name>.*)$', write.views.serve_html)
]
