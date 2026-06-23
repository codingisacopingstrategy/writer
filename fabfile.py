#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This fabfile contains some functions that allow to rebuild and
archive the blog on the server that hosts it. Which is where
the movable type software is installed that takes care of publishing
static html files, handling public comments and trackbacks.
"""

from getpass import getpass
from shlex import quote
from fabric import Connection, task

from write.local_settings import FABRIC_HOSTS, FABRIC_PATH, FABRIC_DJANGO_PATH

HOST = FABRIC_HOSTS[0] if isinstance(FABRIC_HOSTS, (list, tuple)) else FABRIC_HOSTS


def connection():
    return Connection(HOST)


class FabricException(Exception):
    pass


@task
def deploy(c):
    conn = connection()
    with conn.cd(FABRIC_DJANGO_PATH):
        conn.run('git pull origin master')
    conn.sudo('supervisorctl restart tightpants', password=getpass())


@task
def status(c):
    """
    Run `git status` on the server
    """
    conn = connection()
    with conn.cd(FABRIC_PATH):
        conn.run('git status')


@task
def pull(c):
    """
    Pull from GitHub to server
    """
    conn = connection()
    with conn.cd(FABRIC_PATH):
        conn.run('git pull origin master')


@task
def publish(c):
    """
    Rebuild the pages on the server
    """
    conn = connection()
    with conn.cd(FABRIC_PATH):
        conn.run('/home/s/apps/i.liketightpants.net/writer-venv/bin/python /home/s/apps/i.liketightpants.net/writer/manage.py publish')  # rebuild pages
        """ I disabled making screenshots because even if the other pages don’t change,
            their new screenshots are never identical, so in git all these little png’s have
            to be updated.
            Need to write some logic that only makes screenshots for pages with modification
            dates higher than the latest commit.
        """
        # run('python screenshots.py') # generate screenshots for the archive


@task
def commit(c, slug=None, message=None):
    """
    Commit on the server
    Specify the message in a command line argument as such:
    fab commit --message="This is the commit message"
    """
    conn = connection()
    with conn.cd(FABRIC_PATH):
        # Add all posts’ html
        conn.run('ls *.html | grep -v googled | xargs git add')  # skip the Google Webmaster verification file google*.html
        if slug:
            # Add assets for this specific post
            conn.run('''cat ''' + slug + '''.html | python -c 'import re; import fileinput; r = re.compile(""""\\/and\\/(assets\\/[^"]+)""" + chr(34)); print "\\n".join(["\\n".join(s.replace("/and/","") for s in r.findall(line)) for line in fileinput.input() if len(r.findall(line)) > 0])' | xargs git add ''')
            # Screenshot this post, add it to git
            # run('/home/s/apps/i.liketightpants.net/writer-venv/bin/python manage.py screenshot %s' % slug)
            conn.run('git add assets/as/screenshots/of/%s.png' % slug, warn=True)
            if message:
                conn.run('git commit -m %s' % quote(message))
            else:
                result = conn.run('git ls-files --error-unmatch %s.html' % slug, warn=True, hide=True)
                if result.ok:
                    conn.run('git commit -m "Modified post %s"' % slug)
                else:
                    conn.run('git commit -m "Added post %s"' % slug)
        elif message:
            conn.run('git commit -m %s' % quote(message))


@task
def archive(c):
    """
    Push from the server to GitHub
    """
    conn = connection()
    with conn.cd(FABRIC_PATH):
        conn.run('git push origin master')  # push to github


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
