"""
Django settings for chaguoil project.

Configuration file for Production environment using Google Cloud Storage (GCS)
for Static and Media files.
"""

import os
import json
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from google.oauth2 import service_account
from storages.backends.gcloud import GoogleCloudStorage

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-^j_@e@m#zhpukh@dihazvzftkyr($0!q8m8yja&6!=v*6lyz)i'

# USALAMA: Zima DEBUG katika Production (Inalazimisha kutumia STATICFILES_STORAGE)
DEBUG = False 

# Badilisha na IP Address mpya ya VM, na nimeacha '*'
ALLOWED_HOSTS = ['*','34.61.173.58']


# =======================================================
# --- GOOGLE CLOUD STORAGE SETTINGS (PRODUCTION) ---
# =======================================================

GS_BUCKET_NAME = 'chagufilling'
GS_FILE_OVERWRITE = False

# Hizi settings mbili mpya zitaeleza GCS storage classes path ya kuweka faili.
GS_LOCATION = 'media' 
GS_STATIC_LOCATION = 'static'

# Hii inapakia credentials za GCS
try:
    # GS_CREDENTIALS inatumiwa na test_gcs_upload.py, na pia base GCS storage class
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        os.path.join(BASE_DIR, 'gcs_service_account.json')
    )
    print("GCS Credentials loaded successfully from dedicated JSON file in settings.py.")
except Exception as e:
     GS_CREDENTIALS = None 
     print(f"!!! CRITICAL ERROR: Failed to load GCS credentials in settings.py: {e} !!!")


# 1. Tumia Base Class moja kwa moja kutoka kwenye django-storages
# Hii huondoa tatizo la circular import/import failure
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStaticStorage' # Tumia StaticStorage tofauti

# Media files (uploads)
MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/{GS_LOCATION}/'
# *HAKUNA* MEDIA_ROOT

# Static files (CSS, JavaScript, Images)
STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/{GS_STATIC_LOCATION}/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 
# *HAKUNA* STATIC_ROOT ni lazima uwepo kwa ajili ya collectstatic, lakini haitatumika kwa ku-serve.

from django.core.files.storage import default_storage # Hii inahitajika kwa kufuta faili la zamani

try:
    MediaStorage = GoogleCloudStorage
except Exception:
    MediaStorage = type(default_storage)  # fallback to current storage type

is_gcs_storage = isinstance(default_storage, MediaStorage)    
print(f"DEBUG: default_storage is MediaStorage (GCS): {is_gcs_storage}")

storage_class_name = default_storage.__class__.__module__ + "." + default_storage.__class__.__name__

print(f"Default media storage Name: {storage_class_name}")

# =======================================================
# --- END GOOGLE CLOUD STORAGE SETTINGS ---
# =======================================================


# Application definition

INSTALLED_APPS = [
    # Weka 'storages' HAPA MWANZO
    'storages', 
    'account.apps.AccountConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize' ,
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'chaguoil.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'chaguoil.wsgi.application'


# Database - CLOUD SQL SETTINGS (Inabaki vilevile)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mafuta', 
        'USER': 'chaguoil', 
        'PASSWORD': 'Chagu@me12', 
        'HOST': '34.71.9.5', # PUBLIC_IP_YA_CLOUDSQL
        'PORT': '5432',
    }
}


# Password validation (Hakuna mabadiliko hapa)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'fanyabiasharaapp@gmail.com'
EMAIL_HOST_PASSWORD = 'whrzddczljnprbyy'


STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
