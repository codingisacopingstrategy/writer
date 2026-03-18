#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os.path

from datetime import datetime

from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.template import loader
from django.contrib.staticfiles.views import serve
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from write.models import MtEntry, MtComment
from write.forms import CommentForm


def get_client_ip(request):
    """
    We’re behind a proxy but if our nginx is configured correctly we
    should be able to get the request ip in 'HTTP_X_FORWARDED_FOR'
    Otherwise fall back to REMOTE_ADDRESS which should be 127.0.0.1
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def latest_entry_read(request):
    """
    /and/ redirects to /and/the-latest-article
    """
    e = MtEntry.objects.filter(published=True).first()
    return redirect('entry-read', slug=e.slug)


def latest_entry_write(request):
    """
    /or/ redirects to /or/the-latest-article
    """
    e = MtEntry.objects.all().first()
    return redirect('entry-write', slug=e.slug)


def archives(request):
    """
    A page that shows all the posts
    """
    cutoff = timezone.make_aware(datetime(2026, 3, 11))

    tpl_params = {}
    tpl_params['entries_before'] = MtEntry.objects.filter(published=True, created_on__lt=cutoff)
    tpl_params['entries_after'] = MtEntry.objects.filter(published=True, created_on__gte=cutoff)
    tpl_params['latest_entry'] = tpl_params['entries_after'].filter(published=True)[0]
    tpl_params['EDITING'] = False
    tpl_params['andor'] = '/and/'
    tpl_params['title'] = 'Archives'
    return render(request, "themes/roxanne/archives.html", tpl_params)


@login_required(login_url='/or/login')
def wall(request):
    """
    An interface similar to calendar apps to allow to schedule post publishing
    """
    tpl_params = {}
    tpl_params['entries'] = MtEntry.objects.all()
    tpl_params['latest_entry'] = tpl_params['entries'].filter(published=True).first()
    entries_hash = [e.event() for e in MtEntry.objects.all()]
    tpl_params['entries_json'] = json.dumps(entries_hash, indent=2, ensure_ascii=False)
    tpl_params['EDITING'] = True
    tpl_params['andor'] = '/or/'
    return render(request, "themes/2011/wall.html", tpl_params)


def entry(request, slug, editing=False, comment_form=None):
    """
    The main view, a blog article (the same view is reused for editing and static mode)
    :param request: A Django HTTP Request object
    :param slug:
    :param editing: Add the editing interface.
    :param comment_form: Does this do something right now ?
    :return:
    """
    try:
        entry = MtEntry.objects.get(slug=slug)
    except MtEntry.DoesNotExist:
        if not editing:
            raise Http404
        entry = MtEntry(slug=slug)
        entry.author = User.objects.get(pk=3)  # glit by default
        entry.created_on = timezone.make_aware(datetime.now())
        entry.body = """
        <p>Hello dear start the editing process.</p>
        """

        entry.entry_title = slug.replace('-', ' ').title()
        entry.published = False  # draft by default

    """
    # We can not read unpublished entries, except when providing a ‘secret token’
    # This is not supposed to be a secure: it is more of a low garden fence
    # than it is a lock
    if not editing and not entry.published and not request.user.is_authenticated:
        if request.GET.get('the_secret_question', '') != 'the_secret_answer':
            return HttpResponseForbidden()
    """

    if comment_form:
        form = comment_form
    else:
        form = CommentForm(initial={'entry': entry})

    author_ids = (3, 4, 5, 6, 7, 8)  # the i.liketightpant contributors
    authors = User.objects.all()
    main_authors = User.objects.filter(pk__in=author_ids)
    main_authors_excluding_current_author = main_authors.exclude(pk=entry.author.pk)

    published_entries = MtEntry.objects.filter(published=True)
    published_entries_ids = [e.pk for e in published_entries]
    visible_comments = MtComment.objects.filter(visible=True).filter(entry__pk__in=published_entries_ids)

    tpl_params = {}
    tpl_params['EDITING'] = editing
    tpl_params['andor'] = '/or/' if editing else '/and/'

    tpl_params['e'] = entry
    tpl_params['e_comments'] = entry.mtcomment_set.filter(visible=True).order_by('created_on')
    tpl_params['title'] = entry.title
    tpl_params['a'] = entry.author
    tpl_params['a_entries'] = published_entries.filter(author=entry.author).exclude(pk=entry.pk)
    tpl_params['a_comments'] = visible_comments.filter(mt_author=entry.author)[:10]

    tpl_params['authors'] = authors
    tpl_params['author_ids'] = author_ids
    tpl_params['main_authors'] = main_authors
    tpl_params['main_authors_excluding_current_author'] = main_authors_excluding_current_author
    tpl_params['recent_entries'] = published_entries.filter(published=True)[:10]
    tpl_params['latest_entry'] = tpl_params['recent_entries'][0]
    tpl_params['recent_comments'] = visible_comments[:10]
    tpl_params['parent'] = None

    tpl_params['form'] = form

    template = "themes/roxanne/entry.html"
    if entry.uses_old_style_templates():
        template = "themes/2011/entry.html"
    return render(request, template, tpl_params)


def entries_by_author(request, author_slug):
    """
    Archives by author
    :param request: A Django HTTP Request object
    :param author_slug: username for author
    :return:
    """
    author_ids = (3, 4, 5, 6, 7, 8)  # the i.liketightpant contributors
    main_authors = User.objects.filter(pk__in=author_ids)
    current_author = User.objects.get(username=author_slug)
    main_authors_excluding_current_author = main_authors.exclude(pk=current_author.pk)

    published_entries = MtEntry.objects.filter(published=True)

    tpl_params = {}
    tpl_params['andor'] = '/and/'
    tpl_params['a'] = current_author
    tpl_params['a_entries'] = published_entries.filter(author=current_author)
    tpl_params['latest_entry'] = published_entries[0]
    tpl_params['title'] = "Stories by " + str(current_author)

    tpl_params['main_authors_excluding_current_author'] = main_authors_excluding_current_author

    return render(request, "themes/roxanne/entries_by_author.html", tpl_params)


def entry_read(request, slug):
    return entry(request, slug, False)


@login_required(login_url='/or/login')
def entry_write(request, slug):
    return entry(request, slug, True)


@csrf_exempt
def handle_comment(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        post = request.POST.copy()
        # create a form instance and populate it with data from the request:
        form = CommentForm(post)
        form.data['ip'] = request.META['REMOTE_ADDR']
        if not form.is_valid():
            return render(request, "themes/roxanne/verify_comment.html", {'form': form})

        comment = form.save(commit=False)
        comment.visible = True
        comment.ip = get_client_ip(request)
        comment.save()
        #comment.entry.commit()
        return redirect('entry-read', slug=comment.entry.slug)

    # if a GET (or any other method):
    else:
        return HttpResponseForbidden()


def about(request):
    """
    An about page
    """
    return render(request, "themes/roxanne/about.html", {})


def index_php(request):
    """
    Generate a simple PHP file that will redirect to the latest post.
    Won’t work through Python, but the publish step saves this as a file, which will work on the simple PHP + statics
    host where the final set of HTML files will be hosted
    """
    e = MtEntry.objects.filter(published=True).first()
    return HttpResponse("""<?php header('Location: %s'); ?>""" % e.get_absolute_url(),
                        content_type="text/plain; charset=utf-8")


def feed(request):
    """
    An RSS feed in atom+xml format.
    It was designed to be compatible with the Movable Type / Open Melody software that ran the blog before
    """
    tpl_params = {}
    tpl_params['entries'] = MtEntry.objects.filter(published=True)[:15]

    t = loader.get_template('recent_entries.xml')
    return HttpResponse(t.render(tpl_params), content_type="application/atom+xml; charset=utf-8")


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
