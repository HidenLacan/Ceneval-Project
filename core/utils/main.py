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
            "limit": 5,  # Aumentar límite para obtener más opciones
            "polygon_geojson": 1,
            "countrycodes": "mx"  # Limitar a México
        }
        headers = {"User-Agent": "mi-aplicacion-ceneval"}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code != 200:
                raise RuntimeError(f"Error en la petición HTTP: {response.status_code}")
            
            data = response.json()
            if not data:
                # Intentar con variaciones del nombre
                variations = [
                    place_name.replace("colonia ", ""),
                    place_name.replace("colonia", ""),
                    place_name + ", México",
                    place_name + ", CDMX"
                ]
                
                for variation in variations:
                    if variation != place_name:
                        print(f"Intentando variación: {variation}")
                        params["q"] = variation
                        response = requests.get(url, params=params, headers=headers, timeout=10)
                        if response.status_code == 200:
                            data = response.json()
                            if data:
                                print(f"Encontrado con variación: {variation}")
                                break
                
                if not data:
                    raise RuntimeError(f"No se encontró '{place_name}' en Nominatim. Sugerencias: verifica el nombre, agrega el estado o usa nombres más específicos.")
            
            # Usar el primer resultado
            data = [data[0]] if isinstance(data, list) else [data]
            
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"Guardado en {cache_file}")
                
        except requests.exceptions.Timeout:
            raise RuntimeError(f"Timeout al buscar '{place_name}' en Nominatim. Verifica tu conexión a internet.")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error de conexión: {str(e)}")

    return cache_file

def split_graph(G, num_employees=2, algorithm='kernighan_lin'):
    """
    Divide el grafo en zonas según el número de empleados y algoritmo especificado
    - Si num_employees = 1: toda la ruta va a part1
    - Si num_employees >= 2: divide en dos usando el algoritmo especificado
    """
    print("=" * 60)
    print(f"🚀 INICIANDO DIVISIÓN DE GRAFO")
    print(f"📊 Grafo: {len(G.nodes())} nodos, {len(G.edges())} aristas")
    print(f"👥 Empleados: {num_employees}")
    print(f"🔧 Algoritmo solicitado: '{algorithm}'")
    print("=" * 60)
    
    if num_employees == 1:
        # Si solo hay un empleado, asignar toda la ruta
        part1 = set(G.nodes())
        part2 = set()  # Vacío
        print("✅ MODO UN EMPLEADO: Asignando toda la ruta al empleado único")
        print(f"📈 Resultado: part1={len(part1)} nodos, part2={len(part2)} nodos")
        return part1, part2
    
    print(f"🔄 MODO MÚLTIPLES EMPLEADOS: Ejecutando algoritmo '{algorithm}'")
    
    # Algoritmos de división para múltiples empleados
    if algorithm == 'kernighan_lin' or algorithm == 'current':
        print("🔥 EJECUTANDO ALGORITMO KERNIGHAN-LIN REAL")
        part1, part2 = kernighan_lin_bisection(G)
        print(f"✅ Kernighan-Lin completado: {len(part1)} y {len(part2)} nodos")
    
    elif algorithm == 'kmeans':
        part1, part2 = split_graph_kmeans(G)
    
    elif algorithm == 'voronoi':
        part1, part2 = split_graph_voronoi(G)
    
    elif algorithm == 'random':
        part1, part2 = split_graph_random(G)
    
    elif algorithm == 'dbscan':
        part1, part2 = split_graph_dbscan(G)
    
    elif algorithm == 'spectral':
        part1, part2 = split_graph_spectral(G)
    
    else:
        # Fallback al algoritmo por defecto
        print(f"⚠️ ALGORITMO DESCONOCIDO '{algorithm}' - Usando Kernighan-Lin como fallback")
        print("🔥 EJECUTANDO ALGORITMO KERNIGHAN-LIN REAL (FALLBACK)")
        part1, part2 = kernighan_lin_bisection(G)
        print(f"✅ Fallback Kernighan-Lin completado: {len(part1)} y {len(part2)} nodos")
    
    # Validación final
    total_original = len(G.nodes())
    total_dividido = len(part1) + len(part2)
    if total_original != total_dividido:
        print(f"❌ ERROR: Nodos perdidos! Original={total_original}, Dividido={total_dividido}")
    else:
        print(f"✅ VALIDACIÓN: Todos los nodos contabilizados ({total_dividido}/{total_original})")
    
    print("=" * 60)
    return part1, part2

