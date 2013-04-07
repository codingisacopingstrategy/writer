#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is an auto-generated Django model module.
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

# Because we’ll be calling out for screenshots
from django.db.models.signals import post_save
from django.dispatch import receiver

from screenshots import screenshot

class MtAsset(models.Model):
    asset_id = models.IntegerField(primary_key=True)
    asset_blog_id = models.IntegerField()
    asset_class = models.CharField(max_length=765, blank=True)
    asset_created_by = models.IntegerField(null=True, blank=True)
    asset_created_on = models.DateTimeField(null=True, blank=True)
    asset_description = models.TextField(blank=True)
    asset_file_ext = models.CharField(max_length=60, blank=True)
    asset_file_name = models.CharField(max_length=765, blank=True)
    asset_file_path = models.CharField(max_length=765, blank=True)
    asset_label = models.CharField(max_length=765, blank=True)
    asset_mime_type = models.CharField(max_length=765, blank=True)
    asset_modified_by = models.IntegerField(null=True, blank=True)
    asset_modified_on = models.DateTimeField(null=True, blank=True)
    asset_parent = models.IntegerField(null=True, blank=True)
    asset_url = models.CharField(max_length=765, blank=True)
    def __unicode__(self):
        return self.asset_file_name
    class Meta:
        db_table = u'mt_asset'

class MtAssetMeta(models.Model):
    asset_meta_asset_id = models.IntegerField(primary_key=True)
    asset_meta_type = models.CharField(max_length=225)
    asset_meta_vchar = models.CharField(max_length=765, blank=True)
    asset_meta_vchar_idx = models.CharField(max_length=765, blank=True)
    asset_meta_vdatetime = models.DateTimeField(null=True, blank=True)
    asset_meta_vdatetime_idx = models.DateTimeField(null=True, blank=True)
    asset_meta_vinteger = models.IntegerField(null=True, blank=True)
    asset_meta_vinteger_idx = models.IntegerField(null=True, blank=True)
    asset_meta_vfloat = models.FloatField(null=True, blank=True)
    asset_meta_vfloat_idx = models.FloatField(null=True, blank=True)
    asset_meta_vblob = models.TextField(blank=True)
    asset_meta_vclob = models.TextField(blank=True)
    class Meta:
        db_table = u'mt_asset_meta'

class MtAssociation(models.Model):
    association_id = models.IntegerField(primary_key=True)
    association_author_id = models.IntegerField(null=True, blank=True)
    association_blog_id = models.IntegerField(null=True, blank=True)
    association_created_by = models.IntegerField(null=True, blank=True)
    association_created_on = models.DateTimeField(null=True, blank=True)
    association_group_id = models.IntegerField(null=True, blank=True)
    association_modified_by = models.IntegerField(null=True, blank=True)
    association_modified_on = models.DateTimeField(null=True, blank=True)
    association_role_id = models.IntegerField(null=True, blank=True)
    association_type = models.IntegerField()
    class Meta:
        db_table = u'mt_association'

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

class MtAuthorMeta(models.Model):
    author_meta_author_id = models.IntegerField(primary_key=True)
    author_meta_type = models.CharField(max_length=225)
    author_meta_vchar = models.CharField(max_length=765, blank=True)
    author_meta_vchar_idx = models.CharField(max_length=765, blank=True)
    author_meta_vdatetime = models.DateTimeField(null=True, blank=True)
    author_meta_vdatetime_idx = models.DateTimeField(null=True, blank=True)
    author_meta_vinteger = models.IntegerField(null=True, blank=True)
    author_meta_vinteger_idx = models.IntegerField(null=True, blank=True)
    author_meta_vfloat = models.FloatField(null=True, blank=True)
    author_meta_vfloat_idx = models.FloatField(null=True, blank=True)
    author_meta_vblob = models.TextField(blank=True)
    author_meta_vclob = models.TextField(blank=True)
    class Meta:
        db_table = u'mt_author_meta'

