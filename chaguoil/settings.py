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
from storages.backends.gcloud import GoogleCloudStorage # Import mpya

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
# Hizi LAZIMA ziwe hapa kabla ya kurejelewa na Storage Classes
# =======================================================

GS_BUCKET_NAME = 'chagufilling'
GS_FILE_OVERWRITE = False
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    os.path.join(BASE_DIR, 'gcs_service_account.json')
)
print("GCS Credentials loaded successfully from dedicated JSON file in settings.py.")

# 1. Kufafanua Storage Classes NDANI ya settings.py ili kuhakikisha mpangilio sahihi wa upakiaji
class MediaStorage(GoogleCloudStorage):
    # **IMEONGEZWA KWA AJILI YA DEBUGGING:** Inathibitisha kuwa hii class inatumiwa
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(">>> SUCCESS: MediaStorage (GCS) has been initialized as DEFAULT_FILE_STORAGE.")
        
    # Hizi parameters zinapatikana kwa urahisi kwa sababu zimetajwa hapo juu
    bucket_name = GS_BUCKET_NAME
    file_overwrite = GS_FILE_OVERWRITE
    credentials = GS_CREDENTIALS
    location = 'media' # Weka picha zote ndani ya folder la 'media'

class StaticStorage(GoogleCloudStorage):
    bucket_name = GS_BUCKET_NAME
    file_overwrite = GS_FILE_OVERWRITE
    credentials = GS_CREDENTIALS
    location = 'static' # Weka static files zote ndani ya folder la 'static'


# 2. Rejelea Storage Classes zilizofafanuliwa hivi punde
DEFAULT_FILE_STORAGE = 'chaguoil.settings.MediaStorage'
STATICFILES_STORAGE = 'chaguoil.settings.StaticStorage'

# Media files (uploads)
MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/media/'

# Static files (CSS, JavaScript, Images)
STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # Bado inahitajika kwa collectstatic

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
# ... (Middleware haina mabadiliko)
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
# ... (Templates haina mabadiliko)
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
# ... (Database haina mabadiliko)
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
# ... (Validators haina mabadiliko)
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
