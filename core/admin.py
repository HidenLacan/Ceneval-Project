from django.contrib import admin
from .models import ColoniaProcesada, ConfiguracionRuta

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
    list_display = ['colonia', 'empleados_count', 'creado_por', 'estado', 'fecha_creacion', 'tiempo_calculado_display']
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
            'fields': ('notas', 'datos_ruta', 'mapa_calculado', 'tiempo_calculado')
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
