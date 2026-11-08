import json
import os
import tempfile
from datetime import datetime
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import Permission, User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone
from PIL import Image

from write.auth import can_delete_entry, can_publish
from write.forms import CommentForm
from write.models import MtComment, MtEntry, git_identity, page_commit_message, staged_page_changed
from write.publish import AUTHOR_SLUGS, generated_output_paths, write_site_indexes
from write.sanitize import sanitize_comment_html
from write.screenshots import screenshot_entry, screenshot_path


def grant(user, *codenames):
    for codename in codenames:
        user.user_permissions.add(Permission.objects.get(codename=codename))


class StagedPageTests(TestCase):
    def test_new_html_counts_as_a_change(self):
        changes = {
            'add': [b'smartphones-never-die.html'],
            'modify': [],
            'delete': [],
        }
        self.assertTrue(staged_page_changed('smartphones-never-die.html', changes))

    def test_edited_html_counts_as_a_change(self):
        changes = {'add': [], 'modify': [b'hello.html'], 'delete': []}
        self.assertTrue(staged_page_changed('hello.html', changes))

    def test_unchanged_html_does_not(self):
        changes = {'add': [], 'modify': [], 'delete': []}
        self.assertFalse(staged_page_changed('hello.html', changes))

    def test_str_paths_from_newer_dulwich_still_match(self):
        changes = {'add': ['new.html'], 'modify': [], 'delete': []}
        self.assertTrue(staged_page_changed('new.html', changes))


class GitIdentityTests(TestCase):
    def test_bytes_do_not_leak_repr_into_the_identity(self):
        self.assertEqual(
            git_identity(b'bnf', b'eric@ericschrijver.nl'),
            'bnf <eric@ericschrijver.nl>',
        )

    def test_text_stays_text(self):
        self.assertEqual(
            git_identity('bnf', 'eric@ericschrijver.nl'),
            'bnf <eric@ericschrijver.nl>',
        )


class PageCommitMessageTests(TestCase):
    def test_first_publish_says_publish(self):
        self.assertEqual(
            page_commit_message(True, 'I like tight pants and draft'),
            'Publish: I like tight pants and draft',
        )

    def test_later_save_says_update(self):
        self.assertEqual(
            page_commit_message(False, 'I like tight pants and draft'),
            'Update: I like tight pants and draft',
        )


class PublishRightsTests(TestCase):
    def test_permissions_not_superuser_alone(self):
        owner = User.objects.create_superuser('eric', 'eric@example.com', 'x')
        assist = User.objects.create_user('assist')
        self.assertTrue(can_publish(owner))
        self.assertTrue(can_delete_entry(owner))
        self.assertFalse(can_publish(assist))
        self.assertFalse(can_delete_entry(assist))
        self.assertFalse(can_publish(None))

    def test_explicit_publish_and_delete_perms(self):
        editor = User.objects.create_user('editor')
        grant(editor, 'change_mtentry', 'publish_mtentry')
        editor = User.objects.get(pk=editor.pk)
        self.assertTrue(can_publish(editor))
        self.assertFalse(can_delete_entry(editor))
        grant(editor, 'delete_mtentry')
        editor = User.objects.get(pk=editor.pk)
        self.assertTrue(can_delete_entry(editor))


class EntryApiAuthTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser('eric', 'eric@example.com', 'secret')
        self.assist = User.objects.create_user('assist', 'assist@example.com', 'secret')
        grant(self.assist, 'add_mtentry', 'change_mtentry', 'add_mtcomment', 'change_mtcomment')
        self.draft = MtEntry.objects.create(
            author=self.owner,
            title='Draft',
            slug='draft',
            body='<p>hi</p>',
            published=False,
        )
        self.live = MtEntry.objects.create(
            author=self.owner,
            title='Live',
            slug='live',
            body='<p>hi</p>',
            published=True,
        )

    def api(self, method, path, user=None, payload=None):
        if user is not None:
            self.client.force_login(user)
        else:
            self.client.logout()
        extra = {'content_type': 'application/json'}
        body = json.dumps(payload) if payload is not None else None
        return getattr(self.client, method)(path, data=body, **extra)

    def test_anonymous_is_rejected(self):
        response = self.api('get', '/api/entry/%s/' % self.draft.pk)
        self.assertEqual(response.status_code, 401)

    def test_assistant_cannot_publish_a_draft(self):
        response = self.api(
            'patch',
            '/api/entry/%s/' % self.draft.pk,
            user=self.assist,
            payload={'title': 'Draft', 'published': True},
        )
        self.assertEqual(response.status_code, 202)
        self.draft.refresh_from_db()
        self.assertFalse(self.draft.published)
        self.assertEqual(self.draft.title, 'Draft')

    def test_assistant_save_does_not_unpublish(self):
        response = self.api(
            'patch',
            '/api/entry/%s/' % self.live.pk,
            user=self.assist,
            payload={'title': 'Still live', 'published': False},
        )
        self.assertEqual(response.status_code, 202)
        self.live.refresh_from_db()
        self.assertTrue(self.live.published)
        self.assertEqual(self.live.title, 'Still live')

    def test_superuser_can_publish(self):
        response = self.api(
            'patch',
            '/api/entry/%s/' % self.draft.pk,
            user=self.owner,
            payload={'published': True},
        )
        self.assertEqual(response.status_code, 202)
        self.draft.refresh_from_db()
        self.assertTrue(self.draft.published)

    def test_assistant_cannot_delete_an_article(self):
        response = self.api(
            'delete',
            '/api/entry/%s/' % self.draft.pk,
            user=self.assist,
        )
        self.assertEqual(response.status_code, 401)
        self.assertTrue(MtEntry.objects.filter(pk=self.draft.pk).exists())

    def test_superuser_can_delete_an_article(self):
        response = self.api(
            'delete',
            '/api/entry/%s/' % self.draft.pk,
            user=self.owner,
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(MtEntry.objects.filter(pk=self.draft.pk).exists())

    def test_change_without_add_cannot_create(self):
        only_change = User.objects.create_user('changer')
        grant(only_change, 'change_mtentry')
        response = self.api(
            'post',
            '/api/entry/',
            user=only_change,
            payload={
                'author': self.owner.pk,
                'title': 'Nope',
                'slug': 'nope',
                'body': '<p>x</p>',
            },
        )
        self.assertEqual(response.status_code, 401)
        self.assertFalse(MtEntry.objects.filter(slug='nope').exists())

    def test_publish_perm_can_publish(self):
        publisher = User.objects.create_user('publisher')
        grant(publisher, 'change_mtentry', 'publish_mtentry')
        response = self.api(
            'patch',
            '/api/entry/%s/' % self.draft.pk,
            user=publisher,
            payload={'published': True},
        )
        self.assertEqual(response.status_code, 202)
        self.draft.refresh_from_db()
        self.assertTrue(self.draft.published)

    def test_delete_perm_can_delete(self):
        deleter = User.objects.create_user('deleter')
        grant(deleter, 'change_mtentry', 'delete_mtentry')
        response = self.api(
            'delete',
            '/api/entry/%s/' % self.draft.pk,
            user=deleter,
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(MtEntry.objects.filter(pk=self.draft.pk).exists())

    def test_assistant_create_stays_unpublished(self):
        response = self.api(
            'post',
            '/api/entry/',
            user=self.assist,
            payload={
                'author': self.owner.pk,
                'title': 'New',
                'slug': 'new-one',
                'body': '<p>x</p>',
                'published': True,
            },
        )
        self.assertEqual(response.status_code, 201)
        created = MtEntry.objects.get(slug='new-one')
        self.assertFalse(created.published)

    def test_entry_head_includes_custom_css(self):
        entry = MtEntry.objects.create(
            author=self.owner,
            title='Styled',
            slug='styled',
            body='<p>hi</p>',
            published=True,
            custom_css='article .as-page { color: #0058ed; }',
        )
        response = self.client.get('/is/%s' % entry.slug)
        self.assertContains(response, 'id="entry-custom-css"', html=False)
        self.assertContains(response, 'article .as-page { color: #0058ed; }')

    def test_can_change_entry_created_on(self):
        response = self.api(
            'patch',
            '/api/entry/%s/' % self.draft.pk,
            user=self.owner,
            payload={'created_on': '2012-10-12T22:00:00'},
        )
        self.assertEqual(response.status_code, 202)
        self.draft.refresh_from_db()
        self.assertEqual(
            timezone.localtime(self.draft.created_on).strftime('%Y-%m-%dT%H:%M:%S'),
            '2012-10-12T22:00:00',
        )

    def test_can_change_comment_created_on(self):
        comment = MtComment.objects.create(
            entry=self.draft,
            author='bnf',
            mt_author=self.owner,
            text='<p>hi</p>',
            visible=True,
        )
        response = self.api(
            'patch',
            '/api/comment/%s/' % comment.pk,
            user=self.owner,
            payload={'created_on': '2014-02-01T21:20:20'},
        )
        self.assertEqual(response.status_code, 202)
        comment.refresh_from_db()
        self.assertEqual(
            timezone.localtime(comment.created_on).strftime('%Y-%m-%dT%H:%M:%S'),
            '2014-02-01T21:20:20',
        )

    def test_entry_head_omits_empty_custom_css(self):
        entry = MtEntry.objects.create(
            author=self.owner,
            title='Plain',
            slug='plain',
            body='<p>hi</p>',
            published=True,
        )
        response = self.client.get('/is/%s' % entry.slug)
        self.assertNotContains(response, 'id="entry-custom-css"')

    def test_read_reply_wires_parent_and_comment_form(self):
        comment = MtComment.objects.create(
            entry=self.live,
            author="O'Brien",
            text='<p>hi</p>',
            visible=True,
        )
        response = self.client.get('/is/%s' % self.live.slug)
        self.assertContains(response, '/and/scripts/being/script.js')
        self.assertContains(response, 'id="id_parent"', html=False)
        self.assertContains(response, 'id="id_text"', html=False)
        self.assertContains(response, 'id="reply"', html=False)
        self.assertContains(
            response,
            "mtReplyCommentOnClick(%s, '%s')" % (comment.pk, "O\\u0027Brien"),
            html=False,
        )

    def test_roxanne_editor_loads_logged_in_statics(self):
        self.client.force_login(self.owner)
        response = self.client.get('/or/%s' % self.live.slug)
        self.assertContains(response, '/and/logged/in/roxanne/squire/squire-raw.js')
        self.assertContains(response, '/and/logged/in/roxanne/js/edit-entry-roxanne.js')
        self.assertNotContains(response, '/and/js/edit-entry-roxanne.js')
        self.assertNotContains(response, '/and/squire/squire-raw.js')
        self.assertNotContains(response, 'id="comments-open"', html=False)
        self.assertContains(response, 'mt:entry_author_id', html=False)

    def test_old_editor_loads_logged_in_statics(self):
        old = MtEntry.objects.create(
            author=self.owner,
            title='Old',
            slug='old-style',
            body='<p>hi</p>',
            published=True,
        )
        old.created_on = timezone.make_aware(datetime(2012, 10, 12, 22, 0, 0))
        old.save(update_fields=['created_on'])
        self.client.force_login(self.owner)
        response = self.client.get('/or/%s' % old.slug)
        self.assertContains(response, '/and/logged/in/2011/aloha/lib/aloha.js')
        self.assertContains(response, '/and/logged/in/2011/js/edit-entry.js')
        self.assertNotContains(response, '{{ STATIC_URL }}aloha/lib/aloha.js')
        self.assertNotContains(response, 'src="/and/aloha/lib/aloha.js"')

    def old_entry(self, published):
        old = MtEntry.objects.create(
            author=self.owner,
            title='Old',
            slug='old-style',
            body='<p>hi</p>',
            published=published,
        )
        old.created_on = timezone.make_aware(datetime(2012, 10, 12, 22, 0, 0))
        old.save(update_fields=['created_on'])
        return old

    def test_old_editor_offers_publish_on_a_draft(self):
        old = self.old_entry(published=False)
        self.client.force_login(self.owner)
        response = self.client.get('/or/%s' % old.slug)
        self.assertContains(response, 'id="publish-entry">Publish</button>')
        self.assertContains(response, 'id="publish-all"')

    def test_old_editor_offers_save_modifications_on_a_live_entry(self):
        old = self.old_entry(published=True)
        self.client.force_login(self.owner)
        response = self.client.get('/or/%s' % old.slug)
        self.assertContains(response, 'id="publish-entry">Save Modifications</button>')

    def test_old_editor_hides_publish_without_the_permission(self):
        old = self.old_entry(published=False)
        self.client.force_login(self.assist)
        response = self.client.get('/or/%s' % old.slug)
        self.assertNotContains(response, 'id="publish-entry"')
        self.assertNotContains(response, 'id="publish-all"')

    def test_read_comment_form_loads_squire(self):
        response = self.client.get('/is/%s' % self.live.slug)
        self.assertContains(response, '/and/logged/in/roxanne/squire/squire-raw.js')
        self.assertContains(response, '/and/logged/in/roxanne/js/squire-toolbar.js')
        self.assertContains(response, '/and/scripts/being/comment-squire.js')
        self.assertContains(response, 'id="comment-squire"', html=False)
        self.assertContains(response, 'data-action="html"', html=False)


class CommentSanitizeTests(TestCase):
    def test_keeps_the_tags_the_form_advertises(self):
        html = (
            '<p>Hello <strong>there</strong> <em>world</em> '
            '<a href="https://example.com" title="ex">link</a></p>'
            '<ul><li>one</li></ul><blockquote>q</blockquote>'
        )
        self.assertEqual(sanitize_comment_html(html), html)

    def test_strips_script_and_event_handlers(self):
        html = (
            '<p onclick="alert(1)">hi<script>alert(2)</script></p>'
            '<a href="javascript:alert(3)">x</a>'
        )
        self.assertEqual(sanitize_comment_html(html), '<p>hi</p><a>x</a>')

    def test_form_stores_cleaned_html(self):
        entry = MtEntry.objects.create(
            author=User.objects.create_user('eric', 'eric@example.com', 'x'),
            title='Live',
            slug='live-comment',
            body='<p>hi</p>',
            published=True,
        )
        form = CommentForm({
            'author': 'Ada',
            'email': 'ada@example.com',
            'text': '<p>ok<script>bad()</script></p>',
            'entry': entry.pk,
            'captcha_code': 'brussels',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['text'], '<p>ok</p>')

    def test_form_rejects_empty_html_after_stripping(self):
        entry = MtEntry.objects.create(
            author=User.objects.create_user('eric', 'eric@example.com', 'x'),
            title='Live',
            slug='live-empty',
            body='<p>hi</p>',
            published=True,
        )
        form = CommentForm({
            'author': 'Ada',
            'email': 'ada@example.com',
            'text': '<script>alert(1)</script>',
            'entry': entry.pk,
            'captcha_code': 'brussels',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)


class EntryPublishActionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser('eric', 'eric@example.com', 'secret')
        self.assist = User.objects.create_user('assist', 'assist@example.com', 'secret')
        grant(self.assist, 'add_mtentry', 'change_mtentry')
        self.draft = MtEntry.objects.create(
            author=self.owner,
            title='Draft',
            slug='draft',
            body='<p>hi</p>',
            published=False,
        )

    def post_publish(self, user, update_all=False):
        if user is not None:
            self.client.force_login(user)
        else:
            self.client.logout()
        return self.client.post(
            '/api/entry/%s/publish/' % self.draft.pk,
            data=json.dumps({'update_all': update_all}),
            content_type='application/json',
        )

    def test_anonymous_cannot_publish(self):
        response = self.post_publish(None)
        self.assertEqual(response.status_code, 401)
        self.draft.refresh_from_db()
        self.assertFalse(self.draft.published)

    def test_assistant_cannot_publish(self):
        response = self.post_publish(self.assist)
        self.assertEqual(response.status_code, 401)
        self.draft.refresh_from_db()
        self.assertFalse(self.draft.published)

    @patch('write.publish.regenerate_published_site')
    @patch('write.models.MtEntry.commit', return_value=b'cid')
    def test_publisher_commits_this_entry(self, mock_commit, mock_all):
        publisher = User.objects.create_user('publisher')
        grant(publisher, 'change_mtentry', 'publish_mtentry')
        response = self.post_publish(publisher)
        self.assertEqual(response.status_code, 200)
        self.draft.refresh_from_db()
        self.assertTrue(self.draft.published)
        mock_commit.assert_called_once()
        self.assertEqual(
            mock_commit.call_args.kwargs['message'],
            'Publish: I like tight pants and draft',
        )
        mock_all.assert_not_called()

    @patch('write.publish.commit_repo_paths', return_value=b'cid')
    @patch('write.publish.regenerate_published_site')
    def test_update_all_commits_the_whole_site(self, mock_all, mock_commit_all):
        response = self.post_publish(self.owner, update_all=True)
        self.assertEqual(response.status_code, 200)
        mock_all.assert_called_once_with()
        mock_commit_all.assert_called_once()
        self.assertGreater(len(mock_commit_all.call_args[0][0]), 1)
        self.assertEqual(
            mock_commit_all.call_args.kwargs['message'],
            'Publish: I like tight pants and draft',
        )

    @patch('write.publish.commit_repo_paths', return_value=b'cid')
    @patch('write.publish.regenerate_published_site')
    def test_later_update_all_uses_update_message(self, mock_all, mock_commit_all):
        self.draft.published = True
        self.draft.save()
        response = self.post_publish(self.owner, update_all=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            mock_commit_all.call_args.kwargs['message'],
            'Update: I like tight pants and draft',
        )


class LatestEntryTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user('glit')
        self.make_entry('older', True, datetime(2026, 4, 1))
        self.make_entry('newer', True, datetime(2026, 6, 1))
        self.make_entry('newest-draft', False, datetime(2026, 7, 1))

    def make_entry(self, slug, published, created_on):
        entry = MtEntry.objects.create(
            author=self.author,
            title=slug,
            slug=slug,
            body='<p>hi</p>',
            published=published,
        )
        # created_on is auto_now_add, so it can only be set after creating
        MtEntry.objects.filter(pk=entry.pk).update(created_on=timezone.make_aware(created_on))

    def test_and_redirects_to_the_latest_published_entry(self):
        response = self.client.get('/and/')
        self.assertRedirects(response, '/and/newer', fetch_redirect_response=False)

    def test_latest_txt_is_the_slug_and_a_newline(self):
        response = self.client.get('/is/latest.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'newer\n')
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')

    def test_publish_writes_latest_txt_and_not_index_php(self):
        for username in AUTHOR_SLUGS:
            User.objects.get_or_create(username=username)
        with tempfile.TemporaryDirectory() as output, patch('write.publish.OUTPUT_DIR', output):
            write_site_indexes()
            with open(os.path.join(output, 'latest.txt'), 'rb') as handle:
                self.assertEqual(handle.read(), b'newer\n')
            self.assertFalse(os.path.exists(os.path.join(output, 'index.php')))

    def test_update_all_commits_latest_txt_and_not_index_php(self):
        with patch('write.publish.OUTPUT_DIR', '/output'):
            paths = generated_output_paths()
        self.assertIn('/output/latest.txt', paths)
        self.assertNotIn('/output/index.php', paths)

    def test_publish_writes_about_html_with_working_links(self):
        for username in AUTHOR_SLUGS:
            User.objects.get_or_create(username=username)
        with tempfile.TemporaryDirectory() as output, patch('write.publish.OUTPUT_DIR', output):
            write_site_indexes()
            with open(os.path.join(output, 'about.html'), encoding='utf-8') as handle:
                html = handle.read()
        self.assertIn('<a href="/and/newer">latest</a>', html)
        self.assertIn('<a href="/and/archives">index</a>', html)
        self.assertIn('<li>and reading ‘about’ pages</li>', html)

    def test_update_all_commits_about_html(self):
        with patch('write.publish.OUTPUT_DIR', '/output'):
            self.assertIn('/output/about.html', generated_output_paths())


class LinksJsonTests(TestCase):
    def test_lists_only_published_entries(self):
        author = User.objects.create_user('glit')
        for slug, published in (('live-post', True), ('some-draft', False)):
            MtEntry.objects.create(
                author=author,
                title=slug.replace('-', ' ').title(),
                slug=slug,
                body='<p>hi</p>',
                published=published,
            )
        response = self.client.get('/or/links.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json; charset=utf-8')
        self.assertEqual(json.loads(response.content), [{
            'link': '/and/live-post',
            'id': '/and/live-post',
            'name': 'I like tight pants and live post',
            'type': 'website',
        }])


class PublishCommandTests(TestCase):
    def setUp(self):
        author = User.objects.create_user('glit')
        for slug, published in (('live', True), ('draft', False)):
            MtEntry.objects.create(
                author=author,
                title=slug.title(),
                slug=slug,
                body='<p>hi</p>',
                published=published,
            )

    @patch('write.management.commands.publish.regenerate_published_site')
    def test_slug_writes_only_that_post(self, mock_all):
        with tempfile.TemporaryDirectory() as output, patch('write.publish.OUTPUT_DIR', output):
            call_command('publish', 'live', stdout=StringIO())
            self.assertEqual(os.listdir(output), ['live.html'])
        mock_all.assert_not_called()

    def test_draft_and_unknown_slugs_are_refused(self):
        for slug in ('draft', 'no-such-post'):
            with self.subTest(slug=slug):
                with tempfile.TemporaryDirectory() as output, patch('write.publish.OUTPUT_DIR', output):
                    with self.assertRaises(CommandError):
                        call_command('publish', slug)
                    self.assertEqual(os.listdir(output), [])

    @patch('write.management.commands.publish.regenerate_published_site')
    def test_no_slug_regenerates_the_site(self, mock_all):
        call_command('publish')
        mock_all.assert_called_once_with()


class EntryScreenshotTests(TestCase):
    def setUp(self):
        self.editor = User.objects.create_user('editor')
        grant(self.editor, 'change_mtentry', 'publish_mtentry')
        self.assist = User.objects.create_user('assist')
        grant(self.assist, 'change_mtentry')
        self.stranger = User.objects.create_user('stranger')
        self.live = MtEntry.objects.create(
            author=self.editor,
            title='Live',
            slug='live',
            body='<p>hi</p>',
            published=True,
        )
        old = MtEntry.objects.create(
            author=self.editor,
            title='Old',
            slug='old-style',
            body='<p>hi</p>',
            published=True,
        )
        old.created_on = timezone.make_aware(datetime(2012, 10, 12, 22, 0, 0))
        old.save(update_fields=['created_on'])

    def request_screenshot(self, user, method='post'):
        if user is not None:
            self.client.force_login(user)
        else:
            self.client.logout()
        return getattr(self.client, method)('/api/entry/%s/screenshot/' % self.live.pk)

    @patch('write.api.screenshot_entry')
    def test_editor_takes_a_screenshot_of_the_entry(self, mock_shot):
        response = self.request_screenshot(self.editor)
        self.assertEqual(response.status_code, 200)
        mock_shot.assert_called_once_with(self.live)
        self.assertEqual(
            json.loads(response.content),
            {'screenshot_url': '/and/assets/as/screenshots/of/live.png'},
        )

    @patch('write.screenshots.commit_repo_paths', return_value=b'cid')
    @patch('write.screenshots.screenshot')
    def test_the_new_screenshot_is_committed_as_the_author(self, mock_shot, mock_commit):
        self.live.author.email = 'editor@example.com'
        self.live.author.save()
        screenshot_entry(self.live)
        mock_shot.assert_called_once_with(['live'])
        mock_commit.assert_called_once_with(
            [screenshot_path('live')],
            message='Screenshot: I like tight pants and live',
            name='editor',
            email='editor@example.com',
        )
        self.assertTrue(screenshot_path('live').endswith('/assets/as/screenshots/of/live.png'))

    @patch('write.api.screenshot_entry')
    def test_anonymous_and_users_without_publish_rights_are_refused(self, mock_shot):
        for user in (None, self.stranger, self.assist):
            with self.subTest(user=user):
                self.assertEqual(self.request_screenshot(user).status_code, 401)
        mock_shot.assert_not_called()

    @patch('write.api.screenshot_entry')
    def test_only_post_is_allowed(self, mock_shot):
        self.assertEqual(self.request_screenshot(self.editor, method='get').status_code, 405)
        mock_shot.assert_not_called()

    @patch('write.api.screenshot_entry', side_effect=RuntimeError('no browser'))
    def test_a_failed_screenshot_is_an_error_response(self, mock_shot):
        # Tastypie answers with a 500 but also signals the exception, which the test client re-raises
        self.client.raise_request_exception = False
        self.assertEqual(self.request_screenshot(self.editor).status_code, 500)

    def test_both_editors_show_the_button_to_editors(self):
        self.client.force_login(self.editor)
        for slug in ('live', 'old-style'):
            with self.subTest(slug=slug):
                response = self.client.get('/or/%s' % slug)
                self.assertContains(response, 'id="screenshot-entry"')

    def test_both_editors_hide_the_button_without_publish_rights(self):
        for user in (self.stranger, self.assist):
            self.client.force_login(user)
            for slug in ('live', 'old-style'):
                with self.subTest(user=user, slug=slug):
                    response = self.client.get('/or/%s' % slug)
                    self.assertNotContains(response, 'id="screenshot-entry"')


class ArchivesScreenshotSizeTests(TestCase):
    def setUp(self):
        author = User.objects.create_user('editor')
        for slug in ('with-screenshot', 'without-screenshot'):
            MtEntry.objects.create(author=author, title=slug, slug=slug, body='<p>hi</p>', published=True)
        self.shots = tempfile.TemporaryDirectory()
        self.addCleanup(self.shots.cleanup)
        Image.new('RGB', (1190, 3000)).save(os.path.join(self.shots.name, 'with-screenshot.png'))
        patcher = patch('write.models.screenshot_path', lambda slug: os.path.join(self.shots.name, '%s.png' % slug))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_screenshot_size_reads_the_png(self):
        self.assertEqual(MtEntry.objects.get(slug='with-screenshot').screenshot_size(), (1190, 3000))
        self.assertIsNone(MtEntry.objects.get(slug='without-screenshot').screenshot_size())

    def test_archives_give_each_screenshot_its_size(self):
        response = self.client.get('/is/archives')
        self.assertContains(
            response,
            '<img src="/and/assets/as/screenshots/of/with-screenshot.png" width="1190" height="3000" style="width:200px;height:auto;"',
        )
        self.assertContains(
            response,
            '<img src="/and/assets/as/screenshots/of/without-screenshot.png" style="width:200px;height:auto;"',
        )
