"""
Django settings for innotter project.

Generated by 'django-admin startproject' using Django 4.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path

from environs import Env

env = Env()
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.str("ALLOWED_HOSTS").split()

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party packages
    "rest_framework",
    "corsheaders",
    # Local
    "accounts",
    "authentication",
    "posts",
    "authentication",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    # 'csp.middleware.CSPMiddleware',
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Local
    "innotter.middleware.JWTMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "innotter.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "innotter.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": env.str("ENGINE"),
        "NAME": env.str("NAME"),
        "USER": env.str("USER"),
        "PASSWORD": env.str("PASSWORD"),
        "HOST": "db",
        "PORT": env.str("PORT"),
    }
}

REST_FRAMEWORK = {
    # "DEFAULT_AUTHENTICATION_CLASSES": (
    #     "authentication.authentication.SafeJWTAuthentication",
    # ),
    #  "DEFAULT_PERMISSION_CLASSES": [
    #     "rest_framework.permissions.IsAuthenticated",
    # ],
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTH_USER_MODEL = "accounts.User"

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CSRF_TRUSTED_ORIGINS = ['http://0.0.0.0:8000/']

CORS_ORIGIN_WHITELIST = tuple(env.list("CORS_ALLOWED_ORIGINS"))
CORS_ALLOW_CREDENTIALS = True  # to accept cookies via ajax request

ACCESS_PUBLIC = bytes(env.str("ACCESS_TOKEN_PUBLIC_KEY"), "utf-8")
ACCESS_PRIVATE = bytes(env.str("ACCESS_TOKEN_PRIVATE_KEY"), "utf-8")
ACCESS_PHRASE = bytes(env.str("ACCESS_TOKEN_PASSPHRASE"), "utf-8")
ACCESS_EXP_M = env.int("ACCESS_TOKEN_EXPIRES_IN_MINUTES")

REFRESH_PUBLIC = bytes(env.str("REFRESH_TOKEN_PUBLIC_KEY"), "utf-8")
REFRESH_PRIVATE = bytes(env.str("REFRESH_TOKEN_PRIVATE_KEY"), "utf-8")
REFRESH_PHRASE = bytes(env.str("REFRESH_TOKEN_PASSPHRASE"), "utf-8")
REFRESH_EXP_D = env.int("REFRESH_TOKEN_EXPIRES_IN_DAYS")

JWT_UNAUTHENTICATED_URL_PATTERNS = env.list("JWT_UNAUTHENTICATED_URL_PATTERNS")
REGEX_BEARER = env.str("REGEX_BEARER")

INTERNAL_EXTRA_JWT_OPTIONS = env.dict("INTERNAL_EXTRA_JWT_OPTIONS")
# serailizers в git stash
CORS_ORIGIN_WHITELIST = tuple(env.str("CORS_ALLOWED_ORIGINS").split())
CORS_ALLOW_CREDENTIALS = True # to accept cookies via ajax request
