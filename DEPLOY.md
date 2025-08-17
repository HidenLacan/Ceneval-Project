# Guía de Deploy - Ceneval Routes

## Configuración para Render.com

### 1. Archivos de Configuración Creados

- `requirements-deploy.txt` - Dependencias optimizadas para deploy
- `runtime.txt` - Versión de Python (3.11.18)
- `Procfile` - Comando de inicio para la aplicación
- `render.yaml` - Configuración específica para Render.com
- `pip.conf` - Configuración de pip para usar solo wheels precompilados

### 2. Variables de Entorno Necesarias

Configura estas variables en tu panel de Render.com:

```
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://user:password@host:port
```

### 3. Pasos para Deploy

1. **Conecta tu repositorio** a Render.com
2. **Crea un nuevo Web Service**
3. **Configura las variables de entorno** mencionadas arriba
4. **Usa el archivo `requirements-deploy.txt`** en lugar de `requirements.txt`
5. **Comando de build:**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install --only-binary=all numpy==2.2.6 scipy==1.11.4
   pip install --only-binary=all scikit-learn==1.3.2
   pip install --only-binary=all -r requirements-deploy.txt
   ```
6. **Comando de inicio:**
   ```bash
   python manage.py collectstatic --noinput
   python manage.py migrate
   gunicorn --bind 0.0.0.0:$PORT --workers 3 --timeout 120 routes_project.wsgi:application
   ```

### 4. Solución de Problemas

#### Error de compilación de scipy/scikit-learn:
- Usa `--only-binary=all` en los comandos de pip
- Asegúrate de usar Python 3.11 (no 3.13)
- Instala numpy y scipy antes que scikit-learn

#### Error de dependencias:
- Verifica que todas las versiones en `requirements-deploy.txt` sean compatibles
- Usa el archivo `pip.conf` para forzar el uso de wheels

### 5. Verificación Post-Deploy

1. Verifica que la aplicación responda en la URL proporcionada
2. Revisa los logs en Render.com para errores
3. Ejecuta las migraciones si es necesario
4. Verifica que los archivos estáticos se sirvan correctamente

### 6. Configuración de Base de Datos

Si usas PostgreSQL en Render.com:
1. Crea una base de datos PostgreSQL
2. Configura la variable `DATABASE_URL`
3. Ejecuta las migraciones: `python manage.py migrate`

### 7. Configuración de Redis (Opcional)

Si usas Redis para cache/Celery:
1. Crea un servicio Redis en Render.com
2. Configura la variable `REDIS_URL`
3. Asegúrate de que Celery esté configurado correctamente
