# Proyecto Django - Aprendizaje (Back End)

## Descripción y objetivo
Este proyecto ha sido desarrollado como parte de las actividades académicas para el aprendizaje de desarrollo Back End utilizando el framework Django en Python. El objetivo principal es poner en práctica los fundamentos del desarrollo web, la gestión de modelos, vistas y rutas dentro del ecosistema de Django.

## Requisitos previos
Para ejecutar este proyecto en tu entorno local, asegúrate de tener instalado:
* Python: v3.14.5
* pip: Gestor de paquetes de Python.
* Git: Para el control de versiones.

## Instalación

### 1. Clonación del repositorio
Abre tu terminal y ejecuta el siguiente comando para descargar el proyecto:
git clone https://github.com/Moniiwiis/django-p2c1-MunozJulio.git
cd django-p2c1-MunozJulio

### 2. Creación y activación de entorno virtual (.venv)
Es recomendable aislar las dependencias del proyecto en un entorno virtual:

* En Windows:
python -m venv .venv
.venv\Scripts\activate

* En macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate

### 3. Instalación de dependencias
Instala los paquetes necesarios definidos en el archivo requirements.txt:
pip install -r requirements.txt

## Comandos de verificación
Una vez instaladas las dependencias, puedes verificar que Django esté correctamente configurado intentando ejecutar el servidor de desarrollo:
python manage.py runserver
Si el comando se ejecuta sin errores, podrás acceder a la aplicación desde http://127.0.0.1:8000/ en tu navegador.

## Estado actual y próximos pasos
* Estado actual: El proyecto se encuentra en etapa de desarrollo académico.
* Próximos pasos:
    * Continuar con la implementación de funcionalidades base según los requerimientos de la clase.
    * Realizar las migraciones necesarias para la base de datos (python manage.py migrate).
