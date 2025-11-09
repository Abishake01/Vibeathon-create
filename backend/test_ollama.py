#!/usr/bin/env python3
"""Quick test script to verify Ollama is running and accessible via LangChain"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_ollama_connection():
    """Test if Ollama server is accessible"""
    import requests
    
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama is running at {OLLAMA_BASE_URL}")
            if models:
                print(f"📦 Available models: {', '.join([m.get('name', 'unknown') for m in models])}")
            else:
                print("⚠️  No models found. Pull a model with: ollama pull llama3.2")
            return True
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Ollama at {OLLAMA_BASE_URL}")
        print("   Please start Ollama with: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_langchain_ollama():
    """Test LangChain Ollama integration"""
    try:
        from langchain_ollama import ChatOllama
        
        OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        print("\n🧪 Testing LangChain Ollama integration...")
        llm = ChatOllama(
            model="llama3",  # Use llama3 (available model)
            base_url=OLLAMA_BASE_URL,
            temperature=0.7,
            timeout=30.0
        )
        
        # Simple test
        response = llm.invoke("Say 'Hello from Ollama!' in one sentence.")
        print(f"✅ LangChain Ollama test successful!")
        print(f"   Response: {response.content[:100]}...")
        return True
    except ImportError:
        print("❌ langchain-ollama not installed. Run: pip install langchain-ollama")
        return False
    except Exception as e:
        print(f"❌ LangChain Ollama test failed: {str(e)}")
        if "Connection" in str(e) or "timeout" in str(e).lower():
            print("   Make sure Ollama is running: ollama serve")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Ollama Integration Test")
    print("=" * 60)
    
    # Test 1: Connection
    print("\n1. Testing Ollama server connection...")
    connection_ok = test_ollama_connection()
    
    if connection_ok:
        # Test 2: LangChain integration
        print("\n2. Testing LangChain Ollama integration...")
        langchain_ok = test_langchain_ollama()
        
        if langchain_ok:
            print("\n" + "=" * 60)
            print("✅ All tests passed! Ollama is ready to use.")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("⚠️  Ollama server is running but LangChain test failed.")
            print("=" * 60)
            sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("❌ Ollama is not running. Please start it first:")
        print("   1. Install Ollama: https://ollama.ai")
        print("   2. Start server: ollama serve")
        print("   3. Pull model: ollama pull llama3.2")
        print("=" * 60)
        sys.exit(1)

