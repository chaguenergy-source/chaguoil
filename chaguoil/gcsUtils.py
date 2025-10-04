from storages.backends.gcloud import GoogleCloudStorage


Media = lambda: GoogleCloudStorage(location='media')