# 📍 Sistema de Gestión de Rutas - Documentación Completa

## 🏗️ **Arquitectura del Proyecto**

### **Estructura de Módulos**
```
Ceneval-Project/
├── accounts/                 # Gestión de usuarios y autenticación
│   ├── models.py            # Modelos de usuario y roles
│   ├── views.py             # Vistas de autenticación y dashboard
│   ├── urls.py              # URLs de la aplicación accounts
│   ├── utils.py             # Utilidades para PDF y email
│   └── templates/           # Plantillas HTML
├── core/                    # Lógica principal del sistema
│   ├── models.py            # Modelos de colonias y rutas
│   ├── views.py             # Vistas principales
│   ├── utils/               # Utilidades de procesamiento geográfico
│   │   ├── main.py          # Lógica principal de división de rutas
│   │   ├── polygon_logic.py # Lógica de polígonos
│   │   └── temporal.py      # Utilidades temporales
│   └── templates/           # Plantillas del core
├── routes_project/          # Configuración del proyecto Django
│   ├── settings.py          # Configuraciones del proyecto
│   └── urls.py              # URLs principales
└── media/                   # Archivos multimedia
```

## 👥 **Tipos de Usuario y Roles**

### **Jerarquía de Usuarios**
1. **Admin** (`admin`): Acceso completo al sistema
2. **Staff** (`staff`): Gestión de rutas y empleados
3. **Employee** (`employee`): Ejecución de rutas asignadas
4. **Researcher** (`researcher`): Acceso de solo lectura

### **Permisos por Rol**
- **Admin**: CRUD completo, gestión de usuarios, configuración del sistema
- **Staff**: Crear/editar rutas, asignar empleados, enviar emails, consultar rutas
- **Employee**: Ver rutas asignadas, marcar como completadas
- **Researcher**: Consultar datos, generar reportes

## 🗄️ **Modelos de Base de Datos**

### **1. User (Django Auth)**
```python
# Extensión del modelo User de Django
class User(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    # Campos adicionales según el rol
```

### **2. ColoniaProcesada (core/models.py)**
```python
class ColoniaProcesada(models.Model):
    nombre = models.CharField(max_length=255)
    archivo_poligono = models.FileField(upload_to='colonias/')
    fecha_procesamiento = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='pendiente')
    datos_geograficos = models.JSONField(default=dict)
```

### **3. ConfiguracionRuta (core/models.py)**
```python
class ConfiguracionRuta(models.Model):
    colonia = models.ForeignKey(ColoniaProcesada, on_delete=models.CASCADE)
    empleados_asignados = models.ManyToManyField(User, related_name='rutas_asignadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, default='pendiente')
    notas = models.TextField(blank=True)
    datos_ruta = models.JSONField(default=dict)
    mapa_calculado = models.JSONField(default=dict)  # Datos del mapa renderizable
    tiempo_calculado = models.DurationField(null=True, blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rutas_creadas')
    tiempo_de_asignacion = models.DateTimeField(auto_now_add=True)
```

## 🔗 **Relaciones entre Modelos**

### **Diagrama de Relaciones**
```
User (1) ←→ (N) ConfiguracionRuta (empleados_asignados)
User (1) ←→ (N) ConfiguracionRuta (creado_por)
ColoniaProcesada (1) ←→ (N) ConfiguracionRuta
```

### **Relaciones Específicas**
- **User → ConfiguracionRuta**: Un usuario puede estar asignado a múltiples rutas
- **User → ConfiguracionRuta**: Un staff puede crear múltiples rutas
- **ColoniaProcesada → ConfiguracionRuta**: Una colonia puede tener múltiples configuraciones de ruta

## 🧮 **Funciones Principales**

### **1. División de Rutas (core/utils/main.py)**

#### **split_graph(G, num_employees=2)**
```python
def split_graph(G, num_employees=2):
    """
    Divide el grafo en zonas según el número de empleados
    - Si num_employees = 1: toda la ruta va a part1
    - Si num_employees >= 2: divide en dos usando kernighan_lin_bisection
    """
```
**Lógica de División:**
- **1 empleado**: Toda la ruta se asigna al empleado único
- **2 empleados**: Se divide usando el algoritmo Kernighan-Lin
- **3+ empleados**: Error de validación (máximo 2 permitidos)

#### **procesar_poligono_completo(nombre_archivo, num_employees=2)**
```python
def procesar_poligono_completo(nombre_archivo: str, num_employees=2):
    """
    Procesa un polígono completo y genera rutas divididas
    Retorna: calles_ruta1, calles_ruta2, mapa_calculado
    """
```

