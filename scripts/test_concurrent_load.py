"""
Script para simular carga concurrente y verificar el comportamiento del pool.

Simula múltiples usuarios accediendo al frontend y usando el AI simultáneamente.
"""

import requests
import concurrent.futures
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"


def call_visualization():
    """Simula request del frontend a /data/visualization."""
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/data/visualization", timeout=10)
        elapsed = time.time() - start
        return {
            "endpoint": "visualization",
            "status": response.status_code,
            "time": f"{elapsed:.2f}s",
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "endpoint": "visualization",
            "status": "error",
            "time": "N/A",
            "success": False,
            "error": str(e)
        }


def call_categories():
    """Simula request del frontend a /data/categories."""
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/data/categories", timeout=10)
        elapsed = time.time() - start
        return {
            "endpoint": "categories",
            "status": response.status_code,
            "time": f"{elapsed:.2f}s",
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "endpoint": "categories",
            "status": "error",
            "time": "N/A",
            "success": False,
            "error": str(e)
        }


def call_insights():
    """Simula request del frontend a /insights."""
    try:
        start = time.time()
        response = requests.get(f"{BASE_URL}/insights", timeout=10)
        elapsed = time.time() - start
        return {
            "endpoint": "insights",
            "status": response.status_code,
            "time": f"{elapsed:.2f}s",
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "endpoint": "insights",
            "status": "error",
            "time": "N/A",
            "success": False,
            "error": str(e)
        }


def simulate_frontend_load():
    """Simula un usuario cargando el frontend (múltiples requests simultáneos)."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(call_visualization),
            executor.submit(call_categories),
            executor.submit(call_insights),
        ]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    return results


def test_concurrent_users(num_users=5):
    """
    Simula múltiples usuarios accediendo simultáneamente.
    
    Args:
        num_users (int): Número de usuarios simultáneos a simular.
    """
    print("=" * 80)
    print(f"  TEST DE CARGA CONCURRENTE - {num_users} USUARIOS SIMULTÁNEOS")
    print("=" * 80)
    print(f"\nInicio: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Simulando {num_users} usuarios cargando el frontend simultáneamente...")
    print("-" * 80)
    
    start_time = time.time()
    
    # Simular usuarios concurrentes
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [executor.submit(simulate_frontend_load) for _ in range(num_users)]
        all_results = []
        for future in concurrent.futures.as_completed(futures):
            all_results.extend(future.result())
    
    elapsed = time.time() - start_time
    
    # Analizar resultados
    successful = sum(1 for r in all_results if r.get("success"))
    failed = len(all_results) - successful
    
    print(f"\n{'=' * 80}")
    print(f"  RESULTADOS")
    print(f"{'=' * 80}")
    print(f"\nRequests totales: {len(all_results)}")
    print(f"Exitosos: {successful} ({successful/len(all_results)*100:.1f}%)")
    print(f"Fallidos: {failed} ({failed/len(all_results)*100:.1f}%)")
    print(f"Tiempo total: {elapsed:.2f}s")
    print(f"Throughput: {len(all_results)/elapsed:.2f} requests/segundo")
    
    # Agrupar por endpoint
    print(f"\n{'=' * 80}")
    print(f"  DESGLOSE POR ENDPOINT")
    print(f"{'=' * 80}")
    
    endpoints = {}
    for result in all_results:
        endpoint = result.get("endpoint")
        if endpoint not in endpoints:
            endpoints[endpoint] = []
        endpoints[endpoint].append(result)
    
    for endpoint, results in endpoints.items():
        success_count = sum(1 for r in results if r.get("success"))
        times = [float(r.get("time", "0").replace("s", "")) for r in results if r.get("success")]
        avg_time = sum(times) / len(times) if times else 0
        
        print(f"\n{endpoint.upper()}:")
        print(f"  Exitosos: {success_count}/{len(results)}")
        print(f"  Tiempo promedio: {avg_time:.2f}s")
    
    # Verificar estado del pool
    print(f"\n{'=' * 80}")
    print(f"  ESTADO FINAL DEL POOL")
    print(f"{'=' * 80}")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            pool = response.json().get("database", {}).get("pool", {})
            opened = pool.get("opened", 0)
            busy = pool.get("busy", 0)
            max_conn = pool.get("max", 0)
            
            print(f"\nAbiertas: {opened}/{max_conn}")
            print(f"En uso: {busy}")
            print(f"Disponibles: {opened - busy}")
            
            utilization = (busy / max_conn * 100) if max_conn > 0 else 0
            if utilization > 80:
                print(f"\n⚠️  ALERTA: Utilización alta ({utilization:.1f}%)")
            elif utilization > 50:
                print(f"\n⚡ INFO: Utilización moderada ({utilization:.1f}%)")
            else:
                print(f"\n✅ OK: Utilización baja ({utilization:.1f}%)")
    except Exception as e:
        print(f"\n❌ No se pudo obtener estado del pool: {e}")
    
    # Conclusión
    print(f"\n{'=' * 80}")
    if failed == 0:
        print("  ✅ TODOS LOS REQUESTS EXITOSOS")
        print("  El pool maneja bien la carga concurrente.")
    elif failed < len(all_results) * 0.1:  # < 10% de fallos
        print("  ⚠️  ALGUNOS FALLOS DETECTADOS")
        print(f"  {failed} de {len(all_results)} requests fallaron.")
        print("  Considera investigar si es necesario.")
    else:
        print("  ❌ MUCHOS FALLOS DETECTADOS")
        print(f"  {failed} de {len(all_results)} requests fallaron.")
        print("  Revisa la configuración del pool o la capacidad del servidor.")
    print(f"{'=' * 80}\n")


def main():
    """Punto de entrada principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test de carga concurrente")
    parser.add_argument(
        "--users",
        "-u",
        type=int,
        default=5,
        help="Número de usuarios simultáneos a simular (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Verificar que el servidor esté corriendo
    try:
        requests.get(BASE_URL, timeout=2)
    except Exception:
        print(f"\n❌ ERROR: Backend no está corriendo en {BASE_URL}")
        print("Asegúrate de que el servidor esté activo:\n")
        print("   cd app/back")
        print("   uvicorn main:app --reload --port 8000\n")
        return 1
    
    test_concurrent_users(args.users)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

