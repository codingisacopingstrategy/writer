#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime

from dulwich.repo import Repo
from dulwich.porcelain import get_tree_changes, add, commit

from django.db import models

# Because we’ll be calling out for screenshots
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import striptags
from django.test.client import Client
from django.utils import timezone

from write.settings import PUBLIC_PATH

REPO = Repo(PUBLIC_PATH)
rex = re.compile(r'\W+')


def as_text(value):
    if value is None or value is False:
        return ''
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return str(value)


def git_path(value):
    if isinstance(value, bytes):
        return value
    return as_text(value).encode('utf-8')


def staged_page_changed(filename, changes):
    name = git_path(filename)
    for key in ('modify', 'add'):
        for item in changes.get(key, ()):
            if git_path(item) == name:
                return True
    return False


def git_identity(name, email):
    return '%s <%s>' % (as_text(name), as_text(email))


def page_commit_message(first, title):
    return '%s: %s' % ('Publish' if first else 'Update', title)


def commit_repo_paths(paths, message, name, email):
    existing = [path for path in paths if os.path.exists(path)]
    if existing:
        add(REPO, existing)
    changes = get_tree_changes(REPO)
    if not (changes.get('add') or changes.get('modify') or changes.get('delete')):
        return None
    identity = git_identity(name, email)
    return commit(
        REPO,
        message=as_text(message),
        author=identity,
        committer=identity,
    )

"""
A simple data model: Authors, Articles (entries), Comments.

For the authors the standard Django user model is used, django.contrib.auth.models.User
"""


class MtEntry(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=765)
    slug = models.SlugField(max_length=765)
    published = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    excerpt = models.TextField(blank=True)
    preview_image = models.URLField(blank=True, max_length=765)
    body = models.TextField()

    def tight_pants_title(self):
        return "I like tight pants and %s" % self.title.lower().rstrip()

    def screenshot_url(self):
        return '/and/assets/as/screenshots/of/%s.png' % self.slug
    
    def editing_uri(self):
        return '/or/' + self.slug
    
    def get_absolute_url(self):
        return '/and/' + self.slug

    def uses_old_style_templates(self):
        """
        The 9th of March 2026 we launched the new website
        """
        cutoff = timezone.make_aware(datetime(2026, 3, 9))
        return self.created_on < cutoff

    def event(self):
        return {'title': self.title,
                'start': self.created_on.isoformat(),
                'url': self.editing_uri(),
                'id': self.id,
                'screenshot_url': self.screenshot_url(),
                'resource_uri': "/api/entry/%s/" % self.pk,
                'allDay': False}
        
    # http://stackoverflow.com/questions/2214852/next-previous-links-from-a-query-set-generic-views
    def next(self):
        if self.id:
            next = MtEntry.objects.filter(published=True).filter(id__gt=self.id).order_by('created_on')
            if next:
                return next[0]
        return False

    def previous(self):
        if self.id:
            prev = MtEntry.objects.filter(published=True).filter(id__lt=self.id)
            if prev:
                return prev[0]
        return False
    
    """
    Returns a string with the HTML content for this page
    """
    def generate(self):
        # Props to https://github.com/mtigas/django-medusa for the excellent idea
        # of using Django’s test client for the job.
        c = Client()
        response = c.get("/is/%s" % self.slug)
        
        if response.status_code != 200:
            raise Exception(response.status_code)
        
        return response.content
    
    """
    Generate the HTML of the page and commit it to the Git repository
    """
    def commit(self, message=False, commiter_name=False, commiter_email=False):
        filename = "%s.html" % self.slug
        absolute_path = os.path.join(PUBLIC_PATH, filename)

        with open(absolute_path, 'wb') as f:
            f.write(self.generate())

        # In Git (through Dulwich) we work with relative paths
        add(REPO, absolute_path)

        # If generating the HTML and adding it to the index changes
        # nothing we should not commit.
        # New posts land in `add`, edits in `modify`.
        changes = get_tree_changes(REPO)
        if not staged_page_changed(filename, changes):
            return

        if not message:
            is_new = any(
                git_path(item) == git_path(filename)
                for item in changes.get('add', ())
            )
            message = page_commit_message(is_new, self.tight_pants_title())
        if not commiter_name:
            commiter_name = self.author.username
        if not commiter_email:
            commiter_email = self.author.email

        identity = git_identity(commiter_name, commiter_email)
        commit_id = commit(
            REPO,
            message=as_text(message),
            author=identity,
            committer=identity,
        )
        return commit_id

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('-created_on',)
        permissions = [
            ('publish_mtentry', 'Can publish entries'),
        ]


class MtComment(models.Model):
    entry = models.ForeignKey('MtEntry', on_delete=models.CASCADE)  # CASCADE used to be the default, it means that when
    # the referenced model is deleted this object will also be deleted
    author = models.CharField(max_length=300, blank=True)
    mt_author = models.ForeignKey('auth.User', null=True, blank=True, default=None, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    email = models.CharField(max_length=381, blank=True)
    ip = models.CharField(max_length=150, default='127.0.0.1')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    text = models.TextField()
    url = models.CharField(max_length=765, blank=True)
    visible = models.BooleanField(default=False)

    def get_commenter_url(self):
        if self.mt_author:
            return "http://i.liketightpants.net/authors#%s" % self.author
        if self.url:
            return self.url
        return ""

    def __str__(self):
        text = rex.sub(' ', striptags(self.text))
        return "%s: %s" % (self.author, text[:60])

    class Meta:
        ordering = ('-created_on',)


"""
Screenshots are used in the view where an editor can
organise the relative timing of different blog posts.

We are not going to use the following two event handlers,
for now. They get triggered everytime an entry or
comment is updated, which is quite often. This would
spawn too many (expensive) screenshot requests.

This could be mitigated by having a queue with a rate
limit, i.e. it ignores requests that come too quick
upon the previous one.

Because currently there is only one person editing the
entries at the time, and others don’t need to see live
updates of this page in the editing view, we can suffice
with a trigger at the moment the entry page is left.

This is to be implemented still.
"""


@receiver(post_save, sender=MtEntry)
def screenshot_handler_entry(sender, instance, created, raw, using, **kwargs):
    print("Entry %s Saved!" % instance.title)


@receiver(post_save, sender=MtComment)
def screenshot_handler_comment(sender, instance, created, raw, using, **kwargs):
    print("Comment on Entry %s Saved!" % instance.entry.title)
