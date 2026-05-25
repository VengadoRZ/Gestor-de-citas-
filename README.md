# 📅 Gestor de Citas

Un sistema de gestión de citas desarrollado en **Django** que conecta empresas con sus clientes. Diseñado para que cualquier negocio pueda registrar y ofrecer sus servicios, permitiendo a los consumidores agendar citas de manera eficiente y sin conflictos de horario.

---

## ✨ Características Principales

*   **Autenticación y Autorización:** Sistema de registro, inicio de sesión y recuperación de contraseñas.
*   **Verificación por Correo Electrónico:** Activación de cuentas a través de enlaces seguros enviados por correo.
*   **Perfiles Duales:**
    *   🏢 **Empresa:** Permite registrar detalles del negocio (NIT/RIF, dirección), publicar servicios (con nombre y precio) y visualizar la agenda mensual de citas programadas.
    *   👤 **Cliente:** Permite completar datos personales, explorar el catálogo de servicios mediante un buscador y agendar citas.
*   **Gestión de Servicios:** Las empresas pueden crear y gestionar los servicios que ofrecen a sus clientes.
*   **Buscador y Catálogo:** Los clientes pueden buscar servicios por el nombre del servicio o el nombre de la empresa.
*   **Validación de Horarios:** El sistema previene choques de horarios (citas duplicadas) al momento de agendar para un mismo servicio.

## 🛠️ Tecnologías Utilizadas

*   **Backend:** Python 3, Django
*   **Base de Datos:** SQLite (por defecto, escalable a PostgreSQL/MySQL)
*   **Frontend:** HTML5, CSS3, plantillas de Django (Templates)
*   **Autenticación:** Django Auth System (Modelo `AbstractUser` extendido)

## ⚙️ Requisitos Previos

Asegúrate de tener instalado en tu sistema:
*   [Python 3.8+](https://www.python.org/downloads/)
*   `pip` (Gestor de paquetes de Python)
*   `virtualenv` (Recomendado para manejar entornos virtuales)

## 🚀 Instalación y Configuración Local

Sigue estos pasos para desplegar el proyecto en tu entorno local:

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/Gestor-de-citas-.git
   cd Gestor-de-citas-
   ```

2. **Crear y activar un entorno virtual**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. **Instalar las dependencias**
   Asegúrate de instalar Django. *(Si se añade un `requirements.txt` en el futuro, usar `pip install -r requirements.txt`)*
   ```bash
   pip install django
   ```

4. **Aplicar las migraciones a la base de datos**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **(Opcional) Crear un superusuario**
   Para acceder al panel de administración de Django y gestionar la aplicación:
   ```bash
   python manage.py createsuperuser
   ```

6. **Ejecutar el servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```
   El proyecto estará disponible en `http://127.0.0.1:8000/`.

## 📖 Uso del Sistema

1. **Registro:** Un usuario nuevo se registra e interactúa con el correo de verificación para activar su cuenta de forma segura.
2. **Elección de Perfil:** Al iniciar sesión por primera vez, el usuario elige si será un **Cliente** o una **Empresa** y completa sus datos correspondientes.
3. **Empresa:** 
   * Navega a la opción de crear servicios y añade el catálogo de lo que ofrece el negocio.
   * Consulta el apartado "Agenda" para ver las reservas programadas para el mes en curso.
4. **Cliente:**
   * Busca servicios a través de la barra de búsqueda o explora el catálogo general.
   * Selecciona un servicio, elige una fecha y hora, y agenda su cita.

## 📂 Estructura del Proyecto

```text
Gestor-de-citas-/
├── citas/               # Aplicación principal (modelos, vistas, urls, formularios)
│   ├── migrations/      # Archivos de migración de la base de datos
│   ├── static/          # Archivos estáticos (CSS, JS, Imágenes)
│   └── templates/       # Plantillas HTML
├── gestor_citas/        # Configuración principal del proyecto Django (settings, urls)
├── db.sqlite3           # Base de datos SQLite (se genera localmente)
└── manage.py            # Utilidad de línea de comandos de Django
```

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Si deseas mejorar este proyecto, por favor sigue estos pasos:

1. Haz un Fork del repositorio.
2. Crea una rama para tu característica (`git checkout -b feature/NuevaCaracteristica`).
3. Haz commit de tus cambios (`git commit -m 'Añade nueva característica'`).
4. Haz push a la rama (`git push origin feature/NuevaCaracteristica`).
5. Abre un Pull Request.
