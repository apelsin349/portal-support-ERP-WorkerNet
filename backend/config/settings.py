"""
Django settings for WorkerNet Portal project.
"""

import os
from pathlib import Path
import environ
import importlib.util

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    ALLOWED_HOSTS_EXTRA=(list, []),
)

# Read .env file
# Load variables from .env if present
env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# Разрешенные хосты: берем из окружения, добавляем дополнительные и удобные значения для разработки
ALLOWED_HOSTS = env('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '0.0.0.0'])
ALLOWED_HOSTS += env('ALLOWED_HOSTS_EXTRA', default=[])

# В режиме разработки можно автоматически разрешить локальные/внутренние IP
if DEBUG:
    # Добавьте сюда нужные IP для dev-среды; IP из окружения также поддерживается через ALLOWED_HOSTS_EXTRA
    for var in ('SERVER_NAME', 'HOST', 'HOSTNAME'):
        val = os.environ.get(var)
        if val and val not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(val)

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'django_celery_beat',
    'django_celery_results',
    'channels',
    'django_prometheus',
]

# Подключаем локальные приложения только если соответствующие пакеты существуют
def _app_exists(dotted: str) -> bool:
    module_to_check = dotted.split('.apps.')[0] if '.apps.' in dotted else dotted
    try:
        return importlib.util.find_spec(module_to_check) is not None
    except Exception:
        return False

_LOCAL_APP_CANDIDATES = [
    'app.core',
    'app.api',
    'app.utils',
]

LOCAL_APPS = [name for name in _LOCAL_APP_CANDIDATES if _app_exists(name)]

# Размещаем корневое приложение 'app' раньше admin, чтобы кастомная модель пользователя была доступна
INSTALLED_APPS = ['app'] + DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Пользовательская модель пользователя
AUTH_USER_MODEL = 'app.User'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'test': env.db('DATABASE_TEST_URL', default='sqlite:///test.db'),
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Поддерживаемые языки
LANGUAGES = [
    ('ru', 'Русский'),
    ('en', 'English'),
]

# Пути к файлам локализации
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = env('STATIC_URL', default='/static/')
STATIC_ROOT = env('STATIC_ROOT', default=BASE_DIR / 'staticfiles')

MEDIA_URL = env('MEDIA_URL', default='/media/')
MEDIA_ROOT = env('MEDIA_ROOT', default=BASE_DIR / 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(seconds=env('JWT_ACCESS_TOKEN_LIFETIME', default=3600)),
    'REFRESH_TOKEN_LIFETIME': timedelta(seconds=env('JWT_REFRESH_TOKEN_LIFETIME', default=604800)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': env('JWT_SECRET_KEY', default=SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# CORS settings
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = env('CORS_ALLOW_CREDENTIALS', default=True)

# CSRF settings
CSRF_TRUSTED_ORIGINS = env('CSRF_TRUSTED_ORIGINS', default=[])

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_CACHE_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/2')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379/3')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [env('REDIS_URL', default='redis://127.0.0.1:6379/0')],
        },
    },
}

# Email
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@workernet.com')

# Logging
# Гарантируем наличие каталога для логов
LOG_DIR = BASE_DIR / 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': str(LOG_DIR / 'django.log'),
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': env('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': env('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'app': {
            'handlers': ['console', 'file'],
            'level': env('LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}

# API Documentation
SPECTACULAR_SETTINGS = {
    'TITLE': 'WorkerNet Portal API',
    'DESCRIPTION': 'API for WorkerNet ERP Support Portal',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
}

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# File upload
FILE_UPLOAD_MAX_MEMORY_SIZE = env('MAX_UPLOAD_SIZE', default=10485760)  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = env('MAX_UPLOAD_SIZE', default=10485760)  # 10MB

# Feature Flags
FEATURE_FLAGS_ENABLED = env('FEATURE_FLAGS_ENABLED', default=True)
AB_TESTING_ENABLED = env('AB_TESTING_ENABLED', default=True)

# API Versioning
API_VERSION = env('API_VERSION', default='v1')
API_VERSIONING_STRATEGY = env('API_VERSIONING_STRATEGY', default='url')

# Multitenancy
MULTITENANCY_ENABLED = env('MULTITENANCY_ENABLED', default=True)
TENANT_HEADER = env('TENANT_HEADER', default='X-Tenant-ID')

# Performance
CACHE_TTL = env('CACHE_TTL', default=3600)
RATE_LIMIT_ENABLED = env('RATE_LIMIT_ENABLED', default=True)

# Development
DEVELOPMENT_MODE = env('DEVELOPMENT_MODE', default=False)
HOT_RELOAD = env('HOT_RELOAD', default=False)
DEBUG_TOOLBAR = env('DEBUG_TOOLBAR', default=False)

if DEBUG and DEBUG_TOOLBAR:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1', 'localhost']
