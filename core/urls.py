
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("procesar_colonia/", views.procesar_colonia, name="procesar_colonia"),
    path("editor/", views.mapa_editor, name="mapa_editor"),
    path("editor/config/", views.config_editor, name="config_editor"),
    path("editor/guardar/", views.guardar_poligono_editor, name="guardar_poligono_editor"),
    path("editor/reporte/", views.generar_reporte_colonia, name="generar_reporte_colonia"),
]
