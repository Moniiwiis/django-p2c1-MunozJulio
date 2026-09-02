# Sistema de Monitoreo Energético EcoEnergy - Django (Fase 1)

Aplicación web desarrollada en Django para el monitoreo dinámico de zonas de consumo energético y dispositivos instalados, utilizando procesamiento de colecciones JSON del lado del servidor.

---

## 1. Requisitos Previos
- **Python**: v3.10 o superior (probadado en Python 3.12/3.14).
- **pip**: Gestor de paquetes de Python.
- **Git**: Sistema de control de versiones.

---

## 2. Instalación y Configuración

### Clonación del Repositorio
```bash
git clone https://github.com/Moniiwiis/django-p2c1-MunozJulio.git
cd django-p2c1-MunozJulio
```

### Creación y Activación del Entorno Virtual (.venv)
- **Windows (PowerShell / Command Prompt)**:
  ```powershell
  python -m venv .venv
  .venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```

---

## 3. Ejecución del Proyecto
Para iniciar el servidor de desarrollo local de Django:
```bash
python manage.py runserver
```
Acceda en el navegador a: `http://127.0.0.1:8000/`

---

## 4. Rutas Funcionales de la Aplicación

| Ruta URL | Nombre de Ruta (`name`) | Descripción |
| :--- | :--- | :--- |
| `/` | `dispositivos:inicio` | Página de bienvenida e información general de EcoEnergy. |
| `/zonas/` | `dispositivos:zonas` | Listado dinámico de todas las zonas de consumo registradas con conteo de dispositivos y acceso al detalle. |
| `/zonas/<zona_id>/` | `dispositivos:zona_detalle` | Detalle específico de una zona: límite, consumo total (kWh), estado (`NORMAL` / `ALERTA`), y tabla de dispositivos instalados. |
| `/dispositivos/` | `dispositivos:catalogo` | Catálogo general de todos los dispositivos registrados en el sistema. |

---

## 5. Comprobación y Verificación

### Verificación de Configuración de Django
```bash
python manage.py check
```

### Pruebas de Funcionamiento y Escenarios
1. **Listado de Zonas (`/zonas/`)**: Carga dinámica desde `data/zonas.json` y `data/dispositivos.json`.
2. **Cálculo de Estados**:
   - `NORMAL`: Consumo total $\le$ Límite de la zona.
   - `ALERTA`: Consumo total $>$ Límite de la zona.
3. **Zona sin Dispositivos**: Probar con la zona ID 4 (`/zonas/4/`), observando el mensaje informativo "Esta zona no tiene dispositivos", consumo `0.0 kWh` y estado `NORMAL`.
4. **Respuesta 404 Controlada**: Probar ingresando a `/zonas/999/`, verificando que Django responde con la página 404 controlada (`Http404`).
5. **Carga Dinámica JSON**: Si se agregan o modifican dispositivos en `data/dispositivos.json`, los cambios se reflejan inmediatamente en la aplicación al recargar la página en el navegador.

---

## 6. Documentación Adicional
- **`ANALISIS.md`**: Explicación del modelo de datos, relaciones de entidades, llaves de conexión y la matriz de criterios de aceptación vs. componentes.
- **`IA.md`**: Registro y declaración del uso responsable de herramientas de Inteligencia Artificial durante el desarrollo del proyecto.
