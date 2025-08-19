# 🚀 Sistema de Optimización de Rutas con Inteligencia Artificial

## 📋 Descripción del Proyecto

Este es un sistema avanzado de optimización de rutas para distribución de colonias que utiliza técnicas de **Inteligencia Artificial** y **Machine Learning** para mejorar la eficiencia en la asignación y ejecución de rutas de trabajo.

### 🎯 Características Principales

- **Algoritmos de IA**: K-means, DBSCAN, Spectral Clustering, Random Forest
- **Optimización de Rutas**: División inteligente de territorios
- **Predicción de Tiempos**: Machine Learning para estimar duración de rutas
- **Dashboard Interactivo**: Interfaz moderna para diferentes roles de usuario
- **Sistema de Completado**: Seguimiento en tiempo real de rutas
- **Métricas Avanzadas**: Silhouette Score, eficiencia, balance de zonas

## 🏗️ Arquitectura del Sistema

### Roles de Usuario

1. **👨‍💼 Admin**: Gestión completa del sistema
2. **👨‍🔧 Staff**: Supervisión y asignación de rutas
3. **👷 Employee**: Ejecución y marcado de rutas completadas
4. **🔬 Researcher**: Análisis de algoritmos y métricas

### Tecnologías Utilizadas

- **Backend**: Django 4.x, Django REST Framework
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Base de Datos**: SQLite/PostgreSQL
- **IA/ML**: Scikit-learn, NumPy, Pandas
- **Mapas**: Leaflet.js, OpenStreetMap
- **Visualización**: Chart.js, Folium

## 🚀 Instalación y Configuración

### Prerrequisitos

```bash
# Python 3.8+
python --version

# pip
pip --version

# Git
git --version
```

### Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd Ceneval-Project
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Crear superusuario**
```bash
python manage.py createsuperuser
```

6. **Ejecutar el servidor**
```bash
python manage.py runserver
```

### Dependencias Principales

```txt
Django==4.2.7
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
scikit-learn==1.3.0
numpy==1.24.3
pandas==2.0.3
folium==0.14.0
osmnx==1.5.1
networkx==3.1
shapely==2.0.1
psutil==5.9.5
```

## 🎮 Uso del Sistema

### 1. Dashboard de Administrador

**URL**: `/accounts/admin_dashboard/`

**Funcionalidades**:
- Gestión de usuarios y roles
- Control de colonias y polígonos
- Configuración de algoritmos
- Búsqueda inteligente de colonias (optimizada para México)

### 2. Dashboard de Staff

**URL**: `/accounts/staff_dashboard/`

**Funcionalidades**:
- Asignación de rutas a empleados
- Visualización de mapas con polígonos
- **Supervisión de rutas en tiempo real**
- **Marcado de rutas completadas por empleados**

### 3. Dashboard de Empleado

**URL**: `/accounts/employee_dashboard/`

**Funcionalidades**:
- Visualización de rutas asignadas
- **Marcado de rutas como completadas**
- Chat de equipo integrado
- Modo individual/compartido de visualización

### 4. Dashboard de Investigador

**URL**: `/accounts/researcher_dashboard/`

**Funcionalidades**:
- Comparación de algoritmos de IA
- Análisis de métricas de eficiencia
- **Dashboard de Random Forest**
- Visualización de Silhouette Score

## 🤖 Algoritmos de Inteligencia Artificial

### 1. Algoritmos de Clustering

#### K-means Clustering
- **Propósito**: División de territorios basada en centroides
- **Ventajas**: Rápido, eficiente para grandes datasets
- **Uso**: División inicial de colonias

#### DBSCAN (Density-Based Spatial Clustering)
- **Propósito**: Clustering basado en densidad espacial
- **Ventajas**: Detecta clusters de forma arbitraria
- **Uso**: División de zonas con densidad variable

#### Spectral Clustering
- **Propósito**: Clustering basado en similitud de grafos
- **Ventajas**: Efectivo para datos no lineales
- **Uso**: División compleja de territorios

### 2. Random Forest para Predicción

#### Características
- **Entrada**: 15 features (distancia, nodos, experiencia, etc.)
- **Salida**: Tiempo estimado de completado
- **Métricas**: MAE, R², RMSE
- **Persistencia**: Modelos serializados con pickle

#### Features Utilizadas
```python
features = [
    'distancia_km', 'num_nodos', 'area_zona_m2',
    'densidad_nodos_km2', 'densidad_calles_m_km2',
    'experiencia_empleado_dias', 'hora_inicio',
    'dia_semana', 'temperatura_celsius'
]
```

## 📊 Métricas y Análisis

### Silhouette Score
- **Propósito**: Evaluar calidad de clustering
- **Rango**: -1 a 1 (mayor es mejor)
- **Cálculo**: Tiempo real en cada ejecución de algoritmo

### Métricas de Eficiencia
- **Balance de Zonas**: Distribución equitativa de carga
- **Eficiencia de Rutas**: Optimización de distancias
- **Equidad de Cargas**: Balance entre empleados
- **Compactness**: Densidad de nodos por área

## 🔄 Sistema de Completado de Rutas

### Para Empleados
1. **Visualizar rutas asignadas** en el dashboard
2. **Hacer clic en "Completar"** en una ruta pendiente
3. **Llenar formulario** con tiempo real y notas
4. **Confirmar completado** - datos se guardan automáticamente

### Para Staff
1. **Acceder al panel de supervisión**
2. **Ver todas las rutas** y su estado
3. **Marcar como completada** cualquier ruta de cualquier empleado
4. **Ingresar datos** de tiempo real y fechas

