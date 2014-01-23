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
    """
    Run `git status` on the server
    """
    with cd(env.path):
        run('git status')

def pull():
    """
    Pull from GitHub to server
    """
    with cd(env.path):
        run('git pull origin master')

def publish():
    """
    Rebuild the pages on the server
    """
    with cd(env.path):
        run('/home/s/apps/mt.schr.fr/melody/tools/re') # rebuild pages
        """ I disabled making screenshots because even if the other pages don’t change,
            their new screenshots are never identical, so in git all these little png’s have
            to be updated.
            Need to write some logic that only makes screenshots for pages with modification
            dates higher than the latest commit.
        """
        # run('python screenshots.py') # generate screenshots for the archive

def commit(message):
    """
    Commit on the server
    Specify the message in a command line argument as such:
    fab publish:message="This is the commit message"
    """
    with cd(env.path):
        run('git add .')
        run('git commit -m %s' % quote(message))

def archive():
    """
    Push from the server to GitHub
    """
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
