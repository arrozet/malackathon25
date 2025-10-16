#!/usr/bin/env python3
"""
Script de prueba para verificar la integración del chat frontend con el backend.

Este script simula las llamadas que haría el frontend de chat para verificar
que el servicio de IA está correctamente configurado y responde adecuadamente.

Uso:
    python scripts/test_chat_frontend.py
"""

import requests
import json
from typing import Dict, Any, List

# Configuración
BACKEND_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BACKEND_URL}/ai/chat"
HEALTH_ENDPOINT = f"{BACKEND_URL}/ai/health"


def check_health() -> Dict[str, Any]:
    """
    Verifica el estado de salud del servicio de IA.
    
    Returns:
        Dict con el estado de salud del servicio.
    """
    print("🔍 Verificando salud del servicio de IA...")
    
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        response.raise_for_status()
        
        health_data = response.json()
        
        print(f"✅ Estado: {health_data.get('status', 'unknown')}")
        print("📊 Componentes:")
        for component, status in health_data.get('components', {}).items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {component}: {'activo' if status else 'inactivo'}")
        
        return health_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al verificar salud: {e}")
        return {"status": "error", "error": str(e)}


def send_chat_message(message: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Envía un mensaje al servicio de chat.
    
    Args:
        message: Mensaje del usuario.
        chat_history: Historial de conversación opcional.
    
    Returns:
        Dict con la respuesta del asistente.
    """
    if chat_history is None:
        chat_history = []
    
    payload = {
        "message": message,
        "chat_history": chat_history
    }
    
    print(f"\n💬 Enviando mensaje: {message[:50]}...")
    
    try:
        response = requests.post(
            CHAT_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Timeout más largo para permitir procesamiento de IA
        )
        response.raise_for_status()
        
        response_data = response.json()
        
        print(f"✅ Respuesta recibida ({len(response_data.get('response', ''))} caracteres)")
        print(f"🔧 Herramientas usadas: {', '.join(response_data.get('tool_calls', []))}")
        print(f"📝 Respuesta: {response_data.get('response', '')[:200]}...")
        
        return response_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al enviar mensaje: {e}")
        return {"error": str(e)}


def test_conversation():
    """
    Ejecuta una conversación de prueba simulando el flujo del frontend.
    """
    print("\n" + "="*60)
    print("🧪 PRUEBA DE CONVERSACIÓN CON BRAIN AI")
    print("="*60)
    
    # Verificar salud primero
    health = check_health()
    
    if health.get('status') != 'healthy':
        print("\n⚠️ El servicio no está saludable. Continuando de todas formas...")
    
    # Historial de conversación (se acumula como en el frontend)
    conversation_history = []
    
    # Mensaje 1: Consulta simple
    print("\n" + "-"*60)
    print("TEST 1: Consulta simple sobre datos")
    print("-"*60)
    
    message1 = "¿Cuántos episodios de admisión hay en total en la base de datos?"
    response1 = send_chat_message(message1, conversation_history)
    
    if 'error' not in response1:
        # Actualizar historial como lo haría el frontend
        conversation_history.append({"role": "user", "content": message1})
        conversation_history.append({
            "role": "assistant",
            "content": response1.get('response', '')
        })
    
    # Mensaje 2: Pregunta de seguimiento (usa historial)
    print("\n" + "-"*60)
    print("TEST 2: Pregunta de seguimiento con contexto")
    print("-"*60)
    
    message2 = "¿Y cuántos de esos son readmisiones?"
    response2 = send_chat_message(message2, conversation_history)
    
    if 'error' not in response2:
        conversation_history.append({"role": "user", "content": message2})
        conversation_history.append({
            "role": "assistant",
            "content": response2.get('response', '')
        })
    
    # Mensaje 3: Análisis más complejo
    print("\n" + "-"*60)
    print("TEST 3: Solicitud de análisis")
    print("-"*60)
    
    message3 = "Analiza la distribución de episodios por género"
    response3 = send_chat_message(message3, conversation_history)
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE LA PRUEBA")
    print("="*60)
    print(f"✅ Mensajes enviados: 3")
    print(f"✅ Longitud del historial: {len(conversation_history)} mensajes")
    print(f"✅ Integración frontend-backend: {'FUNCIONANDO' if 'error' not in response3 else 'CON ERRORES'}")
    
    print("\n💡 SIGUIENTE PASO:")
    print("   Accede a http://localhost:5173/chat en tu navegador para probar la interfaz de usuario.")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_conversation()