class MtAuthorSummary(models.Model):
    author_summary_author_id = models.IntegerField(primary_key=True)
    author_summary_type = models.CharField(max_length=765)
    author_summary_class = models.CharField(max_length=225)
    author_summary_vchar_idx = models.CharField(max_length=765, blank=True)
    author_summary_vinteger_idx = models.IntegerField(null=True, blank=True)
    author_summary_vblob = models.TextField(blank=True)
    author_summary_vclob = models.TextField(blank=True)
    author_summary_expired = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'mt_author_summary'

class MtBlog(models.Model):
    blog_id = models.IntegerField(primary_key=True)
    blog_allow_anon_comments = models.IntegerField(null=True, blank=True)
    blog_allow_comment_html = models.IntegerField(null=True, blank=True)
    blog_allow_commenter_regist = models.IntegerField(null=True, blank=True)
    blog_allow_comments_default = models.IntegerField(null=True, blank=True)
    blog_allow_pings = models.IntegerField(null=True, blank=True)
    blog_allow_pings_default = models.IntegerField(null=True, blank=True)
    blog_allow_reg_comments = models.IntegerField(null=True, blank=True)
    blog_allow_unreg_comments = models.IntegerField(null=True, blank=True)
    blog_archive_path = models.CharField(max_length=765, blank=True)
    blog_archive_tmpl_category = models.CharField(max_length=765, blank=True)
    blog_archive_tmpl_daily = models.CharField(max_length=765, blank=True)
    blog_archive_tmpl_individual = models.CharField(max_length=765, blank=True)
    blog_archive_tmpl_monthly = models.CharField(max_length=765, blank=True)
    blog_archive_tmpl_weekly = models.CharField(max_length=765, blank=True)
    blog_archive_type = models.CharField(max_length=765, blank=True)
    blog_archive_type_preferred = models.CharField(max_length=75, blank=True)
    blog_archive_url = models.CharField(max_length=765, blank=True)
    blog_autodiscover_links = models.IntegerField(null=True, blank=True)
    blog_autolink_urls = models.IntegerField(null=True, blank=True)
    blog_basename_limit = models.IntegerField(null=True, blank=True)
    blog_cc_license = models.CharField(max_length=765, blank=True)
    blog_children_modified_on = models.DateTimeField(null=True, blank=True)
    blog_convert_paras = models.CharField(max_length=90, blank=True)
    blog_convert_paras_comments = models.CharField(max_length=90, blank=True)
    blog_created_by = models.IntegerField(null=True, blank=True)
    blog_created_on = models.DateTimeField(null=True, blank=True)
    blog_custom_dynamic_templates = models.CharField(max_length=75, blank=True)
    blog_days_on_index = models.IntegerField(null=True, blank=True)
    blog_description = models.TextField(blank=True)
    blog_email_new_comments = models.IntegerField(null=True, blank=True)
    blog_email_new_pings = models.IntegerField(null=True, blank=True)
    blog_entries_on_index = models.IntegerField(null=True, blank=True)
    blog_file_extension = models.CharField(max_length=30, blank=True)
    blog_google_api_key = models.CharField(max_length=96, blank=True)
    blog_internal_autodiscovery = models.IntegerField(null=True, blank=True)
    blog_is_dynamic = models.IntegerField(null=True, blank=True)
    blog_junk_folder_expiry = models.IntegerField(null=True, blank=True)
    blog_junk_score_threshold = models.FloatField(null=True, blank=True)
    blog_language = models.CharField(max_length=15, blank=True)
    blog_manual_approve_commenters = models.IntegerField(null=True, blank=True)
    blog_moderate_pings = models.IntegerField(null=True, blank=True)
    blog_moderate_unreg_comments = models.IntegerField(null=True, blank=True)
    blog_modified_by = models.IntegerField(null=True, blank=True)
    blog_modified_on = models.DateTimeField(null=True, blank=True)
    blog_mt_update_key = models.CharField(max_length=90, blank=True)
    blog_name = models.CharField(max_length=765)
    blog_old_style_archive_links = models.IntegerField(null=True, blank=True)
    blog_ping_blogs = models.IntegerField(null=True, blank=True)
    blog_ping_google = models.IntegerField(null=True, blank=True)
    blog_ping_others = models.TextField(blank=True)
    blog_ping_technorati = models.IntegerField(null=True, blank=True)
    blog_ping_weblogs = models.IntegerField(null=True, blank=True)
    blog_remote_auth_token = models.CharField(max_length=150, blank=True)
    blog_require_comment_emails = models.IntegerField(null=True, blank=True)
    blog_sanitize_spec = models.CharField(max_length=765, blank=True)
    blog_server_offset = models.FloatField(null=True, blank=True)
    blog_site_path = models.CharField(max_length=765, blank=True)
    blog_site_url = models.CharField(max_length=765, blank=True)
    blog_sort_order_comments = models.CharField(max_length=24, blank=True)
    blog_sort_order_posts = models.CharField(max_length=24, blank=True)
    blog_status_default = models.IntegerField(null=True, blank=True)
    blog_use_comment_confirmation = models.IntegerField(null=True, blank=True)
    blog_welcome_msg = models.TextField(blank=True)
    blog_words_in_excerpt = models.IntegerField(null=True, blank=True)
    blog_use_revision = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'mt_blog'

