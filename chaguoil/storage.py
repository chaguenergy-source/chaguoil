import os
import json
from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage
from storages.backends.gcloud import GoogleCloudStaticStorage
from django.core.exceptions import ImproperlyConfigured

# =======================================================
# UTARATIBU WA KUPATA CREDENTIALS KWA USAHIHI
# =======================================================
def get_gcs_credentials():
    """
    Ina-retrieve GCS credentials dictionary kutoka settings.
    Hii inalinda dhidi ya makosa ya settings wakati wa startup.
    """
    try:
        # Tunategemea settings.py kupakia GCS_CREDENTIALS_DICT vizuri
        return settings.GCS_CREDENTIALS_DICT
    except AttributeError:
        # Hili litatokea kama settings.py haikupakia vizuri.
        raise ImproperlyConfigured(
            "CRITICAL: GCS_CREDENTIALS_DICT not found in settings. Check settings.py configuration for GCS setup."
        )

# =======================================================
# STORAGE CLASS YA MEDIA FILES (UPLOADS)
# =======================================================
class MediaStorage(GoogleCloudStorage):
    """
    Hutumiwa kwa ajili ya Model Files (mfano: Company Logo)
    """
    # Mipangilio ya darasa
    bucket_name = settings.GS_BUCKET_NAME
    location = 'media'
    default_acl = settings.GS_DEFAULT_ACL
    querystring_auth = False
    
    # REKEBISHO MUHIMU: Tunalazimisha credentials kupitia __init__
    def __init__(self, *args, **kwargs):
        # Tutaweka credentials kwa nguvu kama kwargs
        kwargs['credentials'] = get_gcs_credentials()
        super().__init__(*args, **kwargs)


# =======================================================
# STORAGE CLASS YA STATIC FILES (CSS, JS)
# =======================================================
class StaticStorage(GoogleCloudStaticStorage):
    """
    Hutumiwa kwa ajili ya Static Files (CSS, JS)
    """
    bucket_name = settings.GS_BUCKET_NAME
    location = 'static'
    default_acl = settings.GS_DEFAULT_ACL
    querystring_auth = False
    
    def __init__(self, *args, **kwargs):
        kwargs['credentials'] = get_gcs_credentials()
        super().__init__(*args, **kwargs)
