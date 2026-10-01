# 🏛️ Sistema de Gestión de Resultados (SGR) — Django BackEnd
### Ilustre Municipalidad de La Serena | INACAP — Evaluación Sumativa II (TI3041)

[![Estado](https://img.shields.io/badge/Estado-Completado%20100%25-brightgreen.svg)](https://github.com/)
[![Asignatura](https://img.shields.io/badge/Asignatura-Programaci%C3%B3n%20Back%20End-red.svg)](https://www.inacap.cl/)
[![Framework](https://img.shields.io/badge/Framework-Django%206.1-blue.svg)](https://www.djangoproject.com/)

---

## 📋 Descripción del Proyecto

El **Sistema de Gestión de Resultados (SGR)** centraliza, mide y controla la gestión operativa de funcionarios y delegaciones de la **Ilustre Municipalidad de La Serena** (*Delegación La Serena Centro, Las Compañías, Rural, entre otras*).

Esta aplicación desarrollada en **Django** incluye un backend desacoplado en aplicaciones de dominio (`accounts`, `activities`, `agenda`, `configuration`, `core`, `analytics`), un **Django Admin personalizado y avanzado (Admin Pro)** con auditoría, inlines, acciones personalizadas, validaciones controladas `clean()`, y restricción de visibilidad por perfil y delegación (**Scoping por Delegación**).

---

## 🛠️ Arquitectura del Sistema y Módulos

El proyecto está organizado en 6 aplicaciones independientes con responsabilidades delimitadas:

1. **`core`**: Proporciona el `BaseModel` abstracto con los campos de auditoría requeridos (`created_at`, `updated_at`, `deleted_at`) y la lógica de borrado lógico (*Soft Delete*). Contiene además el comando de carga reproducible `seed_data`.
2. **`accounts`**: Gestión de `Delegacion`, `Cargo`, `Funcionario` (vinculado a `User`), `Rol` y `FuncionarioRol`.
3. **`configuration`**: Gestión de `Periodo`, `CatalogoActividad`, `ItemMedicion` y `ConfiguracionMeta` (incluyendo fórmulas de semáforo, cumplimiento ponderado y tope del 150%).
4. **`activities`**: Gestión de `Actividad` (con autogeneración de `codigo_evidencia_unico`), `Evidencia`, `ValidacionEvidencia` y `AtencionSocialGestion`.
5. **`agenda`**: Registro de `CompromisoAgenda` (tubo de trabajo) y `AjusteDesempenio`.
6. **`analytics`**: Módulo de reportabilidad e indicadores consolidados.

---

## 🔑 Cuentas de Prueba y Restricciones de Seguridad (Scoping)

Para demostrar las restricciones de seguridad por rol y delegación en la aplicación y en **Django Admin**:

| Usuario | Contraseña | Rol / Contexto | Permisos en Django Admin |
| :--- | :--- | :--- | :--- |
| **`admin_sgr`** | `Admin1234!` | Superusuario / Administrador | **Acceso Total**: Visualiza y edita todas las delegaciones y registros. |
| **`delegado_centro`** | `User1234!` | Delegado Centro (Staff) | **Scoping**: Consulta su nómina y gestiona actividades/compromisos de **Delegación La Serena Centro**. |
| **`delegado_companias`** | `User1234!` | Delegado Las Compañías (Staff) | **Scoping**: Consulta su nómina y gestiona actividades/compromisos de **Delegación Las Compañías**. |
| **`funcionario_juan`** | `User1234!` | Funcionario (Staff) | Registra y actualiza sus actividades/compromisos; no elimina ni administra otros perfiles. |
| **`coordinador_sgr`** | `User1234!` | Coordinador del sistema | Consulta transversal de indicadores y módulos; sin acciones de escritura. |
| **`verificador_centro`** | `User1234!` | Verificador | Consulta actividades y aprueba/rechaza evidencias; no edita otros datos. |
| **`consulta_sgr`** | `User1234!` | Usuario de consulta | Acceso de solo lectura a inicio e informes. |

### Actores y responsabilidades

| Actor | Responsabilidad principal en la aplicación |
| :--- | :--- |
| Administrador | Configura delegaciones, usuarios, cargos, catálogos, períodos, metas, ponderaciones y permisos. |
| Coordinador del sistema | Supervisa la operación transversal y consulta indicadores, criterios y reportes. |
| Delegado o jefatura | Consulta su delegación, registra/revisa compromisos y acompaña el cumplimiento de su equipo. |
| Funcionario | Registra actividades y compromisos propios, y actualiza su avance operativo. |
| Verificador | Revisa evidencias, aprueba o rechaza registros y deja trazabilidad de la decisión. |
| Usuario de consulta | Accede a tableros e informes sin modificar información operativa. |

---

## ⚡ Django Admin Pro: Funcionalidades Implementadas

1. **Inlines Reutilizables**:
   - `EvidenciaInline`, `ValidacionEvidenciaInline`, `AtencionSocialGestionInline` dentro de `ActividadAdmin`.
   - `FuncionarioRolInline` dentro de `FuncionarioAdmin`.
   - `ItemMedicionInline` dentro de `CargoAdmin`.
2. **Acciones Personalizadas**:
   - `aprobar_evidencias` y `rechazar_evidencias` en `ActividadAdmin`.
   - `marcar_como_pendiente`, `marcar_como_realizado` y `marcar_como_en_proceso` en `CompromisoAgendaAdmin`.
3. **Auditoría visible en Admin**: `created_at`, `updated_at` y `deleted_at` aparecen como datos de solo lectura; `updated_at` y `deleted_at` también se incluyen en las columnas.
4. **Validación Controlada (`clean()`)**:
   - `Periodo.clean()`: Valida que la `fecha_termino` no sea anterior a la `fecha_inicio`.
   - `ConfiguracionMeta.clean()`: Valida que `valor_objetivo` > 0 y `ponderacion` entre 0% y 100%.
   - `Actividad.clean()`: Valida que la `fecha_actividad` esté dentro del rango del período seleccionado.
5. **Optimización de Consultas (`list_select_related`)**:
   - Implementado en todos los ModelAdmins para evitar consultas $N+1$ en relaciones de clave foránea.

---

## 🚀 Instrucciones de Instalación y Ejecución Desde un Entorno Limpio

### 1. Clonar el repositorio y crear el entorno virtual
```bash
git clone https://github.com/Moniiwiis/django-p2c1-MunozJulio.git
cd django-p2c1-MunozJulio

# Crear y activar entorno virtual
python -m venv .venv
# En Windows PowerShell:
source .venv\Scripts\Activate.ps1
# En Linux/macOS:
source .venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno (.env)
Copiar el archivo de plantilla `.env.example` a `.env`:
```bash
cp .env.example .env
```
*(Por defecto viene configurado para usar `sqlite` con `db.sqlite3`. Si se desea MySQL/WAMP, modificar las variables en `.env`)*.

### 4. Ejecutar verificación y migraciones
```bash
python manage.py check
python manage.py migrate
```

### 5. Cargar datos de prueba reproducibles (Seed Data / Fixtures)

Se disponen de **dos mecanismos equivalentes y reproducibles**:

**Opción A (Management Command - Recomendado):**
```bash
python manage.py seed_data
```

**Opción B (Fixture JSON):**
```bash
python manage.py loaddata fixtures/seed.json
```

### 6. Iniciar el servidor de desarrollo
```bash
python manage.py runserver
```
Acceder al panel de administración en: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🛡️ Trazabilidad Git y Gestión de Ramas

- **Rama Principal**: `main`
- **Trabajo en Ramas de Desarrollo**: `feature/reproducible-seeds-fixtures`, `feature/role-based-tables`, `fix/admin-activity-delegate-scope`
```bash
git log --oneline --graph --all
```

---

## 👥 Equipo y Créditos

- **Institución**: INACAP — Sede La Serena
- **Asignatura**: Programación Back End (TI3041)
- **Docente**: Javier Ahumada
- **Evaluación**: Evaluación Sumativa II — Taller "Aplicación web con Django Admin" (25%)
