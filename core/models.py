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


class EficienciaAlgoritmica(models.Model):
    """Modelo para almacenar métricas de eficiencia de algoritmos de división"""
    
    ALGORITMO_CHOICES = [
        ('kernighan_lin', 'Kernighan-Lin'),
        ('current', 'Kernighan-Lin (Current)'),
        ('kmeans', 'K-Means Clustering'),
        ('voronoi', 'Voronoi Diagram'),
        ('random', 'Random Division'),
        ('dbscan', 'DBSCAN Clustering'),
        ('spectral', 'Spectral Clustering'),
    ]
    
    # Información básica
    colonia = models.ForeignKey(ColoniaProcesada, on_delete=models.CASCADE, related_name='eficiencias_algoritmo')
    algoritmo_tipo = models.CharField(max_length=20, choices=ALGORITMO_CHOICES)
    num_empleados = models.IntegerField()
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)
    usuario_ejecutor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analisis_realizados')
    
    # Métricas de rendimiento (performance)
    tiempo_ejecucion_segundos = models.FloatField(help_text='Tiempo de ejecución del algoritmo en segundos')
    memoria_usada_mb = models.FloatField(help_text='Memoria RAM utilizada en MB')
    
    # Métricas de calidad de división
    balance_zonas_porcentaje = models.FloatField(help_text='Balance entre zonas (0-100%)')
    eficiencia_rutas_porcentaje = models.FloatField(help_text='Eficiencia de las rutas generadas (0-100%)')
    equidad_cargas_porcentaje = models.FloatField(help_text='Equidad en la distribución de cargas (0-100%)')
    compacidad_porcentaje = models.FloatField(help_text='Compacidad de las zonas generadas (0-100%)')
    
    # Datos detallados del grafo procesado
    total_nodos = models.IntegerField(help_text='Total de nodos en el grafo')
    total_aristas = models.IntegerField(help_text='Total de aristas en el grafo')
    nodos_zona1 = models.IntegerField(help_text='Nodos asignados a la zona 1')
    nodos_zona2 = models.IntegerField(help_text='Nodos asignados a la zona 2')
    
    # Métricas de área y longitud
    area_total_m2 = models.FloatField(help_text='Área total procesada en metros cuadrados')
    area_zona1_m2 = models.FloatField(help_text='Área de la zona 1 en metros cuadrados')
    area_zona2_m2 = models.FloatField(help_text='Área de la zona 2 en metros cuadrados')
    longitud_total_m = models.FloatField(help_text='Longitud total de calles en metros')
    longitud_zona1_m = models.FloatField(help_text='Longitud de calles en zona 1 en metros')
    longitud_zona2_m = models.FloatField(help_text='Longitud de calles en zona 2 en metros')
    
    # Métricas de densidad
    densidad_nodos_zona1_por_km2 = models.FloatField(help_text='Densidad de nodos por km² en zona 1')
    densidad_nodos_zona2_por_km2 = models.FloatField(help_text='Densidad de nodos por km² en zona 2')
    densidad_calles_zona1_m_por_km2 = models.FloatField(help_text='Densidad de calles en metros por km² en zona 1')
    densidad_calles_zona2_m_por_km2 = models.FloatField(help_text='Densidad de calles en metros por km² en zona 2')
    
    # Datos JSON para información adicional
    zonas_generadas = models.JSONField(null=True, blank=True, help_text='Información detallada de las zonas generadas')
    parametros_algoritmo = models.JSONField(null=True, blank=True, help_text='Parámetros específicos utilizados por el algoritmo')
    metadatos_ejecucion = models.JSONField(null=True, blank=True, help_text='Metadatos adicionales de la ejecución')
    
    # Notas y observaciones
    notas = models.TextField(blank=True, null=True, help_text='Notas u observaciones sobre esta ejecución')
    
    class Meta:
        verbose_name = "Eficiencia Algorítmica"
        verbose_name_plural = "Eficiencias Algorítmicas"
        ordering = ['-fecha_ejecucion']
        indexes = [
            models.Index(fields=['colonia', 'algoritmo_tipo']),
            models.Index(fields=['fecha_ejecucion']),
            models.Index(fields=['algoritmo_tipo', 'num_empleados']),
        ]
    
    def __str__(self):
        return f"{self.algoritmo_tipo} - {self.colonia.nombre} ({self.num_empleados} emp.) - {self.fecha_ejecucion.strftime('%d/%m/%Y %H:%M')}"
    
    def get_score_general(self):
        """Calcula un score general promediando todas las métricas de calidad"""
        return round((
            self.balance_zonas_porcentaje + 
            self.eficiencia_rutas_porcentaje + 
            self.equidad_cargas_porcentaje + 
            self.compacidad_porcentaje
        ) / 4, 2)
    
    def get_eficiencia_temporal(self):
        """Retorna clasificación de eficiencia temporal"""
        if self.tiempo_ejecucion_segundos < 1.0:
            return "Excelente"
        elif self.tiempo_ejecucion_segundos < 3.0:
            return "Buena"
        elif self.tiempo_ejecucion_segundos < 5.0:
            return "Regular"
        else:
            return "Lenta"
    
    def get_eficiencia_memoria(self):
        """Retorna clasificación de eficiencia de memoria"""
        if self.memoria_usada_mb < 10.0:
            return "Excelente"
        elif self.memoria_usada_mb < 25.0:
            return "Buena"
        elif self.memoria_usada_mb < 50.0:
            return "Regular"
        else:
            return "Alta"
    
    def get_balance_calificacion(self):
        """Retorna calificación del balance de zonas"""
        if self.balance_zonas_porcentaje >= 90.0:
            return "Excelente"
        elif self.balance_zonas_porcentaje >= 80.0:
            return "Buena"
        elif self.balance_zonas_porcentaje >= 70.0:
            return "Regular"
        else:
            return "Deficiente"
    
    @classmethod
    def get_mejor_algoritmo_por_colonia(cls, colonia_id):
        """Retorna el algoritmo con mejor score general para una colonia específica"""
        resultados = cls.objects.filter(colonia_id=colonia_id).values('algoritmo_tipo').annotate(
            score_promedio=models.Avg(
                (models.F('balance_zonas_porcentaje') + 
                 models.F('eficiencia_rutas_porcentaje') + 
                 models.F('equidad_cargas_porcentaje') + 
                 models.F('compacidad_porcentaje')) / 4
            )
        ).order_by('-score_promedio')
        
        return resultados.first() if resultados else None
    
    @classmethod
    def get_estadisticas_algoritmo(cls, algoritmo_tipo):
        """Retorna estadísticas generales de un algoritmo específico"""
        resultados = cls.objects.filter(algoritmo_tipo=algoritmo_tipo)
        
        if not resultados.exists():
            return None
        
        return {
            'total_ejecuciones': resultados.count(),
            'tiempo_promedio': resultados.aggregate(models.Avg('tiempo_ejecucion_segundos'))['tiempo_ejecucion_segundos__avg'],
            'memoria_promedio': resultados.aggregate(models.Avg('memoria_usada_mb'))['memoria_usada_mb__avg'],
            'balance_promedio': resultados.aggregate(models.Avg('balance_zonas_porcentaje'))['balance_zonas_porcentaje__avg'],
            'score_promedio': resultados.aggregate(
                score_avg=models.Avg(
                    (models.F('balance_zonas_porcentaje') + 
                     models.F('eficiencia_rutas_porcentaje') + 
                     models.F('equidad_cargas_porcentaje') + 
                     models.F('compacidad_porcentaje')) / 4
                )
            )['score_avg']
        }


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
    mapa_html = models.TextField(null=True, blank=True)  # HTML completo del mapa para renderizar
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


