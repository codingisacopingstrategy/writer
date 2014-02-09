#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is an auto-generated Django model module.
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

import os
import re

static_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'assets')

local_static_files = []
for root, dirs, files in os.walk(static_dir):
    web_root = "/and/assets%s" % root.split('/assets')[-1]
    for f in files:
        local_static_files.append(os.path.join(os.sep, web_root, f))
local_static_files = set(local_static_files)

rex = re.compile(r'\W+')
match_mentioned_files = re.compile('"(\/[^"]+)"')

from dulwich.repo import Repo

from django.db import models

# Because we’ll be calling out for screenshots
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.defaultfilters import striptags
from django.test.client import Client

from screenshots import screenshot
from write.settings import PUBLIC_PATH

REPO = Repo(PUBLIC_PATH)


class MtAuthor(models.Model):
    author_id = models.IntegerField(primary_key=True)
    author_api_password = models.CharField(max_length=180, blank=True)
    author_auth_type = models.CharField(max_length=150, blank=True)
    author_basename = models.CharField(max_length=765, blank=True)
    author_can_create_blog = models.IntegerField(null=True, blank=True)
    author_can_view_log = models.IntegerField(null=True, blank=True)
    author_created_by = models.IntegerField(null=True, blank=True)
    author_created_on = models.DateTimeField(null=True, blank=True)
    author_email = models.CharField(max_length=381, blank=True)
    author_entry_prefs = models.CharField(max_length=765, blank=True)
    author_external_id = models.CharField(max_length=765, blank=True)
    author_hint = models.CharField(max_length=225, blank=True)
    author_is_superuser = models.IntegerField(null=True, blank=True)
    author_modified_by = models.IntegerField(null=True, blank=True)
    author_modified_on = models.DateTimeField(null=True, blank=True)
    author_name = models.CharField(max_length=765)
    author_nickname = models.CharField(max_length=765, blank=True)
    author_password = models.CharField(max_length=180)
    author_preferred_language = models.CharField(max_length=150, blank=True)
    author_public_key = models.TextField(blank=True)
    author_remote_auth_token = models.CharField(max_length=150, blank=True)
    author_remote_auth_username = models.CharField(max_length=150, blank=True)
    author_status = models.IntegerField(null=True, blank=True)
    author_text_format = models.CharField(max_length=90, blank=True)
    author_type = models.IntegerField()
    author_url = models.CharField(max_length=765, blank=True)
    author_userpic_asset_id = models.IntegerField(null=True, blank=True)
    def __unicode__(self):
        return self.author_nickname
    class Meta:
        db_table = u'mt_author'

class MtComment(models.Model):
    comment_id = models.IntegerField(primary_key=True)
    comment_author = models.CharField(max_length=300, blank=True)
    comment_blog_id = models.IntegerField()
    comment_commenter_id = models.IntegerField(null=True, blank=True)
    comment_created_by = models.IntegerField(null=True, blank=True)
    comment_created_on = models.DateTimeField(null=True, blank=True)
    comment_email = models.CharField(max_length=381, blank=True)
    comment_entry_id = models.IntegerField()
    comment_ip = models.CharField(max_length=150, blank=True)
    comment_junk_log = models.TextField(blank=True)
    comment_junk_score = models.FloatField(null=True, blank=True)
    comment_junk_status = models.IntegerField(null=True, blank=True)
    comment_last_moved_on = models.DateTimeField()
    comment_modified_by = models.IntegerField(null=True, blank=True)
    comment_modified_on = models.DateTimeField(null=True, blank=True)
    comment_parent_id = models.IntegerField(null=True, blank=True)
    comment_text = models.TextField(blank=True)
    comment_url = models.CharField(max_length=765, blank=True)
    comment_visible = models.IntegerField(null=True, blank=True)
    def get_commenter_url(self):
        if self.comment_commenter_id in [3, 4, 5, 6, 7, 8]:
            return u"http://i.liketightpants.net/authors#%s" % self.comment_author
        if self.comment_url:
            return self.comment_url
        return ""
    def comment_entry(self):
        return MtEntry.objects.get(pk=self.comment_entry_id)
    def __unicode__(self):
        text = rex.sub( ' ', striptags(self.comment_text) )
        return u"%s: %s" % (self.comment_author, text)
    class Meta:
        db_table = u'mt_comment'
        ordering = ('-comment_created_on',)


