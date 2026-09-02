# Registro de Uso de Inteligencia Artificial (IA.md)

En cumplimiento con los requerimientos de evaluación para la Fase 1 del proyecto **EcoEnergy**, a continuación se declara formalmente el uso y apoyo de herramientas de Inteligencia Artificial durante el desarrollo de la solución.

---

## 1. Herramienta Utilizada
- **Herramienta**: Google Antigravity / Gemini 3.6 Flash.
- **Entorno de desarrollo**: VS Code con Antigravity Assistant.

---

## 2. Prompts Utilizados y Propósito

### Prompt 1: Generación y Validación de Archivos de Datos (JSON)
- **Prompt**: *"Generar datos iniciales válidos para zonas.json, categorias.json y dispositivos.json respetando los tipos de datos (int, float, str) y las relaciones de llaves foráneas entre zona_id, categoria_id e id de zona/categoría."*
- **Respuesta utilizada**: Estructuras JSON iniciales con claves `limite_kwh`, `consumo_kwh`, `zona_id`, `categoria_id`.

### Prompt 2: Lógica de Servicio en Python para Procesamiento Dinámico
- **Prompt**: *"Diseñar una función en Python para Django que lea dinámicamente zonas.json y dispositivos.json en cada petición, calcule la suma del consumo por zona, determine si se supera el límite para marcar el estado como ALERTA o NORMAL, y lance un error 404 de Django si la zona solicitada no existe."*
- **Respuesta utilizada**: Implementación de las funciones `obtener_zonas()` y `obtener_detalle_zona()` en `dispositivos/services.py`.

### Prompt 3: Maquetación Bootstrap Accesible para Vistas MVT
- **Prompt**: *"Diseñar la plantilla zona_detalle.html en Django utilizando Bootstrap 5 y Bootstrap Icons de forma accesible, mostrando métricas de límite, consumo total, dispositivos y un badge con texto e icono para el estado (ALERTA / NORMAL), además de un contenedor adaptable para la tabla de dispositivos."*
- **Respuesta utilizada**: Estructura de plantilla HTML con bloques Django `{% extends 'base.html' %}`, componentes card, badges e iconos accesibles.

---

## 3. Cambios y Adaptaciones Propias del Desarrollador
- **Ajuste de Carga Dinámica**: Se eliminó la carga global de archivos JSON al momento de importar el módulo en `services.py`, forzando la relectura en cada invocación de función para garantizar que la app reaccione dinámicamente cuando el docente agregue o modifique registros en `data/*.json`.
- **Manejo de Zona Vacía**: Se implementó una verificación explícita para evitar errores de tipo o división cuando una zona no tiene dispositivos asignados, retornando un consumo de `0.0 kWh` y el mensaje de estado alternativo.
- **Jerarquía Visual y Accesibilidad**: Se agregaron etiquetas `aria-label`, contraste adecuado y combinación de texto e íconos en los badge# Registro de Uso de IA

## 4. Pruebas y Verificación Realizadas
1. **Comprobación de Django**: Ejecución exitosa de `python manage.py check`.
2. **Prueba de Rutas y 404**: Navegación por `/zonas/`, `/zonas/1/`, `/zonas/2/`, `/zonas/4/` y solicitud de `/zonas/999/` verificando la captura adecuada de 404.
3. **Prueba Dinámica de JSON**: Modificación manual de registros en `dispositivos.json` y verificación inmediata del recálculo de totales sin reinicio del servidor.