class MtBlogMeta(models.Model):
    blog_meta_blog_id = models.IntegerField(primary_key=True)
    blog_meta_type = models.CharField(max_length=225)
    blog_meta_vchar = models.CharField(max_length=765, blank=True)
    blog_meta_vchar_idx = models.CharField(max_length=765, blank=True)
    blog_meta_vdatetime = models.DateTimeField(null=True, blank=True)
    blog_meta_vdatetime_idx = models.DateTimeField(null=True, blank=True)
    blog_meta_vinteger = models.IntegerField(null=True, blank=True)
    blog_meta_vinteger_idx = models.IntegerField(null=True, blank=True)
    blog_meta_vfloat = models.FloatField(null=True, blank=True)
    blog_meta_vfloat_idx = models.FloatField(null=True, blank=True)
    blog_meta_vblob = models.TextField(blank=True)
    blog_meta_vclob = models.TextField(blank=True)
    class Meta:
        db_table = u'mt_blog_meta'

class MtCategory(models.Model):
    category_id = models.IntegerField(primary_key=True)
    category_allow_pings = models.IntegerField(null=True, blank=True)
    category_author_id = models.IntegerField(null=True, blank=True)
    category_basename = models.CharField(max_length=765, blank=True)
    category_blog_id = models.IntegerField()
    category_class = models.CharField(max_length=765, blank=True)
    category_created_by = models.IntegerField(null=True, blank=True)
    category_created_on = models.DateTimeField(null=True, blank=True)
    category_description = models.TextField(blank=True)
    category_label = models.CharField(max_length=300)
    category_modified_by = models.IntegerField(null=True, blank=True)
    category_modified_on = models.DateTimeField(null=True, blank=True)
    category_parent = models.IntegerField(null=True, blank=True)
    category_ping_urls = models.TextField(blank=True)
    class Meta:
        db_table = u'mt_category'

class MtCategoryMeta(models.Model):
    category_meta_category_id = models.IntegerField(primary_key=True)
    category_meta_type = models.CharField(max_length=225)
    category_meta_vchar = models.CharField(max_length=765, blank=True)
    category_meta_vchar_idx = models.CharField(max_length=765, blank=True)
    category_meta_vdatetime = models.DateTimeField(null=True, blank=True)
    category_meta_vdatetime_idx = models.DateTimeField(null=True, blank=True)
    category_meta_vinteger = models.IntegerField(null=True, blank=True)
    category_meta_vinteger_idx = models.IntegerField(null=True, blank=True)
    category_meta_vfloat = models.FloatField(null=True, blank=True)
    category_meta_vfloat_idx = models.FloatField(null=True, blank=True)
    category_meta_vblob = models.TextField(blank=True)
    category_meta_vclob = models.TextField(blank=True)
    class Meta:
        db_table = u'mt_category_meta'

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
    def __unicode__(self):
        return u"%s: %s" % (self.comment_author, self.comment_text.splitlines()[0])
    class Meta:
        db_table = u'mt_comment'
        ordering = ('-comment_id',)

