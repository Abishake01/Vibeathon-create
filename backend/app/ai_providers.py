import json
import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()

# Provider configurations
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

class AIProvider:
    """Base class for AI providers"""
    
    def chat_completion(self, messages: List[Dict], model: str, temperature: float = 0.7, max_tokens: int = 4000, response_format: Optional[Dict] = None) -> Dict[str, Any]:
        raise NotImplementedError
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 characters)"""
        return len(text) // 4


class GroqProvider(AIProvider):
    """Groq AI provider"""
    
    def __init__(self):
        from groq import Groq
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        self.client = Groq(api_key=GROQ_API_KEY)
        self.default_model = "llama-3.3-70b-versatile"
    
    def chat_completion(self, messages: List[Dict], model: str = None, temperature: float = 0.7, max_tokens: int = 4000, response_format: Optional[Dict] = None) -> Dict[str, Any]:
        model = model or self.default_model
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        if response_format:
            params["response_format"] = response_format
        
        response = self.client.chat.completions.create(**params)
        return {
            "content": response.choices[0].message.content.strip(),
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if hasattr(response.usage, 'prompt_tokens') else 0,
                "completion_tokens": response.usage.completion_tokens if hasattr(response.usage, 'completion_tokens') else 0,
                "total_tokens": response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else 0
            }
        }


class OpenAIProvider(AIProvider):
    """OpenAI provider"""
    
    def __init__(self):
        try:
            from openai import OpenAI
        except ImportError:
            raise ValueError("OpenAI package not installed. Install with: pip install openai")
        
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.default_model = "gpt-4o-mini"
    
    def chat_completion(self, messages: List[Dict], model: str = None, temperature: float = 0.7, max_tokens: int = 4000, response_format: Optional[Dict] = None) -> Dict[str, Any]:
        model = model or self.default_model
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        if response_format:
            params["response_format"] = response_format
        
        response = self.client.chat.completions.create(**params)
        return {
            "content": response.choices[0].message.content.strip(),
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }


class OllamaProvider(AIProvider):
    """Ollama provider (local)"""
    
    def __init__(self):
        import requests
        self.requests = requests
        self.base_url = OLLAMA_BASE_URL.rstrip('/')
        self.default_model = "llama3.2"
        # Test connection - make it optional, don't fail if server is slow
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                print(f"Warning: Ollama server returned status {response.status_code}, but continuing...")
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # Don't fail - just warn, user can still try to use it
            print(f"Warning: Ollama server not available at {self.base_url}. It will be tried when used.")
        except Exception as e:
            print(f"Warning: Ollama connection check failed: {str(e)}, but continuing...")
    
    def chat_completion(self, messages: List[Dict], model: str = None, temperature: float = 0.7, max_tokens: int = 4000, response_format: Optional[Dict] = None) -> Dict[str, Any]:
        model = model or self.default_model
        
        # Convert messages format for Ollama
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        payload = {
            "model": model,
            "messages": ollama_messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            },
            "stream": False
        }
        
        # If response_format is JSON, add format parameter
        if response_format and response_format.get("type") == "json_object":
            payload["format"] = "json"
        
        try:
            response = self.requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=300  # Increased timeout for longer generations
            )
            
            if response.status_code != 200:
                error_text = response.text[:500] if response.text else "Unknown error"
                raise Exception(f"Ollama API error (status {response.status_code}): {error_text}")
            
            data = response.json()
            content = data.get("message", {}).get("content", "")
            
            if not content:
                raise Exception("Ollama returned empty response")
            
            return {
                "content": content.strip(),
                "usage": {
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                }
            }
        except requests.exceptions.Timeout:
            raise Exception(f"Ollama request timed out after 300 seconds. The model might be too slow or the request too large.")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Cannot connect to Ollama server at {self.base_url}. Make sure Ollama is running.")
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")


class LangChainProvider(AIProvider):
    """LangChain provider - supports multiple models via LangChain"""
    
    def __init__(self, model_type: str = "ollama"):
        """
        Initialize LangChain provider.
        model_type: "ollama", "groq", "openai"
        """
        self.model_type = model_type.lower()
        self.default_model = None
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LangChain LLM based on model_type"""
        try:
            if self.model_type == "ollama":
                from langchain_ollama import ChatOllama
                self.llm = ChatOllama(
                    model="llama3.2",
                    base_url=OLLAMA_BASE_URL,
                    temperature=0.7,
                    timeout=300.0
                )
                self.default_model = "llama3.2"
            elif self.model_type == "groq":
                from langchain_groq import ChatGroq
                if not GROQ_API_KEY:
                    raise ValueError("GROQ_API_KEY environment variable is not set")
                self.llm = ChatGroq(
                    model="llama-3.3-70b-versatile",
                    groq_api_key=GROQ_API_KEY,
                    temperature=0.7
                )
                self.default_model = "llama-3.3-70b-versatile"
            elif self.model_type == "openai":
                from langchain_openai import ChatOpenAI
                if not OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY environment variable is not set")
                self.llm = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=OPENAI_API_KEY,
                    temperature=0.7
                )
                self.default_model = "gpt-4o-mini"
            else:
                raise ValueError(f"Unknown LangChain model_type: {self.model_type}. Supported: ollama, groq, openai")
        except ImportError as e:
            raise ValueError(f"LangChain package not installed. Install with: pip install langchain langchain-community langchain-ollama langchain-groq langchain-openai. Error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to initialize LangChain {self.model_type} provider: {str(e)}")
    
    def chat_completion(self, messages: List[Dict], model: str = None, temperature: float = 0.7, max_tokens: int = 4000, response_format: Optional[Dict] = None) -> Dict[str, Any]:
        """Chat completion using LangChain"""
        from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
        
        # Convert messages to LangChain format
        langchain_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:  # user
                langchain_messages.append(HumanMessage(content=content))
        
        try:
            # Invoke the LLM
            response = self.llm.invoke(langchain_messages)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Estimate usage (LangChain doesn't always provide token counts)
            total_chars = sum(len(msg.get("content", "")) for msg in messages) + len(content)
            estimated_tokens = total_chars // 4
            
            return {
                "content": content.strip(),
                "usage": {
                    "prompt_tokens": estimated_tokens // 2,
                    "completion_tokens": estimated_tokens // 2,
                    "total_tokens": estimated_tokens
                }
            }
        except Exception as e:
            if "Connection" in str(e) or "timeout" in str(e).lower():
                if self.model_type == "ollama":
                    raise Exception(f"Cannot connect to Ollama at {OLLAMA_BASE_URL}. Make sure Ollama is running. Start it with: ollama serve")
                else:
                    raise Exception(f"LangChain {self.model_type} connection error: {str(e)}")
            raise Exception(f"LangChain {self.model_type} error: {str(e)}")


def get_provider(provider_name: str = "langchain") -> AIProvider:
    """Get AI provider instance. Default is langchain (using Ollama)."""
    provider_name = provider_name.lower()
    
    if provider_name == "langchain" or provider_name == "langchain-ollama":
        # Default LangChain provider uses Ollama
        return LangChainProvider(model_type="ollama")
    elif provider_name == "langchain-groq":
        return LangChainProvider(model_type="groq")
    elif provider_name == "langchain-openai":
        return LangChainProvider(model_type="openai")
    elif provider_name == "groq":
        return GroqProvider()
    elif provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "ollama":
        return OllamaProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}. Supported: langchain (default, uses Ollama), langchain-groq, langchain-openai, groq, openai, ollama")

