from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),  # todas las rutas de la app core
    # redirige /home o /inicio si es necesario
    path("home/", RedirectView.as_view(pattern_name="inicio", permanent=False)),
]
