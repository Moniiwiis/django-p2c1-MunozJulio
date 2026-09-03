import json
from django.conf import settings
from django.http import Http404


def cargar_json(nombre_archivo):
    """Carga y parsea dinámicamente un archivo JSON desde el directorio data/."""
    ruta = settings.BASE_DIR / "data" / nombre_archivo
    with ruta.open(encoding="utf-8") as archivo:
        datos = json.load(archivo)
    if not isinstance(datos, list):
        raise ValueError(f"{nombre_archivo} debe contener una lista")
    return datos


def obtener_zonas():
    """Retorna el listado de zonas incluyendo el conteo dinámico de dispositivos."""
    zonas = cargar_json("zonas.json")
    dispositivos = cargar_json("dispositivos.json")

    for zona in zonas:
        conteo = sum(1 for d in dispositivos if d.get("zona_id") == zona.get("id"))
        zona["cantidad_dispositivos"] = conteo

    return zonas


def obtener_detalle_zona(zona_id):
    """
    Retorna el detalle completo de una zona específica:
    datos de la zona, lista de dispositivos con nombre de categoría,
    consumo total y estado (NORMAL o ALERTA). Lanza Http404 si la zona no existe.
    """
    zonas = cargar_json("zonas.json")
    zona = next((z for z in zonas if z.get("id") == zona_id), None)
    if not zona:
        raise Http404("La zona requerida no existe.")

    dispositivos_todos = cargar_json("dispositivos.json")
    categorias_todas = cargar_json("categorias.json")

    # Mapa de categorías para resolución eficiente por id
    mapa_categorias = {c["id"]: c["nombre"] for c in categorias_todas if "id" in c and "nombre" in c}

    dispositivos_zona = []
    for d in dispositivos_todos:
        if d.get("zona_id") == zona_id:
            cat_id = d.get("categoria_id")
            item = dict(d)
            item["categoria_nombre"] = mapa_categorias.get(cat_id, "Desconocida")
            dispositivos_zona.append(item)

    consumo_total = round(sum(float(d.get("consumo_kwh", 0)) for d in dispositivos_zona), 2)
    limite = float(zona.get("limite_kwh", 0))
    estado = "ALERTA" if consumo_total > limite else "NORMAL"

    return {
        "zona": zona,
        "dispositivos": dispositivos_zona,
        "consumo_total": consumo_total,
        "limite_kwh": limite,
        "cantidad_dispositivos": len(dispositivos_zona),
        "estado": estado,
    }


def cargar_dispositivos():
    """Retorna el catálogo completo de dispositivos con nombre de zona y categoría."""
    dispositivos = cargar_json("dispositivos.json")
    categorias = cargar_json("categorias.json")
    zonas = cargar_json("zonas.json")

    mapa_cat = {c["id"]: c["nombre"] for c in categorias}
    mapa_zona = {z["id"]: z["nombre"] for z in zonas}

    for d in dispositivos:
        d["categoria_nombre"] = mapa_cat.get(d.get("categoria_id"), "Desconocida")
        d["zona_nombre"] = mapa_zona.get(d.get("zona_id"), "Desconocida")

    return dispositivos
def obtener_resumen_zonas():
    """
    Retorna el resumen de consumo energético por zonas.
    """
    zonas = cargar_json("zonas.json")
    dispositivos = cargar_json("dispositivos.json")
    for zona in zonas:
            conteo = sum(1 for d in dispositivos if d.get("zona_id") == zona.get("id"))
            zona["cantidad_dispositivos"] = conteo
    consumo_total = sum(float(d.get("consumo_kwh", 0)) for d in dispositivos)
    limite = float(zona.get("limite_kwh", 0))
    estado = "Límite superado" if consumo_total > limite else "Dentro del límite"
    return {
        "zonas": zonas,
        "cantidad_zonas": len(zonas),
        "cantidad_dispositivos": len(dispositivos),
        "total_consumo": round(consumo_total, 2),
        "limite_kwh": limite,
        "estado": estado,
        }
   


