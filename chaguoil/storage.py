import os
import json
from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage # Hili ndilo darasa kuu tunalotumia
from django.core.exceptions import ImproperlyConfigured

# =======================================================
# UTARATIBU WA KUPATA CREDENTIALS KWA USAHIHI
# =======================================================
def get_gcs_credentials():
    """
    Ina-retrieve GCS credentials dictionary kutoka settings.
    """
    try:
        # Tunafikia GCS_CREDENTIALS_DICT ambayo tuliiongeza kwenye settings.py
        return settings.GCS_CREDENTIALS_DICT
    except AttributeError:
        raise ImproperlyConfigured(
            "CRITICAL: GCS_CREDENTIALS_DICT not found in settings. Check settings.py configuration."
        )

# =======================================================
# STORAGE CLASS YA MEDIA FILES (UPLOADS)
# =======================================================
class MediaStorage(GoogleCloudStorage):
    """
    Hutumiwa kwa ajili ya Model Files (mfano: Company Logo)
    """
    bucket_name = settings.GS_BUCKET_NAME
    location = 'media' # Eneo files za Media zitakavyokaa
    # Setti nyingine za GCS
    default_acl = None
    querystring_auth = False
    
    # Tunalazimisha credentials kupitishwa kupitia __init__
    def __init__(self, *args, **kwargs):
        kwargs['credentials'] = get_gcs_credentials()
        super().__init__(*args, **kwargs)


# =======================================================
# STORAGE CLASS YA STATIC FILES (CSS, JS)
# =======================================================
class StaticStorage(GoogleCloudStorage): # Sasa inatumia GoogleCloudStorage
    """
    Hutumiwa kwa ajili ya Static Files (CSS, JS).
    """
    bucket_name = settings.GS_BUCKET_NAME
    location = 'static' # Eneo files za Static zitakavyokaa
    # Setti nyingine za GCS
    default_acl = None
    querystring_auth = False
    
    def __init__(self, *args, **kwargs):
        kwargs['credentials'] = get_gcs_credentials()
        super().__init__(*args, **kwargs)
