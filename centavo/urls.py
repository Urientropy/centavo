# centavo/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from .views import LandingOrDashboardView  # Asegúrate de que esta importación exista

urlpatterns = [
    # --- RUTA RAÍZ ESPECÍFICA ---
    # PRINCIPIO ARQUITECTÓNICO: Django evalúa las URLs en orden.
    # Al colocar esta ruta específica para la raíz ('') ANTES del "catch-all",
    # nos aseguramos de que las visitas a la página principal sean interceptadas
    # por nuestra vista con lógica condicional.
    path('', LandingOrDashboardView.as_view(), name='landing-or-dashboard'),

    # --- RUTAS DE LA API (sin cambios) ---
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('users.urls')),
    path('api/v1/inventory/', include('inventory.urls')),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/production-logs/', include('production.urls')),
    path('api/v1/finance/', include('finance.urls')),

    # --- RUTA CATCH-ALL PARA LA SPA (DEBE SER LA ÚLTIMA) ---
    # Esta ruta ahora se encargará de todas las demás peticiones que no sean la raíz
    # ni de la API (ej. /login, /register, /dashboard, /products/5),
    # sirviendo el index.html para que Vue Router tome el control.
    re_path(r'^(?!api/|admin/).*$', TemplateView.as_view(template_name='index.html'), name='app'),
]

# --- MODIFICACIÓN EN LA VISTA PARA LA REDIRECCIÓN ---
# En `centavo/views.py`, la redirección debe apuntar ahora a una ruta manejada por la SPA,
# por ejemplo, '/dashboard'. El nombre de la URL ya no es necesario.
#
# return redirect('/dashboard/') # Ejemplo de cómo debería quedar en LandingOrDashboardView