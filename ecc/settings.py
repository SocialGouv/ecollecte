import os
import environ
from dotenv import load_dotenv

env = environ.Env(
    DEBUG=(bool, False),
    EMAIL_USE_TLS=(bool, False),
    EMAIL_USE_SSL=(bool, False),
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*']

SHOW_DEBUG_TOOLBAR = env('SHOW_DEBUG_TOOLBAR', default=DEBUG)

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda r: SHOW_DEBUG_TOOLBAR,
    'SHOW_COLLAPSED': True,
}

# Application definition

INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'mozilla_django_oidc',  # Load after auth

    # Third-party apps
    'debug_toolbar',
    'model_utils',
    'ordered_model',
    'django_extensions',
    'actstream',
    'rest_framework',
    'celery',
    'django_celery_beat',
    'django_cleanup.apps.CleanupConfig',
    'ckeditor',
    'django_filters',
    'django_admin',
    'email_obfuscator',
    'django_softdelete',

    # Project's apps
    'backoffice',
    'config',
    'control',
    'demo',
    'editor',
    'faq',
    'reporting',
    'user_profiles',
    'utils',
    'session',
    'soft_deletion',
    'tos',
    'logs',
    'parametres',
    'alerte',
    'presentation',

    # Central app - loaded last
    'ecc',
]

# Keycloak configuration
KEYCLOAK_ACTIVE = env('KEYCLOAK_ACTIVE', default=False)
if KEYCLOAK_ACTIVE:
    KEYCLOAK_URL = env('KEYCLOAK_URL', default='http://localhost:8080/auth/')
    KEYCLOAK_REALM = env('KEYCLOAK_REALM', default='collectepro')
    OPENID_PREFIX = f'{KEYCLOAK_URL}realms/{KEYCLOAK_REALM}/protocol/openid-connect'
    OIDC_OP_JWKS_ENDPOINT = f'{OPENID_PREFIX}/certs'
    OIDC_OP_AUTHORIZATION_ENDPOINT = f'{OPENID_PREFIX}/auth'
    OIDC_OP_TOKEN_ENDPOINT = f'{OPENID_PREFIX}/token'
    OIDC_OP_USER_ENDPOINT = f'{OPENID_PREFIX}/userinfo'
    OIDC_OP_LOGOUT_ENDPOINT= f'{OPENID_PREFIX}/logout'
    OIDC_OP_LOGOUT_URL_METHOD = env('OIDC_OP_LOGOUT_URL_METHOD', default='ecc.provider_logout')
    OIDC_RP_CLIENT_ID = env('OIDC_RP_CLIENT_ID', default='')
    OIDC_RP_CLIENT_SECRET = env('OIDC_RP_CLIENT_SECRET', default='')
    OIDC_VERIFY_SSL = env('OIDC_VERIFY_SSL', default=True)
    OIDC_RP_SIGN_ALGO = env('OIDC_RP_SIGN_ALGO', default='RS256')
    AUTHENTICATION_BACKENDS = (
        'ecc.auth.EccOIDCAuthenticationBackend',
    )
    KEYCLOAK_ADMIN_USERNAME = env('KEYCLOAK_ADMIN_USERNAME', default='admin')
    KEYCLOAK_ADMIN_PASSWORD = env('KEYCLOAK_ADMIN_PASSWORD', default='admin')
    KEYCLOAK_URL_CLIENT_ID = env('KEYCLOAK_URL_CLIENT_ID', default='url_client_id')

LOGIN_REDIRECT_URL = "/accueil"
LOGOUT_REDIRECT_URL = "/"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django_permissions_policy.PermissionsPolicyMiddleware',
    'csp.middleware.CSPMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'tos.middleware.WelcomeMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'ecc.custom_cache_control_middleware.CustomCacheControlMiddleware',
]

ROOT_URLCONF = 'ecc.urls'

TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'ecc.context_processors.current_site',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecc.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {'default': env.db()}

SITE_ID = 1

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# HTTP Security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
FEATURE_POLICY = {
    'geolocation': 'none',
    'autoplay': ['self', ],
    'accelerometer': 'none',
    'camera': 'none',
    'gyroscope': 'none',
    'magnetometer': 'none',
    'microphone': 'none',
    'payment': 'none',
    'usb': 'none',
}
# Strict-Transport-Security
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Strict'
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
# Can't use Strict mode in order to use Keycloak
SESSION_COOKIE_SAMESITE = 'Lax'
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 30
# Content-Security-Policy
CSP_DEFAULT_SRC = env('CSP_DEFAULT_SRC', default=("'self'", "'frame-src youtube.com www.youtube.com;'"))

CSP_STYLE_SRC = env('CSP_STYLE_SRC', default=("'self'", "'unsafe-inline'"))
CSP_STYLE_SRC += ("https://static.piste.gouv.fr",)

CSP_SCRIPT_SRC = env('CSP_SCRIPT_SRC', default=("'self'", "'unsafe-eval'", "'unsafe-inline'"))
CSP_SCRIPT_SRC += ("https://code.jquery.com",)

CSP_IMG_SRC = env('CSP_IMG_SRC', default=("'self'","https:",))

if DEBUG:
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False

