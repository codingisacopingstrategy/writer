#!/usr/bin/env
# -*- coding: utf-8 -*-

"""
Create screenshots for the archive page
"""

from glob import iglob
from random import randint
from sys import argv, exit
import os
import subprocess

APP_PATH = os.path.abspath(os.path.dirname(__file__))

def screenshot(slugs=[]):
    posts = {}
    for i in slugs:
        posts[i] = 'http://127.0.0.1:8000/or/' + i
    
    for post, url in posts.iteritems():
        print "taking a screenshot of post", post, url
        # append a random query string to the uri so webkit doesn’t use a cached result
        url = "%s?id=%s" % (url, randint(222222, 777777))
        fullfile = os.path.join(APP_PATH, "static", "assets", "as", "screenshots", "of", "%s-full.png" % post)
        finalfile = fullfile.replace('-full', '')
        pipe = subprocess.Popen(['phantomjs', os.path.join(APP_PATH, 'rasterise.js'), url, fullfile])
        if pipe.wait() != 0:
            exit("Aborting")
        # convert post-full.png to 150 by 110 assets/as/screenshots/of/post.png
        pipe = subprocess.Popen("convert %s -resize 210x154^ -gravity North -extent 150x110 %s" % (fullfile, finalfile), shell=True)
        pipe.wait()
        # remove post-full.png
        os.remove(fullfile)