class ChatMessage(models.Model):
    """Modelo para mensajes del sistema de chat por ruta"""
    TIPO_MENSAJE_CHOICES = [
        ('texto', 'Mensaje de Texto'),
        ('sistema', 'Mensaje del Sistema'),
        ('ubicacion', 'Compartir Ubicación'),
        ('rapido', 'Mensaje Rápido'),
    ]
    
    configuracion_ruta = models.ForeignKey(
        ConfiguracionRuta, 
        on_delete=models.CASCADE, 
        related_name='mensajes_chat'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='mensajes_enviados'
    )
    contenido = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    tipo_mensaje = models.CharField(max_length=20, choices=TIPO_MENSAJE_CHOICES, default='texto')
    es_leido = models.BooleanField(default=False)
    mensaje_padre = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='respuestas'
    )
    metadatos = models.JSONField(null=True, blank=True)  # Para coordenadas, etc.
    
    class Meta:
        verbose_name = "Mensaje de Chat"
        verbose_name_plural = "Mensajes de Chat"
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.usuario.username}: {self.contenido[:50]}... ({self.timestamp.strftime('%d/%m %H:%M')})"
    
    def get_tiempo_relativo(self):
        """Retorna tiempo relativo del mensaje"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        diff = now - self.timestamp
        
        if diff < timedelta(minutes=1):
            return "Hace menos de 1 minuto"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"Hace {minutes} minuto{'s' if minutes > 1 else ''}"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"Hace {hours} hora{'s' if hours > 1 else ''}"
        else:
            return self.timestamp.strftime('%d/%m/%Y %H:%M')
    
    def marcar_como_leido(self, usuario):
        """Marca el mensaje como leído por un usuario específico"""
        # Para simplicidad, usaremos un enfoque básico
        # En el futuro se puede crear un modelo ChatMessageRead separado
        if usuario != self.usuario:  # No marcar nuestros propios mensajes
            self.es_leido = True
            self.save()


class ChatParticipant(models.Model):
    """Modelo para tracking de participantes en chat"""
    ROLE_CHOICES = [
        ('staff', 'Staff'),
        ('empleado', 'Empleado'),
    ]
    
    configuracion_ruta = models.ForeignKey(
        ConfiguracionRuta, 
        on_delete=models.CASCADE, 
        related_name='participantes_chat'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    ultimo_visto = models.DateTimeField(auto_now_add=True)
    notificaciones_activas = models.BooleanField(default=True)
    rol_en_chat = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    class Meta:
        verbose_name = "Participante de Chat"
        verbose_name_plural = "Participantes de Chat"
        unique_together = ('configuracion_ruta', 'usuario')
    
    def __str__(self):
        return f"{self.usuario.username} en {self.configuracion_ruta.colonia.nombre}"
    
    def get_mensajes_no_leidos(self):
        """Retorna el número de mensajes no leídos para este participante"""
        return ChatMessage.objects.filter(
            configuracion_ruta=self.configuracion_ruta,
            timestamp__gt=self.ultimo_visto
        ).exclude(usuario=self.usuario).count()
    
    def actualizar_ultimo_visto(self):
        """Actualiza el timestamp de último visto"""
        from django.utils import timezone
        self.ultimo_visto = timezone.now()
        self.save()
