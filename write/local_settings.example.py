import os

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
# Where to write the static files
PUBLIC_PATH = PUBLISH_DIR = os.path.join(PROJECT_DIR, '..', '..', 'I-like-tight-pants-and-mathematics')

# Additional locations of static files
STATICFILES_DIRS = (
    PUBLIC_PATH,
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# MySQL example
# For local development the settings in settings.py work well
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'melody',                     # Or path to database file if using sqlite3.
        'USER': 'foobar',                     # Not used with sqlite3.
        'PASSWORD': 'foobar',                 # Not used with sqlite3.
        'HOST': 'example.com',                # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                       # Set to empty string for default. Not used with sqlite3.
    }
}

# This I had to use when connecting to an old Movable Type Databse
DATABASE_OPTIONS = {
    'charset': 'latin1',
    'use_unicode': False,
}
