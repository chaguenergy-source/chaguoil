
from storages.backends.gcloud import GoogleCloudStorage
from django.conf import settings

class Media(GoogleCloudStorage):
	location = 'media'
	bucket_name = getattr(settings, 'GS_BUCKET_NAME', None)
	file_overwrite = getattr(settings, 'GS_FILE_OVERWRITE', False)
	credentials = getattr(settings, 'GS_CREDENTIALS', None)

class Static(GoogleCloudStorage):
	location = 'static'
	bucket_name = getattr(settings, 'GS_BUCKET_NAME', None)
	file_overwrite = getattr(settings, 'GS_FILE_OVERWRITE', False)
	credentials = getattr(settings, 'GS_CREDENTIALS', None)
