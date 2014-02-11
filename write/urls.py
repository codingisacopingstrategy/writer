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
    url(r'^or/$', 'write.views.wall', name='wall'),

    url(r'^is/about$', 'write.views.about', name='about'),
    url(r'^is/archives$', 'write.views.archives', name='archives'),    
    url(r'^is/(?P<slug>[\w-]+)$', 'write.views.entry_read', name='entry-read'),
    url(r'^or/(?P<slug>[\w-]+)$', 'write.views.entry_write', name='entry-write'),

    
    url(r'^admin/', include(admin.site.urls)),
    (r'^api/', include(entry_resource.urls)),
    (r'^api/', include(comment_resource.urls)),
)
