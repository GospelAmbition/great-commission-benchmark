#!/usr/bin/env python3
"""
Simple command-line interface for LM Studio LLM
Connects to http://192.168.68.61:1234
Model: qwen/qwen3-coder-30b
"""

import requests
import json
import sys

BASE_URL = "http://192.168.68.61:1234"
LLM_URL = f"{BASE_URL}/v1/chat/completions"
MODEL = None  # Will be auto-detected


def get_available_model() -> str:
    """Get the first available model from the server"""
    try:
        response = requests.get(f"{BASE_URL}/v1/models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("data", [])
            if models:
                # Try to find qwen model first, otherwise use first available
                for model in models:
                    model_id = model.get("id", "")
                    if "qwen" in model_id.lower():
                        return model_id
                return models[0].get("id", "unknown")
        return None
    except Exception as e:
        print(f"Warning: Could not fetch models: {e}")
        return None


def ask_llm(question: str, model_name: str, conversation_history: list = None) -> str:
    """Send a question to the LLM and return the response"""
    if conversation_history is None:
        conversation_history = []
    
    # Add the new question to history
    messages = conversation_history + [{"role": "user", "content": question}]
    
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.7,
        "stream": False
    }
    
    try:
        response = requests.post(LLM_URL, json=payload, timeout=60)
        
        # Handle 400 errors with detailed message
        if response.status_code == 400:
            try:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", response.text)
                return f"Error 400: {error_msg}\n\nTried model: {model_name}\nPayload: {json.dumps(payload, indent=2)}"
            except:
                return f"Error 400: Bad Request\nResponse: {response.text[:500]}\n\nTried model: {model_name}"
        
        response.raise_for_status()
        data = response.json()
        
        # Extract the assistant's reply
        if "choices" in data and len(data["choices"]) > 0:
            reply = data["choices"][0]["message"]["content"]
            return reply
        else:
            return f"Error: Unexpected response format\n{json.dumps(data, indent=2)}"
    
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to LLM. Is LM Studio running at http://192.168.68.61:1234?"
    except requests.exceptions.Timeout:
        return "Error: Request timed out. The LLM may be processing a long response."
    except requests.exceptions.HTTPError as e:
        return f"HTTP Error {e.response.status_code}: {e.response.text[:500]}"
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
    except json.JSONDecodeError:
        return f"Error: Invalid JSON response\n{response.text[:500]}"
    except Exception as e:
        return f"Error: {str(e)}"


def test_connection():
    """Test if the LLM server is available and return model name"""
    try:
        # Try to get models list
        response = requests.get(f"{BASE_URL}/v1/models", timeout=5)
        if response.status_code == 200:
            print("✓ Connected to LM Studio")
            models = response.json().get("data", [])
            if models:
                model_names = [m.get("id", "unknown") for m in models]
                print(f"✓ Available models: {', '.join(model_names)}")
                # Return the first model (or qwen if available)
                model_name = get_available_model()
                if model_name:
                    print(f"✓ Using model: {model_name}")
                    return True, model_name
            return False, None
        else:
            print(f"✗ Server responded with status {response.status_code}")
            return False, None
    except Exception as e:
        print(f"✗ Could not connect: {e}")
        return False, None


def main():
    global MODEL
    
    print("=" * 60)
    print("LM Studio Chat Interface")
    print(f"Server: {BASE_URL}")
    print("=" * 60)
    print()
    
    # Test connection and get model name
    connected, model_name = test_connection()
    if not connected or not model_name:
        print("\nPlease make sure:")
        print("1. LM Studio is running")
        print("2. The server is accessible at http://192.168.68.61:1234")
        print("3. A model is loaded in LM Studio")
        sys.exit(1)
    
    MODEL = model_name
    print(f"\nModel: {MODEL}")
    
    print("\nType your questions below. Type 'quit', 'exit', or 'q' to exit.")
    print("Type 'clear' to clear conversation history.")
    print("-" * 60)
    print()
    
    conversation_history = []
    
    while True:
        try:
            # Get user input
            question = input("You: ").strip()
            
            # Handle exit commands
            if question.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            # Handle clear command
            if question.lower() == 'clear':
                conversation_history = []
                print("Conversation history cleared.\n")
                continue
            
            # Skip empty input
            if not question:
                continue
            
            # Show thinking indicator
            print("LLM: ", end="", flush=True)
            
            # Get response
            reply = ask_llm(question, MODEL, conversation_history)
            
            # Print response
            print(reply)
            
            # Update conversation history
            conversation_history.append({"role": "user", "content": question})
            conversation_history.append({"role": "assistant", "content": reply})
            
            # Keep history manageable (last 20 messages)
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
            
            print()  # Blank line for readability
        
        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'quit' to exit or continue asking questions.")
        except EOFError:
            print("\n\nGoodbye!")
            break


if __name__ == "__main__":
    main()
