#!/usr/bin/env
# -*- coding: utf-8 -*-

from django.urls import include, re_path
from django.views.generic import RedirectView
from django.contrib import admin

from django.contrib.auth.views import LoginView, LogoutView

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
    re_path(r'^or/login$',  LoginView.as_view(template_name='themes/2011/login.html'),  name='login'),
    re_path(r'^or/logout$', LogoutView.as_view(template_name='themes/2011/logout.html'), name='logout'),
    
    re_path(r'^$', RedirectView.as_view(url='/or/', permanent=False)),
    re_path(r'^or/$', write.views.latest_entry_write, name='latest-entry-write'),
    re_path(r'^or/archives$', write.views.wall, name='wall'),
    re_path(r'^or/links.json$', write.views.links, name='links-json'),
    re_path(r'^or/(?P<slug>[\w-]+)$', write.views.entry_write, name='entry-write'),

    # /is/ -> These files are the live views from which Django will generate the static files
    #          Some of these (i.e. the post views) have a corresponding edit page,
    #          but others, like the RSS feed, are read only
    re_path(r'^is/index.php$', write.views.index_php, name='index-php'),
    re_path(r'^is/$', write.views.latest_entry_read, name='latest-entry-read'),
    re_path(r'^is/about$', write.views.about, name='about'),
    re_path(r'^is/feed/us/recent_entries.xml$', write.views.feed, name='feed'),
    re_path(r'^is/archives$', write.views.archives, name='archives'),
    re_path(r'^is/stories/by/(?P<author_slug>[\w-]+)$', write.views.entries_by_author, name='entries-by-author'),
    re_path(r'^is/(?P<slug>[\w-]+)$', write.views.entry_read, name='entry-read'),

    # handle the comments (the URL is a shout out to Movable Type / Melody — from the generated HTML you would not
    # know we moved on from this system)
    re_path(r'^comments.cgi$', write.views.handle_comment, name='comments'),

    # Django Admin useful for some tasks where no frontend was developed
    re_path(r'^admin/', admin.site.urls),

    # The API (using TastyPie) is necessary to allow the WYSIWYG editing to work
    re_path(r'^api/', include(entry_resource.urls)),
    re_path(r'^api/', include(comment_resource.urls)),

    # This serves up the generated static files. In production the webserver should take care of it
    re_path(r'^and/(?P<file_name>.*)$', write.views.serve_html)
]