class MtCommentMeta(models.Model):
    comment_meta_comment_id = models.IntegerField(primary_key=True)
    comment_meta_type = models.CharField(max_length=225)
    comment_meta_vchar = models.CharField(max_length=765, blank=True)
    comment_meta_vchar_idx = models.CharField(max_length=765, blank=True)
    comment_meta_vdatetime = models.DateTimeField(null=True, blank=True)
    comment_meta_vdatetime_idx = models.DateTimeField(null=True, blank=True)
    comment_meta_vinteger = models.IntegerField(null=True, blank=True)
    comment_meta_vinteger_idx = models.IntegerField(null=True, blank=True)
    comment_meta_vfloat = models.FloatField(null=True, blank=True)
    comment_meta_vfloat_idx = models.FloatField(null=True, blank=True)
    comment_meta_vblob = models.TextField(blank=True)
    comment_meta_vclob = models.TextField(blank=True)
    class Meta:
        db_table = u'mt_comment_meta'

class MtConfig(models.Model):
    config_id = models.IntegerField(primary_key=True)
    config_data = models.TextField(blank=True)
    class Meta:
        db_table = u'mt_config'

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
    
    def entry_screenshot_url(self):
        return '/and/assets/as/screenshots/of/%s.png' % self.entry_basename.replace('_','-')
    
    def entry_slug(self):
        return self.entry_basename.replace('_','-')
    
    # http://stackoverflow.com/questions/2214852/next-previous-links-from-a-query-set-generic-views
    def next(self):
        if self.entry_id:
            next = MtEntry.objects.filter(entry_id__gt=self.entry_id)
            if next:
                return next[0]
        return False
    def previous(self):
        if self.entry_id:
            prev = MtEntry.objects.filter(entry_id__lt=self.entry_id)
            if prev:
                return prev[0]
        return False

    def __unicode__(self):
        return self.entry_title
    class Meta:
        db_table = u'mt_entry'
        ordering = ('-entry_authored_on',)

class MtEntryMeta(models.Model):
    entry_meta_entry_id = models.IntegerField(primary_key=True)
    entry_meta_type = models.CharField(max_length=225)
    entry_meta_vchar = models.CharField(max_length=765, blank=True)
    entry_meta_vchar_idx = models.CharField(max_length=765, blank=True)
    entry_meta_vdatetime = models.DateTimeField(null=True, blank=True)
    entry_meta_vdatetime_idx = models.DateTimeField(null=True, blank=True)
    entry_meta_vinteger = models.IntegerField(null=True, blank=True)
    entry_meta_vinteger_idx = models.IntegerField(null=True, blank=True)
    entry_meta_vfloat = models.FloatField(null=True, blank=True)
    entry_meta_vfloat_idx = models.FloatField(null=True, blank=True)
    entry_meta_vblob = models.TextField(blank=True)
    entry_meta_vclob = models.TextField(blank=True)
    class Meta:
        db_table = u'mt_entry_meta'

class MtEntryRev(models.Model):
    entry_rev_id = models.IntegerField(primary_key=True)
    entry_rev_changed = models.CharField(max_length=765)
    entry_rev_created_by = models.IntegerField(null=True, blank=True)
    entry_rev_created_on = models.DateTimeField(null=True, blank=True)
    entry_rev_description = models.CharField(max_length=765, blank=True)
    entry_rev_entry = models.TextField()
    entry_rev_entry_id = models.IntegerField()
    entry_rev_label = models.CharField(max_length=765, blank=True)
    entry_rev_modified_by = models.IntegerField(null=True, blank=True)
    entry_rev_modified_on = models.DateTimeField(null=True, blank=True)
    entry_rev_rev_number = models.IntegerField()
    class Meta:
        db_table = u'mt_entry_rev'

class MtEntrySummary(models.Model):
    entry_summary_entry_id = models.IntegerField(primary_key=True)
    entry_summary_type = models.CharField(max_length=765)
    entry_summary_class = models.CharField(max_length=225)
    entry_summary_vchar_idx = models.CharField(max_length=765, blank=True)
    entry_summary_vinteger_idx = models.IntegerField(null=True, blank=True)
    entry_summary_vblob = models.TextField(blank=True)
    entry_summary_vclob = models.TextField(blank=True)
    entry_summary_expired = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'mt_entry_summary'

