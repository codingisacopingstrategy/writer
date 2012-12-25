from django.contrib import admin
from write.models import *

admin.site.register((MtComment, MtCommentMeta, MtEntry, MtEntryRev, MtEntrySummary))

