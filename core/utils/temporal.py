# main.py (actualizado): Proyecto: División de rutas para vendedores en una colonia

import osmnx as ox
import networkx as nx
from networkx.algorithms.community.kernighan_lin import kernighan_lin_bisection
import folium
from shapely.geometry import shape, Polygon
import json
import os
import re
import geopandas as gpd
import requests
import matplotlib.pyplot as plt
from shapely.geometry import Point
from editor_launcher import launch_polygon_editor,shutdown_server

def sanitize_filename(name: str) -> str:
    return re.sub(r'\W+', '_', name.lower())

def download_bbox(place_name: str):
    print(f"Descargando bounding box de {place_name}...")

    cache_file = f"cache/{sanitize_filename(place_name)}.json"
    os.makedirs("cache", exist_ok=True)

    if os.path.exists(cache_file):
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

def split_graph(G, num_employees=2):
    """
    Divide el grafo en zonas según el número de empleados
    - Si num_employees = 1: toda la ruta va a part1
    - Si num_employees >= 2: divide en dos usando kernighan_lin_bisection
    """
    print(f"Dividiendo grafo para {num_employees} empleado(s)...")
    
    if num_employees == 1:
        # Si solo hay un empleado, asignar toda la ruta
        part1 = set(G.nodes())
        part2 = set()  # Vacío
        print("✅ Asignando toda la ruta al empleado único")
    else:
        # Si hay múltiples empleados, dividir en dos
        part1, part2 = kernighan_lin_bisection(G)
        print(f"✅ Dividiendo ruta en dos zonas: {len(part1)} y {len(part2)} nodos")
    
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
    output_folder = "mapas_division"
       # Generar nombre de archivo limpio y ruta completa
    filename = output_html or f"mapa_{sanitize_filename(place_name)}.html"
    nombre_archivo = os.path.join(output_folder, filename)
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
    print(f"🗺️ Mapa guardado en: {nombre_archivo}")

if __name__ == '__main__':
    colonia = "San Lorenzo Tezonco, Ciudad de México"
    cache_path = download_bbox(colonia)
    ruta_poligono = launch_polygon_editor(colonia,cache_path)
    shutdown_server()
    with open(ruta_poligono, "r", encoding="utf-8") as f:
        geojson = json.load(f)
        geometry = shape(geojson["geometry"])
        G = ox.graph_from_polygon(geometry, network_type='walk')
        G = nx.Graph(G)

    part1, part2 = split_graph(G)
    print(f"📊 Total de nodos: {len(G.nodes)}")
    print(f"🔴 Zona 1 (vendedor A): {len(part1)} nodos")
    print(f"🔵 Zona 2 (vendedor B): {len(part2)} nodos")
    long1, long2 = calcular_longitud_por_zona(G, part1, part2)
    print(f"🛣️ Longitud total zona 1 (rojo): {long1:.2f} m")
    print(f"🛣️ Longitud total zona 2 (azul): {long2:.2f} m")
    area1, area2 = calcular_area_por_zona(G, part1, part2)
    print(f"📐 Área zona 1 (rojo): {area1:.2f} m²")
    print(f"📐 Área zona 2 (azul): {area2:.2f} m²")
    dens_nodos1 = len(part1) / area1
    dens_nodos2 = len(part2) / area2
    dens_calles1 = long1 / area1
    dens_calles2 = long2 / area2
    print(f"🔗 Densidad de nodos zona 1: {dens_nodos1:.2f} nodos/km²")
    print(f"🔗 Densidad de nodos zona 2: {dens_nodos2:.2f} nodos/km²")
    print(f"🚏 Densidad de calles zona 1: {dens_calles1:.2f} m/km²")
    print(f"🚏 Densidad de calles zona 2: {dens_calles2:.2f} m/km²")
    draw_partitioned_graph(G, part1, part2)
    draw_graph_folium(G, part1, part2, place_name=colonia)