from storages.backends.gcloud import GoogleCloudStorage
from django.conf import settings
import os

# Google Cloud Storage Settings
_GCS_BUCKET_NAME = getattr(settings, 'GS_BUCKET_NAME', 'chagufilling')
_GCS_FILE_OVERWRITE = getattr(settings, 'GS_FILE_OVERWRITE', False)
_GCS_CREDENTIALS = getattr(settings, 'GS_CREDENTIALS', None)

# --- Class ya Media Files ---
class Media(GoogleCloudStorage):
    # Hii inatumia credentials kutoka kwenye settings
    bucket_name = _GCS_BUCKET_NAME
    file_overwrite = _GCS_FILE_OVERWRITE
    credentials = _GCS_CREDENTIALS
    location = 'media' # Weka picha zote ndani ya folder la 'media'

# --- Class ya Static Files ---
class Static(GoogleCloudStorage):
    # Hii inatumia credentials kutoka kwenye settings
    bucket_name = _GCS_BUCKET_NAME
    file_overwrite = _GCS_FILE_OVERWRITE
    credentials = _GCS_CREDENTIALS
    location = 'static' # Weka static files zote ndani ya folder la 'static'
