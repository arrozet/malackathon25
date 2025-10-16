#!/usr/bin/env python3
"""
Test script for Mermaid diagram generation via AI.

This script tests the diagram specialist agent to ensure it generates
valid Mermaid diagrams that can be rendered in the frontend.
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000/api"
CHAT_ENDPOINT = f"{API_BASE_URL}/ai/chat"


def test_diagram_generation():
    """
    Test diagram generation with various requests.
    """
    print("\n" + "="*70)
    print("TESTING MERMAID DIAGRAM GENERATION")
    print("="*70 + "\n")
    
    # Test queries that should trigger diagram generation
    test_queries = [
        "Genera un diagrama de flujo del proceso de admisión hospitalaria",
        "Muéstrame un diagrama del flujo de trabajo de evaluación de pacientes",
        "Crea un diagrama de secuencia del proceso de registro",
        "Diagrama de estados para el ciclo de vida de un episodio",
    ]
    
    print("Consultas de prueba disponibles:\n")
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. {query}")
    
    print(f"{len(test_queries) + 1}. Escribir consulta personalizada\n")
    
    try:
        choice = input("Selección (1-5): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(test_queries):
            message = test_queries[int(choice) - 1]
        elif choice == str(len(test_queries) + 1):
            message = input("\nEscribe tu consulta para generar un diagrama: ").strip()
            if not message:
                print("❌ Consulta vacía. Saliendo.")
                return
        else:
            print("❌ Selección inválida. Saliendo.")
            return
        
        print(f"\n{'='*70}")
        print(f"Enviando consulta: {message}")
        print(f"{'='*70}\n")
        
        # Prepare request
        payload = {
            "message": message,
            "chat_history": []
        }
        
        # Send request
        response = requests.post(CHAT_ENDPOINT, json=payload, timeout=120)
        
        if response.status_code != 200:
            print(f"❌ Error HTTP {response.status_code}")
            print(response.text)
            return
        
        # Parse response
        data = response.json()
        response_text = data.get("response", "")
        tools_used = data.get("tool_calls", [])
        
        print("✅ Respuesta recibida\n")
        print(f"{'='*70}")
        print("Herramientas utilizadas:")
        print(f"{'='*70}\n")
        print(", ".join(tools_used) if tools_used else "Ninguna")
        
        print(f"\n{'='*70}")
        print("Respuesta del AI:")
        print(f"{'='*70}\n")
        print(response_text)
        
        # Check if response contains Mermaid code
        if "```mermaid" in response_text or "flowchart" in response_text or "graph" in response_text:
            print(f"\n{'='*70}")
            print("✅ ¡Diagrama Mermaid detectado en la respuesta!")
            print(f"{'='*70}\n")
            print("El diagrama debería renderizarse automáticamente en el frontend.")
            print("Navega a http://localhost:5173/chat y verifica la visualización.")
        else:
            print(f"\n{'='*70}")
            print("⚠️  No se detectó código Mermaid en la respuesta")
            print(f"{'='*70}\n")
            print("Es posible que el AI haya respondido de otra forma.")
            print("Intenta con una consulta más específica solicitando un diagrama.")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        print("\nAsegúrate de que el backend esté corriendo:")
        print("  cd app && python -m app.back.main")
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    test_diagram_generation()

