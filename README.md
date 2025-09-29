 

---



# Centavo - Plataforma de Gestión para Productores

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white) ![Vue.js](https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D)

**Centavo** es una aplicación web robusta, diseñada para empoderar a pequeños y medianos productores, artesanos y fabricantes. Su misión es reemplazar las hojas de cálculo complejas y los registros manuales con una plataforma centralizada, inteligente y fácil de usar para la gestión integral del ciclo de producción y finanzas.

---

## 1. Justificación y Propósito

En el corazón de la economía productiva, miles de pequeños empresarios luchan diariamente con la gestión de sus operaciones. Los desafíos son universales:

*   **Falta de Visibilidad:** ¿Cuánto inventario de materia prima queda realmente? ¿Cuál es el costo real de fabricar un producto?
*   **Gestión Ineficiente:** El tiempo dedicado a registrar manualmente compras, producciones y gastos es tiempo que no se invierte en crecer el negocio.
*   **Decisiones a Ciegas:** Sin datos centralizados, es casi imposible calcular la rentabilidad real, identificar los productos más rentables o planificar la producción de manera efectiva.

**Centavo nace para resolver estos problemas.** Su propósito es proporcionar una **fuente única de la verdad** para el productor, automatizando tareas tediosas y transformando datos crudos en inteligencia de negocio accionable. Centavo permite a sus usuarios tomar el control de su inventario, entender sus costos, optimizar su producción y, en última instancia, aumentar su rentabilidad.

## 2. Características Principales (Features)

El sistema está construido sobre una arquitectura multi-tenant, garantizando que los datos de cada empresa estén completamente aislados y seguros.

### Módulo de Autenticación y Seguridad
*   **Multi-Tenancy por Diseño:** Cada recurso en la aplicación (materias primas, productos, gastos, etc.) está estrictamente vinculado a una empresa (`Tenant`), garantizando un aislamiento de datos completo.
*   **Autenticación JWT:** Sistema de autenticación moderno y seguro basado en JSON Web Tokens (`djangorestframework-simplejwt`) con flujos de registro, login, logout y refresco de token.

### Módulo de Inventario
*   **Gestión de Materias Primas:** CRUD completo para el catálogo de insumos, con búsqueda, paginación y filtrado.
*   **Gestión de Lotes de Compra:** Registro de cada compra de materia prima, incluyendo fecha, cantidad y costo total.
*   **Control de Stock Preciso:** El sistema gestiona el stock restante (`quantity_remaining`) de cada lote de forma individual, permitiendo una trazabilidad perfecta.
*   **Cálculo de Stock Total:** La API calcula y expone automáticamente el stock total disponible de cada materia prima, sumando el stock restante de todos sus lotes.

### Módulo de Productos y Producción
*   **Catálogo de Productos Terminados:** CRUD completo para los productos que el usuario vende.
*   **Gestión de Recetas (Bill of Materials):** Una interfaz de API avanzada permite definir y gestionar la lista de materias primas y cantidades necesarias para fabricar cada producto (escritura anidada).
*   **Registro de Producción con Lógica FIFO:** El corazón del sistema. Un endpoint transaccional y seguro permite registrar la producción de nuevos lotes, descontando automáticamente las materias primas de los lotes de compra más antiguos primero (First-In, First-Out).

### Módulo de Finanzas
*   **Registro Manual de Ingresos y Gastos:** Endpoints CRUD para que el usuario pueda registrar transacciones financieras que no están directamente ligadas a la producción (ej. alquiler, ventas manuales).
*   **Visualización de Datos:** Endpoints optimizados para alimentar dashboards y gráficos, como el historial de evolución de stock de un producto.

---

### **Funcionalidades Futuras (En Desarrollo Activo)**

Las siguientes funcionalidades están planificadas y en desarrollo para las próximas versiones de Centavo, consolidando su posición como una plataforma de gestión integral.

