DATABASES = {

        'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': 'chaguoil',
        'NAME': 'mafuta',
        'USER': 'postgres',
        'PASSWORD' : '1152',
        'HOST' : 'localhost'

 }

}

MEDIA_URL = '/media/'
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Only used for collectstatic


