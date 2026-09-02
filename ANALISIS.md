# Documento de Análisis del Sistema EcoEnergy - Fase 1

## 1. Modelo de Datos y Relaciones

El sistema EcoEnergy opera en esta primera versión desacoplado de la capa de ORM/Base de datos de Django, utilizando archivos JSON estructurados como fuente de datos persistente.

### Diagrama Conceptual de Entidades y Multiplicidades

```
+------------------+         1           0..*         +------------------+
|      Zona        |----------------------------------|    Dispositivo   |
+------------------+ (zona_id)                        +------------------+
| id (int)         |                                  | id (int)         |
| nombre (str)     |                                  | nombre (str)     |
| limite_kwh (float|                                  | consumo_kwh (fl) |
+------------------+                                  | zona_id (int)    |
                                                      | categoria_id(int)|
+------------------+         1           0..*         +------------------+
|    Categoria     |----------------------------------|                  |
+------------------+ (categoria_id)                   +------------------+
| id (int)         |
| nombre (str)     |
| descripcion(str) |
+------------------+
```

### Relaciones y Claves de Conexión
1. **Zona <-> Dispositivo**: Relación de uno a muchos ($1 : 0..*$). Una zona de consumo puede alojar cero o múltiples dispositivos instalados. La conexión se establece mediante la clave foránea `zona_id` presente en el archivo `dispositivos.json`, referenciando al atributo `id` de `zonas.json`.
2. **Categoría <-> Dispositivo**: Relación de uno a muchos ($1 : 0..*$). Una categoría agrupa cero o múltiples dispositivos. La conexión se realiza a través del campo `categoria_id` en `dispositivos.json`, referenciando al atributo `id` de `categorias.json`.

---

## 2. Matriz de Criterios de Aceptación vs. Archivos y Pruebas

| Código | Criterio de Aceptación | Archivo / Componente Involucrado | Método / Escenario de Prueba Realizado |
| :--- | :--- | :--- | :--- |
| **CA-01** | El listado muestra todas las zonas registradas en `zonas.json`. | `dispositivos/services.py`, `templates/dispositivos/zonas.html` | Acceder a `/zonas/` y verificar la renderización dinámica de cada objeto zona. |
| **CA-02** | Cada zona muestra nombre, límite, cantidad de dispositivos y acceso al detalle. | `templates/dispositivos/zonas.html` | Inspección visual en `/zonas/` confirmando campos y botón `[ Ver detalle ]`. |
| **CA-03** | El detalle muestra dispositivos, categoría, consumo, métricas y estado de la zona. | `dispositivos/views.py`, `templates/dispositivos/zona_detalle.html` | Navegar a `/zonas/1/` y verificar tarjetas de resumen y tabla de dispositivos con categoría. |
| **CA-04** | Cantidades, sumas y estados se calculan dinámicamente en Python. | `dispositivos/services.py` | Modificar un `consumo_kwh` en JSON y corroborar recalculo inmediato sin recargar código Python. |
| **CA-05** | `ALERTA` cuando `consumo_total > limite_kwh` y `NORMAL` cuando `consumo_total <= limite_kwh`. | `dispositivos/services.py` | Configurar zona con consumo superior e inferior al límite y validar banderas producidas. |
| **CA-06** | Incorporación de nuevos registros en el JSON sin modificar Views ni Templates. | `data/dispositivos.json`, `dispositivos/services.py` | Agregar nuevo dispositivo válido en el JSON y comprobar su aparición automática en interfaz. |
| **CA-07** | Zona sin dispositivos mantiene la aplicación operativa con mensaje comprensible. | `templates/dispositivos/zona_detalle.html` | Consultar `/zonas/4/` (sin dispositivos) comprobando consumo 0.0 kWh, estado NORMAL y mensaje. |
| **CA-08** | Identificador de zona inexistente responde de forma controlada mediante 404. | `dispositivos/views.py` (`Http404`) | Solicitar `/zonas/999/` verificando respuesta 404 sin trazas expuestas del sistema. |
| **CA-09** | La interfaz conserva su estructura adaptable y controles accesibles. | `templates/base.html` | Probar la web con distintos anchos de pantalla y volúmenes de datos. |
| **CA-10** | Tablas extensas permiten desplazamiento en contenedor adaptable. | `templates/dispositivos/zona_detalle.html` | Validar clase `.table-responsive` y contenedor con scroll vertical/horizontal. |
| **CA-11** | Jerarquía visual coherente en Header, tarjetas, tablas y botones. | `templates/base.html`, `zonas.html`, `zona_detalle.html` | Revisar uso de estilos Bootstrap 5, badges y contenedores. |
| **CA-12** | Estados utilizan apoyo visual (texto + íconos/badges); no solo color. | `templates/dispositivos/zona_detalle.html` | Verificar que ALERTA y NORMAL incluyan ícono (`bi-exclamation-triangle-fill` / `bi-check-circle-fill`) y texto explícito. |
| **CA-13** | Instalación limpia desde el repositorio, Django funcional y pasa `python manage.py check`. | `manage.py`, `config/settings.py` | Ejecución del comando de verificación nativo de Django en terminal. |