### **2. Gestión de Rutas (accounts/views.py)**

#### **dividir_poligono_para_empleados**
```python
@login_required
def dividir_poligono_para_empleados(request):
    """
    API endpoint para dividir polígono según empleados asignados
    - Valida máximo 2 empleados
    - Procesa división real del grafo
    - Retorna datos de rutas calculadas
    """
```

#### **guardar_configuracion_rutas**
```python
@login_required
def guardar_configuracion_rutas(request):
    """
    Guarda configuración de ruta con datos reales calculados
    - Procesa polígono completo
    - Almacena mapa_calculado con coordenadas reales
    - Calcula tiempo estimado basado en datos reales
    """
```

#### **consultar_rutas_staff**
```python
@login_required
def consultar_rutas_staff(request):
    """
    Vista para consultar rutas guardadas
    - Lista rutas del staff actual
    - Permite enviar emails a empleados
    - Renderiza mapa_calculado almacenado
    """
```

### **3. Envío de Emails (accounts/utils.py)**

#### **send_route_email**
```python
def send_route_email(configuracion_ruta, empleados_info):
    """
    Envía email con PDF de ruta a empleados asignados
    - Genera PDF con reportlab
    - Adjunta mapa de la ruta
    - Envía via SMTP configurado
    """
```

#### **generate_route_pdf**
```python
def generate_route_pdf(configuracion_ruta, empleados_info):
    """
    Genera PDF con información de la ruta
    - Detalles de la colonia
    - Información de empleados
    - Métricas de la ruta
    """
```

## 📊 **Estructura de Datos JSON**

### **mapa_calculado (ConfiguracionRuta)**
```json
{
  "rutas": [
    {
      "empleado_id": 7,
      "empleado_nombre": "useremployee2",
      "color_ruta": "#e74c3c",
      "puntos": [
        {"lat": 25.803322, "lon": -100.321804},
        {"lat": 25.804748, "lon": -100.321649}
      ],
      "distancia": 2.01,
      "tiempo_estimado": 26
    }
  ],
  "centro_colonia": {
    "center_lat": 25.80332285,
    "center_lon": -100.32180455,
    "bbox": [25.8013292, 25.8053165, -100.3234295, -100.3201796]
  },
  "poligono_colonia": {
    "type": "Feature",
    "properties": {},
    "geometry": {
      "type": "Polygon",
      "coordinates": [[[...]]]
    }
  }
}
```

### **datos_ruta (ConfiguracionRuta)**
```json
{
  "fecha_creacion_frontend": "2024-01-15T10:30:00Z",
  "empleados_ids": [1, 2],
  "empleados_usernames": ["empleado1", "empleado2"],
  "distancia_total": 15.5,
  "puntos_parada": 12,
  "tipo_ruta": "optimizada",
  "num_empleados": 2
}
```

## 🌐 **Endpoints de API**

### **Gestión de Rutas**
- `POST /accounts/dividir_poligono_para_empleados/` - Dividir ruta según empleados
- `POST /accounts/guardar_configuracion_rutas/` - Guardar configuración de ruta
- `GET /accounts/consultar_rutas_staff/` - Consultar rutas del staff
- `POST /accounts/obtener_mapa_calculado/` - Obtener datos del mapa

### **Envío de Emails**
- `POST /accounts/enviar_rutas_por_email/` - Enviar rutas desde consulta
- `POST /accounts/enviar_rutas_desde_dashboard/` - Enviar rutas desde dashboard

### **Autenticación**
- `GET /accounts/login/` - Página de login
- `POST /accounts/login/` - Procesar login
- `GET /accounts/logout/` - Cerrar sesión

## 🎨 **Interfaces de Usuario**

### **Staff Dashboard (accounts/templates/staff_dashboard.html)**
- **Selección de Colonia**: Dropdown con colonias disponibles
- **Selección de Empleados**: Checkbox múltiple (máximo 2)
- **Botones de Acción**:
  - "Guardar" - Guarda configuración de ruta
  - "Consultar Ruta" - Navega a consulta de rutas
  - "MANDAR INFORMACIÓN" - Envía emails con PDF

### **Consultar Rutas (accounts/templates/consultar_rutas_staff.html)**
- **Lista de Rutas**: Tabla con rutas guardadas
- **Visualización de Mapa**: Renderizado con Leaflet
- **Botón "Mandar información"**: Envía emails a empleados

### **Email Template (accounts/templates/email_route_assignment.html)**
- **Información de Colonia**: Nombre y detalles
- **Empleados Asignados**: Lista con información de contacto
- **Detalles de Ruta**: Distancia, tiempo estimado, puntos de parada

