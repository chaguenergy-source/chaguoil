import os
from google.oauth2 import service_account
from storages.backends.gcloud import GoogleCloudStorage

# Njia rahisi ya kupata BASE_DIR
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Pata Credentials kutoka kwenye faili la service account
# Hii inahitaji `gcs_service_account.json` kuwa hapo kwenye BASE_DIR
try:
    GCS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        os.path.join(BASE_DIR, 'gcs_service_account.json')
    )
except Exception as e:
    print(f"ERROR: Failed to load GCS service account file. {e}")
    GCS_CREDENTIALS = None


# Kufafanua Media Storage (Inatumiwa kwa ImageField/FileField)
class MediaStorage(GoogleCloudStorage):
    bucket_name = 'chagufilling'
    file_overwrite = False
    credentials = GCS_CREDENTIALS
    location = 'media'
    
    # Ujumbe wa mwisho wa uthibitisho
    print(">>> FINAL CHECK: MediaStorage class loaded successfully.")


# Kufafanua Static Storage (Inatumiwa na collectstatic)
class StaticStorage(GoogleCloudStorage):
    bucket_name = 'chagufilling'
    file_overwrite = True
    credentials = GCS_CREDENTIALS
    location = 'static'
