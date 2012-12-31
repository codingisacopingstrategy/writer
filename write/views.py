from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext, Template, Context

from write.models import (MtEntry, MtTemplate, MtAuthor, MtAsset, MtComment)

def wall(request):
    tpl_params = {}
    tpl_params['entries'] = MtEntry.objects.all()
    return render_to_response("wall.html", tpl_params, context_instance = RequestContext(request))

def entry(request, slug):
    try:
        entry = MtEntry.objects.get(entry_basename=slug)
    except MtEntry.DoesNotExist:
        entry = MtEntry(entry_basename=slug)
        entry.entry_author_id=3 # glit by default
    if request.method == 'GET':
        author = MtAuthor.objects.get(pk=entry.entry_author_id)
        authors = MtAuthor.objects.filter(author_created_by=True) # This happens to get all the authors we need
        a_thumbnail = MtAsset.objects.get(pk = author.author_userpic_asset_id)

        

        tpl_params = {}
        tpl_params['e'] = entry
        tpl_params['e_comments'] = MtComment.objects.filter(comment_visible=1).filter(comment_entry_id=entry.entry_id).order_by('comment_created_on')
        tpl_params['a'] = author
        tpl_params['a_thumbnail_url'] = a_thumbnail.asset_url % "http://mt.schr.fr/lib"
        tpl_params['a_entries'] = MtEntry.objects.filter(entry_author_id=author.author_id)
        tpl_params['a_comments'] = MtComment.objects.filter(comment_commenter_id=author.author_id)[:10]
        tpl_params['authors'] =authors
        tpl_params['recent_entries'] = MtEntry.objects.all()[:10]
        tpl_params['recent_comments'] = MtComment.objects.filter(comment_visible=1)[:10]
        tpl_params['parent'] = None

        return render_to_response("entry.html", tpl_params, context_instance = RequestContext(request))