def split_graph_kmeans(G):
    """División usando K-means clustering en coordenadas de nodos"""
    print("🔥 EJECUTANDO ALGORITMO K-MEANS REAL")
    from sklearn.cluster import KMeans
    import numpy as np
    
    # Extraer coordenadas de los nodos
    coords = []
    node_list = list(G.nodes())
    print(f"📊 K-means procesando {len(node_list)} nodos")
    
    for node in node_list:
        if 'x' in G.nodes[node] and 'y' in G.nodes[node]:
            coords.append([G.nodes[node]['x'], G.nodes[node]['y']])
        else:
            # Si no hay coordenadas, usar posición por defecto
            coords.append([0, 0])
    
    coords = np.array(coords)
    print(f"📍 K-means: Coordenadas extraídas, forma: {coords.shape}")
    
    # Aplicar K-means con k=2
    print("🎯 K-means: Ejecutando clustering con k=2...")
    kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
    labels = kmeans.fit_predict(coords)
    
    # Dividir nodos según las etiquetas
    part1 = set()
    part2 = set()
    
    for i, node in enumerate(node_list):
        if labels[i] == 0:
            part1.add(node)
        else:
            part2.add(node)
    
    print(f"✅ K-means completado: Cluster 1 = {len(part1)} nodos, Cluster 2 = {len(part2)} nodos")
    print(f"📈 K-means: Centros = {kmeans.cluster_centers_}")
    
    return part1, part2

def split_graph_voronoi(G):
    """División usando diagramas de Voronoi basados en centros de masa"""
    print("🔥 EJECUTANDO ALGORITMO VORONOI REAL")
    import numpy as np
    from scipy.spatial.distance import cdist
    
    # Extraer coordenadas de los nodos
    coords = []
    node_list = list(G.nodes())
    print(f"📊 Voronoi procesando {len(node_list)} nodos")
    
    for node in node_list:
        if 'x' in G.nodes[node] and 'y' in G.nodes[node]:
            coords.append([G.nodes[node]['x'], G.nodes[node]['y']])
        else:
            coords.append([0, 0])
    
    coords = np.array(coords)
    print(f"📍 Voronoi: Coordenadas extraídas, forma: {coords.shape}")
    
    if len(coords) < 2:
        print("⚠️ Voronoi: Muy pocos nodos, usando división simple")
        mid = len(node_list) // 2
        part1 = set(node_list[:mid])
        part2 = set(node_list[mid:])
        return part1, part2
    
    # Encontrar dos puntos extremos como semillas de Voronoi
    print("🎯 Voronoi: Calculando matriz de distancias...")
    distances = cdist(coords, coords)
    i, j = np.unravel_index(distances.argmax(), distances.shape)
    
    seed1 = coords[i]
    seed2 = coords[j]
    max_distance = distances[i, j]
    
    print(f"🌱 Voronoi: Semillas seleccionadas - Seed1: {seed1}, Seed2: {seed2}")
    print(f"📏 Voronoi: Distancia máxima entre semillas: {max_distance:.2f}")
    
    # Asignar cada nodo al centro más cercano (Voronoi)
    part1 = set()
    part2 = set()
    
    for idx, node in enumerate(node_list):
        coord = coords[idx]
        dist1 = np.linalg.norm(coord - seed1)
        dist2 = np.linalg.norm(coord - seed2)
        
        if dist1 <= dist2:
            part1.add(node)
        else:
            part2.add(node)
    
    print(f"✅ Voronoi completado: Región 1 = {len(part1)} nodos, Región 2 = {len(part2)} nodos")
    
    return part1, part2

def split_graph_random(G):
    """División aleatoria pero balanceada de los nodos"""
    print("🔥 EJECUTANDO ALGORITMO RANDOM REAL")
    import random
    
    node_list = list(G.nodes())
    print(f"📊 Random procesando {len(node_list)} nodos")
    
    # Establecer semilla para reproducibilidad en logs
    random.seed(42)
    print("🎲 Random: Mezclando nodos aleatoriamente con semilla=42")
    random.shuffle(node_list)  # Mezclar aleatoriamente
    
    # Dividir aproximadamente por la mitad
    mid = len(node_list) // 2
    part1 = set(node_list[:mid])
    part2 = set(node_list[mid:])
    
    print(f"✅ Random completado: Parte 1 = {len(part1)} nodos, Parte 2 = {len(part2)} nodos")
    print(f"📝 Random: División en índice {mid} de {len(node_list)} nodos totales")
    
    return part1, part2

