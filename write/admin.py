#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin
from write.models import *


class MtEntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',), }

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        if not request.user.has_perm('write.publish_mtentry') and 'published' not in fields:
            fields.append('published')
        return fields


admin.site.register(MtEntry, MtEntryAdmin)
admin.site.register(MtComment)
