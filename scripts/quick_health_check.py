"""
Quick health check script for Brain backend and frontend connectivity.

This script performs rapid diagnostics to verify:
- Backend is running and responsive
- Database connection pool is healthy
- Frontend proxy is working
- Critical endpoints are operational
"""

import requests
import sys
from typing import Dict, Any

BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173/api"

def check_endpoint(url: str, name: str) -> Dict[str, Any]:
    """
    Checks if an endpoint is responsive and healthy.
    
    Args:
        url (str): The endpoint URL to check
        name (str): Human-readable name for the endpoint
    
    Returns:
        dict: Result dictionary with status and details
    """
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            return {
                "name": name,
                "status": "✅ OK",
                "code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else None
            }
        else:
            return {
                "name": name,
                "status": "❌ ERROR",
                "code": response.status_code,
                "error": response.text[:200]
            }
    except requests.exceptions.ConnectionError:
        return {
            "name": name,
            "status": "❌ NO CONNECTION",
            "error": "Cannot connect to server"
        }
    except requests.exceptions.Timeout:
        return {
            "name": name,
            "status": "❌ TIMEOUT",
            "error": "Request timed out"
        }
    except Exception as e:
        return {
            "name": name,
            "status": "❌ ERROR",
            "error": str(e)
        }

def main():
    """
    Main health check routine.
    """
    print("=" * 80)
    print("  BRAIN - HEALTH CHECK RÁPIDO")
    print("=" * 80)
    print()
    
    # Check endpoints
    checks = [
        (f"{BACKEND_URL}/health", "Backend Directo (/health)"),
        (f"{FRONTEND_URL}/health", "Frontend Proxy (/api/health)"),
        (f"{FRONTEND_URL}/data/categories", "Categories Endpoint"),
        (f"{FRONTEND_URL}/data/visualization", "Visualization Endpoint"),
    ]
    
    results = []
    all_ok = True
    
    for url, name in checks:
        result = check_endpoint(url, name)
        results.append(result)
        
        if "ERROR" in result["status"] or "TIMEOUT" in result["status"] or "NO CONNECTION" in result["status"]:
            all_ok = False
        
        print(f"{result['status']} {name}")
        
        # Print pool stats for health endpoint
        if "/health" in url and result.get("data"):
            pool_info = result["data"].get("database", {}).get("pool", {})
            if pool_info:
                print(f"    Pool: {pool_info.get('busy', 0)}/{pool_info.get('max', 0)} conexiones ocupadas")
    
    print()
    print("=" * 80)
    
    if all_ok:
        print("✅ TODOS LOS SISTEMAS OPERATIVOS")
        print()
        print("El frontend debería poder conectarse sin problemas.")
        print("Si ves errores en el navegador, prueba:")
        print("  1. Refrescar la página (Ctrl + F5)")
        print("  2. Borrar caché del navegador")
        print("  3. Verificar la consola del navegador para errores")
        return 0
    else:
        print("❌ ALGUNOS SISTEMAS PRESENTAN PROBLEMAS")
        print()
        print("Acciones recomendadas:")
        print("  1. Verificar que el backend esté corriendo")
        print("  2. Verificar que el frontend esté corriendo")
        print("  3. Revisar logs del backend para errores")
        print("  4. Reiniciar servicios si es necesario")
        return 1

if __name__ == "__main__":
    sys.exit(main())

