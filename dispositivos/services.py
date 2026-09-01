import json
from django.conf import settings


def cargar_json(nombre_archivo):
    ruta = settings.BASE_DIR / "data" / nombre_archivo
    with ruta.open(encoding="utf-8") as archivo:
        datos = json.load(archivo)
    if not isinstance(datos, list):
        raise ValueError(f"{nombre_archivo} debe contener una lista")
    return datos


def cargar_dispositivos():
    dispositivos = cargar_json("dispositivos.json")
    for dispositivo in dispositivos:
        dispositivo.setdefault("estado", "Activo" if dispositivo.get("id", 0) % 2 else "Inactivo")
    return dispositivos


zonas = cargar_json("zonas.json")
categorias = cargar_json("categorias.json")
dispositivos = cargar_json("dispositivos.json")


