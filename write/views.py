# -*- coding: utf-8 -*-

import json
import os.path
from datetime import datetime

from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, Template, Context, loader
from django.contrib.staticfiles.views import serve
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from write.models import MtEntry, MtComment
from write.forms import CommentForm


@login_required(login_url='/or/login')
def wall(request):
    tpl_params = {}
    tpl_params['entries'] = MtEntry.objects.all()
    tpl_params['latest_entry'] = tpl_params['entries'].filter(published=True).first()
    entries_hash = [e.event() for e in MtEntry.objects.all()]
    tpl_params['entries_json'] = json.dumps(entries_hash, indent=2, ensure_ascii=False)
    tpl_params['EDITING'] = True
    tpl_params['andor'] = '/or/'
    return render_to_response("wall.html", tpl_params, context_instance=RequestContext(request))


def index_php(request):
    e = MtEntry.objects.filter(published=True).first()
    return HttpResponse("""<?php header('Location: %s'); ?>""" % e.get_absolute_url(),
                        content_type="text/plain; charset=utf-8")


def latest_entry_read(request):
    e = MtEntry.objects.filter(published=True).first()
    return redirect('entry-read', slug=e.slug)


def latest_entry_write(request):
    e = MtEntry.objects.all().first()
    return redirect('entry-write', slug=e.slug)


def archives(request):
    tpl_params = {}
    tpl_params['entries'] = MtEntry.objects.filter(published=True)
    tpl_params['latest_entry'] = tpl_params['entries'].filter(published=True)[0]
    tpl_params['EDITING'] = False
    tpl_params['andor'] = '/and/'
    return render_to_response("archives.html", tpl_params, context_instance=RequestContext(request))


def entry(request, slug, editing=False, comment_form=None):
    try:
        entry = MtEntry.objects.get(slug=slug)
    except MtEntry.DoesNotExist:
        if not editing:
            raise Http404
        entry = MtEntry(slug=slug)
        entry.author = User.objects.get(pk=3)  # glit by default
        entry.body = """
        <p>Hello dear start the editing process.</p>
        """

        entry.entry_title = slug.replace('-', ' ').title()
        entry.published = False  # draft by default

    # We can not read unpublished entries, except when providing a ‘secret token’
    # This is not supposed to be a secure: it is more of a low garden fence
    # than it is a lock
    if not editing and not entry.published and not request.user.is_authenticated():
        if request.GET.get('the_secret_question', '') != 'the_secret_answer':
            return HttpResponseForbidden()

    if comment_form:
        form = comment_form
    else:
        form = CommentForm(initial={'entry': entry})

    author_ids = (3, 4, 5, 6, 7, 8)  # the i.liketightpant contributors
    authors = User.objects.all()
    main_authors = User.objects.filter(pk__in=author_ids)

    published_entries = MtEntry.objects.filter(published=True)
    published_entries_ids = [e.pk for e in published_entries]
    visible_comments = MtComment.objects.filter(visible=True).filter(entry__pk__in=published_entries_ids)

    tpl_params = {}
    tpl_params['EDITING'] = editing
    tpl_params['andor'] = '/or/' if editing else '/and/'

    tpl_params['e'] = entry
    tpl_params['e_comments'] = entry.mtcomment_set.filter(visible=True).order_by('created_on')
    tpl_params['a'] = entry.author
    tpl_params['a_entries'] = published_entries.filter(author=entry.author).exclude(pk=entry.pk)
    tpl_params['a_comments'] = visible_comments.filter(mt_author=entry.author)[:10]

    tpl_params['authors'] = authors
    tpl_params['author_ids'] = author_ids
    tpl_params['main_authors'] = main_authors
    tpl_params['recent_entries'] = published_entries.filter(published=True)[:10]
    tpl_params['latest_entry'] = tpl_params['recent_entries'][0]
    tpl_params['recent_comments'] = visible_comments[:10]
    tpl_params['parent'] = None

    tpl_params['form'] = form

    return render_to_response("entry.html", tpl_params, context_instance=RequestContext(request))


