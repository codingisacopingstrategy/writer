from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

from django.contrib import admin
admin.autodiscover()

from write.api import *

entry_resource = MtEntryResource()
comment_resource = MtCommentResource()

urlpatterns = patterns('',
    url(r'^or/login$', 'django.contrib.auth.views.login',  {'template_name': 'login.html'}, name='login'),
    url(r'^or/logout$', 'django.contrib.auth.views.logout',{'template_name': 'logout.html'}, name='logout'),
    
    url(r'^$', RedirectView.as_view(url='/or/')),
    url(r'^or/$', 'write.views.latest_entry_write', name='latest-entry-write'),
    url(r'^or/archives$', 'write.views.wall', name='wall'),

    url(r'^is/$', 'write.views.latest_entry_read', name='latest-entry-read'),
    url(r'^is/about$', 'write.views.about', name='about'),
    url(r'^is/feed/us/recent_entries.xml$', 'write.views.feed', name='feed'),
    url(r'^is/archives$', 'write.views.archives', name='archives'),    
    url(r'^is/(?P<slug>[\w-]+)$', 'write.views.entry_read', name='entry-read'),
    url(r'^or/(?P<slug>[\w-]+)$', 'write.views.entry_write', name='entry-write'),

    
    url(r'^admin/', include(admin.site.urls)),
    (r'^api/', include(entry_resource.urls)),
    (r'^api/', include(comment_resource.urls)),
)
