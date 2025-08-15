#!/usr/bin/env python
"""
Script para probar el manejo de errores mejorado en la búsqueda de colonias
"""

import os
import sys
import django
import requests

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'routes_project.settings')
django.setup()

def test_error_handling():
    """Prueba el manejo de errores en diferentes casos"""
    print("=== Prueba de manejo de errores ===")
    
    base_url = "http://localhost:8000"
    
    # Casos de prueba que deberían fallar
    test_cases = [
        "colonia inexistente 12345",
        "colonia san jorge escobedo nuevo leon",  # El caso problemático
        "lugar que no existe",
        "123456789",
        ""
    ]
    
    for colonia in test_cases:
        print(f"\nProbando: '{colonia}'")
        try:
            response = requests.get(f"{base_url}/editor/config/?colonia={colonia}")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Éxito: {data}")
            else:
                try:
                    error_data = response.json()
                    print(f"  ❌ Error: {error_data.get('error', 'Error desconocido')}")
                    if 'suggestion' in error_data:
                        print(f"  💡 Sugerencia: {error_data['suggestion']}")
                except:
                    print(f"  ❌ Error: {response.text}")
                    
        except Exception as e:
            print(f"  💥 Excepción: {str(e)}")

def test_successful_cases():
    """Prueba casos que deberían funcionar"""
    print("\n=== Prueba de casos exitosos ===")
    
    base_url = "http://localhost:8000"
    
    # Casos que deberían funcionar
    success_cases = [
        "San Jerónimo",
        "Colonia Roma",
        "Centro Histórico",
        "Coyoacán"
    ]
    
    for colonia in success_cases:
        print(f"\nProbando: '{colonia}'")
        try:
            response = requests.get(f"{base_url}/editor/config/?colonia={colonia}")
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Éxito: {data}")
            else:
                print(f"  ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"  💥 Excepción: {str(e)}")

if __name__ == "__main__":
    print("🧪 Iniciando pruebas de manejo de errores\n")
    
    try:
        test_error_handling()
        test_successful_cases()
        
        print("\n✅ Todas las pruebas completadas!")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {str(e)}")
        import traceback
        traceback.print_exc()
