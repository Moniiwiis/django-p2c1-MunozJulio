from django.urls import path
from . import views

app_name = "dispositivos"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("zonas/", views.zonas_list, name="zonas"),
    path("zonas/<int:zona_id>/", views.zona_detalle, name="zona_detalle"),
    path("dispositivos/", views.catalogo, name="catalogo"),
    path("resumen_zonas/", views.resumen_zonas, name="resumen_zonas")
]



