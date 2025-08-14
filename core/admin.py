from django.contrib import admin
from .models import ColoniaProcesada, ConfiguracionRuta, ChatMessage, ChatParticipant, EficienciaAlgoritmica

@admin.register(ColoniaProcesada)
class ColoniaProcesadaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'nombre_normalizado', 'fecha_creacion', 'creado_por', 'tiene_imagen', 'tiene_poligono']
    list_filter = ['fecha_creacion', 'creado_por']
    search_fields = ['nombre', 'nombre_normalizado']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion', 'nombre_normalizado']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'nombre_normalizado', 'creado_por')
        }),
        ('Archivos', {
            'fields': ('imagen', 'poligono_geojson', 'datos_json', 'configuracion')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def tiene_imagen(self, obj):
        return bool(obj.imagen)
    tiene_imagen.boolean = True
    tiene_imagen.short_description = 'Tiene Imagen'
    
    def tiene_poligono(self, obj):
        return bool(obj.poligono_geojson)
    tiene_poligono.boolean = True
    tiene_poligono.short_description = 'Tiene Polígono'


@admin.register(ConfiguracionRuta)
class ConfiguracionRutaAdmin(admin.ModelAdmin):
    list_display = ['colonia', 'empleados_count', 'creado_por', 'estado', 'fecha_creacion', 'tiempo_calculado_display', 'tiene_mapa_html']
    list_filter = ['estado', 'fecha_creacion', 'colonia', 'creado_por']
    search_fields = ['colonia__nombre', 'empleados_asignados__username', 'notas', 'chat_asignado']
    readonly_fields = ['fecha_creacion', 'tiempo_de_asignacion', 'tiempo_calculado_display']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('colonia', 'empleados_asignados', 'creado_por', 'estado')
        }),
        ('Información de Empleados', {
            'fields': ('informacion_empleados',),
            'classes': ('collapse',)
        }),
        ('Detalles de Ruta', {
            'fields': ('notas', 'datos_ruta', 'mapa_calculado', 'mapa_html', 'tiempo_calculado')
        }),
        ('Comunicación', {
            'fields': ('chat_asignado',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'tiempo_de_asignacion'),
            'classes': ('collapse',)
        }),
    )
    
    def empleados_count(self, obj):
        return obj.get_empleados_count()
    empleados_count.short_description = 'Empleados'
    
    def tiempo_calculado_display(self, obj):
        return obj.get_tiempo_formateado()
    tiempo_calculado_display.short_description = 'Tiempo Est.'
    
    def tiene_mapa_html(self, obj):
        return bool(obj.mapa_html)
    tiene_mapa_html.boolean = True
    tiene_mapa_html.short_description = 'Mapa HTML'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['configuracion_ruta', 'usuario', 'contenido_corto', 'tipo_mensaje', 'timestamp', 'es_leido']
    list_filter = ['tipo_mensaje', 'timestamp', 'es_leido', 'configuracion_ruta__colonia']
    search_fields = ['contenido', 'usuario__username', 'configuracion_ruta__colonia__nombre']
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Información del Mensaje', {
            'fields': ('configuracion_ruta', 'usuario', 'contenido', 'tipo_mensaje')
        }),
        ('Estado y Metadata', {
            'fields': ('es_leido', 'mensaje_padre', 'metadatos', 'timestamp'),
            'classes': ('collapse',)
        }),
    )
    
    def contenido_corto(self, obj):
        return obj.contenido[:100] + '...' if len(obj.contenido) > 100 else obj.contenido
    contenido_corto.short_description = 'Contenido'


@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ['configuracion_ruta', 'usuario', 'rol_en_chat', 'ultimo_visto', 'notificaciones_activas', 'mensajes_no_leidos_count']
    list_filter = ['rol_en_chat', 'notificaciones_activas', 'configuracion_ruta__colonia']
    search_fields = ['usuario__username', 'configuracion_ruta__colonia__nombre']
    readonly_fields = ['ultimo_visto']
    
    fieldsets = (
        ('Información del Participante', {
            'fields': ('configuracion_ruta', 'usuario', 'rol_en_chat')
        }),
        ('Estado y Configuración', {
            'fields': ('ultimo_visto', 'notificaciones_activas')
        }),
    )
    
    def mensajes_no_leidos_count(self, obj):
        return obj.get_mensajes_no_leidos()
    mensajes_no_leidos_count.short_description = 'Mensajes No Leídos'


@admin.register(EficienciaAlgoritmica)
class EficienciaAlgoritmicaAdmin(admin.ModelAdmin):
    list_display = [
        'colonia', 
        'algoritmo_tipo', 
        'num_empleados', 
        'fecha_ejecucion',
        'usuario_ejecutor',
        'tiempo_ejecucion_segundos',
        'memoria_usada_mb',
        'get_score_general',
        'get_eficiencia_temporal',
        'get_balance_calificacion'
    ]
    
    list_filter = [
        'algoritmo_tipo', 
        'num_empleados', 
        'fecha_ejecucion',
        'usuario_ejecutor',
        'colonia'
    ]
    
    search_fields = [
        'colonia__nombre', 
        'usuario_ejecutor__username',
        'algoritmo_tipo'
    ]
    
    readonly_fields = [
        'fecha_ejecucion',
        'get_score_general',
        'get_eficiencia_temporal',
        'get_eficiencia_memoria',
        'get_balance_calificacion'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('colonia', 'algoritmo_tipo', 'num_empleados', 'usuario_ejecutor', 'fecha_ejecucion')
        }),
        ('Métricas de Rendimiento', {
            'fields': ('tiempo_ejecucion_segundos', 'memoria_usada_mb', 'get_eficiencia_temporal', 'get_eficiencia_memoria')
        }),
        ('Métricas de Calidad', {
            'fields': (
                'balance_zonas_porcentaje', 
                'eficiencia_rutas_porcentaje', 
                'equidad_cargas_porcentaje', 
                'compacidad_porcentaje',
                'get_score_general',
                'get_balance_calificacion'
            )
        }),
        ('Datos del Grafo', {
            'fields': ('total_nodos', 'total_aristas', 'nodos_zona1', 'nodos_zona2'),
            'classes': ('collapse',)
        }),
        ('Métricas de Área y Longitud', {
            'fields': (
                'area_total_m2', 'area_zona1_m2', 'area_zona2_m2',
                'longitud_total_m', 'longitud_zona1_m', 'longitud_zona2_m'
            ),
            'classes': ('collapse',)
        }),
        ('Métricas de Densidad', {
            'fields': (
                'densidad_nodos_zona1_por_km2', 'densidad_nodos_zona2_por_km2',
                'densidad_calles_zona1_m_por_km2', 'densidad_calles_zona2_m_por_km2'
            ),
            'classes': ('collapse',)
        }),
        ('Datos Adicionales', {
            'fields': ('zonas_generadas', 'parametros_algoritmo', 'metadatos_ejecucion', 'notas'),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-fecha_ejecucion']
    
    def get_score_general(self, obj):
        return f"{obj.get_score_general()}%"
    get_score_general.short_description = 'Score General'
    
    def get_eficiencia_temporal(self, obj):
        return obj.get_eficiencia_temporal()
    get_eficiencia_temporal.short_description = 'Eficiencia Temporal'
    
    def get_balance_calificacion(self, obj):
        return obj.get_balance_calificacion()
    get_balance_calificacion.short_description = 'Calificación Balance'
