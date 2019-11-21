"""
Only for testcases.
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if os.path.exists(os.path.join(BASE_DIR, 'oneid', 'settings.py')):
    exec(open(os.path.join(BASE_DIR, 'oneid', 'settings.py')).read())

if os.path.exists(os.path.join(BASE_DIR, 'oneid', 'settings_test.py')):
    exec(open(os.path.join(BASE_DIR, 'oneid', 'settings_test.py')).read())

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'test', 'data', 'unittest.sqlite3'),
    },
}

TEST_RUNNER = 'test.utils.test_runner.TestDiscoverRunner'
