from django.conf.urls import include, url
from django.views.generic import RedirectView

from django.contrib import admin
admin.autodiscover()

import django.contrib.auth.views

from write.api import MtEntryResource, MtCommentResource

import write.views

entry_resource = MtEntryResource()
comment_resource = MtCommentResource()

urlpatterns = [
    url(r'^or/login$', django.contrib.auth.views.login,  {'template_name': 'login.html'}, name='login'),
    url(r'^or/logout$', django.contrib.auth.views.logout, {'template_name': 'logout.html'}, name='logout'),
    
    url(r'^$', RedirectView.as_view(url='/or/', permanent=False)),
    url(r'^or/$', write.views.latest_entry_write, name='latest-entry-write'),
    url(r'^or/archives$', write.views.wall, name='wall'),
    url(r'^or/links.json$', write.views.links, name='links-json'),

    url(r'^is/index.php$', write.views.index_php, name='index-php'),
    url(r'^is/$', write.views.latest_entry_read, name='latest-entry-read'),
    url(r'^is/about$', write.views.about, name='about'),
    url(r'^is/feed/us/recent_entries.xml$', write.views.feed, name='feed'),
    url(r'^is/archives$', write.views.archives, name='archives'),
    url(r'^is/(?P<slug>[\w-]+)$', write.views.entry_read, name='entry-read'),
    url(r'^or/(?P<slug>[\w-]+)$', write.views.entry_write, name='entry-write'),

    url(r'^comments.cgi$', write.views.handle_comment, name='comments'),

    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(entry_resource.urls)),
    url(r'^api/', include(comment_resource.urls)),

    url(r'^and/(?P<file_name>.*)$', write.views.serve_html)
]
