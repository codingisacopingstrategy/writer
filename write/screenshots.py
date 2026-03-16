#!/usr/bin/env
# -*- coding: utf-8 -*-

"""
Create screenshots for the archive page
"""

from random import randint
import os
from playwright.sync_api import sync_playwright

from write.settings import PUBLIC_PATH
try:
    from write.settings import DEV_SERVER
except ImportError:
    DEV_SERVER = 'http://127.0.0.1:8000/'


def screenshot(slugs=[]):
    posts = {}
    for i in slugs:
        posts[i] = DEV_SERVER + '/is/' + i

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1190, "height": 600},
                                      device_scale_factor=1)

        for post, url in posts.items():
            # print "taking a screenshot of post", post, url
            # append a random query string to the uri so webkit doesn’t use a cached result
            # also: add the ‘secret’ key to view unpublished articles
            url = "%s?id=%s&the_secret_question=the_secret_answer" % (url, randint(222222, 777777))
            filename = os.path.join(PUBLIC_PATH, "assets", "as", "screenshots", "of", "%s.png" % post)
            page = context.new_page()
            try:
                page.goto(url, wait_until="networkidle", timeout=15000)
            except Exception as e:
                pass
            # remove open comment form for screenshot
            page.evaluate("""
                const el = document.getElementById("comments-open");
                if (el) el.remove();
            """)
            page.add_style_tag(content="header#site { display: none; } footer { position: static !important; }")
            page.locator(".article").screenshot(path=filename)
            page.close()
