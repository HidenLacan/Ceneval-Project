from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from core.utils.main import download_bbox,procesar_poligono_completo, sanitize_filename
import json
import requests   
from django.views.decorators.csrf import csrf_exempt
from core.utils.polygon_logic import get_colonia_config 
import os
from pathlib import Path
# Create your views here.

def home(request):
    return render(request, "home.html")

def procesar_colonia(request):
    colonia = request.GET.get("colonia")
    if not colonia:
        return HttpResponseBadRequest("Falta el parámetro 'colonia'")

    try:
        cache_path = download_bbox(colonia)
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)  # 🔁 Aquí ya es una lista con la info original de Nominatim
        return JsonResponse(data, safe=False)  # ✅ Devolverlo tal cual
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

# GET /editor/
def mapa_editor(request):
    return render(request, "mapa.html")

# GET /editor/config/
def config_editor(request):
    colonia = request.GET.get("colonia")
    if not colonia:
        return HttpResponseBadRequest("Falta parámetro 'colonia'")

    try:
        # Usar el nombre original para la consulta a Nominatim
        cache_file_name = f"{sanitize_filename(colonia)}.json"
        base_cache_dir = Path(__file__).resolve().parent / "cache"
        cache_path = base_cache_dir / cache_file_name
        
        # Descargar si no existe
        if not cache_path.exists():
            try:
                download_bbox(colonia)
            except Exception as download_error:
                print(f"Error descargando {colonia}: {str(download_error)}")
                return JsonResponse({
                    "error": f"No se encontró '{colonia}' en Nominatim. Intenta con un nombre más específico.",
                    "details": str(download_error)
                }, status=404)
        
        # Verificar que el archivo existe después de la descarga
        if not cache_path.exists():
            return JsonResponse({
                "error": f"No se pudo obtener información para '{colonia}'",
                "suggestion": "Verifica el nombre de la colonia e intenta de nuevo"
            }, status=404)
        
        config = get_colonia_config(str(cache_path))
        return JsonResponse(config)
    except Exception as e:
        print(f"Error en config_editor: {str(e)}")
        return JsonResponse({
            "error": f"Error interno del servidor: {str(e)}",
            "suggestion": "Contacta al administrador"
        }, status=500)

# POST /editor/guardar/
@csrf_exempt
def guardar_poligono_editor(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Solo se permite POST")
    try:
        data = json.loads(request.body)
        nombre = data.get("nombre", "colonia_sin_nombre").strip().lower().replace(" ", "_")
        output_dir = os.path.join("core", "polygons")
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"{nombre}.json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return JsonResponse({"status": "ok", "message": f"Polígono guardado en {path}"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    

def generar_reporte_colonia(request):
    archivo = request.GET.get("archivo")
    if not archivo:
        return HttpResponseBadRequest("Falta el parámetro 'archivo'")

    try:
        resultado = procesar_poligono_completo(archivo)
        return JsonResponse(resultado)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
