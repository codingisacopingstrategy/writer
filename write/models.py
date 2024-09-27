#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from dulwich.repo import Repo
from dulwich.porcelain import get_tree_changes, add, commit

from django.db import models

# Because we’ll be calling out for screenshots
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import striptags
from django.test.client import Client

from write.settings import PUBLIC_PATH

REPO = Repo(PUBLIC_PATH)
rex = re.compile(r'\W+')


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
            return u"http://i.liketightpants.net/authors#%s" % self.author
        if self.url:
            return self.url
        return ""

    def __unicode__(self):
        text = rex.sub(' ', striptags(self.text))
        return u"%s: %s" % (self.author, text)

    class Meta:
        ordering = ('-created_on',)


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
            next = MtEntry.objects.filter(published=True).filter(id__gt=self.id)
            if next:
                return next[0]
        return False

    def previous(self):
        if self.id:
            prev = MtEntry.objects.filter(published=True).filter(id__lt=self.id)
            if prev:
                return prev[0]
        return False
    
    def generate(self):
        # Props to https://github.com/mtigas/django-medusa for the excellent idea
        # of using Django’s test client for the job.
        c = Client()
        response = c.get(u"/is/%s" % self.slug)
        
        if response.status_code != 200:
            raise Exception(response.status_code)
        
        return response.content
    
    def commit(self, message=False, commiter_name=False, commiter_email=False):
        filename = u"%s.html" % self.slug
        absolute_path = os.path.join(PUBLIC_PATH, filename)

        with open(absolute_path, 'w') as f:
            f.write(self.generate())

        # In Git (through Dulwich) we work with relative paths
        # All lower-level functions in Dulwich take byte strings
        # rather than unicode strings
        # REPO.stage([filename.encode('utf-8')])
        add(REPO, filename.encode('utf-8'))

        # If generating the HTML and adding it to the index changes
        # nothing we should not commit.
        # We expect `get_tree_changes` to return something like:
        # {'add': [], 'modify': ['the-underwater-screen-or-lessons-from-wordperfect.html'], 'delete': []}
        changes = get_tree_changes(REPO)
        if filename not in changes['modify']:
            return

        if not message:
            message = ("Update: %s" % self.tight_pants_title()).encode('utf-8')
        if not commiter_name:
            commiter_name = self.author.username.encode('utf-8')
        if not commiter_email:
            commiter_email = self.author.email.encode('utf-8')

        commiter = ("%s <%s>" % (commiter_name, commiter_email)).encode('utf-8')

        commit_id = commit(REPO, message=message, committer=commiter)
        return commit_id

    def __unicode__(self):
        return self.title

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
    print "Entry %s Saved!" % instance.title


@receiver(post_save, sender=MtComment)
def screenshot_handler_comment(sender, instance, created, raw, using, **kwargs):
    print "Comment on Entry %s Saved!" % instance.entry.title
