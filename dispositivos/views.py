from django.http import HttpResponse
from django.shortcuts import render

from .services import cargar_dispositivos, cargar_json


def inicio(request):
    contexto = {
        "sistema": "EcoEnergy",
        "mensaje": "Monitoreo energético responsable",
        "asignatura": "Programación Back End",
    }
    return render(request, "dispositivos/inicio.html", contexto)


def zonas(request):
    zonas = cargar_json("zonas.json")
    return render(request, "dispositivos/zonas.html", {"zonas": zonas})


def dispositivos_zona(request, zona_id):
    if zona_id not in (1, 2, 3):
        return HttpResponse("Zona no encontrada", status=404)
    return HttpResponse(f"Dispositivos de la zona {zona_id}")


def catalogo(request):
    dispositivos = cargar_dispositivos()
    activos = sum(1 for item in dispositivos if item.get("estado") == "Activo")
    contexto = {
        "dispositivos": dispositivos,
        "total": len(dispositivos),
        "total_activos": activos,
    }
    return render(request, "dispositivos/catalogo.html", contexto)