### Integración con ML
- Cada ruta completada se convierte en **datos de entrenamiento**
- **Features automáticas** se extraen y almacenan
- **Modelo Random Forest** se puede re-entrenar con nuevos datos

## 🗄️ Modelos de Base de Datos

### Modelos Principales

#### ColoniaProcesada
```python
- nombre: Nombre de la colonia
- poligono_geojson: Datos GeoJSON del polígono
- area_aproximada: Área en km²
- fecha_creacion: Timestamp de creación
```

#### ConfiguracionRuta
```python
- colonia: FK a ColoniaProcesada
- rutas_data: JSON con datos de rutas
- algoritmo_usado: Algoritmo de división utilizado
- mapa_calculado: Datos del mapa generado
- estado: Estado de la configuración
```

#### RutaCompletada
```python
- empleado: FK a User
- configuracion_ruta: FK a ConfiguracionRuta
- tiempo_real_minutos: Tiempo real de ejecución
- eficiencia_porcentaje: Eficiencia calculada
- features_ml: Datos para entrenamiento de ML
```

#### ModeloPrediccionTiempo
```python
- nombre: Nombre del modelo
- version: Versión del modelo
- accuracy_score: Precisión del modelo
- modelo_archivo: Archivo serializado del modelo
- features_usadas: Lista de features utilizadas
```

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# settings.py
DEBUG = True
SECRET_KEY = 'your-secret-key'
DATABASE_URL = 'sqlite:///db.sqlite3'

# Configuración de algoritmos
DEFAULT_ALGORITHM = 'kernighan_lin'
ENABLE_ML_PREDICTIONS = True
```

### Configuración de Algoritmos
```python
# Algoritmos disponibles
ALGORITMOS_CHOICES = [
    ('kernighan_lin', 'Kernighan-Lin'),
    ('kmeans', 'K-means Clustering'),
    ('dbscan', 'DBSCAN'),
    ('spectral', 'Spectral Clustering'),
    ('voronoi', 'Voronoi'),
    ('random', 'Random Division')
]
```

## 📈 API Endpoints

### Rutas de Empleados
```http
GET /accounts/api/rutas_empleado/
POST /accounts/api/marcar_ruta_completada/
```

### Rutas de Staff
```http
GET /accounts/api/rutas_staff_supervision/
POST /accounts/api/marcar_ruta_completada_staff/
```

### Random Forest
```http
POST /accounts/api/entrenar_modelo_rf/
POST /accounts/api/predecir_tiempo_rf/
GET /accounts/api/estadisticas_rf/
```

### Algoritmos de IA
```http
POST /accounts/analizar_algoritmo/
GET /accounts/comparacion_algoritmos/
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Tests unitarios
python manage.py test

# Tests específicos
python manage.py test accounts.tests
python manage.py test core.tests
```

### Scripts de Prueba
```bash
# Probar Random Forest
python test_random_forest.py

# Probar algoritmos de clustering
python test_ai_algorithms.py
```

## 🚀 Despliegue

### Producción con Gunicorn
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 ceneval_project.wsgi:application
```

### Docker (Opcional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 📝 Logs y Debugging

### Logs del Sistema
```python
# Los logs se muestran en consola con emojis
print("✅ Ruta marcada como completada")
print("❌ Error en procesamiento")
print("🔄 Cargando datos...")
```

### Debugging de Algoritmos
```python
# Logs detallados de ejecución
print(f"🤖 Ejecutando {algoritmo} en colonia {colonia_id}")
print(f"📊 Métricas calculadas: {metricas}")
```

## 🔮 Roadmap y Mejoras Futuras

### Próximas Funcionalidades
- [ ] **API de Clima**: Integración con OpenWeatherMap
- [ ] **Optimización Dinámica**: Re-asignación en tiempo real
- [ ] **Machine Learning Avanzado**: Deep Learning para predicciones
- [ ] **Mobile App**: Aplicación móvil para empleados
- [ ] **Notificaciones**: Sistema de alertas en tiempo real

### Mejoras Técnicas
- [ ] **Caché Redis**: Optimización de consultas
- [ ] **Celery**: Procesamiento asíncrono
- [ ] **WebSockets**: Comunicación en tiempo real
- [ ] **Microservicios**: Arquitectura distribuida

## 🤝 Contribución

### Guías de Contribución
1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

### Estándares de Código
- **Python**: PEP 8
- **JavaScript**: ESLint
- **CSS**: BEM methodology
- **Commits**: Conventional Commits

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Autores

- **Desarrollador Principal**: [Tu Nombre]
- **Contribuidores**: [Lista de contribuidores]

## 🙏 Agradecimientos

- **Scikit-learn**: Por las librerías de Machine Learning
- **OpenStreetMap**: Por los datos de mapas
- **Django**: Por el framework web
- **Leaflet.js**: Por la visualización de mapas

## 📞 Soporte

### Contacto
- **Email**: [tu-email@ejemplo.com]
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/proyecto/issues)
- **Documentación**: [Wiki del proyecto](https://github.com/tu-usuario/proyecto/wiki)

### FAQ
**Q: ¿Cómo cambio el algoritmo por defecto?**
A: Ve a Admin Dashboard > Configuración de Algoritmos

**Q: ¿Cómo entreno el modelo Random Forest?**
A: Ve a Researcher Dashboard > Random Forest > Entrenar Modelo

**Q: ¿Cómo marco una ruta como completada?**
A: Como empleado: Employee Dashboard > Mis Rutas > Completar
Como staff: Staff Dashboard > Supervisión > Completar

---

**⭐ ¡No olvides dar una estrella al proyecto si te fue útil!**
