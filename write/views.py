import json
from datetime import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext, Template, Context
from django.contrib.auth.decorators import login_required

from write.models import (MtEntry, MtTemplate, MtAuthor, MtAsset, MtComment)

@login_required(login_url='/or/login')
def wall(request):
    tpl_params = {}
    tpl_params['entries'] = MtEntry.objects.all()
    tpl_params['latest_entry'] = tpl_params['entries'].filter(entry_status=2)[0]
    entries_hash = [e.entry_event() for e in MtEntry.objects.all()]
    tpl_params['entries_json'] = json.dumps(entries_hash, indent=2, ensure_ascii=False)
    tpl_params['EDITING'] = True
    tpl_params['andor'] = '/or/'
    return render_to_response("wall.html", tpl_params, context_instance = RequestContext(request))

def entry(request, slug, editing=False):
    """
    Strictly speaking, the following is *not* a good idea.
    Because we are required to not use hyphens in entry_basename.
    
    An entry with entry_basename bowie_star-man is
    generated by Movable Type as bowie-star-man.html
    
    There is no straight-forward way then, to go from
    the url back to the basename. The way we do it,
    with url /bowie-star-man, the system would replace the - with _
    and look for the entry with entry_basename bowie_star_man
    """
    basename = slug.replace('-','_')
    try:
        entry = MtEntry.objects.get(entry_basename=basename)
    except MtEntry.DoesNotExist:
        if not editing:
            return Http404
        entry = MtEntry(entry_basename=basename)
        entry.entry_authored_on = entry.entry_created_on = datetime.now()
        entry.entry_created_by = entry.entry_author_id= 3 # glit by default
        entry.entry_text = """
        <p>Hello dear start the editing process.</p>
        """
        
        entry.entry_title = slug.replace('-',' ').title()
        entry.entry_status = 1 # draft by default
    if request.method == 'GET':
        author = MtAuthor.objects.get(pk=entry.entry_author_id)
        
        author_ids = (3, 4, 5, 6, 7, 8) # the i.liketightpant contributors
        authors = MtAuthor.objects.all()
        main_authors = MtAuthor.objects.filter(author_id__in=author_ids)
        a_thumbnail = MtAsset.objects.get(pk = author.author_userpic_asset_id)
        
        tpl_params = {}
        
        tpl_params['EDITING'] = editing
        tpl_params['andor'] = '/or/' if editing else '/and/'
        
        tpl_params['e'] = entry
        tpl_params['e_comments'] = MtComment.objects.filter(comment_visible=1).filter(comment_entry_id=entry.entry_id).order_by('comment_created_on')
        tpl_params['a'] = author
        tpl_params['a_thumbnail_url'] = a_thumbnail.asset_url % "http://mt.schr.fr/lib"
        tpl_params['a_entries'] = MtEntry.objects.filter(entry_author_id=author.author_id).filter(entry_status=2).exclude(pk=entry.entry_id)
        tpl_params['a_comments'] = MtComment.objects.filter(comment_visible=1).filter(comment_commenter_id=author.author_id)[:10]
        
        tpl_params['authors'] = authors
        tpl_params['author_ids'] = author_ids
        tpl_params['main_authors'] = main_authors
        tpl_params['recent_entries'] = MtEntry.objects.filter(entry_status=2)[:10]
        tpl_params['latest_entry'] = tpl_params['recent_entries'][0]
        tpl_params['recent_comments'] = MtComment.objects.filter(comment_visible=1)[:10]
        tpl_params['parent'] = None

        return render_to_response("entry.html", tpl_params, context_instance = RequestContext(request))

def entry_read(request, slug):
    return entry(request, slug, False)

@login_required(login_url='/or/login')
def entry_write(request, slug):
    return entry(request, slug, True)
