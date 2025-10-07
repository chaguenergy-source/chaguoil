from storages.backends.gcloud import GoogleCloudStorage

# Njia rahisi zaidi: GoogleCloudStorage itachukua settings zote (GS_BUCKET_NAME, GS_CREDENTIALS, n.k.)
# kutoka settings.py. Tunatambulisha tu eneo la faili.

class MediaStorage(GoogleCloudStorage):
    """
    Hutumiwa kwa ajili ya Media Files (mfano: Company Logo)
    """
    # Location ndio kitu pekee tunachobadilisha kutoka kwa default
    location = 'media' 


class StaticStorage(GoogleCloudStorage):
    """
    Hutumiwa kwa ajili ya Static Files (CSS, JS)
    """
    # Location ndio kitu pekee tunachobadilisha kutoka kwa default
    location = 'static' 
