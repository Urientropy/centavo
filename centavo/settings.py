# ==============================================================================
# ARCHIVO DE CONFIGURACIÓN DE DJANGO PARA "CENTAVO"
# Versión: FINAL v5.0 - A Prueba de Balas para Azure
# ==============================================================================

from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
import pymysql

# --- Configuración Fundamental ---
pymysql.install_as_MySQLdb()
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD Y ENTORNO
# ==============================================================================
# En producción, estos valores SIEMPRE vendrán del App Service Settings.
# En local, .env será leído por tu runner (ej. Pycharm, o si usas python-decouple).
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
# DEBUG nunca debe ser True en producción. Si la variable no existe, es False.
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# --- CONFIGURACIÓN DE HOSTS PERMITIDOS ---
ALLOWED_HOSTS = []
# Leemos el host de producción desde las variables de entorno de Azure.
APP_HOST = os.environ.get('APP_HOST')
if APP_HOST:
    ALLOWED_HOSTS.append(APP_HOST)
# Si estamos en modo DEBUG, añadimos los hosts de desarrollo.
if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])

# --- CONFIGURACIÓN PARA PROXIES (AZURE) ---
# Confía en las cabeceras que añade el equilibrador de carga de Azure.
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# --- CONFIGURACIÓN DE SEGURIDAD CSRF y CORS ---
# Orígenes de confianza para peticiones seguras.
CSRF_TRUSTED_ORIGINS = []
if APP_HOST:
    CSRF_TRUSTED_ORIGINS.append(f"https://{APP_HOST}")

CORS_ALLOWED_ORIGINS = []
if APP_HOST:
    CORS_ALLOWED_ORIGINS.append(f"https://{APP_HOST}")
if DEBUG:
    CORS_ALLOWED_ORIGINS.extend([
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:8000", "http://127.0.0.1:8000",
    ])

# ==============================================================================
# APLICACIONES
# ==============================================================================
INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages',
    'whitenoise.runserver_nostatic', 'django.contrib.staticfiles',
    'django_vite', 'rest_framework', 'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist', 'corsheaders', 'django_extensions',
    'users.apps.UsersConfig', 'tenants.apps.TenantsConfig', 'inventory.apps.InventoryConfig',
    'products.apps.ProductsConfig', 'production.apps.ProductionConfig', 'finance.apps.FinanceConfig',
]
AUTH_USER_MODEL = 'users.User'

# ==============================================================================
# MIDDLEWARE
# ==============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==============================================================================
# RUTAS, PLANTILLAS Y WSGI
# ==============================================================================
ROOT_URLCONF = 'centavo.urls'
WSGI_APPLICATION = 'centavo.wsgi.application'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates','DIRS': [BASE_DIR / "templates"],'APP_DIRS': True,'OPTIONS': {'context_processors': ['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages',],},},]

# ==============================================================================
# BASE DE DATOS (Lógica Universal para Local y Producción)
# ==============================================================================
if 'DATABASE_URL' in os.environ:
    # Estamos en PRODUCCIÓN (Azure)
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
    # Añadimos explícitamente las opciones de SSL para PyMySQL/MariaDB
    DATABASES['default']['OPTIONS'] = {
        'ssl': {
            'ca': str(BASE_DIR / 'certs/DigiCertGlobalRootG2.crt.pem')
        }
    }
else:
    # Estamos en DESARROLLO LOCAL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==============================================================================
# ARCHIVOS ESTÁTICOS Y DE MEDIOS
# ==============================================================================
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [BASE_DIR / "frontend" / "dist"]
if DEBUG:
    STATICFILES_DIRS.append(BASE_DIR / "frontend/public")
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==============================================================================
# CONFIGURACIONES DE TERCEROS
# ==============================================================================
REST_FRAMEWORK = {'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),'DEFAULT_PERMISSION_CLASSES': ["rest_framework.permissions.IsAuthenticated",],'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination','PAGE_SIZE': 6}
SIMPLE_JWT = {'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),'REFRESH_TOKEN_LIFETIME': timedelta(days=1),'ROTATE_REFRESH_TOKENS': True,'BLACKLIST_AFTER_ROTATION': True,'UPDATE_LAST_LOGIN': True,'ALGORITHM': "HS256",'SIGNING_KEY': SECRET_KEY,'VERIFYING_KEY': None,'AUDIENCE': None,'ISSUER': None,'JWK_URL': None,'LEEWAY': 0,'AUTH_HEADER_TYPES': ("Bearer",),'AUTH_HEADER_NAME': "HTTP_AUTHORIZATION",'USER_ID_FIELD': "id",'USER_ID_CLAIM': "user_id",'USER_AUTHENTICATION_RULE': "rest_framework_simplejwt.authentication.default_user_authentication_rule",'AUTH_TOKEN_CLASSES': ("rest_framework_simplejwt.tokens.AccessToken",),'TOKEN_TYPE_CLAIM': "token_type",'TOKEN_USER_CLASS': "rest_framework_simplejwt.models.TokenUser",'JTI_CLAIM': "jti",'SLIDING_TOKEN_REFRESH_EXP_CLAIM': "refresh_exp",'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),}
VITE_APP_DIR = BASE_DIR / "frontend"
DJANGO_VITE = {"default": {"dev_mode": DEBUG,"manifest_path": VITE_APP_DIR / "dist" / ".vite" / "manifest.json",}}

# ==============================================================================
# OTRAS CONFIGURACIONES
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},{'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},{'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},]
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Managua'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'