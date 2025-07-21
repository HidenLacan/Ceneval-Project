# 📍 Sistema de Gestión de Rutas - Documentación

## 🗄️ **Dónde se Guardan las Rutas**

Las rutas se guardan en la **base de datos** usando el modelo `ConfiguracionRuta` en `core/models.py`.

### **Tabla: ConfiguracionRuta**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `colonia` | ForeignKey | Referencia a la colonia procesada |
| `empleados_asignados` | ManyToManyField | Empleados asignados a la ruta (máximo 2) |
| `informacion_empleados` | JSONField | Información detallada de cada empleado |
| `fecha_creacion` | DateTimeField | Fecha de creación de la ruta |
| `estado` | CharField | Estado: pendiente/activa/completada/cancelada |
| `notas` | TextField | Notas adicionales sobre la ruta |
| `datos_ruta` | JSONField | Datos específicos de la ruta calculada |
| `mapa_calculado` | JSONField | Datos del mapa con rutas visualizadas |
| `chat_asignado` | CharField | ID del chat asignado para comunicación |
| `tiempo_calculado` | DurationField | Tiempo estimado de la ruta |
| `creado_por` | ForeignKey | Usuario staff que creó la ruta |
| `tiempo_de_asignacion` | DateTimeField | Cuándo se asignó la ruta |

## 🔄 **Flujo de Guardado**

### **1. Frontend (staff_dashboard.html)**
- Staff selecciona colonia y empleados
- Hace clic en "Guardar"
- Se envía POST a `/accounts/guardar_configuracion_rutas/`

### **2. Backend (accounts/views.py)**
- Función `guardar_configuracion_rutas()` procesa la solicitud
- Valida datos y permisos
- Crea registro en `ConfiguracionRuta`
- Retorna confirmación al frontend

### **3. Base de Datos**
- Se guarda en tabla `core_configuracionruta`
- Se crean relaciones ManyToMany con empleados
- Se almacenan datos JSON con información detallada

## 📊 **Datos Guardados por Ruta**

### **Información de Empleados**
```json
{
  "id": 1,
  "username": "empleado1",
  "email": "empleado1@example.com",
  "role": "employee",
  "fecha_asignacion": "2024-01-15T10:30:00Z",
  "estado_asignacion": "activo"
}
```

### **Datos de Ruta**
```json
{
  "fecha_creacion_frontend": "2024-01-15T10:30:00Z",
  "empleados_ids": [1, 2],
  "empleados_usernames": ["empleado1", "empleado2"],
  "distancia_total": 15.5,
  "puntos_parada": 12,
  "tipo_ruta": "optimizada"
}
```

### **Mapa Calculado**
```json
{
  "rutas": [
    {
      "empleado_id": 1,
      "empleado_nombre": "empleado1",
      "color_ruta": "#e74c3c",
      "puntos": [],
      "distancia": 8.2,
      "tiempo_estimado": 25
    }
  ],
  "centro_colonia": {...},
  "poligono_colonia": {...}
}
```

## 🔍 **Consultas Disponibles**

### **Listar Rutas del Staff**
- **URL**: `/accounts/listar_rutas_staff/`
- **Método**: GET
- **Retorna**: Lista de rutas creadas por el usuario staff actual

### **Guardar Nueva Ruta**
- **URL**: `/accounts/guardar_configuracion_rutas/`
- **Método**: POST
- **Datos**: `colonia_id`, `empleados`, `fecha_creacion`

## 🛠️ **Funciones del Modelo**

### **ConfiguracionRuta.get_empleados_count()**
- Retorna el número de empleados asignados

### **ConfiguracionRuta.can_add_employee()**
- Verifica si se puede agregar más empleados (máximo 2)

### **ConfiguracionRuta.get_tiempo_formateado()**
- Retorna el tiempo calculado en formato legible (ej: "1h 30m")

### **ConfiguracionRuta.get_empleados_info()**
- Retorna información detallada de todos los empleados asignados

## 📁 **Archivos Relacionados**

- **Modelo**: `core/models.py` - Clase `ConfiguracionRuta`
- **Vistas**: `accounts/views.py` - Funciones de guardado y listado
- **URLs**: `accounts/urls.py` - Rutas de la API
- **Admin**: `core/admin.py` - Interfaz de administración
- **Frontend**: `accounts/templates/staff_dashboard.html` - Interfaz de usuario

## 🔐 **Validaciones de Seguridad**

- Solo usuarios con rol 'staff' pueden crear rutas
- Máximo 2 empleados por ruta
- Validación de existencia de colonia y empleados
- Verificación de roles de empleados (solo 'employee')

## 📈 **Estados de Ruta**

1. **pendiente**: Ruta creada pero no iniciada
2. **activa**: Ruta en ejecución
3. **completada**: Ruta finalizada exitosamente
4. **cancelada**: Ruta cancelada

## 💾 **Persistencia de Datos**

- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Migraciones**: Automáticas con Django ORM
- **Backup**: Incluido en respaldos de base de datos
- **Integridad**: Claves foráneas y validaciones de modelo 