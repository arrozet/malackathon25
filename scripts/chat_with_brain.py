    #!/usr/bin/env python3
"""
Chat interactivo con Brain via HTTP endpoints.

Este script conecta al servidor FastAPI corriendo y permite chatear con Brain.
Requiere que el servidor esté corriendo: cd app/back && python main.py
"""

import requests
import json
import sys


BASE_URL = "http://localhost:8000"
CHAT_URL = f"{BASE_URL}/ai/chat"
HEALTH_URL = f"{BASE_URL}/ai/health"


def print_colored(text: str, color: str = "white", end: str = "\n"):
    """Print con colores."""
    colors = {
        "blue": "\033[94m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "purple": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[0m",
    }
    end_color = "\033[0m"
    print(f"{colors.get(color, colors['white'])}{text}{end_color}", end=end)


def check_server():
    """Verifica que el servidor esté corriendo."""
    # Primero intentar con el endpoint raíz (más rápido)
    try:
        print_colored("Verificando servidor...", "cyan")
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            print_colored("✓ Servidor FastAPI conectado", "green")
        else:
            print_colored(f"⚠ Servidor responde pero con código: {response.status_code}", "yellow")
    except requests.RequestException as e:
        print_colored(f"✗ No se puede conectar al servidor en {BASE_URL}", "red")
        print_colored(f"  Error: {e}", "red")
        print_colored("\nAsegúrate de que el servidor esté corriendo:", "yellow")
        print_colored("  cd app/back", "yellow")
        print_colored("  python main.py", "yellow")
        return False
    
    # Intentar health check del AI service (puede tardar si está inicializando)
    try:
        print_colored("Verificando AI Service...", "cyan")
        response = requests.get(HEALTH_URL, timeout=30)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            if status == "healthy":
                print_colored("✓ AI Service saludable - Todas las herramientas disponibles", "green")
            elif status == "degraded":
                print_colored("⚠ AI Service degradado - Algunas herramientas pueden no funcionar", "yellow")
            else:
                print_colored(f"⚠ AI Service con estado: {status}", "yellow")
        else:
            print_colored(f"⚠ AI Service responde con código: {response.status_code}", "yellow")
            print_colored("  El chat funcionará pero algunas herramientas pueden fallar", "yellow")
    except requests.RequestException as e:
        print_colored(f"⚠ No se pudo verificar AI Service health: {str(e)[:100]}", "yellow")
        print_colored("  Continuando de todas formas...", "yellow")
    
    return True


def chat_interactive():
    """Modo chat interactivo con Brain."""
    print_colored("\n" + "=" * 80, "purple")
    print_colored("  BRAIN - Chat Interactivo", "purple")
    print_colored("=" * 80, "purple")
    
    # Verificar servidor
    if not check_server():
        sys.exit(1)
    
    print_colored("\nEscribe 'exit', 'quit' o 'salir' para terminar", "cyan")
    print_colored("Escribe 'clear' para limpiar el historial\n", "cyan")
    
    chat_history = []
    
    while True:
        try:
            # Prompt del usuario
            print_colored("\nYou: ", "blue", end="")
            user_input = input().strip()
            
            if not user_input:
                continue
            
            # Comandos especiales
            if user_input.lower() in ['exit', 'quit', 'salir']:
                print_colored("\n¡Hasta luego! 👋\n", "green")
                break
            
            if user_input.lower() == 'clear':
                chat_history = []
                print_colored("\n✓ Historial limpiado\n", "green")
                continue
            
            # Preparar payload
            payload = {
                "message": user_input,
                "chat_history": chat_history
            }
            
            # Hacer petición al servidor
            print_colored("\nBrain: ", "green", end="")
            print_colored("🤔 Pensando...", "yellow")
            
            try:
                response = requests.post(
                    CHAT_URL,
                    json=payload,
                    timeout=120  # 2 minutos para consultas complejas
                )
                
                if response.status_code == 200:
                    data = response.json()
                    brain_response = data.get("response", "")
                    tool_calls = data.get("tool_calls", [])
                    
                    # Mostrar respuesta
                    print_colored("\nBrain: ", "green")
                    print(brain_response)
                    
                    # Mostrar herramientas usadas
                    if tool_calls:
                        tools_str = ", ".join(tool_calls)
                        print_colored(f"\n[Herramientas usadas: {tools_str}]", "cyan")
                    
                    # Actualizar historial
                    chat_history.append({"role": "user", "content": user_input})
                    chat_history.append({"role": "assistant", "content": brain_response})
                
                else:
                    print_colored(f"\n✗ Error del servidor: {response.status_code}", "red")
                    try:
                        error_data = response.json()
                        print_colored(f"  Detalle: {error_data.get('detail', 'Sin detalles')}", "red")
                    except:
                        print_colored(f"  Respuesta: {response.text[:200]}", "red")
            
            except requests.Timeout:
                print_colored("\n✗ Timeout: La consulta tardó demasiado", "red")
                print_colored("  Intenta con una pregunta más simple", "yellow")
            
            except requests.RequestException as e:
                print_colored(f"\n✗ Error de conexión: {e}", "red")
                print_colored("  ¿Sigue el servidor corriendo?", "yellow")
        
        except KeyboardInterrupt:
            print_colored("\n\n¡Hasta luego! 👋\n", "green")
            break
        
        except Exception as e:
            print_colored(f"\n✗ Error inesperado: {e}", "red")


def main():
    """Punto de entrada principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Chat interactivo con Brain AI Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  
  Consultas a Base de Datos:
    - "¿Cuántos episodios hay en total?"
    - "¿Cuál es la distribución por sexo?"
    - "Muéstrame las categorías más frecuentes"
  
  Búsqueda en Internet:
    - "Busca información sobre depresión"
    - "¿Qué es el código CIE-10 F32?"
  
  Análisis con Python:
    - "Calcula la media de 10, 20, 30, 40"
    - "Calcula estadísticas para estos datos: [5, 10, 15, 20]"
  
  Diagramas:
    - "Genera un diagrama del esquema de base de datos"
    - "Crea un diagrama de flujo de admisión"

Nota: El servidor debe estar corriendo en http://localhost:8000
      (cd app/back && python main.py)
        """
    )
    
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL del servidor (default: http://localhost:8000)"
    )
    
    args = parser.parse_args()
    
    global BASE_URL, CHAT_URL, HEALTH_URL
    BASE_URL = args.url
    CHAT_URL = f"{BASE_URL}/ai/chat"
    HEALTH_URL = f"{BASE_URL}/ai/health"
    
    chat_interactive()


if __name__ == "__main__":
    main()

