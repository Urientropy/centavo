# ==============================================================================
# ARCHIVO DE CONFIGURACIÓN DE DJANGO PARA "CENTAVO"
# Versión: FINAL v6.0 - Universal Dev/Prod
# ==============================================================================

from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url
import os


# --- Configuración Fundamental ---
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# CONFIGURACIÓN DE SEGURIDAD Y ENTORNO
# ==============================================================================
SECRET_KEY = config("DJANGO_SECRET_KEY", default="dev-secret-change-me-please-set-in-prod")
DEBUG = config("DEBUG", default=True, cast=bool)

# --- CONFIGURACIÓN DE HOSTS PERMITIDOS (Universal) ---
# Lee el hostname que Azure proporciona automáticamente en producción.
ALLOWED_HOSTS = []
WEBSITE_HOSTNAME = os.environ.get('WEBSITE_HOSTNAME')
if WEBSITE_HOSTNAME:
    ALLOWED_HOSTS.append(WEBSITE_HOSTNAME)
# Si estamos en modo DEBUG, añadimos los hosts de desarrollo.
if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])

# ==============================================================================
# APLICACIONES (SIN CAMBIOS)
# ==============================================================================
INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "finance", "inventory", "products", "production", "tenants", "users",
    "rest_framework", "rest_framework_simplejwt", "rest_framework_simplejwt.token_blacklist",
    "corsheaders", "django_vite", "django_extensions",
]
if DEBUG:
    INSTALLED_APPS.append('whitenoise.runserver_nostatic')

# ==============================================================================
# MIDDLEWARE (SIN CAMBIOS)
# ==============================================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ==============================================================================
# CORS / CSRF (Universal)
# ==============================================================================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
if WEBSITE_HOSTNAME:
    CORS_ALLOWED_ORIGINS.append(f"https://{WEBSITE_HOSTNAME}")

CSRF_TRUSTED_ORIGINS = []
if WEBSITE_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{WEBSITE_HOSTNAME}")
if DEBUG:
    CSRF_TRUSTED_ORIGINS.extend([
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ])

# --- CONFIGURACIÓN PARA PROXIES (AZURE) ---
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'None'
    CSRF_COOKIE_SAMESITE = 'None'

# ==============================================================================
# RUTAS, PLANTILLAS Y WSGI (SIN CAMBIOS)
# ==============================================================================
ROOT_URLCONF = "centavo.urls"
WSGI_APPLICATION = "centavo.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [BASE_DIR / "templates"],"APP_DIRS": True,"OPTIONS": {"context_processors": ["django.template.context_processors.debug", "django.template.context_processors.request","django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages",],},},]

# ==============================================================================
# BASE DE DATOS (Universal)
# ==============================================================================
if "DATABASE_URL" in os.environ:
    # Estamos en PRODUCCIÓN (Azure)
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True # psycopg2 SÍ entiende esto correctamente
        )
    }
else:
    # Estamos en DESARROLLO LOCAL
    DATABASES = {
        "default": {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==============================================================================
# ARCHIVOS ESTÁTICOS, MEDIOS Y VITE (LA SOLUCIÓN UNIVERSAL)
# ==============================================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Directorio donde `collectstatic` reunirá todos los archivos para producción.
# WhiteNoise servirá los archivos desde aquí.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
if DEBUG:
    WHITENOISE_IGNORE_MISSING_FILES = True

# Directorios adicionales para buscar archivos estáticos.
STATICFILES_DIRS = [
    # La carpeta donde django-vite buscará los assets compilados por `npm run build`.
    BASE_DIR / "frontend" / "dist",
]

# La carpeta raíz de la aplicación Vite.
VITE_APP_DIR = BASE_DIR / "frontend"

# Configuración de DJANGO_VITE para manejar ambos entornos.
DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        # En producción, Django-Vite buscará aquí el manifest.json.
        "manifest_path": VITE_APP_DIR / "dist" / ".vite" / "manifest.json",
    }
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ==============================================================================
# OTRAS CONFIGURACIONES (SIN CAMBIOS)
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [{"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},{"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},{"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},]
AUTH_USER_MODEL = "users.User"
LANGUAGE_CODE = "es-es"
TIME_ZONE = "America/Managua"
USE_I18N = True
USE_TZ = True
REST_FRAMEWORK = {'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),"DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated",],'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination','PAGE_SIZE': 6}
SIMPLE_JWT = {"ACCESS_TOKEN_LIFETIME": timedelta(minutes=60), "REFRESH_TOKEN_LIFETIME": timedelta(days=1),"ROTATE_REFRESH_TOKENS": True, "BLACKLIST_AFTER_ROTATION": True, "UPDATE_LAST_LOGIN": True,"ALGORITHM": "HS256", "SIGNING_KEY": SECRET_KEY, "VERIFYING_KEY": None, "AUDIENCE": None,"ISSUER": None, "JWK_URL": None, "LEEWAY": 0, "AUTH_HEADER_TYPES": ("Bearer",),"AUTH_HEADER_NAME": "HTTP_AUTHORIZATION", "USER_ID_FIELD": "id", "USER_ID_CLAIM": "user_id","USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule","AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",), "TOKEN_TYPE_CLAIM": "token_type","TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser", "JTI_CLAIM": "jti","SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp", "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),"SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),}