class MtEntry(models.Model):
    entry_id = models.IntegerField(primary_key=True)
    entry_allow_comments = models.IntegerField(null=True, blank=True)
    entry_allow_pings = models.IntegerField(null=True, blank=True)
    entry_atom_id = models.CharField(max_length=765, blank=True)
    entry_author_id = models.IntegerField()
    entry_authored_on = models.DateTimeField(null=True, blank=True)
    entry_basename = models.CharField(max_length=765, blank=True)
    entry_blog_id = models.IntegerField()
    entry_category_id = models.IntegerField(null=True, blank=True)
    entry_class = models.CharField(max_length=765, blank=True)
    entry_comment_count = models.IntegerField(null=True, blank=True)
    entry_convert_breaks = models.CharField(max_length=90, blank=True)
    entry_created_by = models.IntegerField(null=True, blank=True)
    entry_created_on = models.DateTimeField(null=True, blank=True)
    entry_excerpt = models.TextField(blank=True)
    entry_keywords = models.TextField(blank=True)
    entry_modified_by = models.IntegerField(null=True, blank=True)
    entry_modified_on = models.DateTimeField(null=True, blank=True)
    entry_ping_count = models.IntegerField(null=True, blank=True)
    entry_pinged_urls = models.TextField(blank=True)
    entry_status = models.IntegerField()
    entry_tangent_cache = models.TextField(blank=True)
    entry_template_id = models.IntegerField(null=True, blank=True)
    entry_text = models.TextField(blank=True)
    entry_text_more = models.TextField(blank=True)
    entry_title = models.CharField(max_length=765, blank=True)
    entry_to_ping_urls = models.TextField(blank=True)
    entry_week_number = models.IntegerField(null=True, blank=True)
    entry_current_revision = models.IntegerField()
    
    def static_files(self):
        entry_files = set(match_mentioned_files.findall(self.entry_text))
        return list(entry_files & local_static_files)
    
    def entry_screenshot_url(self):
        return '/and/assets/as/screenshots/of/%s.png' % self.entry_basename.replace('_','-')
    
    def entry_slug(self):
        return self.entry_basename.replace('_','-')
    
    def entry_uri(self):
        return '/or/' + self.entry_slug()
    
    def entry_event(self):
        return { 'title' : self.entry_title,
                 'start' : self.entry_authored_on.isoformat(),
                 'url' : self.entry_uri(),
                 'id' : self.entry_id,
                 'screenshot_url' : self.entry_screenshot_url(),
                 'resource_uri' : "/api/entry/%s/" % self.entry_id,
                 'allDay' : False }
    
    # http://stackoverflow.com/questions/2214852/next-previous-links-from-a-query-set-generic-views
    def next(self):
        if self.entry_id:
            next = MtEntry.objects.filter(entry_status=2).filter(entry_id__gt=self.entry_id)
            if next:
                return next[0]
        return False
    def previous(self):
        if self.entry_id:
            prev = MtEntry.objects.filter(entry_status=2).filter(entry_id__lt=self.entry_id)
            if prev:
                return prev[0]
        return False
    
    def generate(self):
        # Props to https://github.com/mtigas/django-medusa for the excellent idea
        # of using Django’s test client for the job.
        c = Client()
        response = c.get(u"/is/%s" % self.entry_slug())
        
        if response.status_code != 200:
            raise Exception(response.status_code)
        
        return response.content
    
    def commit(self, message, commiter_name, commiter_mail):
        path = os.path.join(PUBLIC_PATH, u"%s.html" % self.entry_slug())
        with open(path, 'w') as f:
            f.write(self.generate())
        
        repo.stage([path])
        
        commiter = u"%s <%s>" % (commiter_name, commiter_email)
        commit_id = repo.do_commit(message, committer=commiter)

    def __unicode__(self):
        return self.entry_title
    class Meta:
        db_table = u'mt_entry'
        ordering = ('-entry_authored_on',)


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
    print "Entry %s Saved!" % instance.entry_title

@receiver(post_save, sender=MtComment)
def screenshot_handler_comment(sender, instance, created, raw, using, **kwargs):
    entry = MtEntry.objects.get(pk=instance.comment_entry_id)
    print "Comment on Entry %s Saved!" % entry.entry_title

