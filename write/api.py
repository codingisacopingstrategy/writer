from tastypie.resources import ModelResource
from write.models import MtEntry, MtComment

class MtEntryResource(ModelResource):
    class Meta:
        queryset = MtEntry.objects.all()
        resource_name = 'entry'

class MtCommentResource(ModelResource):
    class Meta:
        queryset = MtComment.objects.all()
        resource_name = 'comment'
