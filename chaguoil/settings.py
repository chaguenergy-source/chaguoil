"""
Django settings for chaguoil project.

Configuration file for Production environment using Google Cloud Storage (GCS)
for Static and Media files.
"""

import os
import json
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

# Define BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-^j_@e@m#zhpukh@dihazvzftkyr($0!q8m8yja&6!=v*6lyz)i'

# USALAMA: Zima DEBUG katika Production (Inalazimisha kutumia STATICFILES_STORAGE)
DEBUG = False 

# Badilisha na IP Address mpya ya VM, na nimeacha '*'
ALLOWED_HOSTS = ['*','34.61.173.58']


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

# =======================================================
# --- GOOGLE CLOUD STORAGE SETTINGS (PRODUCTION) ---
# =======================================================

# STATIC FILES SETTINGS (Local)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Hili ni jina la folder la ndani la VM ambapo faili hukusanywa kabla ya kutumwa Cloud.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_gcs') 

# TUMEONDOA MEDIA_ROOT KULAZIMISHA GCS kwa Media files (user uploads)
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 

# Sasa tunasoma key moja kwa moja kutoka kwenye faili la ndani la VM.
GCS_KEY_FILE_PATH = os.path.join(BASE_DIR, 'gcs_service_account.json')

if os.path.exists(GCS_KEY_FILE_PATH):
    try:
        # Soma (read) JSON key moja kwa moja kutoka kwenye faili
        with open(GCS_KEY_FILE_PATH, 'r') as f:
            GS_CREDENTIALS = json.load(f)
        
        # Thibitisha settings nyingine ziko sawa
        STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
        DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
        
        # Jina la bucket na Project ID
        GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME', 'chagufilling')
        GS_PROJECT_ID = 'prime-micron-473718-h1' 

        # VIPIELEZO KWA AJILI YA PUBLIC ACCESS NA OVERWRITE
        GS_DEFAULT_ACL = 'publicRead' 
        GS_FILE_OVERWRITE = True

        # URL za STATIC/MEDIA zikielekeza GCS
        STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/static/'
        MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/media/'
        
        # GS_CREDENTIALS_FILE inahitajika kuwa None kwa GCS_CREDENTIALS
        GS_CREDENTIALS_FILE = None 

        print("GCS Credentials loaded successfully from dedicated JSON file.")

    except Exception as e:
        # Hii itaonyesha Gunicorn logini iwapo faili la JSON lina makosa (corrupted)
        print(f"ERROR: Failed to load GCS credentials from file: {e}")
        
        # Weka hizi kwa default iwapo kuna hitilafu ya JSON au file access
        STATIC_URL = '/static/'
        MEDIA_URL = '/media/'
        pass
else:
    # Hali ya default ikiwa JSON Key haipatikani
    print("WARNING: GCS Credentials file not found. Using local files.")
    STATIC_URL = '/static/'
    MEDIA_URL = '/media/'

# ... Msimbo mwingine wa settings.py ...