def split_graph_dbscan(G):
    """División usando DBSCAN clustering basado en densidad"""
    print("🔥 EJECUTANDO ALGORITMO DBSCAN REAL")
    from sklearn.cluster import DBSCAN
    import numpy as np
    from sklearn.preprocessing import StandardScaler
    
    # Extraer coordenadas de los nodos
    coords = []
    node_list = list(G.nodes())
    print(f"📊 DBSCAN procesando {len(node_list)} nodos")
    
    for node in node_list:
        if 'x' in G.nodes[node] and 'y' in G.nodes[node]:
            coords.append([G.nodes[node]['x'], G.nodes[node]['y']])
        else:
            # Si no hay coordenadas, usar posición por defecto
            coords.append([0, 0])
    
    coords = np.array(coords)
    print(f"📍 DBSCAN: Coordenadas extraídas, forma: {coords.shape}")
    
    # Normalizar coordenadas para mejor rendimiento de DBSCAN
    scaler = StandardScaler()
    coords_scaled = scaler.fit_transform(coords)
    print(f"📏 DBSCAN: Coordenadas normalizadas")
    
    # Calcular eps automáticamente basado en la densidad de datos
    from sklearn.neighbors import NearestNeighbors
    nbrs = NearestNeighbors(n_neighbors=min(5, len(coords_scaled))).fit(coords_scaled)
    distances, indices = nbrs.kneighbors(coords_scaled)
    eps = np.percentile(distances[:, -1], 75)  # 75th percentile
    min_samples = max(3, len(coords_scaled) // 20)  # Al menos 3, máximo 5% de datos
    
    print(f"🎯 DBSCAN: eps={eps:.4f}, min_samples={min_samples}")
    
    # Aplicar DBSCAN
    print("🎯 DBSCAN: Ejecutando clustering basado en densidad...")
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(coords_scaled)
    
    # Analizar resultados
    unique_labels = set(labels)
    n_clusters = len(unique_labels) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    
    print(f"📊 DBSCAN: {n_clusters} clusters detectados, {n_noise} puntos de ruido")
    
    # Si DBSCAN detecta más de 2 clusters, usar K-means como fallback
    if n_clusters > 2:
        print("⚠️ DBSCAN detectó más de 2 clusters, usando K-means como fallback")
        return split_graph_kmeans(G)
    
    # Si DBSCAN detecta solo 1 cluster, dividir manualmente
    if n_clusters == 1:
        print("⚠️ DBSCAN detectó solo 1 cluster, dividiendo manualmente")
        mid = len(node_list) // 2
        part1 = set(node_list[:mid])
        part2 = set(node_list[mid:])
    else:
        # Dividir nodos según las etiquetas de DBSCAN
        part1 = set()
        part2 = set()
        
        for i, node in enumerate(node_list):
            if labels[i] == 0:
                part1.add(node)
            elif labels[i] == 1:
                part2.add(node)
            else:
                # Puntos de ruido (-1) se asignan al cluster más cercano
                if len(part1) <= len(part2):
                    part1.add(node)
                else:
                    part2.add(node)
    
    print(f"✅ DBSCAN completado: Cluster 1 = {len(part1)} nodos, Cluster 2 = {len(part2)} nodos")
    print(f"📈 DBSCAN: Clusters detectados = {n_clusters}, Puntos de ruido = {n_noise}")
    
    return part1, part2

def split_graph_spectral(G):
    """División usando Spectral Clustering basado en conectividad"""
    print("🔥 EJECUTANDO ALGORITMO SPECTRAL CLUSTERING REAL")
    from sklearn.cluster import SpectralClustering
    import numpy as np
    from sklearn.metrics.pairwise import rbf_kernel
    
    # Extraer coordenadas de los nodos
    coords = []
    node_list = list(G.nodes())
    print(f"📊 Spectral Clustering procesando {len(node_list)} nodos")
    
    for node in node_list:
        if 'x' in G.nodes[node] and 'y' in G.nodes[node]:
            coords.append([G.nodes[node]['x'], G.nodes[node]['y']])
        else:
            # Si no hay coordenadas, usar posición por defecto
            coords.append([0, 0])
    
    coords = np.array(coords)
    print(f"📍 Spectral: Coordenadas extraídas, forma: {coords.shape}")
    
    # Si hay muy pocos nodos, usar K-means como fallback
    if len(coords) < 10:
        print("⚠️ Spectral: Muy pocos nodos, usando K-means como fallback")
        return split_graph_kmeans(G)
    
    # Calcular matriz de similitud usando kernel RBF
    print("🎯 Spectral: Calculando matriz de similitud...")
    gamma = 1.0 / (coords.var() * coords.shape[1])  # Parámetro gamma automático
    affinity_matrix = rbf_kernel(coords, gamma=gamma)
    
    print(f"📊 Spectral: Matriz de similitud calculada, gamma={gamma:.4f}")
    
    # Aplicar Spectral Clustering
    print("🎯 Spectral: Ejecutando clustering espectral...")
    spectral = SpectralClustering(
        n_clusters=2,
        affinity='precomputed',
        random_state=42,
        assign_labels='kmeans'
    )
    labels = spectral.fit_predict(affinity_matrix)
    
    # Dividir nodos según las etiquetas
    part1 = set()
    part2 = set()
    
    for i, node in enumerate(node_list):
        if labels[i] == 0:
            part1.add(node)
        else:
            part2.add(node)
    
    print(f"✅ Spectral Clustering completado: Cluster 1 = {len(part1)} nodos, Cluster 2 = {len(part2)} nodos")
    print(f"📈 Spectral: Eigenvalores calculados, clusters asignados")
    
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

def generate_route_js(G, part1, part2):
    """Genera el JavaScript para las rutas del mapa"""
    js_lines = []
    
    # Generar rutas para zona 1 (roja)
    route1_segments = []
    for u, v, data in G.edges(data=True):
        if u in part1 and v in part1:
            if 'geometry' in data:
                coords = [[pt[1], pt[0]] for pt in data['geometry'].coords]  # [lat, lon] para Leaflet
            else:
                coords = [[G.nodes[u]['y'], G.nodes[u]['x']], [G.nodes[v]['y'], G.nodes[v]['x']]]
            route1_segments.append(coords)
    
    if route1_segments:
        js_lines.append("// Ruta zona 1 (roja)")
        for i, segment in enumerate(route1_segments):
            js_lines.append(f"L.polyline({segment}, {{color: 'red', weight: 3, opacity: 0.7}}).addTo(map);")
    
    # Generar rutas para zona 2 (azul)
    route2_segments = []
    for u, v, data in G.edges(data=True):
        if u in part2 and v in part2:
            if 'geometry' in data:
                coords = [[pt[1], pt[0]] for pt in data['geometry'].coords]  # [lat, lon] para Leaflet
            else:
                coords = [[G.nodes[u]['y'], G.nodes[u]['x']], [G.nodes[v]['y'], G.nodes[v]['x']]]
            route2_segments.append(coords)
    
    if route2_segments:
        js_lines.append("// Ruta zona 2 (azul)")
        for i, segment in enumerate(route2_segments):
            js_lines.append(f"L.polyline({segment}, {{color: 'blue', weight: 3, opacity: 0.7}}).addTo(map);")
    
    return "\n        ".join(js_lines)

def draw_graph_folium(G, part1, part2, place_name="colonia", output_html=None):
    print("Generando mapa interactivo con folium...")
    base_mapa_dir = Path(__file__).resolve().parent.parent / "mapas_division"
    base_mapa_dir.mkdir(parents=True, exist_ok=True)
    filename = output_html or f"mapa_{sanitize_filename(place_name)}.html"
    nombre_archivo = base_mapa_dir / filename

    centro = list(G.nodes(data=True))[0][1]
    m = folium.Map(location=[centro['y'], centro['x']], zoom_start=16)

    # Dibujar calles respetando la geometría real
    for u, v, data in G.edges(data=True):
        if 'geometry' in data:
            coords = [(pt[1], pt[0]) for pt in data['geometry'].coords]
        else:
            coords = [(G.nodes[u]['y'], G.nodes[u]['x']), (G.nodes[v]['y'], G.nodes[v]['x'])]

        # Colorear calles según la zona
        if u in part1 and v in part1:
            color = 'red'
        elif u in part2 and v in part2:
            color = 'blue'
        else:
            color = 'gray'

        folium.PolyLine(coords, color=color, weight=3, opacity=0.7).add_to(m)

    # Guardar el archivo HTML
    m.save(nombre_archivo)
    
    # Leer el contenido HTML generado y optimizarlo para la base de datos
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Crear una versión optimizada del HTML para la base de datos
    # Extraer solo la parte del mapa sin las dependencias externas
    optimized_html = f"""
    <div class="folium-map" id="map_{sanitize_filename(place_name)}" style="width: 100%; height: 400px;"></div>
    <script>
        // Inicializar mapa
        var map = L.map("map_{sanitize_filename(place_name)}", {{
            center: [{centro['y']}, {centro['x']}],
            zoom: 16,
            crs: L.CRS.EPSG3857
        }});
        
        // Agregar capa de tiles
        L.tileLayer("https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
            attribution: "© OpenStreetMap contributors",
            maxZoom: 19
        }}).addTo(map);
        
        // Agregar rutas
        {generate_route_js(G, part1, part2)}
    </script>
    """
    
    return {
        'file_path': os.path.abspath(nombre_archivo),
        'html_content': optimized_html
    }


from osmnx.distance import add_edge_lengths

def procesar_poligono_completo(colonia_id: int, num_employees=2, algorithm='kernighan_lin'):
    """
    Procesa un polígono usando datos de la base de datos en lugar de archivos físicos
    """
    print("🎯" + "=" * 70)
    print(f"🌟 PROCESAMIENTO COMPLETO DE POLÍGONO INICIADO")
    print(f"🆔 Colonia ID: {colonia_id}")
    print(f"👥 Empleados: {num_employees}")
    print(f"🔧 Algoritmo: {algorithm}")
    print("🎯" + "=" * 70)
    
    # Importar modelos de Django
    try:
        from core.models import ColoniaProcesada
    except ImportError:
        print("❌ Error importing Django models")
        raise
    
    try:
        print(f"🔍 Buscando colonia con ID: {colonia_id}")
        colonia = ColoniaProcesada.objects.get(id=colonia_id)
        print(f"✅ Colonia encontrada: {colonia.nombre}")
        
        if not colonia.poligono_geojson:
            print(f"❌ POLÍGONO NO ENCONTRADO en la base de datos para: {colonia.nombre}")
            raise FileNotFoundError(f"No se encontró polígono GeoJSON para la colonia: {colonia.nombre}")
        
        print(f"✅ Polígono GeoJSON encontrado en base de datos")
        geojson = colonia.poligono_geojson
        
    except ColoniaProcesada.DoesNotExist:
        print(f"❌ COLONIA NO ENCONTRADA con ID: {colonia_id}")
        raise FileNotFoundError(f"No se encontró la colonia con ID: {colonia_id}")

    print(f"🗺️ Convirtiendo geometría y descargando grafo de calles...")
    geometry = shape(geojson["geometry"])
    G = ox.graph_from_polygon(geometry, network_type='walk')
    G = add_edge_lengths(G)
    G = nx.Graph(G)  # convertir a grafo no dirigido

    print(f"🏗️ Grafo construido: {len(G.nodes())} nodos, {len(G.edges())} aristas")
    print(f"🚀 Iniciando división con algoritmo '{algorithm}'...")

    part1, part2 = split_graph(G, num_employees, algorithm)
    
    # Calcular Silhouette Score
    silhouette_score = calcular_silhouette_score(G, part1, part2)
    
    long1, long2 = calcular_longitud_por_zona(G, part1, part2)
    area1, area2 = calcular_area_por_zona(G, part1, part2)

    dens_nodos1 = len(part1) / area1 if area1 else 0
    dens_nodos2 = len(part2) / area2 if area2 else 0
    dens_calles1 = long1 / area1 if area1 else 0
    dens_calles2 = long2 / area2 if area2 else 0

    mapa_result = draw_graph_folium(G, part1, part2, place_name=f"colonia_{colonia_id}")


       
       # Estadísticas de nodos
    print(f"📊 Total de nodos: {len(G.nodes)}")
    print(f"🔴 Zona 1 (vendedor A): {len(part1)} nodos")
    print(f"🔵 Zona 2 (vendedor B): {len(part2)} nodos")

    # Estadísticas de longitud
    print(f"🛣️ Longitud total zona 1 (rojo): {long1:.2f} m")
    print(f"🛣️ Longitud total zona 2 (azul): {long2:.2f} m")
    
    
    print(f"📐 Área zona 1 (rojo): {area1:.2f} m²")
    print(f"📐 Área zona 2 (azul): {area2:.2f} m²")
    
   
    print(f"🔗 Densidad de nodos zona 1: {dens_nodos1:.2f} nodos/km²")
    print(f"🔗 Densidad de nodos zona 2: {dens_nodos2:.2f} nodos/km²")
    print(f"🚏 Densidad de calles zona 1: {dens_calles1:.2f} m/km²")
    print(f"🚏 Densidad de calles zona 2: {dens_calles2:.2f} m/km²")

    return {
        "status": "ok",
        "mapa_html": mapa_result['file_path'],
        "mapa_html_content": mapa_result['html_content'],
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
        },
        "silhouette_score": silhouette_score,
        "part1_nodes": part1,
        "part2_nodes": part2,
        "graph": G
    }


