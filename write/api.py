#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from django.contrib.auth.models import User
from django.urls import re_path
from tastypie import fields, http
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource
from tastypie.utils import trailing_slash

from write.auth import (
    AuthorAuthorization,
    EntryAuthorization,
    LoggedInAuthentication,
    can_publish,
)
from write.models import MtComment, MtEntry
from write.publish import publish_entry


class MtAuthorResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        authentication = LoggedInAuthentication()
        authorization = AuthorAuthorization()
        resource_name = 'author'
        always_return_data = True


class MtEntryResource(ModelResource):
    author = fields.ForeignKey(MtAuthorResource, 'author')

    class Meta:
        queryset = MtEntry.objects.all()
        authentication = LoggedInAuthentication()
        authorization = EntryAuthorization()
        resource_name = 'entry'
        always_return_data = True

    def hydrate(self, bundle):
        # The editor always sends `published`. Ignore it unless the user
        # has write.publish_mtentry (superusers have every permission).
        if not can_publish(bundle.request.user) and 'published' in bundle.data:
            if getattr(bundle.obj, 'pk', None):
                bundle.data['published'] = bundle.obj.published
            else:
                bundle.data['published'] = False
        return bundle

    def dehydrate(self, bundle):
        """
        Django → JSON
        By default TastyPie serialises foreign key like this: "/api/author/232/"
        But we just want the id: 232
        """
        bundle.data['author'] = bundle.obj.author.pk
        return bundle

    def hydrate_author(self, bundle):
        """
        JSON → Django
        TastyPie can parse foreign keys of the following form:
        "/api/author/232/"
        {'pk': 232}
        We only get `232`, so we have to convert it.
        """
        if 'author' in bundle.data:
            bundle.data['author'] = {'pk': bundle.data['author']}
        return bundle

    def prepend_urls(self):
        return [
            re_path(
                r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/publish%s$"
                % (self._meta.resource_name, trailing_slash()),
                self.wrap_view("publish"),
                name="api_entry_publish",
            ),
        ]

    def publish(self, request, **kwargs):
        self.method_check(request, allowed=["post"])
        self.is_authenticated(request)
        if not can_publish(request.user):
            return http.HttpUnauthorized()

        try:
            entry = MtEntry.objects.get(pk=kwargs["pk"])
        except (MtEntry.DoesNotExist, ValueError):
            return http.HttpNotFound()

        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except ValueError:
            payload = {}
        update_all = bool(payload.get("update_all"))
        publish_entry(entry, update_all=update_all)
        return self.create_response(
            request,
            {"published": True, "update_all": update_all},
        )


class MtCommentResource(ModelResource):
    entry = fields.ForeignKey(MtEntryResource, 'entry')
    mt_author = fields.ForeignKey(MtAuthorResource, 'mt_author', null=True)
    parent = fields.ForeignKey('self', 'parent', null=True)

    class Meta:
        queryset = MtComment.objects.all()
        authentication = LoggedInAuthentication()
        authorization = DjangoAuthorization()
        resource_name = 'comment'
        always_return_data = True

    def dehydrate(self, bundle):
        bundle.data['entry'] = bundle.obj.entry.pk
        if bundle.obj.mt_author:
            bundle.data['mt_author'] = bundle.obj.mt_author.pk
        if bundle.obj.parent:
            bundle.data['parent'] = bundle.obj.parent.pk
        return bundle

    def hydrate_entry(self, bundle):
        if 'entry' in bundle.data:
            bundle.data['entry'] = "/api/entry/%s/" % bundle.data['entry']
        return bundle

    def hydrate_mt_author(self, bundle):
        if 'mt_author' in bundle.data and bundle.data['mt_author'] is not None:
            bundle.data['mt_author'] = "/api/author/%s/" % bundle.data['mt_author']
        return bundle

    def hydrate_parent(self, bundle):
        if 'parent' in bundle.data and bundle.data['parent'] is not None:
            bundle.data['parent'] = "/api/comment/%s/" % bundle.data['parent']
        return bundle
