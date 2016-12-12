# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'advisor',
        'USER': 'django',
        'PASSWORD': 'djangoDBpw',
        'HOST': 'dailab-advisor.cgxenmplsqo5.eu-central-1.rds.amazonaws.com',
        'PORT': '5432',
    }
}

# Need "memcache" to be installed in the system
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
