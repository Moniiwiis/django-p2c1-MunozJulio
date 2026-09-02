from django.shortcuts import render
from .services import cargar_dispositivos, obtener_detalle_zona, obtener_zonas


def inicio(request):
    """Página de bienvenida de la aplicación EcoEnergy."""
    contexto = {
        "sistema": "EcoEnergy",
        "mensaje": "Plataforma de Monitoreo Energético",
        "asignatura": "Programación Back End",
    }
    return render(request, "dispositivos/inicio.html", contexto)


def zonas_list(request):
    """Listado dinámico de todas las zonas de consumo."""
    zonas = obtener_zonas()
    return render(request, "dispositivos/zonas.html", {"zonas": zonas})


def zona_detalle(request, zona_id):
    """Vista en detalle de una zona de consumo por su ID."""
    detalle = obtener_detalle_zona(zona_id)
    return render(request, "dispositivos/zona_detalle.html", detalle)


def catalogo(request):
    """Catálogo general de dispositivos."""
    dispositivos = cargar_dispositivos()
    contexto = {
        "dispositivos": dispositivos,
        "total": len(dispositivos),
    }
    return render(request, "dispositivos/catalogo.html", contexto)


