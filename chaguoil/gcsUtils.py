import os
from django.conf import settings
from storages.backends.gcloud import GoogleCloudStorage
from storages.backends.gcloud import GoogleCloudStaticStorage
from django.core.exceptions import ImproperlyConfigured
from google.oauth2 import service_account # Tunahitaji hii hapa

# =======================================================
# KUPAKIA CREDENTIALS
# =======================================================
# Huu msimbo hauhitajiki tena hapa. Django itapakia settings kabla ya kutumia hili file.
# Tunaondoa block ya try/except hapa ili kuepuka kupakia mara mbili au confusion.

# =======================================================
# STORAGE CLASS YA MEDIA FILES (UPLOADS)
# =======================================================
class MediaStorage(GoogleCloudStorage):
    """
    Darasa maalum la kuhifadhi faili za Media (picha za watumiaji, logos)
    """
    # Tunatumia vigezo vya settings moja kwa moja
    bucket_name = settings.GS_BUCKET_NAME
    location = 'media' 
    default_acl = 'publicRead'
    querystring_auth = False
    
    # Hakuna haja ya __init__ override. django-storages itatumia credentials
    # ambazo zimefafanuliwa kama GS_CREDENTIALS katika settings.py
    # (Kama ungetaka kutumia credentials dictionary, ingefaa kama GS_CREDENTIALS_DICT=CREDENTIALS_DICT hapa)
    

# =======================================================
# STORAGE CLASS YA STATIC FILES (CSS, JS)
# =======================================================
class StaticStorage(GoogleCloudStaticStorage):
    """
    Darasa maalum la kuhifadhi faili za Static (CSS, JS, n.k.)
    """
    # Tunatumia vigezo vya settings moja kwa moja
    bucket_name = settings.GS_BUCKET_NAME
    location = 'static'
    default_acl = 'publicRead'
    querystring_auth = False
    
    # Hakuna haja ya __init__ override.
