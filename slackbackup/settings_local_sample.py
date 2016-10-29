import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOMAIN = "http://localhost"
SLACK_CLIENT_ID = ''
SLACK_CLIENT_SECRET = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


DEBUG = True

