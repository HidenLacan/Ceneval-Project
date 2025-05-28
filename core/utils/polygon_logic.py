import json
from pathlib import Path

def get_colonia_config(cache_path: str) -> dict:
    """
    Lee el archivo de cache y construye la configuración para el editor.
    """
    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)[0]

    bbox = [float(x) for x in data["boundingbox"]]  # [south, north, west, east]
    center_lat = (bbox[0] + bbox[1]) / 2
    center_lon = (bbox[2] + bbox[3]) / 2
    nombre = data.get("name", data.get("display_name", "colonia_sin_nombre")).strip().lower().replace(" ", "_")

    return {
        "bbox": bbox,
        "center_lat": center_lat,
        "center_lon": center_lon,
        "nombre": nombre
    }
