# -*- coding: utf-8 -*-
# Django settings for nook project.

import os.path
from os import environ

LOCAL = not 'SERVER_SOFTWARE' in environ
if LOCAL:
    # 本地数据库设置
    SQLITE_FILE = 'database.db'
else: 
    # 线上则使用 SAE 模块
    import sae.const
    MYSQL_DB = sae.const.MYSQL_DB
    MYSQL_USER = sae.const.MYSQL_USER
    MYSQL_PASS = sae.const.MYSQL_PASS
    MYSQL_HOST_M = sae.const.MYSQL_HOST
    MYSQL_HOST_S = sae.const.MYSQL_HOST_S
    MYSQL_PORT = sae.const.MYSQL_PORT

    # 其他 SAE 设置
    # 10M 文件上传内存
    # FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760
    # 使用 Storage 操作文件
    # DEFAULT_FILE_STORAGE = 'sae.ext.django.storage.backend.Storage'
    # 指定操作文件的 bucket 名
    # STORAGE_BUCKET_NAME = 'files'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

EMAIL_ADMIN = ''

EMAIL_USE_TLS = False # 是否需要传输层安全
EMAIL_HOST = '' # 发送邮件的主机地址
EMAIL_PORT = 25 # 端口
EMAIL_HOST_USER = '' # 验证账号
EMAIL_HOST_PASSWORD = '' # 验证密码

# Blog post content 'more' split mark
MARK_MORE_SPLIT = '<!--more-->'

# Akismet API key
AKISMET_API_KEY = ''
AKISMET_PROJECT_UA = 'Nook Blog'
# Static file CDN domain
STATIC_CDN = '//qiniudn.com/'
# Qiniu Appkey config
QINIU_APP_KEY = ''
QINIU_APP_SECRET = ''
QINIU_UPLOAD_BUCKET = ''
QINIU_UPLOAD_CALLBACK = 'http://nook.sinaapp.com/ghost/upload/callback'

# WeChat robot token
WEBOT_TOKEN = ''

# LTP (Language Tech Platform Cloud) API key
LTP_API_KEY = ''

# Baidu LBS API Key
BAIDU_LBS_KEY = ''
BAIDU_LBS_SECRET = ''

# Weibo API Key
WEIBO_API_KEY = ''
WEIBO_API_SECRET = ''

MANAGERS = ADMINS

if LOCAL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': SQLITE_FILE,                      # Or path to database file if using sqlite3.
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': MYSQL_DB,                      # Or path to database file if using sqlite3.
            # The following settings are not used with sqlite3:
            'USER': MYSQL_USER,
            'PASSWORD': MYSQL_PASS,
            'HOST': MYSQL_HOST_M,                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            'PORT': MYSQL_PORT,                      # Set to empty string for default.
        }
    }

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Shanghai'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'zh-cn'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = 'static/'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '123456789'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'nook.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'nook.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), '../templates').replace('\\','/'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog',
    'ghost',
    'webot',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

LOGIN_URL = '/ghost/login'
