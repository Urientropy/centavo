# ==============================================================================
# ARCHIVO DE CONFIGURACIÓN DE DJANGO PARA "CENTAVO"
# Versión: FINAL - Producción-Ready v2.1 (Corregido)
# Optimizado para Azure App Service con PyMySQL y WhiteNoise.
# ==============================================================================

from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url
import pymysql

pymysql.install_as_MySQLdb()
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD Y ENTORNO
# ==============================================================================
SECRET_KEY = config('DJANGO_SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
APP_HOST = config('APP_HOST', default='localhost')
ALLOWED_HOSTS = [APP_HOST]
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
    'whitenoise.runserver_nostatic',
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
    )
}

# Si la URL es MySQL, agrega ssl manualmente
if DATABASES["default"]["ENGINE"] == "django.db.backends.mysql":
    DATABASES["default"]["OPTIONS"] = {
        "ssl": {"ca": "/home/site/wwwroot/certs/DigiCertGlobalRootCA.crt.pem"}
    }

# ==============================================================================
# ARCHIVOS ESTÁTICOS Y DE MEDIOS
# ==============================================================================
VITE_APP_DIR = BASE_DIR / "frontend"

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- INICIO DE LA CONFIGURACIÓN CORREGIDA ---
# Esta es la lista de directorios donde `collectstatic` buscará archivos,
# y donde el servidor de desarrollo buscará estáticos.
STATICFILES_DIRS = [
    # SIEMPRE incluimos la carpeta 'dist', ya que contiene los assets
    # compilados de Vite (para la SPA) y nuestros assets manuales (para la landing).
    VITE_APP_DIR / "dist",
]

# En modo de DESARROLLO, podemos añadir opcionalmente la carpeta 'public'
# si contiene assets que queremos servir directamente sin pasar por el 'build' de Vite.
if DEBUG:
    STATICFILES_DIRS.append(VITE_APP_DIR / "public")
# --- FIN DE LA CONFIGURACIÓN CORREGIDA ---

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
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    f"https://{APP_HOST}",
]
if DEBUG:
    CORS_ALLOWED_ORIGINS.extend(["http://localhost:8000", "http://127.0.0.1:8000"])

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