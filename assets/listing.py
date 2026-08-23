import os

from PIL import Image, UnidentifiedImageError

DEFAULT_REL = 'called'
THUMB_SIZE = 200
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
SCALABLE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}


class ListingError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def assets_root(public_path):
    return os.path.abspath(os.path.join(public_path, 'assets'))


def normalize_rel(rel):
    rel = (rel or '').replace('\\', '/').strip('/')
    if rel in ('.',):
        return ''
    return rel


def resolve(assets_dir, rel):
    assets_dir = os.path.abspath(assets_dir)
    rel = normalize_rel(rel)
    candidate = os.path.abspath(os.path.join(assets_dir, rel)) if rel else assets_dir
    if candidate != assets_dir and not candidate.startswith(assets_dir + os.sep):
        raise ListingError('path is outside assets', 400)
    rel_out = '' if candidate == assets_dir else os.path.relpath(candidate, assets_dir)
    rel_out = normalize_rel(rel_out.replace(os.sep, '/'))
    parts = [part for part in rel_out.split('/') if part]
    if any(part == 'scaled' or part.startswith('.') for part in parts):
        raise ListingError('path is not browsable', 404)
    if not os.path.isdir(candidate):
        raise ListingError('not a directory', 404)
    return candidate, rel_out


def parent_rel(rel):
    rel = normalize_rel(rel)
    if not rel:
        return None
    parent = normalize_rel(os.path.dirname(rel))
    return parent


def is_image_name(name):
    return os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS


def image_size(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == '.svg':
        return None, None
    try:
        with Image.open(path) as image:
            return image.width, image.height
    except (UnidentifiedImageError, OSError, ValueError):
        return None, None


def public_url(rel):
    return '/and/assets/' + rel


def thumb_url(rel):
    ext = os.path.splitext(rel)[1].lower()
    if rel.startswith('called/') and ext in SCALABLE_EXTENSIONS:
        return '/and/assets/scaled/to/%s/%s' % (THUMB_SIZE, rel[len('called/'):])
    return public_url(rel)


def list_directory(assets_dir, rel=DEFAULT_REL, query=''):
    directory, rel = resolve(assets_dir, rel)
    needle = (query or '').strip().lower()
    folders = []
    files = []
    try:
        names = os.listdir(directory)
    except OSError as error:
        raise ListingError(str(error), 404) from error

    for name in names:
        if name.startswith('.') or name == 'scaled':
            continue
        if needle and needle not in name.lower():
            continue
        full = os.path.join(directory, name)
        child = name if not rel else '%s/%s' % (rel, name)
        if os.path.isdir(full):
            folders.append({
                'name': name,
                'type': 'dir',
                'path': child,
            })
            continue
        if not os.path.isfile(full):
            continue
        kind = 'image' if is_image_name(name) else 'file'
        width = height = None
        if kind == 'image':
            width, height = image_size(full)
        files.append({
            'name': name,
            'type': 'file',
            'kind': kind,
            'path': child,
            'url': public_url(child),
            'thumb': thumb_url(child) if kind == 'image' else None,
            'bytes': os.path.getsize(full),
            'width': width,
            'height': height,
        })

    folders.sort(key=lambda item: item['name'].lower())
    files.sort(key=lambda item: item['name'].lower())
    return {
        'path': rel,
        'parent': parent_rel(rel),
        'entries': folders + files,
    }
