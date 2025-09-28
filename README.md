# Proyecto Centavo

Este es el repositorio para la aplicación web "Centavo", una herramienta de gestión financiera.

## Descripción

Centavo es una aplicación monolítica construida con Django y Django REST Framework, diseñada para ayudar a los usuarios a gestionar sus finanzas personales y de pequeñas empresas.

## Configuración del Entorno de Desarrollo

Sigue estos pasos para levantar el proyecto localmente:

1.  **Clona el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd centavo-project
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configura tus variables de entorno:**
    Copia el archivo `.env.example` a un nuevo archivo llamado `.env` y rellena los valores para tu base de datos local.

5.  **Ejecuta las migraciones:**
    ```bash
    python manage.py migrate
    ```

6.  **Inicia el servidor de desarrollo:**
    ```bash
    python manage.py runserver
    ```

## Despliegue en Azure

El despliegue en la infraestructura de Azure está automatizado a través de un pipeline de CI/CD en Azure DevOps.

-   Un `push` a la rama `main` despliega automáticamente a producción.
-   La URL de la aplicación es: `https://app-centavo.azurewebsites.net/`