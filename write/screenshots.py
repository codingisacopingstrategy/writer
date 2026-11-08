#!/usr/bin/env
# -*- coding: utf-8 -*-

"""
Create screenshots for the archive page
"""

from random import randint
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

from write.models import commit_repo_paths, screenshot_path
try:
    from write.settings import DEV_SERVER
except ImportError:
    DEV_SERVER = 'http://127.0.0.1:8000/'


def screenshot_entry(entry):
    """
    Takes the screenshot the archive shows for this entry, and commits it to the public repository
    """
    screenshot([entry.slug])
    return commit_repo_paths(
        [screenshot_path(entry.slug)],
        message="Screenshot: %s" % entry.tight_pants_title(),
        name=entry.author.username,
        email=entry.author.email,
    )


def screenshot(slugs=[]):
    posts = {}
    for i in slugs:
        posts[i] = DEV_SERVER.rstrip('/') + '/is/' + i

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={"width": 1190, "height": 600},
                                      device_scale_factor=1)

        for post, url in posts.items():
            # print "taking a screenshot of post", post, url
            # append a random query string to the uri so webkit doesn’t use a cached result
            # also: add the ‘secret’ key to view unpublished articles
            url = "%s?id=%s&the_secret_question=the_secret_answer" % (url, randint(222222, 777777))
            filename = screenshot_path(post)
            page = context.new_page()
            # The button waits for all of this in one request, so every step has a timeout
            # that keeps the whole well inside gunicorn's 30 second worker timeout
            response = page.goto(url, wait_until="load", timeout=10000)
            if not response or not response.ok:
                raise RuntimeError("%s answered %s" % (posts[post], response.status if response else "nothing"))
            try:
                page.wait_for_load_state("networkidle", timeout=8000)
            except PlaywrightTimeoutError:
                pass  # the page loaded, but something kept the network busy
            # remove open comment form for screenshot
            page.evaluate("""
                const el = document.getElementById("comments-open");
                if (el) el.remove();
            """)
            page.add_style_tag(content="""
                /* The coloured rounded rectangle background is fixed to the viewport,
                stretch it over the whole article instead */
                body:has(> .background-canvas) { position: relative; }
                .background-canvas { position: absolute !important; top: 0 !important; bottom: 0 !important; }
                /* and let the page end where the article ends, so the background’s rounded corners show */
                main.article { margin-bottom: 0 !important; }
                /* Not showing the menus (as they’re display: fixed */
                header#site { display: none; }
                .bottom-gap, footer { display: none !important; }
            """)
            page.locator(".article").screenshot(path=filename, timeout=5000)
            page.close()
