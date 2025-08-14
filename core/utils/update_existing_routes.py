#!/usr/bin/env python
"""
Script para actualizar rutas existentes con HTML del mapa
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'routes_project.settings')
django.setup()

from core.models import ConfiguracionRuta, ColoniaProcesada
from core.utils.main import procesar_poligono_completo
import json
import tempfile


def update_existing_routes():
    """Actualiza las rutas existentes que no tienen mapa_html"""
    
    # Obtener rutas sin mapa_html
    rutas_sin_html = ConfiguracionRuta.objects.filter(mapa_html__isnull=True)
    
    print(f"Encontradas {rutas_sin_html.count()} rutas sin HTML del mapa")
    
    for ruta in rutas_sin_html:
        try:
            print(f"Procesando ruta {ruta.id} - {ruta.colonia.nombre}")
            
            # Verificar que la colonia tiene polígono
            if not ruta.colonia.poligono_geojson:
                print(f"  ❌ Colonia {ruta.colonia.nombre} no tiene polígono")
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
                    print(f"  ✅ HTML del mapa actualizado para ruta {ruta.id}")
                else:
                    print(f"  ❌ No se pudo generar HTML para ruta {ruta.id}")
                    
            finally:
                # Limpiar archivo temporal
                if os.path.exists(ruta_temp):
                    os.remove(ruta_temp)
                    
        except Exception as e:
            print(f"  ❌ Error procesando ruta {ruta.id}: {str(e)}")
    
    print("Proceso de actualización completado")


if __name__ == "__main__":
    update_existing_routes() 