# centavo/views.py

from django.shortcuts import render, redirect
from django.views import View


class LandingOrDashboardView(View):
    """
    Vista para la ruta raíz del proyecto.

    - Si el usuario está autenticado, lo redirige al dashboard de la SPA.
    - Si el usuario no está autenticado, muestra la landing page.
    """

    def get(self, request, *args, **kwargs):
        # PRINCIPIO ARQUITECTÓNICO: La lógica de negocio sobre dónde debe
        # ir un usuario al visitar la raíz reside en el backend.
        if request.user.is_authenticated:
            # Redirigimos a la ruta que carga la SPA para un usuario logueado.
            # Usualmente, la SPA maneja rutas como '/dashboard'.
            # Una redirección a '/' y dejar que la SPA decida ya no es una opción
            # porque crearía un bucle infinito. Asumiremos '/app' como la entrada a la SPA logueada.
            return redirect('app-dashboard')  # Asumimos que la URL de la SPA se llama 'app-dashboard'

        # Si no está autenticado, renderizamos la plantilla de la landing page.
        return render(request, 'landing.html')