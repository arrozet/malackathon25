#!/usr/bin/env python3
"""
Test AI Service REST Endpoints.

This script tests the AI service endpoints via HTTP requests,
simulating real client interactions.
"""

import requests
import json
from typing import Dict, Any


# Configuration
BASE_URL = "http://localhost:8000"
AI_BASE = f"{BASE_URL}/ai"


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_response(response: requests.Response):
    """Print HTTP response in a readable format."""
    print(f"\nStatus: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    try:
        data = response.json()
        print(f"\nResponse JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print(f"\nResponse Text:\n{response.text}")


def test_health():
    """Test AI service health endpoint."""
    print_section("TEST: AI Health Check")
    
    url = f"{AI_BASE}/health"
    print(f"\nGET {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get("status", "unknown")
            print(f"\n✓ Service Status: {status}")
            
            print("\nComponent Health:")
            for component, healthy in data.get("components", {}).items():
                icon = "✓" if healthy else "✗"
                print(f"  {icon} {component}")
        else:
            print(f"\n✗ Health check failed with status {response.status_code}")
    
    except requests.RequestException as e:
        print(f"\n✗ Request failed: {e}")
        print("\nMake sure the server is running: cd app/back && python main.py")


def test_chat():
    """Test AI chat endpoint."""
    print_section("TEST: AI Chat")
    
    url = f"{AI_BASE}/chat"
    print(f"\nPOST {url}")
    
    # Test cases
    test_messages = [
        "¿Cuántos episodios hay en total?",
        "¿Cuál es la estancia promedio?",
        "Muéstrame los diagnósticos más frecuentes",
    ]
    
    for message in test_messages:
        print(f"\n--- Message: {message} ---")
        
        payload = {
            "message": message,
            "chat_history": []
        }
        
        print(f"Payload: {json.dumps(payload, ensure_ascii=False)}")
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            print_response(response)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✓ Chat successful")
                print(f"\nAI Response:")
                print(data.get("response", "No response"))
                print(f"\nTools used: {', '.join(data.get('tool_calls', []))}")
            else:
                print(f"\n✗ Chat failed with status {response.status_code}")
        
        except requests.RequestException as e:
            print(f"\n✗ Request failed: {e}")
        
        print("\n" + "-" * 80)


def test_analyze():
    """Test AI analysis endpoint."""
    print_section("TEST: AI Analysis")
    
    url = f"{AI_BASE}/analyze"
    print(f"\nPOST {url}")
    
    # Test cases
    test_queries = [
        "Analiza la distribución de episodios por severidad",
        "¿Cuál es la relación entre severidad y coste?",
    ]
    
    for query in test_queries:
        print(f"\n--- Query: {query} ---")
        
        payload = {
            "query": query
        }
        
        print(f"Payload: {json.dumps(payload, ensure_ascii=False)}")
        
        try:
            response = requests.post(url, json=payload, timeout=90)
            print_response(response)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✓ Analysis successful")
                print(f"\nAnalysis Response:")
                print(data.get("response", "No response"))
                print(f"\nTools used: {', '.join(data.get('tool_calls', []))}")
            else:
                print(f"\n✗ Analysis failed with status {response.status_code}")
        
        except requests.RequestException as e:
            print(f"\n✗ Request failed: {e}")
        
        print("\n" + "-" * 80)


def test_visualize():
    """Test AI visualization endpoint."""
    print_section("TEST: AI Visualization")
    
    url = f"{AI_BASE}/visualize"
    print(f"\nPOST {url}")
    
    # Test cases
    test_descriptions = [
        "diagrama de esquema de base de datos",
        "flujo de admisión hospitalaria",
        "proceso de análisis de datos",
    ]
    
    for description in test_descriptions:
        print(f"\n--- Description: {description} ---")
        
        payload = {
            "description": description
        }
        
        print(f"Payload: {json.dumps(payload, ensure_ascii=False)}")
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            print_response(response)
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✓ Visualization generated")
                print(f"\nMermaid Code:")
                print(data.get("mermaid_code", "No code"))
            else:
                print(f"\n✗ Visualization failed with status {response.status_code}")
        
        except requests.RequestException as e:
            print(f"\n✗ Request failed: {e}")
        
        print("\n" + "-" * 80)


def test_conversational_chat():
    """Test conversational chat with history."""
    print_section("TEST: Conversational Chat with History")
    
    url = f"{AI_BASE}/chat"
    print(f"\nPOST {url}")
    
    chat_history = []
    
    # Conversation flow
    messages = [
        "¿Cuántos episodios hay en total?",
        "¿Y cuál es la distribución por sexo?",
        "¿Puedes calcular el porcentaje?",
    ]
    
    for idx, message in enumerate(messages, 1):
        print(f"\n--- Turn {idx}: {message} ---")
        
        payload = {
            "message": message,
            "chat_history": chat_history
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                assistant_response = data.get("response", "")
                
                print(f"\nUser: {message}")
                print(f"\nAssistant: {assistant_response}")
                print(f"\nTools: {', '.join(data.get('tool_calls', []))}")
                
                # Update history
                chat_history.append({"role": "user", "content": message})
                chat_history.append({"role": "assistant", "content": assistant_response})
                
                print(f"\n✓ Turn {idx} successful")
            else:
                print(f"\n✗ Turn {idx} failed with status {response.status_code}")
                break
        
        except requests.RequestException as e:
            print(f"\n✗ Request failed: {e}")
            break
        
        print("\n" + "-" * 80)


def main():
    """Run all tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test AI Service Endpoints")
    parser.add_argument(
        "--test",
        choices=["health", "chat", "analyze", "visualize", "conversation", "all"],
        default="all",
        help="Which test to run"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API"
    )
    
    args = parser.parse_args()
    
    global BASE_URL, AI_BASE
    BASE_URL = args.url
    AI_BASE = f"{BASE_URL}/ai"
    
    print("\n" + "=" * 80)
    print("  BRAIN AI SERVICE - ENDPOINT TESTS")
    print("=" * 80)
    print(f"\nBase URL: {BASE_URL}")
    print(f"AI Endpoints: {AI_BASE}")
    
    try:
        # Always test health first
        test_health()
        
        if args.test in ["chat", "all"]:
            test_chat()
        
        if args.test in ["analyze", "all"]:
            test_analyze()
        
        if args.test in ["visualize", "all"]:
            test_visualize()
        
        if args.test == "conversation":
            test_conversational_chat()
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    
    print("\n" + "=" * 80)
    print("  TESTS COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