# Email
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER',)
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_TIMEOUT = env('EMAIL_TIMEOUT', default=3)

EMAIL_USE_TLS = env('EMAIL_USE_TLS')
EMAIL_USE_SSL = env('EMAIL_USE_SSL')

# Time we wait in between emails, to space them out and avoid going over our allowed email quota
EMAIL_SPACING_TIME_MILLIS = env('EMAIL_SPACING_TIME_MILLIS', default=10000)

# The user will get a warning when trying to add an inspector whose email doesn't end with EXPECTED_INSPECTOR_EMAIL_ENDINGS
EXPECTED_INSPECTOR_EMAIL_ENDINGS=env('EXPECTED_INSPECTOR_EMAIL_ENDINGS', default='')

SEND_EMAIL_WHEN_USER_ADDED = env('SEND_EMAIL_WHEN_USER_ADDED', default=False)
SEND_EMAIL_WHEN_USER_REMOVED = env('SEND_EMAIL_WHEN_USER_REMOVED', default=False)

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

LOGIN_URL = 'login'


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# A trick for DRF that does not seems to know about the locale
import locale
try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except locale.Error as e:
    pass  # setlocale can crash, for instance when running on Heroku.

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

ADMIN_URL = env('ADMIN_URL', default='admin/')

# Exclude incoming file if its mime type contains any of the following text
UPLOAD_FILE_MIME_TYPE_BLACKLIST = env(
    'UPLOAD_FILE_MIME_TYPE_BLACKLIST',
    default=('exe', 'msi', 'script'))

UPLOAD_FILE_EXTENSION_BLACKLIST = env('UPLOAD_FILE_EXTENSION_BLACKLIST', default=('.exe', '.dll', '.sql'))

UPLOAD_FILE_MAX_SIZE_MB = env('UPLOAD_FILE_MAX_SIZE_MB', default=256)

MAX_FILENAME_LENGTH = env('MAX_FILENAME_LENGTH', default=150)

STATIC_URL = '/static/'

# Collect static won't work if you haven't configured this
# django.core.exceptions.ImproperlyConfigured: You're using the staticfiles app without having set
#  the STATIC_ROOT setting to a filesystem path.
DEFAULT_STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_ROOT = env('STATIC_ROOT', default=DEFAULT_STATIC_ROOT)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    # NPM modules that we need to link in <script> tags directly : add them to static files.
    os.path.join(BASE_DIR, 'node_modules', 'bootstrap', 'dist', 'js'),
    os.path.join(BASE_DIR, 'node_modules', 'jquery', 'dist'),
]

# Want forever-cacheable files and compression support?
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
DEFAULT_MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_ROOT = env('MEDIA_ROOT', default=DEFAULT_MEDIA_ROOT)

SENDFILE_BACKEND = env('SENDFILE_BACKEND', default='sendfile.backends.simple')

PIWIK_TRACKER_BASE_URL = env('PIWIK_TRACKER_BASE_URL', default=None)
PIWIK_SITE_ID = env('PIWIK_SITE_ID', default=None)

SETTINGS_EXPORT = [
    'PIWIK_SITE_ID',
    'PIWIK_TRACKER_BASE_URL',
    'SESSION_EXPIRE_SECONDS',
    'DEBUG',
    'SAVE_IP_ADDRESS',
    'ENV_NAME',
    'KEYCLOAK_ACTIVE',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    )
}

if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
        'rest_framework.renderers.BrowsableAPIRenderer',
    )

CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_QUEUE = env('CELERY_QUEUE', default='default')
HTTP_AUTHORIZATION = env('HTTP_AUTHORIZATION', default=None)

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ]
    }
}

# Demo application
DEMO_INSPECTOR_USERNAME = env('DEMO_INSPECTOR_USERNAME', default=None)
DEMO_AUDITED_USERNAME = env('DEMO_AUDITED_USERNAME', default=None)
ALLOW_DEMO_LOGIN = env('ALLOW_DEMO_LOGIN', default=False)

# Session management
SESSION_EXPIRE_SECONDS = env('SESSION_EXPIRE_SECONDS', default=24*60*60)
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True

# Ip adress
SAVE_IP_ADDRESS = env('SAVE_IP_ADDRESS', default=False)

# Environnement name
ENV_NAME = env ('ENV_NAME', default='')

# Url of collecte-pro in questionnaire
QUESTIONNAIRE_SITE_URL = env ('QUESTIONNAIRE_SITE_URL', default='')

# Mise à jour pour Django>=3.2
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Jours de relance par défaut avant échéance d'un questionnaire
JOURS_ECHEANCE = env('JOURS_ECHEANCE', default=7)

# Indique si la page par défaut est celle de présentation
PRESENTATION_ACTIVE = env('PRESENTATION_ACTIVE', default=True)

#Captcha
load_dotenv()
GRANT_TYPE = os.getenv('GRANT_TYPE')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
#SCOPE = os.getenv('SCOPE')

OAUTH_URL = os.getenv('OAUTH_URL')
SIMPLE_CAPTCHA_ENDPOINT_URL = os.getenv('SIMPLE_CAPTCHA_ENDPOINT_URL')
VALIDER_CAPTCHA_URL = os.getenv('VALIDER_CAPTCHA_URL')


    
