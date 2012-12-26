from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': '/or/'}),
    url(r'^or/$', 'write.views.wall', name='wall'),
    url(r'^or/(?P<slug>[\w-]+)$', 'write.views.entry', name='entry'),
    url(r'^admin/', include(admin.site.urls)),
)
