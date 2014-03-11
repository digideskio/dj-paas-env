import unittest
import os
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from dj_paas_env import database, provider


class TestDatabaseParse(unittest.TestCase):

    def test_parse_postgres_heroku(self):
        url = 'postgres://hleulxsesqdumt:vULaPXW9n4eGKK64d2_ujxLqGG@' + \
              'ec2-107-20-214-225.compute-1.amazonaws.com:5432/dcj1n178peejs9'
        parsed = database.parse(url)
        parsed_expect = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'dcj1n178peejs9',
            'USERNAME': 'hleulxsesqdumt',
            'PASSWORD': 'vULaPXW9n4eGKK64d2_ujxLqGG',
            'HOST': 'ec2-107-20-214-225.compute-1.amazonaws.com',
            'PORT': 5432
        }
        self.assertDictEqual(parsed, parsed_expect)

    def test_parse_postgres_openshift(self):
        url = 'postgresql://ad_mingpxxnxy:ca5Dp1_yFet3@127.11.207.130:5432'
        parsed = database.parse(url)
        parsed_expect = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': '',
            'USERNAME': 'ad_mingpxxnxy',
            'PASSWORD': 'ca5Dp1_yFet3',
            'HOST': '127.11.207.130',
            'PORT': 5432
        }
        self.assertDictEqual(parsed, parsed_expect)

    def test_parse_mysql_heroku(self):
        url = 'mysql://b819c071b951a9:9ca7bbbb@us-cdbr-east-05.cleardb.net/heroku_ec5fddc308fbe9e?reconnect=true'
        parsed = database.parse(url)
        parsed_expect = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'heroku_ec5fddc308fbe9e',
            'USERNAME': 'b819c071b951a9',
            'PASSWORD': '9ca7bbbb',
            'HOST': 'us-cdbr-east-05.cleardb.net',
            'PORT': ''
        }
        self.assertDictEqual(parsed, parsed_expect)

    def test_parse_mysql_openshift(self):
        url = 'mysql://admingJmQ37x:MDQ22l6xf1P-@127.11.207.130:3306/'
        parsed = database.parse(url)
        self.assertDictEqual(parsed, {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': '',
            'USERNAME': 'admingJmQ37x',
            'PASSWORD': 'MDQ22l6xf1P-',
            'HOST': '127.11.207.130',
            'PORT': 3306
        })

    def test_engine(self):
        url = 'scheme://user:pass@host:123/name'
        parsed = database.parse(url, engine='X')
        self.assertDictEqual(parsed, {
            'ENGINE': 'X',
            'NAME': 'name',
            'USERNAME': 'user',
            'PASSWORD': 'pass',
            'HOST': 'host',
            'PORT': 123
        })

    def test_parse_sqlite(self):
        url = 'sqlite:///directory/file.db'
        parsed = database.parse(url)
        self.assertDictEqual(parsed, {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'directory/file.db',
            'USERNAME': '',
            'PASSWORD': '',
            'HOST': None,
            'PORT': '',
        })

    def test_parse_sqlite_in_memory(self):
        url = 'sqlite://:memory:'
        parsed = database.parse(url)
        self.assertDictEqual(parsed, {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        })
        url = 'sqlite://'
        parsed = database.parse(url)
        self.assertDictEqual(parsed, {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        })


class TestDatabaseConfig(unittest.TestCase):

    def setUp(self):
        self.deleted_env = {}
        for re_key in database.re_keys:
            for key in os.environ:
                if re_key.match(key):
                    self.deleted_env[key] = os.environ[key]
        for key in self.deleted_env:
            del os.environ[key]

    def tearDown(self):
        os.environ.update(self.deleted_env)
        self.deleted_env = None

    def test_config_heroku_promoted(self):
        os.environ['DATABASE_URL'] = 'postgres://asdf:fdsa@qwer:12345/rewq'
        conf = database.config()
        self.assertDictEqual(conf, {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'rewq',
            'USERNAME': 'asdf',
            'PASSWORD': 'fdsa',
            'HOST': 'qwer',
            'PORT': 12345
        })

    def test_config_heroku_postgres(self):
        os.environ['HEROKU_POSTGRESQL_BLACK_URL'] = 'postgres://asdf:fdsa@qwer:12345/rewq'
        conf = database.config()
        self.assertDictEqual(conf, {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'rewq',
            'USERNAME': 'asdf',
            'PASSWORD': 'fdsa',
            'HOST': 'qwer',
            'PORT': 12345
        })

    def test_config_heroku_mysql(self):
        os.environ['CLEARDB_DATABASE_URL'] = 'mysql://asdf:fdsa@qwer:12345/rewq'
        conf = database.config()
        self.assertDictEqual(conf, {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'rewq',
            'USERNAME': 'asdf',
            'PASSWORD': 'fdsa',
            'HOST': 'qwer',
            'PORT': 12345
        })

    def test_config_openshift_postgres(self):
        os.environ['OPENSHIFT_POSTGRESQL_DB_URL'] = 'postgresql://asdf:fdsa@qwer:12345/rewq'
        conf = database.config()
        self.assertDictEqual(conf, {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'rewq',
            'USERNAME': 'asdf',
            'PASSWORD': 'fdsa',
            'HOST': 'qwer',
            'PORT': 12345
        })

    def test_config_openshift_mysql(self):
        os.environ['OPENSHIFT_MYSQL_DB_URL'] = 'mysql://asdf:fdsa@qwer:12345/rewq'
        conf = database.config()
        self.assertDictEqual(conf, {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'rewq',
            'USERNAME': 'asdf',
            'PASSWORD': 'fdsa',
            'HOST': 'qwer',
            'PORT': 12345
        })

    @patch('dj_paas_env.database.parse')
    def test_config_default(self, mocked):
        database.config(default='bbbb')
        mocked.assert_called_with('bbbb', None)

    @patch('dj_paas_env.database.parse')
    def test_config_engine(self, mocked):
        os.environ['DATABASE_URL'] = 'postgres://asdf:fdsa@qwer:12345/rewq'
        database.config(engine='xxxx')
        mocked.assert_called_with('postgres://asdf:fdsa@qwer:12345/rewq', 'xxxx')


class TestProviderDetect(unittest.TestCase):

    def test_detect_heroku(self):
        self.assertEqual(provider.detect({'DYNO': None}), provider.HEROKU)

    def test_detect_openshift(self):
        self.assertEqual(provider.detect({'OPENSHIFT_xxx': None}),
                         provider.OPENSHIFT)

    def test_detect_unknown(self):
        self.assertEqual(provider.detect({'xxx': None}), provider.UNKNOWN)

    def test_detect_use_environ(self):
        os.environ['DYNO'] = ''
        self.assertEqual(provider.detect(), provider.HEROKU)


def suite():
    test_suite = unittest.TestSuite()
    tests = unittest.defaultTestLoader.loadTestsFromName(__name__)
    test_suite.addTests(tests)
    return test_suite

if __name__ == '__main__':
    unittest.main()
