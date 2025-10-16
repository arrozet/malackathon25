"""
Script para monitorear el estado del pool de conexiones en tiempo real.

Este script muestra estadísticas del pool y alerta si se está agotando.
"""

import requests
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"


def get_pool_stats():
    """Obtiene estadísticas del pool de conexiones."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            pool_info = data.get("database", {}).get("pool", {})
            return pool_info
        return None
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return None


def format_pool_stats(pool_stats):
    """Formatea las estadísticas del pool para mostrarlas."""
    if not pool_stats:
        return "❌ No se pudo obtener estadísticas del pool"
    
    opened = pool_stats.get("opened", 0)
    busy = pool_stats.get("busy", 0)
    max_conn = pool_stats.get("max", 0)
    min_conn = pool_stats.get("min", 0)
    
    utilization = (busy / max_conn * 100) if max_conn > 0 else 0
    available = opened - busy
    
    # Status indicator
    if utilization < 50:
        status = "🟢 OK"
    elif utilization < 80:
        status = "🟡 MODERATE"
    else:
        status = "🔴 HIGH"
    
    return f"""
  {status} Pool Utilization: {utilization:.1f}%
  
  📊 Conexiones:
    - Abiertas (opened):  {opened}/{max_conn}
    - En uso (busy):      {busy}
    - Disponibles:        {available}
    - Mínimo (min):       {min_conn}
  
  💡 Capacidad restante: {max_conn - busy} conexiones
"""


def monitor_continuously(interval=3):
    """Monitorea el pool continuamente."""
    print("=" * 80)
    print("  MONITOR DE POOL DE CONEXIONES ORACLE")
    print("=" * 80)
    print(f"\nMonitoreando cada {interval} segundos. Presiona Ctrl+C para detener.\n")
    
    try:
        while True:
            now = datetime.now().strftime("%H:%M:%S")
            pool_stats = get_pool_stats()
            
            print(f"\r[{now}] {format_pool_stats(pool_stats)}", end="")
            
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\n✅ Monitoreo detenido.")
        sys.exit(0)


def check_once():
    """Muestra el estado del pool una sola vez."""
    print("=" * 80)
    print("  ESTADO DEL POOL DE CONEXIONES")
    print("=" * 80)
    
    pool_stats = get_pool_stats()
    print(format_pool_stats(pool_stats))
    
    if pool_stats:
        busy = pool_stats.get("busy", 0)
        max_conn = pool_stats.get("max", 0)
        utilization = (busy / max_conn * 100) if max_conn > 0 else 0
        
        if utilization > 80:
            print("⚠️  ALERTA: Pool casi agotado!")
            print("   Considera aumentar max_connections o investigar conexiones lentas.\n")
        elif utilization > 50:
            print("⚡ INFO: Pool con uso moderado, monitoreando...\n")
        else:
            print("✅ Pool funcionando con capacidad suficiente.\n")


def main():
    """Punto de entrada principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor de pool de conexiones Oracle")
    parser.add_argument(
        "--continuous",
        "-c",
        action="store_true",
        help="Monitorear continuamente (actualización cada 3 segundos)"
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=3,
        help="Intervalo de actualización en segundos (solo con --continuous)"
    )
    
    args = parser.parse_args()
    
    # Verificar que el servidor esté corriendo
    try:
        requests.get(BASE_URL, timeout=2)
    except Exception:
        print(f"\n❌ ERROR: Backend no está corriendo en {BASE_URL}")
        print("Asegúrate de que el servidor esté activo:")
        print("   cd app/back")
        print("   uvicorn main:app --reload --port 8000\n")
        return 1
    
    if args.continuous:
        monitor_continuously(args.interval)
    else:
        check_once()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