class MtFileinfo(models.Model):
    fileinfo_id = models.IntegerField(primary_key=True)
    fileinfo_archive_type = models.CharField(max_length=765, blank=True)
    fileinfo_author_id = models.IntegerField(null=True, blank=True)
    fileinfo_blog_id = models.IntegerField()
    fileinfo_category_id = models.IntegerField(null=True, blank=True)
    fileinfo_entry_id = models.IntegerField(null=True, blank=True)
    fileinfo_file_path = models.TextField(blank=True)
    fileinfo_startdate = models.CharField(max_length=240, blank=True)
    fileinfo_template_id = models.IntegerField(null=True, blank=True)
    fileinfo_templatemap_id = models.IntegerField(null=True, blank=True)
    fileinfo_url = models.CharField(max_length=765, blank=True)
    fileinfo_virtual = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'mt_fileinfo'

class MtIpbanlist(models.Model):
    ipbanlist_id = models.IntegerField(primary_key=True)
    ipbanlist_blog_id = models.IntegerField()
    ipbanlist_created_by = models.IntegerField(null=True, blank=True)
    ipbanlist_created_on = models.DateTimeField(null=True, blank=True)
    ipbanlist_ip = models.CharField(max_length=150)
    ipbanlist_modified_by = models.IntegerField(null=True, blank=True)
    ipbanlist_modified_on = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'mt_ipbanlist'

class MtLog(models.Model):
    log_id = models.IntegerField(primary_key=True)
    log_author_id = models.IntegerField(null=True, blank=True)
    log_blog_id = models.IntegerField(null=True, blank=True)
    log_category = models.CharField(max_length=765, blank=True)
    log_class = models.CharField(max_length=765, blank=True)
    log_created_by = models.IntegerField(null=True, blank=True)
    log_created_on = models.DateTimeField(null=True, blank=True)
    log_ip = models.CharField(max_length=150, blank=True)
    log_level = models.IntegerField(null=True, blank=True)
    log_message = models.TextField(blank=True)
    log_metadata = models.CharField(max_length=765, blank=True)
    log_modified_by = models.IntegerField(null=True, blank=True)
    log_modified_on = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'mt_log'

class MtNotification(models.Model):
    notification_id = models.IntegerField(primary_key=True)
    notification_blog_id = models.IntegerField()
    notification_created_by = models.IntegerField(null=True, blank=True)
    notification_created_on = models.DateTimeField(null=True, blank=True)
    notification_email = models.CharField(max_length=225, blank=True)
    notification_modified_by = models.IntegerField(null=True, blank=True)
    notification_modified_on = models.DateTimeField(null=True, blank=True)
    notification_name = models.CharField(max_length=150, blank=True)
    notification_url = models.CharField(max_length=765, blank=True)
    class Meta:
        db_table = u'mt_notification'

class MtObjectasset(models.Model):
    objectasset_id = models.IntegerField(primary_key=True)
    objectasset_asset_id = models.IntegerField()
    objectasset_blog_id = models.IntegerField(null=True, blank=True)
    objectasset_embedded = models.IntegerField(null=True, blank=True)
    objectasset_object_ds = models.CharField(max_length=150)
    objectasset_object_id = models.IntegerField()
    class Meta:
        db_table = u'mt_objectasset'

class MtObjectscore(models.Model):
    objectscore_id = models.IntegerField(primary_key=True)
    objectscore_author_id = models.IntegerField(null=True, blank=True)
    objectscore_created_by = models.IntegerField(null=True, blank=True)
    objectscore_created_on = models.DateTimeField(null=True, blank=True)
    objectscore_ip = models.CharField(max_length=150, blank=True)
    objectscore_modified_by = models.IntegerField(null=True, blank=True)
    objectscore_modified_on = models.DateTimeField(null=True, blank=True)
    objectscore_namespace = models.CharField(max_length=300)
    objectscore_object_ds = models.CharField(max_length=150)
    objectscore_object_id = models.IntegerField(null=True, blank=True)
    objectscore_score = models.FloatField(null=True, blank=True)
    class Meta:
        db_table = u'mt_objectscore'

