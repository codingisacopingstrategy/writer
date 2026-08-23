import json
import os
import tempfile
from unittest import TestCase as PlainTestCase

from django.contrib.auth.models import Permission, User
from django.test import TestCase

from assets.listing import ListingError, list_directory, resolve, thumb_url


class ResolveTests(PlainTestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.root, 'called'))
        os.makedirs(os.path.join(self.root, 'scaled', 'to', '200'))
        os.makedirs(os.path.join(self.root, 'that', 'are'))

    def test_default_called_exists(self):
        path, rel = resolve(self.root, 'called')
        self.assertEqual(rel, 'called')
        self.assertTrue(path.endswith('called'))

    def test_rejects_escape(self):
        with self.assertRaises(ListingError):
            resolve(self.root, '../')

    def test_rejects_scaled(self):
        with self.assertRaises(ListingError):
            resolve(self.root, 'scaled')
        with self.assertRaises(ListingError):
            resolve(self.root, 'scaled/to/200')


class ListDirectoryTests(PlainTestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.root, 'called', 'nested'))
        os.makedirs(os.path.join(self.root, 'that'))
        os.makedirs(os.path.join(self.root, 'scaled', 'to', '200'))
        with open(os.path.join(self.root, 'called', 'readme.txt'), 'w') as handle:
            handle.write('x')
        with open(os.path.join(self.root, 'called', 'zebra.txt'), 'w') as handle:
            handle.write('z')
        with open(os.path.join(self.root, 'called', '.hidden'), 'w') as handle:
            handle.write('no')

    def test_folders_first_then_files(self):
        payload = list_directory(self.root, 'called')
        types = [item['type'] for item in payload['entries']]
        self.assertEqual(types, ['dir', 'file', 'file'])
        self.assertEqual(payload['entries'][0]['name'], 'nested')
        self.assertEqual(payload['parent'], '')

    def test_skips_scaled_and_dotfiles(self):
        payload = list_directory(self.root, '')
        names = [item['name'] for item in payload['entries']]
        self.assertEqual(names, ['called', 'that'])

    def test_filter_is_substring_on_current_dir(self):
        payload = list_directory(self.root, 'called', query='ZEB')
        self.assertEqual([item['name'] for item in payload['entries']], ['zebra.txt'])

    def test_png_reports_width_and_height(self):
        from PIL import Image
        image_path = os.path.join(self.root, 'called', 'dot.png')
        Image.new('RGB', (12, 8), (0, 0, 0)).save(image_path)
        payload = list_directory(self.root, 'called')
        dots = [item for item in payload['entries'] if item['name'] == 'dot.png']
        self.assertEqual(len(dots), 1)
        self.assertEqual(dots[0]['kind'], 'image')
        self.assertEqual(dots[0]['width'], 12)
        self.assertEqual(dots[0]['height'], 8)
        self.assertEqual(dots[0]['url'], '/and/assets/called/dot.png')
        self.assertEqual(dots[0]['thumb'], '/and/assets/scaled/to/200/dot.png')

    def test_called_image_thumb_uses_scaler(self):
        self.assertEqual(
            thumb_url('called/bowie.jpg'),
            '/and/assets/scaled/to/200/bowie.jpg',
        )
        self.assertEqual(
            thumb_url('that/are/glit.png'),
            '/and/assets/that/are/glit.png',
        )


class BrowseViewTests(TestCase):
    def setUp(self):
        self.editor = User.objects.create_user('robot', password='x')
        self.editor.user_permissions.add(
            Permission.objects.get(codename='change_mtentry')
        )
        self.stranger = User.objects.create_user('commenter', password='x')

    def test_anonymous_gets_401(self):
        response = self.client.get('/or/assets/')
        self.assertEqual(response.status_code, 401)

    def test_logged_in_without_change_gets_403(self):
        self.client.force_login(self.stranger)
        response = self.client.get('/or/assets/')
        self.assertEqual(response.status_code, 403)

    def test_editor_can_list_called(self):
        self.client.force_login(self.editor)
        response = self.client.get('/or/assets/')
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertEqual(payload['path'], 'called')
        self.assertIn('entries', payload)
        self.assertEqual(payload['parent'], '')