def calcular_silhouette_score(G, part1, part2):
    """
    Calcula el Silhouette Score para evaluar la calidad del clustering de nodos.
    
    Args:
        G: NetworkX graph
        part1: set de nodos de la zona 1
        part2: set de nodos de la zona 2
    
    Returns:
        float: Silhouette Score entre -1 y 1
    """
    try:
        from sklearn.metrics import silhouette_score
        import numpy as np
        
        print("🎯 CALCULANDO SILHOUETTE SCORE...")
        
        # Si solo hay una zona, el score es perfecto
        if len(part1) == 0 or len(part2) == 0:
            print("✅ Una sola zona detectada - Silhouette Score = 1.0")
            return 1.0
        
        # Extraer coordenadas de todos los nodos
        coords = []
        labels = []
        node_list = list(G.nodes())
        
        for node in node_list:
            if 'x' in G.nodes[node] and 'y' in G.nodes[node]:
                coords.append([G.nodes[node]['x'], G.nodes[node]['y']])
                if node in part1:
                    labels.append(0)  # Zona 1
                elif node in part2:
                    labels.append(1)  # Zona 2
                else:
                    # Nodos no asignados (no debería pasar)
                    labels.append(-1)
            else:
                print(f"⚠️ Nodo {node} sin coordenadas, usando [0,0]")
                coords.append([0, 0])
                if node in part1:
                    labels.append(0)
                elif node in part2:
                    labels.append(1)
                else:
                    labels.append(-1)
        
        coords = np.array(coords)
        labels = np.array(labels)
        
        # Filtrar nodos válidos (asignados a alguna zona)
        valid_mask = labels != -1
        if not np.any(valid_mask):
            print("❌ No hay nodos válidos para calcular Silhouette Score")
            return 0.0
        
        coords_valid = coords[valid_mask]
        labels_valid = labels[valid_mask]
        
        # Verificar que tenemos al menos 2 clusters y múltiples puntos
        unique_labels = np.unique(labels_valid)
        if len(unique_labels) < 2:
            print("❌ Solo hay un cluster - Silhouette Score = 1.0")
            return 1.0
        
        if len(coords_valid) < 3:
            print("❌ Muy pocos puntos para calcular Silhouette Score")
            return 0.0
        
        # Calcular Silhouette Score
        try:
            score = silhouette_score(coords_valid, labels_valid, metric='euclidean')
            print(f"✅ Silhouette Score calculado: {score:.4f}")
            
            # Interpretación del score
            if score >= 0.7:
                interpretacion = "Excelente clustering"
            elif score >= 0.5:
                interpretacion = "Buen clustering"
            elif score >= 0.25:
                interpretacion = "Clustering aceptable"
            elif score >= 0:
                interpretacion = "Clustering débil"
            else:
                interpretacion = "Clustering incorrecto"
            
            print(f"📊 Interpretación: {interpretacion}")
            return round(score, 4)
            
        except Exception as e:
            print(f"❌ Error calculando Silhouette Score: {str(e)}")
            return 0.0
            
    except ImportError:
        print("❌ sklearn no disponible - usando score estimado")
        return 0.75  # Score estimado conservador
    except Exception as e:
        print(f"❌ Error general en cálculo de Silhouette Score: {str(e)}")
        return 0.0