class MtObjecttag(models.Model):
    objecttag_id = models.IntegerField(primary_key=True)
    objecttag_blog_id = models.IntegerField(null=True, blank=True)
    objecttag_object_datasource = models.CharField(max_length=150)
    objecttag_object_id = models.IntegerField()
    objecttag_tag_id = models.IntegerField()
    class Meta:
        db_table = u'mt_objecttag'

class MtPermission(models.Model):
    permission_id = models.IntegerField(primary_key=True)
    permission_author_id = models.IntegerField()
    permission_blog_id = models.IntegerField()
    permission_blog_prefs = models.CharField(max_length=765, blank=True)
    permission_created_by = models.IntegerField(null=True, blank=True)
    permission_created_on = models.DateTimeField(null=True, blank=True)
    permission_entry_prefs = models.TextField(blank=True)
    permission_modified_by = models.IntegerField(null=True, blank=True)
    permission_modified_on = models.DateTimeField(null=True, blank=True)
    permission_permissions = models.TextField(blank=True)
    permission_restrictions = models.TextField(blank=True)
    permission_role_mask = models.IntegerField(null=True, blank=True)
    permission_template_prefs = models.CharField(max_length=765, blank=True)
    class Meta:
        db_table = u'mt_permission'

class MtPlacement(models.Model):
    placement_id = models.IntegerField(primary_key=True)
    placement_blog_id = models.IntegerField()
    placement_category_id = models.IntegerField()
    placement_entry_id = models.IntegerField()
    placement_is_primary = models.IntegerField()
    class Meta:
        db_table = u'mt_placement'

class MtPlugindata(models.Model):
    plugindata_id = models.IntegerField(primary_key=True)
    plugindata_data = models.TextField(blank=True)
    plugindata_key = models.CharField(max_length=765)
    plugindata_plugin = models.CharField(max_length=150)
    class Meta:
        db_table = u'mt_plugindata'

class MtRole(models.Model):
    role_id = models.IntegerField(primary_key=True)
    role_created_by = models.IntegerField(null=True, blank=True)
    role_created_on = models.DateTimeField(null=True, blank=True)
    role_description = models.TextField(blank=True)
    role_is_system = models.IntegerField(null=True, blank=True)
    role_modified_by = models.IntegerField(null=True, blank=True)
    role_modified_on = models.DateTimeField(null=True, blank=True)
    role_name = models.CharField(max_length=765)
    role_permissions = models.TextField(blank=True)
    role_role_mask = models.IntegerField(null=True, blank=True)
    role_role_mask2 = models.IntegerField(null=True, blank=True)
    role_role_mask3 = models.IntegerField(null=True, blank=True)
    role_role_mask4 = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'mt_role'

class MtSession(models.Model):
    session_id = models.CharField(max_length=240, primary_key=True)
    session_data = models.TextField(blank=True)
    session_email = models.CharField(max_length=765, blank=True)
    session_kind = models.CharField(max_length=6, blank=True)
    session_name = models.CharField(max_length=765, blank=True)
    session_start = models.IntegerField()
    class Meta:
        db_table = u'mt_session'

class MtTag(models.Model):
    tag_id = models.IntegerField(primary_key=True)
    tag_is_private = models.IntegerField(null=True, blank=True)
    tag_n8d_id = models.IntegerField(null=True, blank=True)
    tag_name = models.CharField(max_length=765)
    class Meta:
        db_table = u'mt_tag'

class MtTbping(models.Model):
    tbping_id = models.IntegerField(primary_key=True)
    tbping_blog_id = models.IntegerField()
    tbping_blog_name = models.CharField(max_length=765, blank=True)
    tbping_created_by = models.IntegerField(null=True, blank=True)
    tbping_created_on = models.DateTimeField(null=True, blank=True)
    tbping_excerpt = models.TextField(blank=True)
    tbping_ip = models.CharField(max_length=150)
    tbping_junk_log = models.TextField(blank=True)
    tbping_junk_score = models.FloatField(null=True, blank=True)
    tbping_junk_status = models.IntegerField()
    tbping_last_moved_on = models.DateTimeField()
    tbping_modified_by = models.IntegerField(null=True, blank=True)
    tbping_modified_on = models.DateTimeField(null=True, blank=True)
    tbping_source_url = models.CharField(max_length=765, blank=True)
    tbping_tb_id = models.IntegerField()
    tbping_title = models.CharField(max_length=765, blank=True)
    tbping_visible = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'mt_tbping'

