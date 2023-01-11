import os
from ghostz_cdl.settings.base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('NAME'),
        'USER': os.environ.get('USER'),
        'PASSWORD': os.environ.get('PASSWORD'),
        'HOST': os.environ.get('HOST')
    }
}

try:
    from ghostz_cdl.settings.local_settings import *  # noqa: F403, F401
except ImportError:
    pass
