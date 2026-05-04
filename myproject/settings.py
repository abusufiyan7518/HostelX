# settings.py (Production Ready for Render)

from pathlib import Path
import os

BASE_DIR = Path(**file**).resolve().parent.parent

# ========================

# SECURITY SETTINGS

# ========================

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['.onrender.com', '127.0.0.1', 'localhost']

# ========================

# APPLICATIONS

# ========================

INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',

```
'ComplainXHostel_app',
```

]

# ========================

# MIDDLEWARE

# ========================

MIDDLEWARE = [
'django.middleware.security.SecurityMiddleware',

```
# WhiteNoise (for static files in production)
'whitenoise.middleware.WhiteNoiseMiddleware',

'django.contrib.sessions.middleware.SessionMiddleware',
'django.middleware.common.CommonMiddleware',
'django.middleware.csrf.CsrfViewMiddleware',
'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',
'django.middleware.clickjacking.XFrameOptionsMiddleware',
```

]

ROOT_URLCONF = 'myproject.urls'

# ========================

# TEMPLATES

# ========================

TEMPLATES = [
{
'BACKEND': 'django.template.backends.django.DjangoTemplates',
'DIRS': [BASE_DIR / 'ComplainXHostel_app' / 'templates'],
'APP_DIRS': True,
'OPTIONS': {
'context_processors': [
'django.template.context_processors.request',
'django.contrib.auth.context_processors.auth',
'django.contrib.messages.context_processors.messages',
],
},
},
]

WSGI_APPLICATION = 'myproject.wsgi.application'

# ========================

# DATABASE

# ========================

DATABASES = {
'default': {
'ENGINE': 'django.db.backends.sqlite3',
'NAME': BASE_DIR / 'db.sqlite3',
}
}

# ========================

# PASSWORD VALIDATION

# ========================

AUTH_PASSWORD_VALIDATORS = [
{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ========================

# INTERNATIONALIZATION

# ========================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True
USE_TZ = True

# ========================

# STATIC FILES (IMPORTANT)

# ========================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
BASE_DIR / "ComplainXHostel_app" / "static"
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ========================

# MEDIA FILES

# ========================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ========================

# AUTH SETTINGS

# ========================

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# ========================

# SECURITY HEADERS

# ========================

X_FRAME_OPTIONS = 'SAMEORIGIN'

# ========================

# RAZORPAY (MOVE TO ENV IN FUTURE)

# ========================

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'test_key')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'test_secret')

# ========================

# DEFAULT FIELD

# ========================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