class MtTbpingMeta(models.Model):
    tbping_meta_tbping_id = models.IntegerField(primary_key=True)
    tbping_meta_type = models.CharField(max_length=225)
    tbping_meta_vchar = models.CharField(max_length=765, blank=True)
    tbping_meta_vchar_idx = models.CharField(max_length=765, blank=True)
    tbping_meta_vdatetime = models.DateTimeField(null=True, blank=True)
    tbping_meta_vdatetime_idx = models.DateTimeField(null=True, blank=True)
    tbping_meta_vinteger = models.IntegerField(null=True, blank=True)
    tbping_meta_vinteger_idx = models.IntegerField(null=True, blank=True)
    tbping_meta_vfloat = models.FloatField(null=True, blank=True)
    tbping_meta_vfloat_idx = models.FloatField(null=True, blank=True)
    tbping_meta_vblob = models.TextField(blank=True)
    tbping_meta_vclob = models.TextField(blank=True)
    class Meta:
        db_table = u'mt_tbping_meta'

class MtTemplate(models.Model):
    template_id = models.IntegerField(primary_key=True)
    template_blog_id = models.IntegerField()
    template_build_dynamic = models.IntegerField(null=True, blank=True)
    template_build_interval = models.IntegerField(null=True, blank=True)
    template_build_type = models.IntegerField(null=True, blank=True)
    template_created_by = models.IntegerField(null=True, blank=True)
    template_created_on = models.DateTimeField(null=True, blank=True)
    template_identifier = models.CharField(max_length=150, blank=True)
    template_linked_file = models.CharField(max_length=765, blank=True)
    template_linked_file_mtime = models.CharField(max_length=30, blank=True)
    template_linked_file_size = models.IntegerField(null=True, blank=True)
    template_modified_by = models.IntegerField(null=True, blank=True)
    template_modified_on = models.DateTimeField(null=True, blank=True)
    template_name = models.CharField(max_length=765)
    template_outfile = models.CharField(max_length=765, blank=True)
    template_rebuild_me = models.IntegerField(null=True, blank=True)
    template_text = models.TextField(blank=True)
    template_type = models.CharField(max_length=75)
    template_current_revision = models.IntegerField()
    class Meta:
        db_table = u'mt_template'

class MtTemplateMeta(models.Model):
    template_meta_template_id = models.IntegerField(primary_key=True)
    template_meta_type = models.CharField(max_length=225)
    template_meta_vchar = models.CharField(max_length=765, blank=True)
    template_meta_vchar_idx = models.CharField(max_length=765, blank=True)
    template_meta_vdatetime = models.DateTimeField(null=True, blank=True)
    template_meta_vdatetime_idx = models.DateTimeField(null=True, blank=True)
    template_meta_vinteger = models.IntegerField(null=True, blank=True)
    template_meta_vinteger_idx = models.IntegerField(null=True, blank=True)
    template_meta_vfloat = models.FloatField(null=True, blank=True)
    template_meta_vfloat_idx = models.FloatField(null=True, blank=True)
    template_meta_vblob = models.TextField(blank=True)
    template_meta_vclob = models.TextField(blank=True)
    class Meta:
        db_table = u'mt_template_meta'

class MtTemplateRev(models.Model):
    template_rev_id = models.IntegerField(primary_key=True)
    template_rev_changed = models.CharField(max_length=765)
    template_rev_created_by = models.IntegerField(null=True, blank=True)
    template_rev_created_on = models.DateTimeField(null=True, blank=True)
    template_rev_description = models.CharField(max_length=765, blank=True)
    template_rev_label = models.CharField(max_length=765, blank=True)
    template_rev_modified_by = models.IntegerField(null=True, blank=True)
    template_rev_modified_on = models.DateTimeField(null=True, blank=True)
    template_rev_rev_number = models.IntegerField()
    template_rev_template = models.TextField()
    template_rev_template_id = models.IntegerField()
    class Meta:
        db_table = u'mt_template_rev'

