# ==============================================================================
# ARCHIVO DE CONFIGURACIÓN DE DJANGO PARA "CENTAVO"
# Versión: Producción-Ready v1.0
# Optimizado para Azure App Service con despliegue manual/VS Code.
# ==============================================================================

from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url
import pymysql

# Le decimos a Django que use PyMySQL en lugar del conector por defecto.
# Esto debe hacerse ANTES de cualquier otra operación de base de datos.
pymysql.install_as_MySQLdb()

# --- Rutas Base ---
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD Y ENTORNO
# ==============================================================================

SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = []
# El nombre de tu App Service. Debe estar aquí para producción.
ALLOWED_HOST_PROD = config('ALLOWED_HOST', default=None)
if ALLOWED_HOST_PROD:
    ALLOWED_HOSTS.append(ALLOWED_HOST_PROD)

if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])

# ==============================================================================
# APLICACIONES
# ==============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # Mantenlo simple, WhiteNoise es inteligente.
    'django.contrib.staticfiles',
    'django_vite',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_extensions',
    'users.apps.UsersConfig',
    'tenants.apps.TenantsConfig',
    'inventory.apps.InventoryConfig',
    'products.apps.ProductsConfig',
    'production.apps.ProductionConfig',
    'finance.apps.FinanceConfig',
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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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

# ==============================================================================
# BASE DE DATOS
# ==============================================================================

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=not DEBUG  # SSL solo se requiere cuando NO estamos en DEBUG.
    )
}

# ==============================================================================
# ARCHIVOS ESTÁTICOS Y DE MEDIOS
# ==============================================================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==============================================================================
# CONFIGURACIONES DE TERCEROS
# ==============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 6
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# Orígenes CORS permitidos. Añadiremos el de producción más tarde.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
if DEBUG:
    CORS_ALLOWED_ORIGINS.extend(["http://localhost:8000", "http://127.0.0.1:8000"])

VITE_APP_DIR = BASE_DIR / "frontend"
DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "manifest_path": VITE_APP_DIR / "dist" / "manifest.json",
    }
}

# ==============================================================================
# OTRAS CONFIGURACIONES DE DJANGO
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-ni'
TIME_ZONE = 'America/Managua'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'