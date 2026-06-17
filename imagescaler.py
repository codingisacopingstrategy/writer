from django.core.exceptions import PermissionDenied
from django.http import Http404, FileResponse
from PIL import Image

from write.local_settings import PUBLIC_PATH
import os


def scale_image(request, size, path):
    """
    Images under /and/assets/scaled/to/720/whatever.png
    Are scaled versions of /and/assets/called/whatever.png
    And are served by nginx, but if nginx doesn’t find it, it will delegate to this view.
    Which will save the resized file to disk so nginx can serve it next time.
    """
    root = os.path.abspath(
        os.path.join(PUBLIC_PATH, 'assets', 'called')
    )
    src_image_path = os.path.abspath(
        os.path.join(PUBLIC_PATH, 'assets', 'called', os.path.normpath(path))
    )

    # Only allow images under /and/assets/called/*
    if not src_image_path.startswith(root + os.sep):
        raise Http404

    # Then see if it actually exists
    try:
        image = Image.open(src_image_path, formats=['JPEG', 'PNG'])
    except FileNotFoundError:
        raise Http404
    except ValueError:  # and if it’s the right format
        raise PermissionDenied

    dest_image_path = os.path.join(PUBLIC_PATH, 'assets', 'scaled', 'to', '%s' % size, os.path.normpath(path))
    dest_image_folder = os.path.split(dest_image_path)[0]
    fmt = image.format

    # JPEGS sometimes identify like this
    if fmt in {"MPO", "JPEG"}:
        fmt = "JPEG"

    # the actual resize operation. Whatever width or height is largest becomes the max
    # Aspect ratio stays the same
    image.thumbnail((size, size))

    # create the /scaled/to/INTEGER folder if it does not exist
    os.makedirs(dest_image_folder, exist_ok=True)

    # save the file
    if fmt == 'JPEG':
        image.save(
            dest_image_path,
            format=fmt,
            quality=90,  # 1-95. 85 is good balance. 95 is near-lossless.
            progressive=True,  # Progressive JPEG for web
            optimize=True,  # Huffman table optimization
        )
    if fmt == 'PNG':
        image.save(
            dest_image_path,
            format=image.format,
            compress_level=6,  # 0 (no compression) to 9 (max). Default: 6
            optimize=True,  # Find optimal compression settings
        )
    print(image.get_format_mimetype())
    return FileResponse(
        open(dest_image_path, "rb"),
        content_type=f"image/{fmt.lower()}",
    )
