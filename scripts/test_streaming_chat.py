#!/usr/bin/env python3
"""
Test script for the streaming chat endpoint.

This script tests the new Server-Sent Events (SSE) streaming functionality
that provides real-time progress updates during AI processing.
"""

import requests
import json
import sys
from typing import Generator

# Configuration
API_BASE_URL = "http://localhost:8000/api"
STREAM_ENDPOINT = f"{API_BASE_URL}/ai/chat/stream"


def test_streaming_chat(message: str) -> None:
    """
    Test the streaming chat endpoint.
    
    Args:
        message (str): Message to send to the AI.
    """
    print(f"\n{'='*70}")
    print(f"Testing Streaming Chat")
    print(f"{'='*70}\n")
    print(f"Message: {message}\n")
    print(f"{'='*70}\n")
    
    # Prepare request payload
    payload = {
        "message": message,
        "chat_history": []
    }
    
    try:
        # Send POST request with streaming
        response = requests.post(
            STREAM_ENDPOINT,
            json=payload,
            stream=True,  # Enable streaming
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return
        
        print("✅ Connected to stream\n")
        print(f"{'='*70}")
        print("Real-time Progress Events:")
        print(f"{'='*70}\n")
        
        # Track events
        event_count = 0
        final_response = None
        
        # Process the SSE stream
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            
            # SSE format: "data: {json}\n\n"
            if line.startswith("data: "):
                event_count += 1
                json_str = line[6:]  # Remove "data: " prefix
                
                try:
                    event = json.loads(json_str)
                    event_type = event.get("type", "unknown")
                    message = event.get("message", "")
                    
                    # Display event with icon
                    icon = get_event_icon(event_type)
                    print(f"{icon} [{event_type.upper()}] {message}")
                    
                    # If it's the final response, save it
                    if event_type == "complete":
                        final_response = event.get("response", "")
                        tools_used = event.get("tools_used", [])
                        print(f"\n{'='*70}")
                        print("Final Response:")
                        print(f"{'='*70}\n")
                        print(final_response)
                        print(f"\n{'='*70}")
                        print(f"Tools Used: {', '.join(tools_used) if tools_used else 'None'}")
                        print(f"Total Events: {event_count}")
                        print(f"{'='*70}\n")
                        
                except json.JSONDecodeError as e:
                    print(f"⚠️  Failed to parse event: {json_str}")
                    print(f"   Error: {e}")
        
        if not final_response:
            print("⚠️  Warning: No complete event received")
        else:
            print("✅ Stream completed successfully\n")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)


def get_event_icon(event_type: str) -> str:
    """
    Get an icon for the event type.
    
    Args:
        event_type (str): Type of event.
    
    Returns:
        str: Icon for the event.
    """
    icons = {
        "thinking": "💭",
        "routing": "🔀",
        "specialist_start": "🔍",
        "specialist_complete": "✅",
        "synthesizing": "🔗",
        "complete": "🎯",
        "error": "❌"
    }
    
    return icons.get(event_type, "📌")


def main():
    """Main function."""
    print("\n" + "="*70)
    print("STREAMING CHAT ENDPOINT TEST")
    print("="*70)
    
    # Test queries
    test_queries = [
        "¿Cuántos episodios hay en total?",
        "Analiza la distribución de episodios por género",
        "Busca información sobre esquizofrenia y genera un resumen"
    ]
    
    # Allow user to choose or enter custom query
    print("\nElige una consulta de prueba o escribe la tuya propia:\n")
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. {query}")
    print(f"{len(test_queries) + 1}. Escribir consulta personalizada\n")
    
    try:
        choice = input("Selección (1-4): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(test_queries):
            message = test_queries[int(choice) - 1]
        elif choice == str(len(test_queries) + 1):
            message = input("\nEscribe tu consulta: ").strip()
            if not message:
                print("❌ Consulta vacía. Saliendo.")
                return
        else:
            print("❌ Selección inválida. Saliendo.")
            return
        
        # Run test
        test_streaming_chat(message)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()