## ⚙️ **Configuración del Sistema**

### **Email (routes_project/settings.py)**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu_password_de_aplicacion'
DEFAULT_FROM_EMAIL = 'tu_email@gmail.com'
```

### **Dependencias (requirements.txt)**
```
Django==4.2.0
osmnx==1.3.0
networkx==3.1
folium==0.14.0
shapely==2.0.1
geopandas==0.12.2
reportlab==4.4.3
weasyprint==66.0
```

## 🔒 **Validaciones de Seguridad**

### **Autenticación**
- `@login_required` en todas las vistas sensibles
- Verificación de roles específicos para cada operación
- CSRF protection en todos los formularios

### **Validaciones de Negocio**
- Máximo 2 empleados por ruta
- Solo usuarios 'employee' pueden ser asignados
- Solo usuarios 'staff' pueden crear rutas
- Validación de existencia de colonias y empleados

### **Integridad de Datos**
- Foreign key constraints en base de datos
- Validación de formato JSON en campos JSONField
- Sanitización de datos de entrada

## 📈 **Estados y Flujos**

### **Estados de Ruta**
1. **pendiente**: Ruta creada, lista para asignación
2. **activa**: Ruta en ejecución por empleados
3. **completada**: Ruta finalizada exitosamente
4. **cancelada**: Ruta cancelada por staff

### **Flujo de Creación de Ruta**
1. Staff selecciona colonia y empleados (máximo 2)
2. Sistema divide polígono según número de empleados
3. Se calculan rutas reales con coordenadas
4. Se guarda configuración con mapa_calculado
5. Staff puede enviar emails con PDF a empleados

### **Flujo de Envío de Emails**
1. Staff hace clic en "MANDAR INFORMACIÓN"
2. Sistema genera PDF con datos de la ruta
3. Se envía email individual a cada empleado
4. Se adjunta PDF con mapa y detalles de la ruta

## 🛠️ **Utilidades y Herramientas**

### **Procesamiento Geográfico (core/utils/)**
- **main.py**: Lógica principal de división de grafos
- **polygon_logic.py**: Manejo de polígonos y coordenadas
- **temporal.py**: Utilidades temporales de procesamiento

### **Generación de Documentos (accounts/utils.py)**
- **generate_route_pdf**: Creación de PDFs con reportlab
- **generate_map_image**: Generación de imágenes de mapas
- **send_route_email**: Envío de emails con adjuntos

### **Cache y Almacenamiento**
- **cache/**: Archivos JSON temporales de procesamiento
- **media/**: Archivos subidos (polígonos, imágenes)
- **polygons/**: Datos de polígonos procesados

## 🔍 **Operaciones de Base de Datos**

### **Consultas Comunes**
```sql
-- Listar rutas de un staff
SELECT * FROM core_configuracionruta WHERE creado_por_id = ?;

-- Obtener empleados de una ruta
SELECT u.* FROM auth_user u 
JOIN core_configuracionruta_empleados_asignados cr ON u.id = cr.user_id 
WHERE cr.configuracionruta_id = ?;

-- Limpiar datos (deshabilitar foreign keys)
PRAGMA foreign_keys = OFF;
DELETE FROM core_configuracionruta_empleados_asignados;
DELETE FROM core_configuracionruta;
PRAGMA foreign_keys = ON;
```

### **Métodos del Modelo**
```python
# Obtener información de empleados
configuracion.get_empleados_info()

# Verificar límite de empleados
configuracion.can_add_employee()

# Obtener tiempo formateado
configuracion.get_tiempo_formateado()

# Contar empleados asignados
configuracion.get_empleados_count()
```

## 🚀 **Despliegue y Mantenimiento**

### **Comandos de Django**
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver

# Shell de Django
python manage.py shell
```

### **Configuración de Producción**
- Configurar variables de entorno para emails
- Usar base de datos PostgreSQL
- Configurar servidor web (nginx + gunicorn)
- Configurar SSL/TLS para emails
- Implementar logging y monitoreo

## 📝 **Notas de Desarrollo**

### **Cambios Recientes**
- Implementación de división condicional de rutas (1 vs 2 empleados)
- Integración de generación y envío de PDFs por email
- Creación de vista "Consultar Rutas" para staff
- Mejora en almacenamiento de datos reales en mapa_calculado
- Validación de máximo 2 empleados por ruta

### **Consideraciones Técnicas**
- Los datos en mapa_calculado son completamente renderizables
- El sistema maneja automáticamente la división según número de empleados
- Los emails se envían de forma asíncrona para mejor rendimiento
- Se implementa validación robusta en todos los endpoints 