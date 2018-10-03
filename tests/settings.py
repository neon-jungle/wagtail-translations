import os


INSTALLED_APPS = [
    'tests.app',

    'taggit',
    'modelcluster',
    'wagtailtranslations',

    'wagtail.core',
    'wagtail.admin',
    'wagtail.users',
    'wagtail.sites',
    'wagtail.snippets',
    'wagtail.search',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.routable_page',
    'wagtail.contrib.styleguide',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
]

SECRET_KEY = 'not a secret'

ROOT_URLCONF = 'tests.app.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.sqlite3',
    },
}

WAGTAIL_SITE_NAME = 'Wagtail Translations'

DEBUG = True

USE_TZ = True
TIME_ZONE = 'Australia/Hobart'

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.core.middleware.SiteMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

STATIC_ROOT = os.path.join(os.path.dirname(__file__), 'static')
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'media')

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
