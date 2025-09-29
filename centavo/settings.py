# ==============================================================================
# ARCHIVO DE CONFIGURACIÓN DE DJANGO PARA "CENTAVO"
# Versión: FINAL - Producción-Ready v2.0
# Optimizado para Azure App Service con PyMySQL y WhiteNoise.
# ==============================================================================

from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url
import pymysql

# --- Configuración Fundamental ---
# Le dice a Django que use PyMySQL en lugar del conector por defecto.
# Debe ejecutarse antes de cualquier operación de base de datos.
pymysql.install_as_MySQLdb()

# Define la ruta base del proyecto.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD Y ENTORNO
# ==============================================================================

# Lee la SECRET_KEY de las variables de entorno. CRÍTICO para producción.
SECRET_KEY = config('DJANGO_SECRET_KEY')

# Lee el modo DEBUG de las variables de entorno. Será 'False' en Azure.
DEBUG = config('DEBUG', default=False, cast=bool)

# Lee el host de producción desde las variables de entorno.
APP_HOST = config('APP_HOST', default='localhost')
ALLOWED_HOSTS = [APP_HOST]

# Añade hosts de desarrollo local solo si DEBUG es True.
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
    'whitenoise.runserver_nostatic', # Necesario para servir estáticos en desarrollo.
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
    # WhiteNoise Middleware debe ir justo después de SecurityMiddleware.
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
STATICFILES_DIRS = []

# En modo de DESARROLLO, le decimos a Django que busque estáticos
# en la carpeta 'public' o 'assets' de nuestro frontend.
# ¡AJUSTA ESTA RUTA SI TUS IMÁGENES ESTÁN EN OTRO LADO!
if DEBUG:
    STATICFILES_DIRS.append(BASE_DIR / "frontend/src/assets")
    STATICFILES_DIRS.append(BASE_DIR / "frontend/public")


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

# Orígenes CORS permitidos.
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    f"https://{APP_HOST}",
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