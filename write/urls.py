#!/usr/bin/env
# -*- coding: utf-8 -*-

from django.urls import include, path
from django.views.generic import RedirectView
from django.contrib import admin

from django.contrib.auth.views import LoginView, LogoutView

from imagescaler import scale_image
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
    path('and/assets/scaled/to/<int:size>/<path:path>', scale_image),

    # /or/ -> These urls point to the editable version. You need to be logged to access those.
    path('or/login',  LoginView.as_view(template_name='themes/2011/login.html'),  name='login'),
    path('or/logout', LogoutView.as_view(template_name='themes/2011/logout.html'), name='logout'),
    
    path('', RedirectView.as_view(url='/or/', permanent=False)),
    path('or/', write.views.latest_entry_write, name='latest-entry-write'),
    path('or/archives', write.views.wall, name='wall'),
    path('or/links.json', write.views.links, name='links-json'),
    path('or/assets/', include('assets.urls')),
    path('or/<slug:slug>', write.views.entry_write, name='entry-write'),

    # /is/ -> These files are the live views from which Django will generate the static files
    #          Some of these (i.e. the post views) have a corresponding edit page,
    #          but others, like the RSS feed, are read only
    path('is/index.php', write.views.index_php, name='index-php'),
    path('is/', write.views.latest_entry_read, name='latest-entry-read'),
    path('is/about', write.views.about, name='about'),
    path('is/feed/us/recent_entries.xml', write.views.feed, name='feed'),
    path('is/archives', write.views.archives, name='archives'),
    path('is/stories/by/<slug:author_slug>', write.views.entries_by_author, name='entries-by-author'),
    path('is/<slug:slug>', write.views.entry_read, name='entry-read'),

    # handle the comments (the URL is a shout out to Movable Type / Melody — from the generated HTML you would not
    # know we moved on from this system)
    path('comments.cgi', write.views.handle_comment, name='comments'),

    # Django Admin useful for some tasks where no frontend was developed
    path('admin/', admin.site.urls),

    # The API (using TastyPie) is necessary to allow the WYSIWYG editing to work
    path('api/', include(entry_resource.urls)),
    path('api/', include(comment_resource.urls)),

    # This serves up the generated static files. In production the webserver should take care of it
    path('and/<path:file_name>', write.views.serve_html)
]
