"""
Django settings for chaguoil project.

Configuration file for Production environment using Google Cloud Storage (GCS)
for Static and Media files.
"""

import os
import json
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
# from google.oauth2 import service_account # Tumeondoa import hii
# Tumeondoa import ya Google credentials

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
# SULUHISHO: Tunatumia GS_SERVICE_ACCOUNT_JSON ili kuepuka shida za upakiaji
# =======================================================

GS_BUCKET_NAME = 'chagufilling'
GS_FILE_OVERWRITE = False

# 1. Pakia Credentials kwenye Environment Variable (Njia Bora)
GS_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'gcs_service_account.json')

try:
    with open(GS_CREDENTIALS_PATH, 'r') as f:
        credentials_data = json.load(f)
    
    # Huu ndio mchakato muhimu unaoeleza django-storages kutumia credentials hizi
    os.environ['GS_SERVICE_ACCOUNT_JSON'] = json.dumps(credentials_data)
    
    print("GCS Credentials loaded successfully into OS Environment.")
    # Tumepakia kwenye Environment, kwa hiyo hatuhitaji GS_CREDENTIALS tena
    # GS_CREDENTIALS = None 
    
except FileNotFoundError:
    print(f"!!! CRITICAL ERROR: GCS Service Account file not found at {GS_CREDENTIALS_PATH} !!!")
    
except Exception as e:
    print(f"!!! CRITICAL ERROR: Failed to load GCS credentials: {e} !!!")


# 2. Rejelea Storage Classes kutoka storages.backends.gcloud (Inaelewa environment variable)
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

# LOCATIONs ni muhimu wakati wa kutumia darasa la msingi moja kwa moja
GS_LOCATION = 'media' # Default location, hutumiwa na DEFAULT_FILE_STORAGE (Media files)
STATICFILES_DIRS = [] 
GS_STATIC_LOCATION = 'static' # Location maalum kwa STATICFILES_STORAGE.

# Media files (uploads)
MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/media/'

# Static files (CSS, JavaScript, Images)
STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

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
