#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This fabfile contains some functions that allow to rebuild and
archive the blog on the server that hosts it. Which is where
the movable type software is installed that takes care of publishing
static html files, handling public comments and trackbacks.
"""

from pipes import quote
from fabric.api import run, cd, sudo, env, settings

from write.local_settings import FABRIC_HOSTS, FABRIC_PATH, FABRIC_DJANGO_PATH

env.hosts = FABRIC_HOSTS
env.path = FABRIC_PATH
env.django_path = FABRIC_DJANGO_PATH


class FabricException(Exception):
    pass


def deploy():
    with cd(env.django_path):
        run('git pull origin master')
        sudo('supervisorctl restart tightpants')


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
        run('/home/s/apps/i.liketightpants.net/writer-venv/bin/python /home/s/apps/i.liketightpants.net/writer/manage.py publish')  # rebuild pages
        """ I disabled making screenshots because even if the other pages don’t change,
            their new screenshots are never identical, so in git all these little png’s have
            to be updated.
            Need to write some logic that only makes screenshots for pages with modification
            dates higher than the latest commit.
        """
        # run('python screenshots.py') # generate screenshots for the archive


def commit(slug=None, message=None):
    """
    Commit on the server
    Specify the message in a command line argument as such:
    fab publish:message="This is the commit message"
    """
    with cd(env.path), settings(abort_exception=FabricException):
        # Add all posts’ html
        run('ls *.html | grep -v googled | xargs git add')  # skip the Google Webmaster verification file google*.html
        if slug:
            # Add assets for this specific post
            run('''cat ''' + slug + '''.html | python -c 'import re; import fileinput; r = re.compile(""""\/and\/(assets\/[^"]+)""" + chr(34)); print "\\n".join(["\\n".join(s.replace("/and/","") for s in r.findall(line)) for line in fileinput.input() if len(r.findall(line)) > 0])' | xargs git add ''')
            # Screenshot this post, add it to git
            # run('/home/s/apps/i.liketightpants.net/writer-venv/bin/python manage.py screenshot %s' % slug)
            run('git add assets/as/screenshots/of/%s.png' % slug)
            if message:
                run('git commit -m %s' % quote(message))
            else:
                try:
                    run('git ls-files --error-unmatch %s.html' % slug)
                    run('git commit -m "Modified post %s"' % slug)
                except FabricException:
                    run('git commit -m Added post %s"' % slug)
        elif message:
            run('git commit -m %s' % quote(message))


def archive():
    """
    Push from the server to GitHub
    """
    with cd(env.path):
        run('git push origin master')  # push to github


"""
For reference, the script that used to be used on the server to update
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
