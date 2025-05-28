import osmnx as ox
import networkx as nx
from networkx.algorithms.community import kernighan_lin_bisection
import folium
from shapely.geometry import shape, Polygon
import json
import os
import re
import geopandas as gpd
import requests
import matplotlib.pyplot as plt
from shapely.geometry import Point
#from editor_launcher import launch_polygon_editor,shutdown_server
from pathlib import Path
from osmnx.distance import add_edge_lengths

def sanitize_filename(name: str) -> str:
    return re.sub(r'\W+', '_', name.lower())

def download_bbox(place_name: str):
    print(f"Descargando bounding box de {place_name}...")
    base_cache_dir = Path(__file__).resolve().parent.parent / "cache"
    base_cache_dir.mkdir(parents=True, exist_ok=True)

    cache_file = base_cache_dir / f"{sanitize_filename(place_name)}.json"

    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": place_name,
            "format": "json",
            "limit": 1,
            "polygon_geojson": 1
        }
        headers = {"User-Agent": "mi-aplicacion-ceneval"}
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(f"Error en la petición: {response.status_code}")
        data = response.json()
        if not data:
            raise RuntimeError(f"No se encontró '{place_name}' en Nominatim.")
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Guardado en {cache_file}")

    return cache_file

def split_graph(G):
    print("Dividiendo grafo en dos zonas...")
    part1, part2 = kernighan_lin_bisection(G)
    return part1, part2

def draw_partitioned_graph(G, part1, part2):
    print("Dibujando el grafo con zonas en rojo y azul...")
    color_map = ['red' if node in part1 else 'blue' for node in G.nodes()]
    nx.draw(G, node_color=color_map, node_size=10, edge_color='gray', with_labels=False)
    plt.show()

def calcular_longitud_por_zona(G, part1, part2):
    total_part1 = 0
    total_part2 = 0
    for u, v, data in G.edges(data=True):
        length = data.get("length", 0)
        if u in part1 and v in part1:
            total_part1 += length
        elif u in part2 and v in part2:
            total_part2 += length
    return total_part1, total_part2

def calcular_area_por_zona(G, part1, part2):
    def area_de_particion(nodos):
        puntos = [Point((G.nodes[n]['x'], G.nodes[n]['y'])) for n in nodos]
        gdf = gpd.GeoDataFrame(geometry=puntos, crs="EPSG:4326")
        gdf = gdf.to_crs(epsg=32614)  # UTM zona 14N
        union_geom = gdf.geometry.union_all()
        hull = union_geom.convex_hull
        return hull.area / 1_000_000 if hull.area else 0
    return area_de_particion(part1), area_de_particion(part2)

def draw_graph_folium(G, part1, part2, place_name="colonia", output_html=None):
    print("Generando mapa interactivo con folium...")
    base_mapa_dir = Path(__file__).resolve().parent.parent / "mapas_division"
    base_mapa_dir.mkdir(parents=True, exist_ok=True)
    filename = output_html or f"mapa_{sanitize_filename(place_name)}.html"
    nombre_archivo = base_mapa_dir / filename

    centro = list(G.nodes(data=True))[0][1]
    m = folium.Map(location=[centro['y'], centro['x']], zoom_start=16)

    for u, v, data in G.edges(data=True):
        coords = [(pt[1], pt[0]) for pt in data['geometry'].coords] if 'geometry' in data else [
            (G.nodes[u]['y'], G.nodes[u]['x']),
            (G.nodes[v]['y'], G.nodes[v]['x'])
        ]
        color = 'red' if u in part1 and v in part1 else 'blue' if u in part2 and v in part2 else 'gray'
        folium.PolyLine(coords, color=color, weight=3, opacity=0.7).add_to(m)

    m.save(nombre_archivo)
    return os.path.abspath(nombre_archivo)  # ✅ retorna ruta absoluta correcta


from osmnx.distance import add_edge_lengths

def procesar_poligono_completo(nombre_archivo: str):
    ruta = os.path.join("core", "polygons", nombre_archivo)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

    with open(ruta, "r", encoding="utf-8") as f:
        geojson = json.load(f)

    geometry = shape(geojson["geometry"])
    G = ox.graph_from_polygon(geometry, network_type='walk')
    G = add_edge_lengths(G)
    G = nx.Graph(G)  # convertir a grafo no dirigido

    part1, part2 = split_graph(G)
    long1, long2 = calcular_longitud_por_zona(G, part1, part2)
    area1, area2 = calcular_area_por_zona(G, part1, part2)

    dens_nodos1 = len(part1) / area1 if area1 else 0
    dens_nodos2 = len(part2) / area2 if area2 else 0
    dens_calles1 = long1 / area1 if area1 else 0
    dens_calles2 = long2 / area2 if area2 else 0

    mapa_path = draw_graph_folium(G, part1, part2, place_name=nombre_archivo.replace(".json", ""))

    return {
        "status": "ok",
        "mapa_html": mapa_path,
        "nodos": {
            "zona1": len(part1),
            "zona2": len(part2),
            "total": len(G.nodes),
        },
        "longitudes": {
            "zona1_m": round(long1, 2),
            "zona2_m": round(long2, 2)
        },
        "areas": {
            "zona1_m2": round(area1, 2),
            "zona2_m2": round(area2, 2)
        },
        "densidades": {
            "nodos_por_km2_z1": round(dens_nodos1, 2),
            "nodos_por_km2_z2": round(dens_nodos2, 2),
            "calles_m_por_km2_z1": round(dens_calles1, 2),
            "calles_m_por_km2_z2": round(dens_calles2, 2)
        }
    }
