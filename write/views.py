from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from write.models import (MtEntry, )

def wall(request):
    tpl_params = {}
    tpl_params['entries'] = MtEntry.objects.all()
    return render_to_response("wall.html", tpl_params, context_instance = RequestContext(request))

def entry(request, slug):
    try:
        entry = MtEntry.objects.get(entry_basename=slug)
    except MtEntry.DoesNotExist:
        entry = MtEntry(entry_basename=slug)
    if request.method == 'GET':
        return HttpResponse(entry.entry_text)