#### **Sprint 3: Automatización e Inteligencia Financiera**
*   **Captura Inteligente de Gastos:** Un endpoint que, utilizando **Azure AI Vision**, procesará imágenes de facturas subidas por el usuario. La IA extraerá automáticamente la fecha, el total y el proveedor, pre-llenando el formulario de gastos y vinculando la imagen como comprobante.
*   **Dashboard de "Salud Financiera":** Un nuevo endpoint de agregación (`/api/v1/dashboard/financial-summary/`) que calculará en tiempo real métricas clave como Ingresos Totales, Costos de Producción, Gastos Operativos y **Beneficio Neto**, alimentando una visualización gráfica de la rentabilidad.
*   **Gestión de Clientes y Facturación:** Módulos de CRM y Ventas que permitirán asociar ventas a clientes específicos, descontar stock de productos terminados y generar **facturas en PDF** bajo demanda usando una librería como WeasyPrint.

#### **Sprint 4: Comunidad y Herramientas de Estandarización**
*   **Marketplace de Recursos:** Una plataforma comunitaria donde los usuarios podrán subir y descargar recursos (patrones, moldes, plantillas). La gestión de archivos se realizará de forma segura a través de **Azure Blob Storage**.
*   **Calculadora de Proporciones:** Una herramienta de API que permitirá escalar recetas dinámicamente, facilitando la creación de cotizaciones y la producción personalizada.
*   **Asistente Virtual (v1):** Un sistema de sugerencias basado en reglas que analizará los datos del usuario para ofrecer consejos proactivos sobre estandarización de insumos y optimización de costos.

#### **Sprint 5: Monetización e Inteligencia de Negocio Avanzada**
*   **Monetización del Marketplace:** Integración con una **pasarela de pago** (ej. Stripe) para permitir la venta de recursos premium dentro de la plataforma.
*   **Reportes Avanzados:** Endpoints analíticos para ofrecer simulaciones de pronósticos de ventas y análisis de rentabilidad por producto.
*   **Módulo de Pre-declaración Fiscal:** La funcionalidad culminante que consolidará todos los datos financieros del período para generar un borrador del formulario de pago de impuestos, adaptado a la normativa fiscal nicaragüense.

---

### Herramientas de Desarrollo
*   **Sembrado de Base de Datos (`seed_db`):** Un comando de gestión personalizado que puebla la base de datos con un conjunto completo de datos de prueba realistas, permitiendo un desarrollo y pruebas más rápidos y consistentes.

## 3. Arquitectura y Principios de Diseño

Centavo está construido siguiendo principios de software modernos para garantizar su escalabilidad, mantenibilidad y seguridad.

*   **Backend:** Monolito robusto basado en **Django** y **Django REST Framework (DRF)**.
*   **Frontend:** Single-Page Application (SPA) construida con **Vue.js** y **Vite**, operando como una Progressive Web App (PWA).
*   **Integración:** **`django-vite`** para una integración transparente entre el backend y el frontend.
*   **Paradigma API-First:** El backend expone una API RESTful completa y bien documentada, diseñada para ser consumida por el cliente de Vue.js.
*   **Separación de Responsabilidades:** La lógica de negocio compleja (como el ciclo de producción) está encapsulada en **Servicios** dedicados, manteniendo los `Views` de la API delgados y enfocados en manejar las peticiones HTTP.
*   **Base de Datos:** Diseñado para ser agnóstico, utilizando el ORM de Django. Se inicia con **SQLite** para desarrollo y está preparado para migrar a sistemas más robustos como **MySQL** o **PostgreSQL** para producción.
*   **Seguridad por Diseño:**
    *   **Multi-Tenancy Estricta:** Implementada en una clase base reutilizable (`BaseTenantViewSet`) que filtra automáticamente todos los querysets.
    *   **Validaciones en Serializadores:** La lógica de validación, incluyendo la prevención de acceso a recursos de otros tenants, se maneja en la capa de serialización.
    *   **Transacciones Atómicas:** Las operaciones críticas que modifican múltiples tablas (como el registro de producción) están envueltas en transacciones de base de datos (`@transaction.atomic`) para garantizar la integridad de los datos.

## 4. Guía de Instalación y Puesta en Marcha

### Prerrequisitos
*   Python 3.10+
*   Node.js 18.x+ (y npm)
*   Git
*   `pip` y `venv`

### Pasos de Instalación
1.  **Clonar el repositorio:**
    ```bash
    git clone https://[URL-DEL-REPOSITORIO]/centavo.git
    cd centavo
    ```

