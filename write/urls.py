from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

from django.contrib import admin
admin.autodiscover()

from write.api import *

entry_resource = MtEntryResource()
comment_resource = MtCommentResource()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='/or/')),
    url(r'^or/$', 'write.views.wall', name='wall'),
    url(r'^or/(?P<slug>[\w-]+)$', 'write.views.entry', name='entry'),
    url(r'^admin/', include(admin.site.urls)),
    (r'^api/', include(entry_resource.urls)),
    (r'^api/', include(comment_resource.urls)),
)
