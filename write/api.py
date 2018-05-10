# -*- coding: utf-8 -*-

from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from write.models import MtEntry, MtComment
from django.contrib.auth.models import User


class MtAuthorResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        authorization = Authorization()
        resource_name = 'author'


class MtEntryResource(ModelResource):
    author = fields.ForeignKey(MtAuthorResource, 'author')

    class Meta:
        queryset = MtEntry.objects.all()
        authorization = Authorization()
        resource_name = 'entry'

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


class MtCommentResource(ModelResource):
    entry = fields.ForeignKey(MtEntryResource, 'entry')
    mt_author = fields.ForeignKey(MtAuthorResource, 'mt_author', null=True)
    parent = fields.ForeignKey('self', 'parent', null=True)

    class Meta:
        queryset = MtComment.objects.all()
        authorization = Authorization()
        resource_name = 'comment'

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
