__all__ = ('config', 'parse', 'ENGINES')

import os
import re
import json

try:
    from urllib.parse import urlparse  # Python 3
except ImportError:
    from urlparse import urlparse  # Python 2

from dj_paas_env import provider

ENGINES = {
    'postgres': 'django.db.backends.postgresql_psycopg2',
    'postgresql': 'django.db.backends.postgresql_psycopg2',
    'pgsql': 'django.db.backends.postgresql_psycopg2',
    'mysql': 'django.db.backends.mysql',
    'sqlite': 'django.db.backends.sqlite3',
}

re_keys = [r'.*DATABASE_URL', r'HEROKU_POSTGRESQL_.+_URL',
           r'OPENSHIFT_.+_DB_URL', 'DOTCLOUD_.+_.*SQL_URL']
re_keys = list(map(re.compile, re_keys))


def config(default=None, engine=None):
    if provider.detect() == provider.DOTCLOUD:
        with open('/home/dotcloud/environment.json', 'r') as f:
            os.environ.update(json.load(f))
    for re_key in re_keys:
        for key in os.environ:
            if re_key.match(key):
                return parse(os.environ[key], engine)
    return parse(default, engine)


def parse(url, engine=None):
    if url in ('sqlite://:memory:', 'sqlite://'):
        return {
            'ENGINE': ENGINES['sqlite'],
            'NAME': ':memory:'
        }
    url = urlparse(url)
    return {
        'ENGINE': engine if engine else ENGINES[url.scheme],
        'NAME': url.path[1:].split('?', 2)[0],
        'USERNAME': url.username or '',
        'PASSWORD': url.password or '',
        'HOST': url.hostname,
        'PORT': url.port or ''
    }
