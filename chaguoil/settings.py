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
DEBUG = True 

# Badilisha na IP Address mpya ya VM, na nimeacha '*'
ALLOWED_HOSTS = ['*','34.61.173.58']


# =======================================================
# --- GOOGLE CLOUD STORAGE SETTINGS (PRODUCTION) ---
# =======================================================
GS_BUCKET_NAME = 'chagufilling'
GCS_CREDENTIALS_FILE = os.path.join(BASE_DIR, 'gcs_service_account.json')

# HAKIKISHA GCS INATUMIA JSON DICTIONARY (Njia ya Uhakika)
try:
    with open(GCS_CREDENTIALS_FILE, 'r') as f:
        # Sasa tunapakia kama DICTIONARY, si STRING
        GCS_CREDENTIALS_DICT = json.load(f)
        print(">>> GCS CREDENTIALS SUCCESSFULLY READ AS JSON DICTIONARY.")
except FileNotFoundError:
    raise ImproperlyConfigured(
        f"GCS Service Account JSON file not found at {GCS_CREDENTIALS_FILE}"
    )

# Tumia Class uliyounda kwenye chaguoil.storage
if GS_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = 'chaguoil.gcpUtils.MediaStorage'
    STATICFILES_STORAGE = 'chaguoil.gcpUtils.StaticStorage'
    
    # URL ya MEDIA files
    MEDIA_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/media/"
    
    # URL ya STATIC files
    STATIC_URL = f"https://storage.googleapis.com/{GS_BUCKET_NAME}/static/"
    
    print(">>> FINAL CHECK: DEFAULT_FILE_STORAGE set to GCS.")

    
# from django.core.files.storage import default_storage # Hii inahitajika kwa kufuta faili la zamani

# # try:
# MediaStorage = GoogleCloudStorage
# # except Exception:
# #     MediaStorage = type(default_storage)  # fallback to current storage type

# is_gcs_storage = isinstance(default_storage, MediaStorage)    
# print(f"DEBUG: default_storage is MediaStorage (GCS): {is_gcs_storage}")

# storage_class_name = default_storage.__class__.__module__ + "." + default_storage.__class__.__name__

# print(f"Default media storage Name: {storage_class_name}")

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
