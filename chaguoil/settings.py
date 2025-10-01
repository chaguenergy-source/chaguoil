"""
Django settings for chaguoil project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# **Hili linapaswa kutolewa nje ya msimbo (kwa kutumia environment variables) kwa usalama zaidi!**
SECRET_KEY = 'django-insecure-^j_@e@m#zhpukh@dihazvzftkyr($0!q8m8yja&6!=v*6lyz)i'

# USALAMA: Zima DEBUG katika Production
DEBUG = True 

# Badilisha na IP Address au Domain Name yako halisi
ALLOWED_HOSTS = ['*', '136.114.40.162']


# Application definition

INSTALLED_APPS = [
    'storages', # Imethibitishwa
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


# Database - CLOUD SQL SETTINGS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mafuta', # [JINA_LA_DATABASE]
        'USER': 'chaguoil', # [USER_WA_CLOUDSQL]
        'PASSWORD': 'Chagu@me12', # [PASSWORD_YA_CLOUDSQL]
        'HOST': '34.71.9.5', # [PUBLIC_IP_YA_CLOUDSQL]
        'PORT': '5432',
    }
}

# DATABASES = {

#         'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         # 'NAME': 'chaguoil',
#         'NAME': 'mafuta',
#         'USER': 'postgres',
#         'PASSWORD' : '1152',
#         'HOST' : 'localhost'

#  }

# }


# Password validation
# ... (Hakuna mabadiliko hapa) ...

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


# --- GCS (Google Cloud Storage) SETTINGS ---
# Hifadhi jina la Bucket
GS_BUCKET_NAME = 'chaguoil' 

# Path to GCP credentials file
GOOGLE_APPLICATION_CREDENTIALS = os.path.join(BASE_DIR, 'credidentials.json')

# Hii HAKUNA HAJA KUITUMIA KWENYE VM YAKO kwa sababu Service Account inasimamia ruhusa
# GOOGLE_APPLICATION_CREDENTIALS = os.path.join(BASE_DIR, 'credidentials.json') 

# Ruhusa (ACL)
GS_DEFAULT_ACL = 'publicRead' 


# SANIDI MEDIA FILES (User Uploaded Files)

# Use GCS for media files
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_MEDIA_LOCATION = 'media'
MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/{GS_MEDIA_LOCATION}/'


# SANIDI STATIC FILES (CSS, JS, Fonts)

# Use GCS for static files
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_STATIC_LOCATION = 'static'
STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/{GS_STATIC_LOCATION}/'

# STATIC_ROOT is not needed for production GCS, comment out for production
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'fanyabiasharaapp@gmail.com'
EMAIL_HOST_PASSWORD = 'whrzddczljnprbyy'