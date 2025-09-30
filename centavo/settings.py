# ==============================================================================
# ARCHIVO DE CONFIGURACIÓN DE DJANGO PARA "CENTAVO"
# Versión: FINAL v4.1 - Corregido y Optimizado
# ==============================================================================

from pathlib import Path
from datetime import timedelta
from decouple import config
import dj_database_url

# ------------------------------
# BASE DIR
# Descripción: Define el directorio raíz del proyecto para que las rutas
# relativas funcionen de manera consistente en cualquier sistema operativo.
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------
# VARIABLES DE ENTORNO
# Descripción: Carga de configuraciones sensibles y específicas del entorno
# desde un archivo .env (para desarrollo) o variables de entorno del sistema
# (para producción), utilizando la librería python-decouple.
# ------------------------------
SECRET_KEY = config("DJANGO_SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
DATABASE_URL = config("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
ALLOWED_HOST = config("ALLOWED_HOST", default="127.0.0.1")

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    ALLOWED_HOST,
]

# ------------------------------
# APLICACIONES
# Descripción: Lista de todas las aplicaciones de Django que se activan
# en este proyecto. El orden puede ser importante para plantillas y estáticos.
# ------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Apps locales (en orden alfabético para mayor legibilidad)
    "finance",
    "inventory",
    "products",
    "production",  # <-- CORRECCIÓN 1: App 'production' añadida.
    "tenants",
    "users",

    # Terceros
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_vite",
    "django_extensions", # Muy útil para el comando 'show_urls'
]

# ------------------------------
# MIDDLEWARE
# Descripción: Una serie de "capas" que procesan las peticiones y respuestas.
# El orden es crítico.
# ------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise se coloca aquí, justo después de SecurityMiddleware, para servir estáticos eficientemente.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware", # Maneja las políticas de Cross-Origin Resource Sharing.
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------------
# CORS (CONFIGURACIÓN RECOMENDADA PARA APIs)
# Descripción: Define qué orígenes (dominios) tienen permitido hacer peticiones
# a nuestra API desde un navegador.
# ------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173", # Origen del frontend de Vite en desarrollo
    "http://127.0.0.1:5173",
]
# En producción, deberás añadir la URL de tu frontend, ej: "https://www.tuapp.com"

# ------------------------------
# URLS Y WSGI
# ------------------------------
ROOT_URLCONF = "centavo.urls"
WSGI_APPLICATION = "centavo.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------
# BASE DE DATOS
# Descripción: Configuración de la base de datos. dj_database_url permite
# configurar la BD a través de una única URL (ideal para producción).
# ------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ------------------------------
# TEMPLATES
# Descripción: Configuración de cómo Django encuentra y renderiza plantillas HTML.
# ------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ------------------------------
# AUTH
# Descripción: Configuración del sistema de autenticación de usuarios.
# ------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
AUTH_USER_MODEL = "users.User"

# ------------------------------
# INTERNACIONALIZACIÓN
# ------------------------------
LANGUAGE_CODE = "es-es" # 'es-ni' puede no ser soportado, 'es-es' es más seguro y general.
TIME_ZONE = "America/Managua"
USE_I18N = True
USE_TZ = True

# ------------------------------
# ESTÁTICOS Y MEDIA
# Descripción: Configuración para manejar archivos estáticos (CSS, JS, imágenes
# de la UI) y archivos media (subidos por el usuario).
# ------------------------------
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STATIC_ROOT = BASE_DIR / "staticfiles" # Carpeta para 'collectstatic' en producción.

# --- CORRECCIÓN 2: Directorios de archivos estáticos para desarrollo ---
STATICFILES_DIRS = [
    BASE_DIR / "frontend" / "dist", # Para los assets compilados de Vite
    BASE_DIR / "static",           # Para assets estáticos globales (imágenes, fuentes, etc.)
]
# Almacenamiento para archivos estáticos en producción, gestionado por WhiteNoise.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ------------------------------
# DJANGO VITE CONFIG
# Descripción: Integración con Vite para el desarrollo del frontend.
# ------------------------------
# La lógica para encontrar el manifest.json es correcta, pero es más robusto
# apuntar a la ruta que Vite 3+ usa por defecto.
manifest_path = BASE_DIR / "frontend" / "dist" / ".vite" / "manifest.json"

DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "manifest_path": manifest_path,
    }
}

# ------------------------------
# REST FRAMEWORK (CONFIGURACIÓN RECOMENDADA)
# Descripción: Configuración global para Django REST Framework.
# ------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 6
}

# ------------------------------
# SIMPLE JWT (CONFIGURACIÓN RECOMENDADA)
# Descripción: Configuración para los tokens de autenticación JWT.
# ------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}