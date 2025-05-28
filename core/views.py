from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from core.utils.main import download_bbox,procesar_poligono_completo
import json
import requests   
from django.views.decorators.csrf import csrf_exempt
from core.utils.polygon_logic import get_colonia_config 
import os
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
        cache_path = download_bbox(colonia)
        config = get_colonia_config(cache_path)
        return JsonResponse(config)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

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
