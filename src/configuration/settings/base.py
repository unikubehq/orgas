"""
Django settings for unikube project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from datetime import timedelta

from environs import Env

env = Env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE_DIR, "../version.txt")) as v_file:
    VERSION = v_file.read()

SECRET_KEY = env.str("DJANGO_SECRET_KEY", "<setme>")
SITE_ID = 1

DEBUG = env.bool("DJANGO_DEBUG", False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", ["*"])

ADMINS = [("Michael", "michael@blueshoe.de")]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "hurricane",
    "organization.apps.OrganizationConfig",
    "graphene_django",
    "commons",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "configuration.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("DATABASE_NAME"),
        "USER": env.str("DATABASE_USER"),
        "HOST": env.str("DATABASE_HOST"),
        "PORT": env.int("DATABASE_PORT", 5432),
    }
}
if env.str("DATABASE_PASSWORD", None):
    DATABASES["default"]["PASSWORD"] = env.str("DATABASE_PASSWORD")

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_ROOT = env.str("DJANGO_STATIC_ROOT")
STATIC_URL = env.str("DJANGO_STATIC_URL", "/static")

PUBLIC_URL_PREFIX = os.getenv("PUBLIC_URL_PREFIX", "/orgas/")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "hurricane": {
            "handlers": ["console"],
            "level": os.getenv("HURRICANE_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        # "unikube": {
        #     "handlers": ["console", "mail_admins"],
        #     "level": os.getenv("DJANGO_LOG_LEVEL", "DEBUG"),
        # },
        # "django": {
        #     "handlers": ["console", "mail_admins"],
        #     "level": os.getenv("DJANGO_LOG_LEVEL", "DEBUG"),
        # },
    },
}

GRAPHENE_PER_PAGE = 10

if os.getenv("S3_STORAGE", None) in ["t", "true", "True", 1, "1", True]:
    DEFAULT_FILE_STORAGE = os.getenv("DEFAULT_FILE_STORAGE")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    GS_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_DEFAULT_ACL = os.getenv("AWS_DEFAULT_ACL")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
    AWS_S3_USE_SSL = os.getenv("AWS_S3_USE_SSL", False) in ["t", "true", "True", 1, "1", True]
    AWS_S3_SECURE_URLS = os.getenv("AWS_S3_SECURE_URLS", False) in ["t", "true", "True", 1, "1", True]
    AWS_S3_CUSTOM_DOMAIN = f"{os.getenv('AWS_S3_CUSTOM_DOMAIN', False)}/{AWS_STORAGE_BUCKET_NAME}"

HURRICANE_VERSION = VERSION
