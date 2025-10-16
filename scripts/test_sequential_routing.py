"""
Script para probar el routing secuencial de múltiples especialistas.

Envía una pregunta que requiere tanto SQL como búsqueda en internet,
y verifica que ambos especialistas se ejecuten correctamente.
"""

import requests
import json
import sys
import io

# Configurar stdout para usar UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_sequential_routing():
    """
    Prueba que el orchestrator pueda ejecutar múltiples especialistas en secuencia.
    """
    url = "http://localhost:8000/api/ai/chat/stream"
    
    # Pregunta que debería activar SQL + búsqueda en internet
    test_query = """
    ¿Cuántos episodios de esquizofrenia hay en la base de datos? 
    Además, busca información actualizada sobre los tratamientos más efectivos para la esquizofrenia.
    """
    
    payload = {
        "message": test_query,
        "conversation_history": []
    }
    
    print("=" * 80)
    print("PRUEBA DE ROUTING SECUENCIAL DE ESPECIALISTAS")
    print("=" * 80)
    print(f"\nPregunta: {test_query}")
    print("\n" + "-" * 80)
    print("Esperando respuesta del sistema multiagente...")
    print("-" * 80 + "\n")
    
    specialists_used = set()
    
    try:
        response = requests.post(
            url, 
            json=payload, 
            stream=True,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                
                # Skip comments and empty lines
                if line_str.startswith(':') or not line_str.strip():
                    continue
                
                # Parse SSE data
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # Remove 'data: ' prefix
                    
                    try:
                        event_data = json.loads(data_str)
                        event_type = event_data.get('type')
                        
                        if event_type == 'thinking_start':
                            agent = event_data.get('agent', 'unknown')
                            specialists_used.add(agent)
                            print(f"[OK] Iniciando: {agent}")
                        
                        elif event_type == 'thinking_end':
                            agent = event_data.get('agent', 'unknown')
                            print(f"[OK] Completado: {agent}")
                        
                        elif event_type == 'final_response':
                            content = event_data.get('content', '')
                            print("\n" + "=" * 80)
                            print("RESPUESTA FINAL:")
                            print("=" * 80)
                            print(content)
                        
                        elif event_type == 'error':
                            error_msg = event_data.get('content', 'Unknown error')
                            print(f"\n[ERROR]: {error_msg}")
                            return False
                    
                    except json.JSONDecodeError:
                        # Ignore malformed JSON
                        pass
        
        print("\n" + "=" * 80)
        print("RESUMEN DE ESPECIALISTAS EJECUTADOS:")
        print("=" * 80)
        
        for specialist in specialists_used:
            print(f"  • {specialist}")
        
        print("\n" + "=" * 80)
        
        # Verificar que se ejecutaron múltiples especialistas
        if len(specialists_used) >= 2:
            print("[EXITO] Se ejecutaron multiples especialistas en secuencia")
            return True
        else:
            print(f"[ADVERTENCIA] Solo se ejecuto {len(specialists_used)} especialista(s)")
            print("   Se esperaban al menos 2 (SQL + busqueda en internet)")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR DE CONEXION]: {e}")
        print("\nVerifica que el backend este corriendo en http://localhost:8000")
        return False
    except Exception as e:
        print(f"\n[ERROR INESPERADO]: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_sequential_routing()
    sys.exit(0 if success else 1)

