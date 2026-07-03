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


def _load_env_file():
    env_path = BASE_DIR / '.env'
    if not env_path.exists():
        return

    with env_path.open(encoding='utf-8') as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def _get_bool_env(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


_load_env_file()

# Quick-start development settings - unsuitable for production
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ImproperlyConfigured('Set SECRET_KEY in the .env file.')

# USALAMA: Zima DEBUG katika Production (Inalazimisha kutumia STATICFILES_STORAGE)
DEBUG = _get_bool_env('DEBUG', False)

allowed_hosts = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts.split(',') if host.strip()]

if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['*']

# =======================================================
# --- GOOGLE CLOUD STORAGE SETTINGS (PRODUCTION) ---
# =======================================================

GS_BUCKET_NAME = 'chagufilling'
GS_FILE_OVERWRITE = True
GCS_CREDENTIALS_FILE = os.path.join(BASE_DIR, 'gcs_service_account.json')


# 1. KUPAKIA GS_CREDENTIALS KAMA OBJECT YA SERVICE ACCOUNT
if not DEBUG:
        try:
            # Tumia GS_CREDENTIALS, kama inavyotarajiwa na django-storages
            GS_CREDENTIALS = service_account.Credentials.from_service_account_file(GCS_CREDENTIALS_FILE)
            print(">>> GCS Credentials loaded successfully from dedicated JSON file in settings.py.")
        except FileNotFoundError:
            raise ImproperlyConfigured(
                f"GCS Service Account JSON file not found at {GCS_CREDENTIALS_FILE}"
            )


        # 2. KUPAKIA JSON DICTIONARY KWA AJILI YA SCRIPTS ZA KUCHUNGUZA (DEBUGGING)
        try:
            with open(GCS_CREDENTIALS_FILE, 'r') as f:
                GCS_CREDENTIALS_DICT = json.load(f)
                print(">>> GCS_CREDENTIALS_DICT (for script testing) also loaded.")
        except FileNotFoundError:
            pass


        # 3. KUBAINISHA NJIA ZA STORAGE MOJA KWA MOJA KWA KUTUMIA BASE CLASS
        # Hii huepuka matatizo yote ya ImportError
        DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
        # STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage' 


        # KUWEKA LOCATIONS BAADA YA KUFAFANUA CLASS
        # Hizi ndizo zinazobainisha kuwa faili za media zitawekwa kwenye saraka ya 'media'
        # na static kwenye saraka ya 'static'
        GS_MEDIA_LOCATION = 'media'
        # GS_STATIC_LOCATION = 'static'

        # Media files (uploads)
        MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/{GS_MEDIA_LOCATION}/'

        # Static files (CSS, JavaScript, Images)
        # STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/{GS_STATIC_LOCATION}/'
        # STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # Bado inahitajika kwa collectstatic

        print(">>> FINAL CHECK: DEFAULT_FILE_STORAGE set to GCS.")
        # =======================================================
        # --- END GOOGLE CLOUD STORAGE SETTINGS ---
        # =======================================================

        # Application definition

        GCS_STORAGE_INSTANCE = GoogleCloudStorage(
            bucket_name=GS_BUCKET_NAME,
            credentials=GS_CREDENTIALS,
            location=GS_MEDIA_LOCATION
        )
else:
    # LOCAL DEVELOPMENT SETTINGS (USALAMA: HIZI HAZITUMIKI KATIKA PRODUCTION)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Only used for collectstatic


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

DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.postgresql')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', '5432')

if not DB_NAME or not DB_USER or not DB_PASSWORD or not DB_HOST:
    raise ImproperlyConfigured('Set DB_NAME, DB_USER, DB_PASSWORD, and DB_HOST in the .env file.')

DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
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


# Mipangilio ya Email ya Namecheap
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = _get_bool_env('EMAIL_USE_TLS', True)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

if not EMAIL_HOST or not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD or not DEFAULT_FROM_EMAIL:
    raise ImproperlyConfigured('Set EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, and DEFAULT_FROM_EMAIL in the .env file.')



STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
