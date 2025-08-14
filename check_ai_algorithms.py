#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'routes_project.settings')
django.setup()

from core.models import EficienciaAlgoritmica
from django.db.models import Count

def check_ai_algorithms():
    print("🧠 VERIFICACIÓN DE ALGORITMOS DE INTELIGENCIA ARTIFICIAL")
    print("=" * 60)
    
    # Algoritmos de IA implementados
    ai_algorithms = ['kmeans', 'dbscan', 'spectral']
    traditional_algorithms = ['current', 'random', 'voronoi']
    
    print("📊 ALGORITMOS DE IA EN LA BASE DE DATOS:")
    print("-" * 40)
    
    # Obtener estadísticas por algoritmo
    stats = EficienciaAlgoritmica.objects.values('algoritmo_tipo').annotate(
        count=Count('id')
    ).order_by('algoritmo_tipo')
    
    ai_count = 0
    traditional_count = 0
    
    for stat in stats:
        algo = stat['algoritmo_tipo']
        count = stat['count']
        
        if algo in ai_algorithms:
            print(f"🤖 {algo.upper()}: {count} ejecuciones (ALGORITMO DE IA)")
            ai_count += count
        elif algo in traditional_algorithms:
            print(f"⚙️  {algo.upper()}: {count} ejecuciones (Algoritmo tradicional)")
            traditional_count += count
        else:
            print(f"❓ {algo.upper()}: {count} ejecuciones (Desconocido)")
    
    print("\n📈 RESUMEN:")
    print("-" * 40)
    print(f"🤖 Algoritmos de IA: {ai_count} ejecuciones totales")
    print(f"⚙️  Algoritmos tradicionales: {traditional_count} ejecuciones totales")
    print(f"📊 Total de ejecuciones: {ai_count + traditional_count}")
    
    if ai_count > 0:
        print(f"✅ CONFIRMADO: Se han ejecutado {ai_count} algoritmos de IA")
        print("\n🔬 ALGORITMOS DE IA IMPLEMENTADOS:")
        print("- K-Means: Clustering basado en centroides")
        print("- DBSCAN: Clustering basado en densidad")
        print("- Spectral: Clustering espectral con kernel RBF")
    else:
        print("❌ No se encontraron ejecuciones de algoritmos de IA")
    
    print("\n📚 BIBLIOTECAS DE IA UTILIZADAS:")
    print("- scikit-learn: Machine Learning")
    print("- numpy: Computación numérica")
    print("- scipy: Algoritmos científicos")

if __name__ == '__main__':
    check_ai_algorithms()


