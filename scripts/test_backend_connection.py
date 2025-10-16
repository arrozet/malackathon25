"""
Script para verificar la conexión del backend.

Verifica que todos los endpoints estén funcionando correctamente.
"""

import requests
import sys
import json

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Imprime un separador de sección."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_root():
    """Prueba el endpoint raíz."""
    print_section("1. Test Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_health():
    """Prueba el endpoint de health."""
    print_section("2. Test Health Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_visualization():
    """Prueba el endpoint de visualización."""
    print_section("3. Test Visualization Endpoint")
    try:
        # Test sin filtros
        response = requests.get(f"{BASE_URL}/data/visualization", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total episodios: {data.get('total_episodios', 'N/A')}")
            print(f"Distribución por sexo: {len(data.get('distribucion_sexo', []))} registros")
            print(f"Distribución por edad: {len(data.get('distribucion_edad', []))} registros")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_categories():
    """Prueba el endpoint de categorías."""
    print_section("4. Test Categories Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/data/categories", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            categories = data.get("categories", [])
            print(f"Categorías disponibles: {len(categories)}")
            if categories:
                print(f"Ejemplo: {categories[0]}")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_insights():
    """Prueba el endpoint de insights."""
    print_section("5. Test Insights Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/insights", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            insights = data.get("insights", [])
            print(f"Insights generados: {len(insights)}")
            if insights:
                print(f"Ejemplo: {insights[0].get('titulo', 'N/A')}")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_ai_health():
    """Prueba el health check del servicio de AI."""
    print_section("6. Test AI Health Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/ai/health", timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"AI Status: {data.get('status', 'N/A')}")
            components = data.get('components', {})
            print(f"\nComponentes:")
            for component, status in components.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {component}: {status}")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Ejecuta todos los tests."""
    print("\n" + "=" * 80)
    print("  BACKEND CONNECTION TEST SUITE")
    print("=" * 80)
    
    print(f"\n🔍 Testing backend at: {BASE_URL}")
    
    # Verificar que el servidor está corriendo
    try:
        requests.get(BASE_URL, timeout=2)
    except Exception as e:
        print(f"\n❌ ERROR: Backend no está corriendo en {BASE_URL}")
        print(f"   Detalles: {e}")
        print("\nAsegúrate de que el servidor esté corriendo:")
        print("   cd app/back")
        print("   uvicorn main:app --reload --port 8000")
        return 1
    
    # Ejecutar tests
    results = []
    results.append(("Root Endpoint", test_root()))
    results.append(("Health Endpoint", test_health()))
    results.append(("Visualization Endpoint", test_visualization()))
    results.append(("Categories Endpoint", test_categories()))
    results.append(("Insights Endpoint", test_insights()))
    results.append(("AI Health Endpoint", test_ai_health()))
    
    # Resumen
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 Backend está funcionando correctamente!")
        print("   El frontend debería poder conectarse sin problemas.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        print("   Revisa los logs del backend para más detalles.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

