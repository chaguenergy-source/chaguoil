import os
import time
import sys
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from storages.backends.gcloud import GoogleCloudStorage
from django.conf import settings
from django.core.files.storage import FileSystemStorage 

class Command(BaseCommand):
    """
    Amri hii inajaribu GCS moja kwa moja na kisha inafanya uchunguzi wa kina wa
    darasa linalotumika na default_storage ili kugundua kwa nini inarudi nyuma.
    """
    help = 'Tests Google Cloud Storage (GCS) connectivity and deep storage inspection.'

    def handle(self, *args, **options):
        # 1. Kujaribu kuunda mfano mpya wa GCS Storage (New Instance)
        # Hii inathibitisha credentials na muunganisho bado UNAFANYA KAZI
        self.stdout.write(self.style.NOTICE(">> Kujaribu kuunda mfano mpya wa GoogleCloudStorage moja kwa moja..."))

        # GS_CREDENTIALS sasa zinapatikana kama service_account.Credentials object katika settings
        if not hasattr(settings, 'GS_CREDENTIALS') or not settings.GS_CREDENTIALS:
             self.stdout.write(self.style.ERROR("!! GCS Credentials hazikuonekana kwenye settings.py. Angalia logi za settings.py !!"))
             sys.exit(1)

        try:
            # Tunatumia credentials zilizo kwenye settings moja kwa moja
            gcs_storage_instance = GoogleCloudStorage(
                bucket_name=settings.GS_BUCKET_NAME,
                credentials=settings.GS_CREDENTIALS,
                location='test-path' 
            )
            
            self.stdout.write(self.style.SUCCESS(">> SUCCESS: GoogleCloudStorage imefafanuliwa na credentials ZIMEPITA uhakiki wa awali."))

            # Kufanya Upakiaji wa Kawaida wa Kulazimishwa
            test_filename = f"force_test_{int(time.time())}.txt"
            test_content = b"This is a FORCED GCS connectivity test using the settings-based method."

            self.stdout.write(self.style.NOTICE(f"\n>> Kujaribu KULAZIMISHA upakiaji wa '{test_filename}' kwa kutumia mfano mpya wa GCS..."))
            path = gcs_storage_instance.save(test_filename, ContentFile(test_content))

            if gcs_storage_instance.exists(path):
                self.stdout.write(self.style.SUCCESS(f"SUCCESS: Upakiaji wa KULAZIMISHWA umefanya kazi kwenye GCS: {path}"))
                gcs_storage_instance.delete(path)
                self.stdout.write(self.style.WARNING("Faili la majaribio limefutwa kwa mafanikio."))
            else:
                self.stdout.write(self.style.ERROR(f"ERROR: Faili halikuonekana baada ya kupakia. Hii ni ajabu."))

        except Exception as e:
            self.stdout.write(self.style.ERROR("!! UPAKIAJI WA KULAZIMISHWA UMEZUIWA - KOSA LA MUUNGANISHO WA API !!"))
            self.stdout.write(self.style.ERROR(f"Kosa kamili: {e}"))
            sys.exit(1)


        # 2. UCHUNGUZI WA KINA WA DEFAULT_FILE_STORAGE (Hili ndilo jibu)
        self.stdout.write(self.style.NOTICE("\n>> KUANGALIA DEFAULT_FILE_STORAGE KWA UNDANI:"))

        # Jina kamili la darasa la default_storage
        storage_class_name = default_storage.__class__.__module__ + "." + default_storage.__class__.__name__
        self.stdout.write(self.style.WARNING(f"Aina HALISI ya default_storage: {storage_class_name}"))

        # Kagua kama ni GCS au FileSystemStorage
        is_default_gcs = isinstance(default_storage, GoogleCloudStorage)
        is_default_fs = isinstance(default_storage, FileSystemStorage)

        self.stdout.write(self.style.WARNING(f"Uthibitisho (ni GCS?): {is_default_gcs}"))

        if is_default_gcs:
            self.stdout.write(self.style.SUCCESS(">> MAFANIKIO KUU: DEFAULT_FILE_STORAGE sasa inatumia GCS!"))
        elif is_default_fs:
            self.stdout.write(self.style.ERROR("!! SHIDA INATHIBITISHWA: DEFAULT_FILE_STORAGE inatumia FileSystemStorage (Fallback)."))
            self.stdout.write(self.style.ERROR("Hii inamaanisha Django ILISHINDWA kupakia darasa lililotajwa katika DEFAULT_FILE_STORAGE string."))
        else:
            self.stdout.write(self.style.ERROR("!! DEFAULT_FILE_STORAGE SI GCS wala FileSystemStorage. Tatizo la ajabu sana."))