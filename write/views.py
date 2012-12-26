from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext, Template, Context

from write.models import (MtEntry, MtTemplate )
from write.template import transform

entry_template = Template(transform(MtTemplate.objects.get(pk=11).template_text))

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
        template = transform(MtTemplate.objects.get(pk=11).template_text)
        return HttpResponse(entry_template.render(Context({ 'e' : entry })))

