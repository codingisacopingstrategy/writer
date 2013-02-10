from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from write.models import MtEntry, MtComment

class MtEntryResource(ModelResource):
    class Meta:
        queryset = MtEntry.objects.all()
        authorization = Authorization()
        resource_name = 'entry'

class MtCommentResource(ModelResource):
    class Meta:
        queryset = MtComment.objects.all()
        authorization = Authorization()
        resource_name = 'comment'
