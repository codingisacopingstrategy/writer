from django.contrib import admin
from write.models import *


class MtEntryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',), }

admin.site.register(MtEntry, MtEntryAdmin)
admin.site.register(MtComment)
