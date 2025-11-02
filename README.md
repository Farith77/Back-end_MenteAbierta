# MenteAbierta - Backend (API RESTful)

Este repositorio contiene el código del Backend de MenteAbierta, una plataforma digital para la promoción del bienestar emocional.

## 🛠️ Tecnologías Principales

-   **Lenguaje:** Python 3.10+
-   **Framework:** Django 5.x
-   **API:** Django REST Framework (RESTful)
-   **Autenticación:** JWT (djangorestframework-simplejwt)
-   **Base de Datos:** PostgreSQL (Usando SQLite por ahora)

---

## ⚙️ Configuración Inicial del Entorno

### 1. Clonar el Repositorio

git clone "direccion git del repositorio"

## Crear el entorno (llamado 'venv')
python -m venv venv

pueden usar culaquier nombre, pero yo use venv, solo por si acaso.

## Activar el entorno virtual
### En Windows:
.\venv\Scripts\activate
### En macOS/Linux:
source venv/bin/activate
### En windows bash:
source venv/Scripts/activate

## Instalar dependencias
pip install -r requirements.txt

## Migra la base de datos
python manage.py makemigrations
python manage.py migrate

## Levanta el servidor
python manage.py runserver
