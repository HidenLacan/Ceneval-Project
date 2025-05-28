# editor_launcher.py
import os
import json
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from threading import Thread


def shutdown_server():
    """Apaga el servidor HTTP si está en ejecución."""
    global httpd_reference
    if httpd_reference:
        print("🛑 Cerrando servidor (por función externa)...")
        Thread(target=httpd_reference.shutdown).start()

def launch_polygon_editor(colonia_nombre: str, cache_path: str, timeout: int = 300) -> str:
    """
    Lanza un servidor local con un mapa interactivo centrado en el bounding box
    de la colonia proporcionada. Espera a que el usuario dibuje un polígono y
    lo guarde como GeoJSON. Devuelve la ruta al archivo generado.
    """
    output_path = f"data/poligonos/{colonia_nombre}"
    os.makedirs("data/poligonos", exist_ok=True)

    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)[0]
    bbox = [float(x) for x in data["boundingbox"]]  # south, north, west, east

    center_lat = (bbox[0] + bbox[1]) / 2
    center_lon = (bbox[2] + bbox[3]) / 2
    nombre = data.get("name", data.get("display_name", "colonia_sin_nombre")).strip().lower().replace(" ", "_")

    
    colonia_config = {
        "bbox": bbox,
        "center_lat": center_lat,
        "center_lon": center_lon,
        "nombre": nombre
    }


    class Handler(SimpleHTTPRequestHandler):
        
        def do_GET(self):
            if self.path == "/config":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(colonia_config).encode("utf-8"))
            else:
                super().do_GET()
        
        
        def do_POST(self):
            global httpd_reference
            if self.path == "/guardar":
                content_len = int(self.headers.get('Content-Length'))
                body = self.rfile.read(content_len)
                with open(output_path, "wb") as f:
                    f.write(body)
                self.send_response(200)
                self.end_headers()

                print("🛑 Cerrando servidor (internamente)...")
                
                if httpd_reference:
                    Thread(target=httpd_reference.shutdown).start()

    def run_server():
        global httpd_reference
        with TCPServer(("", 8000), Handler) as httpd:
            httpd_reference = httpd
            webbrowser.open(f"http://localhost:8000/static/mapa.html")
            print("🌐 Servidor iniciado en http://localhost:8000")
            httpd.serve_forever()

    thread = Thread(target=run_server)
    thread.start()
    thread.join()

    if os.path.exists(output_path):
        print(f"✅ Polígono guardado en {output_path}")
        return output_path
    else:
        raise TimeoutError("⏱️ No se recibió polígono en el tiempo esperado.")
