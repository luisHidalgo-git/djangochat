# WebSocket chat en tiempo real 💬
![Vista Previa](./static/img/image.png)

**Características:**
1. Autenticación con JWT
2. Verificación de no soy un robot
3. Mensajería en tiempo real
4. Estado de usuarios en línea
5. Errores y alertas personalizadas
6. Filtro avanzado de búsqueda
7. Indicador de mensajes urgentes
8. Indicador de mensajes por matería
9. Manejo de archivos estaticos
10. Despliegue en Railway.app

## Pasos para hacer uso del proyecto

```
#Clonar repositorio
#Crear y acivar el entorno virtual
python -m venv venv && source venv/bin/activate

#Instalar archivo requirements
pip install -r requirements.txt

#Cargar las migraciones
python manage.py makemigrations && python manage.py migrate

#Ejecutar el proyecto
python manage.py runserver
```