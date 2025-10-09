import os
from django.core.wsgi import get_wsgi_application

# =========================================================================
# === HII NDIO SEHEMU YA MAREKEBISHO KWA GUNICORN/GCS FALLBACK ===
# Tunalazimisha import ya storages.backends.gcloud mapema
# Hii inahakikisha darasa la GCS linapatikana kabla ya Django kutathmini settings.
try:
    import storages.backends.gcloud 
except ImportError:
    # Hii haipaswi kutokea kwani kifurushi kimesakinishwa.
    # Tumeruhusu kupitishwa ili kuzuia kashfa isiyo ya lazima.
    pass
# =========================================================================

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chaguoil.settings')

application = get_wsgi_application()
