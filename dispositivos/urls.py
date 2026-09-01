from django.urls import path
from . import views

app_name = "dispositivos"
urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("zonas/", views.zonas, name="zonas"),
    path("dispositivos/", views.catalogo, name="catalogo"),
]


