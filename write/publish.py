#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from django.conf import settings
from django.test.client import Client

from write.models import MtEntry

OUTPUT_DIR = getattr(settings, "PUBLISH_DIR", None) or settings.PUBLIC_PATH

AUTHOR_SLUGS = ["glit", "bnf", "tellyou", "jenseits", "baseline", "habitus"]


def _client(client=None):
    return client if client is not None else Client()


def write_response(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, "wb") as handle:
        handle.write(content)
    return path


def write_entry_html(entry, client=None):
    response = _client(client).get("/is/%s" % entry.slug)
    if response.status_code != 200:
        raise Exception(response.status_code)
    path = os.path.join(OUTPUT_DIR, "%s.html" % entry.slug)
    return write_response(path, response.content)


def write_site_indexes(client=None):
    client = _client(client)
    writes = [
        ("/is/index.php", os.path.join(OUTPUT_DIR, "index.php")),
        ("/is/archives", os.path.join(OUTPUT_DIR, "archives.html")),
        (
            "/is/feed/us/recent_entries.xml",
            os.path.join(OUTPUT_DIR, "feed", "us", "recent_entries.xml"),
        ),
    ]
    for url, path in writes:
        response = client.get(url)
        if response.status_code != 200:
            raise Exception("%s -> %s" % (url, response.status_code))
        write_response(path, response.content)

    for author in AUTHOR_SLUGS:
        url = "/is/stories/by/" + author
        path = os.path.join(OUTPUT_DIR, "stories", "by", author + ".html")
        response = client.get(url)
        if response.status_code != 200:
            raise Exception("%s -> %s" % (url, response.status_code))
        write_response(path, response.content)


def regenerate_published_site(client=None):
    client = _client(client)
    for entry in MtEntry.objects.filter(published=True):
        write_entry_html(entry, client)
    write_site_indexes(client)


def publish_entry(entry, update_all=False):
    if not entry.published:
        entry.published = True
        entry.save(update_fields=["published"])
    if update_all:
        regenerate_published_site()
    return entry.commit()
