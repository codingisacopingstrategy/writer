import json
from unittest.mock import patch

from django.contrib.auth.models import Permission, User
from django.test import TestCase

from write.auth import can_delete_entry, can_publish
from write.models import MtEntry


def grant(user, *codenames):
    for codename in codenames:
        user.user_permissions.add(Permission.objects.get(codename=codename))


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
        mock_commit.assert_called_once_with()
        mock_all.assert_not_called()

    @patch('write.publish.regenerate_published_site')
    @patch('write.models.MtEntry.commit', return_value=b'cid')
    def test_update_all_regenerates_the_site(self, mock_commit, mock_all):
        response = self.post_publish(self.owner, update_all=True)
        self.assertEqual(response.status_code, 200)
        mock_all.assert_called_once_with()
        mock_commit.assert_called_once_with()
