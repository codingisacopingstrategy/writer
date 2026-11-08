# writer

The Django application behind the blog [*I like tight pants and mathematics*](http://i.liketightpants.net/and/). Authors write in the browser. Publishing renders each article to a static HTML file and commits it to a separate Git repository, and that repository is the public website.

Every post finishes the sentence “I like tight pants and…”. The project began in 2012 as a replacement for Movable Type / Melody and is happy to show it: the models are `MtEntry` and `MtComment`, and comments post to `/comments.cgi`.

**Stack:** Python 3.12, Django 5.1, SQLite, django-tastypie (JSON API), dulwich (Git from Python), Fabric (server tasks), Playwright (screenshots), Pillow (image scaling).

## Two repositories

| Repository                                                                                                            | Holds                                                                                |
| --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `writer` (this one)                                                                                                   | Django code, templates, and the SQLite database `write/write.db` (not in Git)        |
| [`I-like-tight-pants-and-mathematics`](https://github.com/codingisacopingstrategy/I-like-tight-pants-and-mathematics) | The generated HTML, and everything the browser loads: CSS, JavaScript, fonts, images |

Clone them next to each other. Two things follow from the split:

- **The app won’t start without the public repository.** `write/models.py` opens it as a Git repository at import time.
- **The editor’s JavaScript isn’t here.** It’s in `logged/in/` in the public repository, so a change to the editor usually means a commit in each repository.

## `/or/`, `/is/`, `/and/`

The site has three URL spaces, each a word that could follow “I like tight pants”:

| Prefix  | What it is                          | Served by                               | Login |
| ------- | ----------------------------------- | --------------------------------------- | ----- |
| `/or/`  | The editable site                   | Live Django views, with `EDITING` on    | Yes   |
| `/is/`  | A preview of what will be generated | Live Django views                       | No    |
| `/and/` | The final public site               | Static files from the public repository | No    |

Alongside those are `/api/` (the JSON API the editor talks to), `/admin/` (Django admin, for anything the editor doesn’t cover) and `/comments.cgi` (where public comment forms post).

## Getting started

You need Python 3, and SSH access to the server to copy the database.

```bash
git clone git@github.com:codingisacopingstrategy/writer.git
git clone git@github.com:codingisacopingstrategy/I-like-tight-pants-and-mathematics.git
cd writer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp write/local_settings.example.py write/local_settings.py
```

Then fill in `FABRIC_HOSTS`, `FABRIC_PATH` and `FABRIC_DJANGO_PATH` in `write/local_settings.py` so `fab` can reach the server.

Copy the live database and run the server:

```bash
fab mirror  # overwrites write/write.db without a backup
python manage.py migrate write --fake-initial
python manage.py runserver
```

`--fake-initial` records `write.0001_initial` without recreating the article tables, which already exist in the live file, and Django then inserts the **Can publish entries** permission. A brand-new database would use plain `migrate`, but that won’t give you a working site: pages assume at least one published entry, and new articles default to the user with primary key 3.

Then visit:

- `http://localhost:8000/or/`: the editor. Log in with your account from the live database.
- `http://localhost:8000/is/`: the preview, redirecting to the latest post.
- `http://localhost:8000/and/`: the generated files, redirecting to the latest post.

## How it works

### Data

`write/models.py` holds two models, plus Django’s `User` for authors.

- `MtEntry` is an article: title, slug, HTML body, excerpt, preview image, per-article `custom_css`, a `published` flag, and an author.
- `MtComment` belongs to an entry and threads through `parent`. `mt_author` links it to a site user; public commenters have only a name, email and URL.

### Editing

`/or/<slug>` shows the article with editing switched on. If the slug doesn’t exist yet, you get a blank draft that is created on first save.

Edits go to the database through `/api/`, and the article body autosaves about a second after you stop typing. **Saving doesn’t change the public site.** Only publishing does.

Other editor screens:

- `/or/archives` is a calendar “wall” (FullCalendar) of all entries. Dragging an entry changes its `created_on`.
- `/or/assets/` is the read-only JSON listing behind the editor’s image picker. There is no upload: it only lists what is already in the public repository’s `assets/`.

### Publishing

Both editors have a **Publish** button, labelled **Save Modifications** once the article is live:

```
Button on /or/<slug>
  → PATCH /api/entry/<id>/          saves the latest edits
  → POST  /api/entry/<id>/publish/  MtEntryResource.publish, in write/api.py
      → publish_entry, in write/publish.py
          → renders /is/<slug> with Django’s test client
          → writes <slug>.html to the root of the public repository
          → commits with dulwich, attributed to the article’s author
```

Commit messages read `Publish: I like tight pants and …` the first time and `Update: …` after that. Pages are rendered with the test client, whose host is `testserver`, so `settings.py` always adds that name to `ALLOWED_HOSTS`.

**A plain publish only writes that one article’s page.** A new post won’t reach the homepage redirect (`latest.txt`), `archives.html`, `about.html`, the feed or the author pages until someone ticks **update all posts**. That option re-renders every published entry and those index pages, and commits them together.

`python manage.py publish` does the same full re-render from the command line, but doesn’t commit. `python manage.py publish <slug>` writes one published article.

The `2011` editor also keeps its `published` checkbox, the only way to unpublish from an editor. It changes the database and writes no HTML.

### Public comments

Published pages are static, so their comment forms post to `/comments.cgi` (`handle_comment` in `write/views.py`), which is CSRF-exempt for that reason. `CommentForm` checks the required fields and the anti-spam riddle, and `write/sanitize.py` reduces the HTML to an allow-list of tags.

Comments go live immediately, with no moderation step. The article’s page is re-rendered and committed on the spot, so each comment that changes the page becomes a commit in the public repository. Editing a comment through `/or/` only changes the database until the article is next published.

### Themes

There are two themes in `write/templates/themes/`, and the same templates render both edit and public modes, switching on the `EDITING` and `andor` variables.

| Theme     | Used for                                                    | Article editor | CSS (public repository)                |
| --------- | ----------------------------------------------------------- | -------------- | -------------------------------------- |
| `2011`    | Articles before 2026-03-09; also login, logout and the wall | Aloha          | `style/in/`, one stylesheet per author |
| `roxanne` | Newer articles; also archives, author pages, about          | Squire         | `the/style/in/`                        |

The article cutoff is `MtEntry.uses_old_style_templates`. The archives page splits its list at a different date, 2026-03-11, in `views.archives`. Both CSS folders are Less, compiled by the `less.sh` script in each folder (requires `lessc`).

Squire is vendored with a local patch. Read `logged/in/roxanne/squire/TIGHTPANTS-SVG.md` in the public repository before upgrading it.

### Images

Originals are in `assets/called/` in the public repository. A request for `/and/assets/scaled/to/<size>/<path>` is served by nginx if the file exists. Otherwise it falls through to `scale_image` in `imagescaler.py`, which resizes the JPEG or PNG and saves it so nginx finds it next time. In development there is no nginx, so Django handles every such request and rewrites the file each time.

## Structure

```
writer/
├── fabfile.py              Server tasks (see Deployment)
├── imagescaler.py          On-demand image resizing
├── assets/                 App behind the editor’s image picker (/or/assets/)
└── write/                  The main app and Django project
    ├── settings.py         Base settings; imports local_settings.py last
    ├── urls.py             All routes
    ├── models.py           MtEntry, MtComment, Git commit helpers
    ├── views.py            Pages, the comment handler, dev static serving
    ├── api.py              Tastypie resources and the publish endpoint
    ├── auth.py             API authentication and authorization
    ├── publish.py          Rendering pages to disk
    ├── forms.py            Public comment form
    ├── sanitize.py         Comment HTML allow-list
    ├── screenshots.py      Playwright screenshots for the wall
    ├── management/commands/   publish, screenshot
    └── templates/          themes/2011, themes/roxanne, the Atom feed

I-like-tight-pants-and-mathematics/
├── <slug>.html, about.html, archives.html, latest.txt, feed/, stories/by/   Generated
├── assets/                 called/ (originals), scaled/to/, as/screenshots/of/
├── the/style/in/           Roxanne CSS
├── style/in/               2011 CSS
├── scripts/being/          Public JavaScript, including comment-squire.js
└── logged/in/
    ├── roxanne/js/         Squire editor: edit-entry-roxanne.js does saving
    │                       and publishing; also the toolbar and image picker
    └── 2011/               Aloha editor and calendar-view.js (the wall)
```

## Permissions

The `/api/` endpoints require a logged-in session. Rights are Django’s user permissions, the checkboxes on `/admin/auth/user/`. A superuser has them all.

| Permission                         | Allows                                                                                                   |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Can add / change entry and comment | Editing in `/or/`                                                                                        |
| Can publish entries                | Publishing, seeing the publish controls, and flipping `published` (the API ignores that field otherwise) |
| Can delete entry                   | Deleting an article                                                                                      |

The API uses the session cookie and no CSRF token, because the editor’s `fetch()` calls don’t send one. See `LoggedInAuthentication` in `write/auth.py`.

## Tests

```bash
python manage.py test
```

You can find the tests in `write/tests.py` and `assets/tests.py`. They use a temporary database and mock the steps that write to Git, so they don’t touch `write.db` or the public repository’s history. The public repository must still be present. The `Entry … Saved!` lines in the output come from `post_save` handlers in `models.py` and are harmless. The JavaScript in the public repository has no tests.

## Settings

`write/settings.py` holds the defaults, and the gitignored `write/local_settings.py` overrides them.

| Setting                                             | Purpose                                                                                                    |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `PUBLIC_PATH`, `PUBLISH_DIR`                        | The public repository checkout                                                                             |
| `STATICFILES_DIRS`                                  | Must include `PUBLIC_PATH`, or `/and/` won’t work in development                                           |
| `USE_TZ`                                            | Must be `True`. The default in `settings.py` is `False`, and the date cutoffs raise `TypeError` without it |
| `ALLOWED_HOSTS`                                     | Defaults to `localhost` and `127.0.0.1`; set your domain in production. `testserver` is always added       |
| `FABRIC_HOSTS`, `FABRIC_PATH`, `FABRIC_DJANGO_PATH` | The server, and the public repository and this repository on it                                            |
| `DEV_SERVER`                                        | Base URL that screenshots load pages from. Defaults to `http://127.0.0.1:8000/`                            |
| `DEBUG`, `SECRET_KEY`                               | `settings.py` has development values; override both in production                                          |

## Deployment

On the server, Django runs under supervisor as `tightpants` behind nginx, which serves the static files and uses `latest.txt`, holding the latest post’s slug, to rewrite `/and/`. Those configs aren’t in this repository. Run these tasks from your `writer` checkout:

| Command                     | What it does                                                                |
| --------------------------- | --------------------------------------------------------------------------- |
| `fab deploy`                | Pulls this repository on the server and restarts `tightpants`               |
| `fab pull`                  | Pulls the public repository from GitHub to the server                       |
| `fab archive`               | Pushes the server’s public repository to GitHub                             |
| `fab publish`               | Runs `manage.py publish` on the server (no commit)                          |
| `fab commit --message="…"`  | Commits the generated files on the server                                   |
| `fab status`, `fab history` | Shows `git status` or the recent log of the public repository on the server |
| `fab mirror`                | Copies the server’s `write.db` over your local one                          |

To ship a change:

- **Python or templates:** push this repository, then `fab deploy`. It doesn’t run migrations or install requirements, so do those by hand when needed.
- **CSS or JavaScript:** push the public repository, then `fab pull`.

The server’s public repository gains a commit with every publish and comment, so it is usually ahead of GitHub until someone runs `fab archive`.

## Screenshots

Screenshots are the images shown on the wall. You can find them in `assets/as/screenshots/of/` in the public repository. There are two ways to take them:

- **Take Screenshot**, under the publish controls in both editors, captures the article as it was last saved and commits the PNG, attributed to the article’s author, through `POST /api/entry/<id>/screenshot/`. It needs the **Can publish** permission.
- `python manage.py screenshot [slug …]` captures several at once, and defaults to all published entries.

Both use `write/screenshots.py`, which loads `/is/<slug>` from `DEV_SERVER` in headless Chromium, so they need `playwright install chromium` and the site running at that address. For the button on the server, that means `DEV_SERVER` must be an address the server can reach itself at, and Django must be able to answer that page request while the button’s own request is still waiting. On a Linux server Chromium also needs system libraries, which `sudo <venv>/bin/playwright install-deps chromium` installs (Debian and Ubuntu); without them the launch fails with `error while loading shared libraries`. The command doesn’t commit its screenshots; `fab commit` picks them up with the rest of `assets/`.

Articles with the coloured background come out as transparent PNGs that show just the rounded rectangle. 2011 articles have none, and keep their white background.

Screenshots are switched off in `fab publish`, because regenerated PNGs are never identical and would bloat the public repository’s history.

## Known issues

- **`/is/<slug>` shows drafts without a login.** The check in `views.entry` is commented out.
- **Contributors are hard-coded.** Adding one means changing the author IDs in `write/views.py` (two places) and `AUTHOR_SLUGS` in `write/publish.py`.
- **`django.contrib.staticfiles` is deliberately not installed.** Disabling it lets `serve_html` own `/and/` and strip `.html` from URLs, as the production server does.
