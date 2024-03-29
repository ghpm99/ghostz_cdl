import os

from dotenv import load_dotenv

from ghostz_cdl.settings.base import *  # noqa: F403, F401

load_dotenv()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ghostz_cdl',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}

ALLOWED_HOSTS = ['*']

BASE_URL = 'http://localhost:8300'

BASE_URL_WEBHOOK = 'http://localhost:8300'

BASE_URL_FRONTEND = 'http://localhost:3300'

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

try:
    from ghostz_cdl.settings.local_settings import *  # noqa: F403, F401
except ImportError:
    pass
