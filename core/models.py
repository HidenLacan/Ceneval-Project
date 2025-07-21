from django.db import models
from django.conf import settings
import json

class ColoniaProcesada(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    nombre_normalizado = models.CharField(max_length=255, unique=True)
    imagen = models.ImageField(upload_to='colonias/imagenes/', null=True, blank=True)
    poligono_geojson = models.JSONField(null=True, blank=True)
    datos_json = models.JSONField(null=True, blank=True)
    configuracion = models.JSONField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='colonias_creadas')
    
    class Meta:
        verbose_name = "Colonia Procesada"
        verbose_name_plural = "Colonias Procesadas"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha_creacion.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Normalizar el nombre para el nombre_normalizado
        if not self.nombre_normalizado:
            self.nombre_normalizado = self.nombre.strip().lower().replace(' ', '_')
        super().save(*args, **kwargs)
    
    def get_poligono_coordinates(self):
        """Retorna las coordenadas del polígono en formato Leaflet"""
        if self.poligono_geojson and 'geometry' in self.poligono_geojson:
            coords = self.poligono_geojson['geometry']['coordinates'][0]
            # Convertir de [lon, lat] a [lat, lon] para Leaflet
            return [[lat, lon] for lon, lat in coords]
        return []
    
    def get_configuracion_centro(self):
        """Retorna el centro de la colonia para el mapa"""
        if self.configuracion:
            return {
                'center_lat': self.configuracion.get('center_lat'),
                'center_lon': self.configuracion.get('center_lon'),
                'bbox': self.configuracion.get('bbox', [])
            }
        return None


class ConfiguracionRuta(models.Model):
    """Modelo para guardar las configuraciones de rutas asignadas por el staff"""
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('activa', 'Activa'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    colonia = models.ForeignKey(ColoniaProcesada, on_delete=models.CASCADE, related_name='configuraciones_rutas')
    empleados_asignados = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='rutas_asignadas', limit_choices_to={'role': 'employee'})
    informacion_empleados = models.JSONField(null=True, blank=True)  # Información detallada de empleados
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField(blank=True, null=True)
    datos_ruta = models.JSONField(null=True, blank=True)  # Para guardar información específica de la ruta
    mapa_calculado = models.JSONField(null=True, blank=True)  # Datos del mapa con rutas calculadas
    chat_asignado = models.CharField(max_length=255, blank=True, null=True)  # ID o referencia del chat
    tiempo_calculado = models.DurationField(null=True, blank=True)  # Tiempo estimado de la ruta
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rutas_creadas')
    tiempo_de_asignacion = models.DateTimeField(auto_now_add=True)  # Cuándo se asignó la ruta
    
    class Meta:
        verbose_name = "Configuración de Ruta"
        verbose_name_plural = "Configuraciones de Rutas"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        empleados_str = ', '.join([emp.username for emp in self.empleados_asignados.all()])
        return f"Ruta en {self.colonia.nombre} - {empleados_str} ({self.estado})"
    
    def get_empleados_count(self):
        """Retorna el número de empleados asignados"""
        return self.empleados_asignados.count()
    
    def can_add_employee(self):
        """Verifica si se puede agregar más empleados (máximo 2)"""
        return self.empleados_asignados.count() < 2
    
    def get_tiempo_formateado(self):
        """Retorna el tiempo calculado en formato legible"""
        if self.tiempo_calculado:
            total_seconds = int(self.tiempo_calculado.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        return "No calculado"
    
    def get_empleados_info(self):
        """Retorna información detallada de los empleados asignados"""
        empleados = []
        for empleado in self.empleados_asignados.all():
            empleados.append({
                'id': empleado.id,
                'username': empleado.username,
                'email': empleado.email,
                'role': empleado.role,
                'fecha_asignacion': self.tiempo_de_asignacion.isoformat()
            })
        return empleados
