from django.contrib import admin
from write.models import *

admin.site.register((MtComment, MtEntry, MtAuthor))

