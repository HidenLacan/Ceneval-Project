from django.core.management.base import BaseCommand
from core.models import ConfiguracionRuta
from core.utils.main import procesar_poligono_completo
import json
import os


class Command(BaseCommand):
    help = 'Actualiza las rutas existentes con HTML del mapa'

    def handle(self, *args, **options):
        # Obtener rutas sin mapa_html
        rutas_sin_html = ConfiguracionRuta.objects.filter(mapa_html__isnull=True)
        
        self.stdout.write(f"Encontradas {rutas_sin_html.count()} rutas sin HTML del mapa")
        
        for ruta in rutas_sin_html:
            try:
                self.stdout.write(f"Procesando ruta {ruta.id} - {ruta.colonia.nombre}")
                
                # Verificar que la colonia tiene polígono
                if not ruta.colonia.poligono_geojson:
                    self.stdout.write(
                        self.style.ERROR(f"  ❌ Colonia {ruta.colonia.nombre} no tiene polígono")
                    )
                    continue
                
                # Crear archivo temporal con el polígono
                nombre_archivo = f"temp_update_{ruta.id}.json"
                ruta_temp = os.path.join("core", "polygons", nombre_archivo)
                
                with open(ruta_temp, "w", encoding="utf-8") as f:
                    json.dump(ruta.colonia.poligono_geojson, f)
                
                try:
                    # Procesar con el algoritmo
                    num_employees = ruta.empleados_asignados.count()
                    resultado = procesar_poligono_completo(nombre_archivo, num_employees)
                    
                    # Actualizar el mapa_html
                    if 'mapa_html_content' in resultado:
                        ruta.mapa_html = resultado['mapa_html_content']
                        ruta.save()
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✅ HTML del mapa actualizado para ruta {ruta.id}")
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f"  ❌ No se pudo generar HTML para ruta {ruta.id}")
                        )
                        
                finally:
                    # Limpiar archivo temporal
                    if os.path.exists(ruta_temp):
                        os.remove(ruta_temp)
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Error procesando ruta {ruta.id}: {str(e)}")
                )
        
        self.stdout.write(
            self.style.SUCCESS("Proceso de actualización completado")
        ) 