class MtTemplatemap(models.Model):
    templatemap_id = models.IntegerField(primary_key=True)
    templatemap_archive_type = models.CharField(max_length=75)
    templatemap_blog_id = models.IntegerField()
    templatemap_build_interval = models.IntegerField(null=True, blank=True)
    templatemap_build_type = models.IntegerField(null=True, blank=True)
    templatemap_file_template = models.CharField(max_length=765, blank=True)
    templatemap_is_preferred = models.IntegerField(null=True, blank=True)
    templatemap_template_id = models.IntegerField()
    class Meta:
        db_table = u'mt_templatemap'

class MtTheme(models.Model):
    theme_id = models.IntegerField(primary_key=True)
    theme_plugin_sig = models.CharField(max_length=765, blank=True)
    theme_theme_meta = models.TextField(blank=True)
    theme_ts_id = models.CharField(max_length=765, blank=True)
    theme_ts_label = models.CharField(max_length=765, blank=True)
    class Meta:
        db_table = u'mt_theme'

class MtTouch(models.Model):
    touch_id = models.IntegerField(primary_key=True)
    touch_blog_id = models.IntegerField(null=True, blank=True)
    touch_modified_on = models.DateTimeField(null=True, blank=True)
    touch_object_type = models.CharField(max_length=765, blank=True)
    class Meta:
        db_table = u'mt_touch'

class MtTrackback(models.Model):
    trackback_id = models.IntegerField(primary_key=True)
    trackback_blog_id = models.IntegerField()
    trackback_category_id = models.IntegerField()
    trackback_created_by = models.IntegerField(null=True, blank=True)
    trackback_created_on = models.DateTimeField(null=True, blank=True)
    trackback_description = models.TextField(blank=True)
    trackback_entry_id = models.IntegerField()
    trackback_is_disabled = models.IntegerField(null=True, blank=True)
    trackback_modified_by = models.IntegerField(null=True, blank=True)
    trackback_modified_on = models.DateTimeField(null=True, blank=True)
    trackback_passphrase = models.CharField(max_length=90, blank=True)
    trackback_rss_file = models.CharField(max_length=765, blank=True)
    trackback_title = models.CharField(max_length=765, blank=True)
    trackback_url = models.CharField(max_length=765, blank=True)
    class Meta:
        db_table = u'mt_trackback'

class MtTsError(models.Model):
    ts_error_error_time = models.IntegerField(primary_key=True)
    ts_error_funcid = models.IntegerField()
    ts_error_jobid = models.IntegerField()
    ts_error_message = models.CharField(max_length=765)
    class Meta:
        db_table = u'mt_ts_error'

class MtTsExitstatus(models.Model):
    ts_exitstatus_jobid = models.IntegerField(primary_key=True)
    ts_exitstatus_completion_time = models.IntegerField(null=True, blank=True)
    ts_exitstatus_delete_after = models.IntegerField(null=True, blank=True)
    ts_exitstatus_funcid = models.IntegerField()
    ts_exitstatus_status = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'mt_ts_exitstatus'

class MtTsFuncmap(models.Model):
    ts_funcmap_funcid = models.IntegerField(primary_key=True)
    ts_funcmap_funcname = models.CharField(max_length=765)
    class Meta:
        db_table = u'mt_ts_funcmap'

class MtTsJob(models.Model):
    ts_job_jobid = models.IntegerField(primary_key=True)
    ts_job_arg = models.TextField(blank=True)
    ts_job_coalesce = models.CharField(max_length=765, blank=True)
    ts_job_funcid = models.IntegerField()
    ts_job_grabbed_until = models.IntegerField()
    ts_job_insert_time = models.IntegerField(null=True, blank=True)
    ts_job_priority = models.IntegerField(null=True, blank=True)
    ts_job_run_after = models.IntegerField()
    ts_job_uniqkey = models.CharField(max_length=765, blank=True)
    class Meta:
        db_table = u'mt_ts_job'

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

