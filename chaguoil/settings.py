"""
Django settings for chaguoil project.

Configuration file for Production environment using Google Cloud Storage (GCS)
for Static and Media files.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-^j_@e@m#zhpukh@dihazvzftkyr($0!q8m8yja&6!=v*6lyz)i'

# USALAMA: Zima DEBUG katika Production (Inalazimisha kutumia STATICFILES_STORAGE)
DEBUG = False 

# Badilisha na IP Address au Domain Name yako halisi
ALLOWED_HOSTS = ['*', '136.114.40.162']


# Application definition

INSTALLED_APPS = [
    # Kosa limekuwa hapa: Weka 'storages' HAPA MWANZO ili i-override tabia za static files
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


# Database - CLOUD SQL SETTINGS (Tumetumia settings zako ulizopenda)
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


# Password validation
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


# --- STATIC FILES AND MEDIA (GOOGLE CLOUD STORAGE) ---

# Jina la Bucket yako ya GCS
GS_BUCKET_NAME = 'chaguoil' 
GS_DEFAULT_ACL = 'publicRead' 

# Njia ya kukusanya files (Inabaki hivi)
STATIC_ROOT = os.path.join(BASE_DIR, 'static') 
STATICFILES_DIRS = [] # Acha hivi ili kuepuka migogoro ya local storage

# STATICFILES_FINDERS ni nzuri kwa uwazi
STATICFILES_FINDERS = [
    'django.contrib.static.finders.AppDirectoriesFinder', 
    'django.contrib.static.finders.FileSystemFinder',
]

# SANIDI STATIC FILES (CSS, JS, Fonts)
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_STATIC_LOCATION = 'static' # Files zitaenda kwenye folder la 'static/'
STATIC_URL = f'/{GS_STATIC_LOCATION}/'

# SANIDI MEDIA FILES (User Uploaded Files)
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_MEDIA_LOCATION = 'media' # Files zitaenda kwenye folder la 'media/'
MEDIA_URL = f'/{GS_MEDIA_LOCATION}/' 