def entry_read(request, slug):
    return entry(request, slug, False)


@csrf_exempt
def handle_comment(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        post = request.POST.copy()
        # create a form instance and populate it with data from the request:
        form = CommentForm(post)
        form.data['ip'] = request.META['REMOTE_ADDR']
        if not form.is_valid() or not form.data['captcha_code'].strip().lower() in ['bowie', 'jones', 'duke']:
            return render_to_response("verify_comment.html", {'form': form}, context_instance=RequestContext(request))

        comment = form.save(commit=False)
        comment.visible = True
        comment.save()
        comment.entry.commit()
        return redirect('entry-read', slug=comment.entry.slug)

    # if a GET (or any other method):
    else:
        return HttpResponseForbidden()


@login_required(login_url='/or/login')
def entry_write(request, slug):
    return entry(request, slug, True)


def about(request):
    """
    3 = glit
    4 = jenseits
    5 = habitus
    6 = tellyou
    7 = baseline
    8 = bnf
    
    """
    tpl_params = {}

    tpl_params['glit_entries'] = MtEntry.objects.filter(author__pk=3).filter(published=True)
    tpl_params['glit_comments'] = MtComment.objects.filter(visible=True).filter(mt_author__pk=3)[:5]
    tpl_params['jenseits_entries'] = MtEntry.objects.filter(author__pk=4).filter(published=True)
    tpl_params['jenseits_comments'] = MtComment.objects.filter(visible=True).filter(mt_author__pk=4)[:5]
    tpl_params['habitus_entries'] = MtEntry.objects.filter(author__pk=5).filter(published=True)
    tpl_params['habitus_comments'] = MtComment.objects.filter(visible=True).filter(mt_author__pk=5)[:5]
    tpl_params['tellyou_entries'] = MtEntry.objects.filter(author__pk=6).filter(published=True)
    tpl_params['tellyou_comments'] = MtComment.objects.filter(visible=True).filter(mt_author__pk=6)[:5]
    tpl_params['baseline_entries'] = MtEntry.objects.filter(author__pk=7).filter(published=True)
    tpl_params['baseline_comments'] = MtComment.objects.filter(visible=True).filter(mt_author__pk=7)[:5]
    tpl_params['bnf_entries'] = MtEntry.objects.filter(author__pk=8).filter(published=True)
    tpl_params['bnf_comments'] = MtComment.objects.filter(visible=True).filter(mt_author__pk=8)[:5]

    return render_to_response("about.html", tpl_params, context_instance=RequestContext(request))


def feed(request):
    tpl_params = {}
    tpl_params['entries'] = MtEntry.objects.filter(published=True)[:15]

    t = loader.get_template('recent_entries.xml')
    c = Context(tpl_params)
    return HttpResponse(t.render(c), mimetype="application/atom+xml; charset=utf-8")


def links(request):
    """
    Offer the links to integrate with Aloha’s repository API
    http://www.aloha-editor.org/guides/repository.html
    """
    published_entries = MtEntry.objects.filter(published=True)
    entry_links = []
    for entry in published_entries:
        entry_links.append({
            "link": entry.get_absolute_url(),
            "id": entry.get_absolute_url(),
            "name": "I like tight pants and " + entry.entry_title.lower(),
            "type": "website"
        })
    return HttpResponse(json.dumps(entry_links, indent=2, ensure_ascii=False),
                        mimetype="application/json; charset=utf-8")


def serve_html(request, file_name):
    """
    Using Django’s static file serving view in Development,
    with tweaks to reproduce our server setup.

    cf http://stackoverflow.com/questions/29864352/serving-static-html-files-without-extension-in-django

    (PS had do disable the 'django.contrib.staticfiles' app to override its behaviour)
    """
    # homepage (`/and/`) redirects to latest post
    if not file_name:
        e = MtEntry.objects.filter(published=True).first()
        return redirect(e.get_absolute_url())

    # .html gets stripped from urls
    if not os.path.splitext(file_name)[1]:
        file_name = '{}.html'.format(file_name)

    # Serve with Django staticfiles view
    return serve(request, file_name)
