#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This fabfile contains some functions that allow to rebuild and
archive the blog on the server that hosts it. Which is where
the movable type software is installed that takes care of publishing
static html files, handling public comments and trackbacks.
"""

import os.path
from pipes import quote
from fabric.api import run, local, put, cd, sudo, env
from fabric.contrib.console import confirm

env.hosts = ['s@schr.fr:599']
env.path = '/home/s/apps/i.liketightpants.net/public/and/'

def status():
    with cd(env.path):
        run('git status')

def pull():
    with cd(env.path):
        run('git pull origin master')

def publish(message):
    with cd(env.path):
        run('/home/s/apps/mt.schr.fr/melody/tools/re') # rebuild pages
        run('python screenshots.py') # generate screenshots for the archive
        run('git add .')
        run('git commit -m %s' % quote(message))

def archive():
    with cd(env.path):
        run('git push origin master') # push to github

"""
For reference, the script that is used on the server to update
the blog:

#!/usr/bin/perl
use lib('/home/s/apps/mt.schr.fr/melody/lib', '/home/s/apps/mt.schr.fr/melody/extlib/','/home/s/apps/mt.schr.fr/melody/'
);

use MT;
my $mt = new MT;

$mt->rebuild(
              BlogID => 1,
              EntryCallback => sub { print $_[0]->title, "\n" },
          );
"""
