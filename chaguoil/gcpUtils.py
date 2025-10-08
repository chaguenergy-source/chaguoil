import os
from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage
from storages.backends.gcloud import GoogleCloudStaticStorage
from django.core.exceptions import ImproperlyConfigured

# import the gcpUtils module to access the MediaStorage and StaticStorage classes

# =======================================================
# KUPAKIA CREDENTIALS
# =======================================================
# Tunahakikisha tunatumia GCS_CREDENTIALS_DICT tuliyoiunda kwenye settings.py
try:
    CREDENTIALS_DICT = settings.GCS_CREDENTIALS_DICT
except AttributeError:
    # Hii itatokea kama settings.py haikurekebishwa kwa usahihi
    raise ImproperlyConfigured("GCS_CREDENTIALS_DICT must be defined in settings.py as a loaded JSON dictionary.")

# =======================================================
# STORAGE CLASS YA MEDIA FILES (UPLOADS)
# =======================================================
class MediaStorage(GoogleCloudStorage):
    """
    Darasa maalum la kuhifadhi faili za Media (picha za watumiaji, logos)
    """
    bucket_name = settings.GS_BUCKET_NAME
    location = 'media' # Weka media/ kama sehemu ya ndani ya bucket
    default_acl = 'publicRead'
    querystring_auth = False
    
    # KULAZIMISHA MATUMIZI YA DICTIONARY YA CREDENTIALS
    def __init__(self, *args, **kwargs):
        # Tunalazimisha credentials zitumike wakati darasa linapoanzishwa
        kwargs['credentials'] = CREDENTIALS_DICT
        super().__init__(*args, **kwargs)


# =======================================================
# STORAGE CLASS YA STATIC FILES (CSS, JS)
# =======================================================
class StaticStorage(GoogleCloudStaticStorage):
    """
    Darasa maalum la kuhifadhi faili za Static (CSS, JS, n.k.)
    """
    bucket_name = settings.GS_BUCKET_NAME
    location = 'static'
    default_acl = 'publicRead'
    querystring_auth = False
    
    # KULAZIMISHA MATUMIZI YA DICTIONARY YA CREDENTIALS
    def __init__(self, *args, **kwargs):
        kwargs['credentials'] = CREDENTIALS_DICT
        super().__init__(*args, **kwargs)
