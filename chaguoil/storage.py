from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage

# =======================================================
# STORAGE CLASS YA MEDIA FILES (UPLOADS)
# =======================================================
class MediaStorage(GoogleCloudStorage):
    """
    Hutumiwa kwa ajili ya Model Files (mfano: Company Logo)
    GS_CREDENTIALS sasa inasimamiwa na settings.py
    """
    bucket_name = settings.GS_BUCKET_NAME
    location = 'media' # Eneo files za Media zitakavyokaa
    default_acl = settings.GS_DEFAULT_ACL
    querystring_auth = False


# =======================================================
# STORAGE CLASS YA STATIC FILES (CSS, JS)
# =======================================================
class StaticStorage(GoogleCloudStorage):
    """
    Hutumiwa kwa ajili ya Static Files (CSS, JS).
    """
    bucket_name = settings.GS_BUCKET_NAME
    location = 'static' # Eneo files za Static zitakavyokaa
    default_acl = settings.GS_DEFAULT_ACL
    querystring_auth = False