2.  **Configurar el Backend:**
    ```bash
    # Crear y activar un entorno virtual de Python
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    
    # Instalar dependencias de Python
    pip install -r requirements.txt
    ```

3.  **Configurar el Frontend:**
    ```bash
    # Navegar a la carpeta del frontend
    cd frontend
    
    # Instalar dependencias de Node.js
    npm install
    
    # Regresar a la raíz del proyecto
    cd ..
    ```

4.  **Configurar variables de entorno:**
    Crea un archivo `.env` en la raíz del proyecto y añade las configuraciones necesarias:
    ```
    SECRET_KEY='tu-secret-key-super-secreta'
    DEBUG=True
    ```

5.  **Aplicar las migraciones de la base de datos:**
    ```bash
    python manage.py migrate
    ```

6.  **Poblar la base de datos con datos de prueba (¡Recomendado!):**
    Este comando limpiará la BD y la llenará con datos realistas para todas las funcionalidades.
    ```bash
    python manage.py seed_db
    ```
    Tu usuario de prueba será:
    *   **Email:** `productor@ejemplo.com`
    *   **Contraseña:** `password123`

7.  **Ejecutar los servidores de desarrollo:**
    Deberás ejecutar dos terminales simultáneamente en la raíz del proyecto.
    
    *   **Terminal 1 (Backend - Django):**
        ```bash
        source venv/bin/activate
        python manage.py runserver
        ```
    *   **Terminal 2 (Frontend - Vite):**
        ```bash
        cd frontend
        npm run dev
        ```
    La aplicación estará disponible en la URL que indique Vite (normalmente `http://localhost:5173/`).

## 5. Inmersión Técnica: La Lógica de Producción FIFO

La funcionalidad más compleja y crítica de Centavo es el registro de un lote de producción. No es una simple operación CRUD, sino un proceso de negocio que debe ser atómico y seguro contra condiciones de carrera.

**El Problema:** Al registrar la producción de 10 sillas, el sistema debe descontar la cantidad correcta de madera, tornillos, etc., del inventario. Pero, ¿de qué lote de compra se descuentan? La estrategia correcta es FIFO: usar primero la madera más antigua. Además, si dos usuarios registran una producción al mismo tiempo, no pueden interferir entre sí.

**La Solución:** Se implementó un servicio (`production.services.register_production_batch`) que orquesta toda la operación.

*   **Atomicidad (`@transaction.atomic`):** Toda la función está envuelta en una transacción de base de datos. Si cualquier paso falla (ej. no hay suficiente stock), toda la operación se revierte y la base de datos queda como si nada hubiera pasado.
*   **Bloqueo Pesimista (`select_for_update()`):** Antes de verificar el stock, el sistema bloquea a nivel de base de datos las filas de los lotes de compra relevantes. Esto asegura que ninguna otra petición pueda modificar esos lotes hasta que la transacción actual termine, previniendo condiciones de carrera.

### Ejemplo de Código del Servicio (`production/services.py`):

```python
# ... imports ...

@transaction.atomic
def register_production_batch(user, product_id, quantity_to_produce: Decimal):
    # ... (cálculo de requerimientos) ...

    for rm_id, requirement in required_materials.items():
        # ... (lógica para obtener la materia prima) ...

        # **CRÍTICO**: Bloqueamos los lotes relevantes para esta transacción.
        available_batches = PurchaseBatch.objects.select_for_update().filter(
            tenant=tenant,
            raw_material=raw_material,
            quantity_remaining__gt=0
        ).order_by('purchase_date')  # Orden FIFO

        # ... (verificación de si el stock total es suficiente) ...

        # Lógica de descuento FIFO
        remaining_to_deduct = quantity_needed
        for batch in available_batches:
            if remaining_to_deduct <= 0:
                break
            
            # ... (cálculo de costo y lógica de descuento) ...
            
            batch.save() # Guarda el estado actualizado del lote
        
        # ... (cálculo de costo total de producción) ...

    # Finalizar: actualizar stock del producto y crear el registro de producción
    product.stock += quantity_to_produce
    product.save()
    ProductionLog.objects.create(...)

    return production_log
```