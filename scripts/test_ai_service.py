#!/usr/bin/env python3
"""
Test script for AI Service.

This script tests the AI service directly without the FastAPI server,
allowing for quick iteration and debugging during development.
"""

import sys
import os
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent.parent / "app" / "back"
sys.path.insert(0, str(app_dir.parent.parent))

import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = app_dir / ".env"
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"Loaded environment from {env_path}")
else:
    logger.warning(f".env file not found at {env_path}")
    logger.info("Make sure to set GROQ_API_KEY and other required environment variables")


def test_tools():
    """Test individual tools."""
    print("\n" + "=" * 80)
    print("TESTING INDIVIDUAL TOOLS")
    print("=" * 80)
    
    from app.back.services.tools import (
        OracleRAGTool,
        InternetSearchTool,
        PythonExecutorTool,
        MermaidTool,
    )
    
    # Test Oracle RAG Tool
    print("\n--- Testing Oracle RAG Tool ---")
    try:
        oracle_tool = OracleRAGTool()
        result = oracle_tool._run("cuántos episodios hay en total")
        print(f"Result:\n{result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test Python Executor Tool
    print("\n--- Testing Python Executor Tool ---")
    try:
        python_tool = PythonExecutorTool()
        code = """
import statistics
data = [10, 20, 30, 40, 50]
mean = statistics.mean(data)
median = statistics.median(data)
print(f"Mean: {mean}, Median: {median}")
"""
        result = python_tool._run(code)
        print(f"Result:\n{result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test Mermaid Tool
    print("\n--- Testing Mermaid Tool ---")
    try:
        mermaid_tool = MermaidTool()
        result = mermaid_tool._run("diagrama de base de datos")
        print(f"Result:\n{result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test Internet Search Tool (optional - requires API key)
    print("\n--- Testing Internet Search Tool ---")
    try:
        internet_tool = InternetSearchTool()
        result = internet_tool._run("latest research on depression treatment")
        print(f"Result:\n{result[:500]}...")  # Truncate for readability
    except Exception as e:
        print(f"Error (expected if TAVILY_API_KEY not set): {e}")


def test_ai_service():
    """Test AI Service with chat."""
    print("\n" + "=" * 80)
    print("TESTING AI SERVICE")
    print("=" * 80)
    
    try:
        from app.back.services.ai_service import get_ai_service
        
        ai_service = get_ai_service()
        logger.info("AI Service initialized successfully")
        
        # Test 1: Simple database query
        print("\n--- Test 1: Database Query ---")
        print("Query: ¿Cuántos episodios hay en total?")
        result = ai_service.chat("¿Cuántos episodios hay en total?")
        print(f"\nResponse:\n{result['response']}")
        print(f"\nTools used: {result['tool_calls']}")
        
        # Test 2: Statistical analysis
        print("\n--- Test 2: Statistical Analysis ---")
        print("Query: ¿Cuál es la estancia promedio de los episodios?")
        result = ai_service.chat("¿Cuál es la estancia promedio de los episodios?")
        print(f"\nResponse:\n{result['response']}")
        print(f"\nTools used: {result['tool_calls']}")
        
        # Test 3: Data analysis with Python
        print("\n--- Test 3: Analysis Method ---")
        print("Query: Analiza la distribución de episodios por severidad")
        result = ai_service.analyze_data("Analiza la distribución de episodios por severidad")
        print(f"\nResponse:\n{result['response']}")
        print(f"\nTools used: {result['tool_calls']}")
        
        # Test 4: Visualization generation
        print("\n--- Test 4: Visualization ---")
        print("Query: Genera un diagrama de flujo de admisión hospitalaria")
        mermaid_code = ai_service.generate_visualization("flujo de admisión hospitalaria")
        print(f"\nMermaid Code:\n{mermaid_code}")
        
        # Test 5: Health check
        print("\n--- Test 5: Health Check ---")
        health = ai_service.health_check()
        print(f"\nHealth Status:")
        for component, status in health.items():
            status_icon = "✓" if status else "✗"
            print(f"  {status_icon} {component}: {'healthy' if status else 'unhealthy'}")
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\nERROR: {e}")
        print("\nMake sure to set XAI_API_KEY in your .env file")
        print("Get your API key from: https://console.x.ai/")
        print("\nNOTE: We use Grok-4 Fast Reasoning from xAI (Elon Musk's company)")
    except Exception as e:
        logger.error(f"Error testing AI service: {e}", exc_info=True)
        print(f"\nERROR: {e}")


def interactive_mode():
    """Interactive chat mode."""
    print("\n" + "=" * 80)
    print("INTERACTIVE CHAT MODE")
    print("=" * 80)
    print("Type 'exit' or 'quit' to stop")
    print("=" * 80 + "\n")
    
    try:
        from app.back.services.ai_service import get_ai_service
        
        ai_service = get_ai_service()
        chat_history = []
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'salir']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Get AI response
                result = ai_service.chat(user_input, chat_history=chat_history)
                
                # Update chat history
                chat_history.append({"role": "user", "content": user_input})
                chat_history.append({"role": "assistant", "content": result['response']})
                
                # Print response
                print(f"\nBrain: {result['response']}")
                
                if result['tool_calls']:
                    print(f"\n[Tools used: {', '.join(result['tool_calls'])}]")
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"\nError: {e}")
    
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\nERROR: {e}")
        print("\nMake sure to set XAI_API_KEY in your .env file")
        print("Get your API key from: https://console.x.ai/")


def main():
    """Main test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test AI Service")
    parser.add_argument(
        "--mode",
        choices=["tools", "service", "interactive", "all"],
        default="all",
        help="Test mode to run"
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 80)
    print("BRAIN AI SERVICE - TEST SUITE")
    print("=" * 80)
    
    if args.mode in ["tools", "all"]:
        test_tools()
    
    if args.mode in ["service", "all"]:
        test_ai_service()
    
    if args.mode == "interactive":
        interactive_mode()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()

