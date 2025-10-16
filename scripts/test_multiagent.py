"""
Quick test script for Multi-Agent Architecture.

This script performs basic health checks and simple queries to verify
that the multi-agent system is working correctly.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.back.services.ai_service import AIService
from app.back.config import config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def print_section(title: str):
    """Prints a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_health_check():
    """Tests AI service health check."""
    print_section("1. Health Check")
    
    try:
        service = AIService()
        health = service.health_check()
        
        print(f"Status: {health.get('status', 'unknown')}")
        print(f"Model: {health.get('model', 'unknown')}")
        print(f"Architecture: {health.get('architecture', 'unknown')}")
        print(f"XAI API Key: {health.get('xai_api_key', 'unknown')}")
        print(f"Tavily API Key: {health.get('tavily_api_key', 'unknown')}")
        
        if health.get('status') == 'healthy':
            print("\n✅ Health check passed!")
            
            agents = health.get('agents', {})
            print("\nAgents status:")
            for agent_name, status in agents.items():
                print(f"  - {agent_name}: {status}")
            
            return True
        else:
            print(f"\n❌ Health check failed: {health.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        logger.error("Health check failed", exc_info=True)
        return False


def test_simple_query():
    """Tests a simple database query."""
    print_section("2. Simple Database Query")
    
    try:
        service = AIService()
        
        query = "¿Cuántos episodios hay en total en la base de datos?"
        print(f"Query: {query}\n")
        
        print("Executing multi-agent workflow...")
        print("-" * 80)
        
        result = service.chat(query)
        
        print("\nResponse:")
        print("-" * 80)
        print(result.get('response', 'No response'))
        print("-" * 80)
        
        print(f"\nTools used: {result.get('tools_used', [])}")
        print(f"Specialists invoked: {len(result.get('specialist_summaries', []))}")
        print(f"Has errors: {result.get('has_errors', False)}")
        
        # Show specialist summaries for debugging
        summaries = result.get('specialist_summaries', [])
        if summaries:
            print("\nSpecialist Summaries (for debugging):")
            for summary in summaries:
                specialist = summary.get('specialist', 'unknown')
                content = summary.get('summary', 'No summary')
                print(f"\n  [{specialist}]")
                print(f"  {content[:150]}...")
        
        if not result.get('has_errors'):
            print("\n✅ Simple query test passed!")
            return True
        else:
            print("\n⚠️ Query completed with errors")
            return False
            
    except Exception as e:
        print(f"❌ Query test error: {e}")
        logger.error("Query test failed", exc_info=True)
        return False


def test_diagram_generation():
    """Tests diagram generation."""
    print_section("3. Diagram Generation")
    
    try:
        service = AIService()
        
        query = "Genera un diagrama del proceso de admisión hospitalaria"
        print(f"Query: {query}\n")
        
        print("Executing multi-agent workflow...")
        print("-" * 80)
        
        result = service.chat(query)
        
        print("\nResponse:")
        print("-" * 80)
        print(result.get('response', 'No response')[:500])
        print("\n[...response truncated for brevity...]")
        print("-" * 80)
        
        print(f"\nTools used: {result.get('tools_used', [])}")
        print(f"Has errors: {result.get('has_errors', False)}")
        
        # Check if mermaid code is in response
        response = result.get('response', '')
        has_mermaid = '```mermaid' in response
        
        print(f"\nContains Mermaid diagram: {has_mermaid}")
        
        if not result.get('has_errors') and has_mermaid:
            print("\n✅ Diagram generation test passed!")
            return True
        else:
            print("\n⚠️ Diagram test completed but may have issues")
            return False
            
    except Exception as e:
        print(f"❌ Diagram test error: {e}")
        logger.error("Diagram test failed", exc_info=True)
        return False


def main():
    """Main test runner."""
    print("\n" + "=" * 80)
    print("  MULTI-AGENT ARCHITECTURE TEST SUITE")
    print("=" * 80)
    
    # Check configuration
    if not config.XAI_API_KEY:
        print("\n❌ ERROR: XAI_API_KEY not configured!")
        print("Please set XAI_API_KEY in your .env file")
        return 1
    
    print(f"\n✓ XAI API Key: Configured")
    print(f"✓ Tavily API Key: {'Configured' if config.TAVILY_API_KEY else 'Not configured (optional)'}")
    
    # Run tests
    results = []
    
    results.append(("Health Check", test_health_check()))
    results.append(("Simple Query", test_simple_query()))
    results.append(("Diagram Generation", test_diagram_generation()))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Multi-agent architecture is working correctly.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check logs above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

