"""
Promptfoo local provider for LM Studio.

This provider connects to LM Studio's OpenAI-compatible API endpoint.
LM Studio typically runs on http://localhost:1234/v1

Requirements:
    pip install requests

Usage in promptfoo.yaml:
  providers:
    - id: 'file:///absolute/path/to/lmstudio.py'
      config:
        base_url: http://localhost:1234/v1
        api_key: lm-studio
        model: local-model
        max_tokens: 1000
        temperature: 0.7
"""

import json
import os
from typing import Dict, Any, Optional
import requests


def call_api(
    prompt: str,
    options: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Call LM Studio API via OpenAI-compatible endpoint.
    
    Args:
        prompt: The input prompt string
        options: Configuration options from promptfoo config
        context: Additional context (may include vars, etc.)
    
    Returns:
        Dictionary with 'output' key containing the response text
    """
    # Get configuration from options or use defaults
    base_url = options.get('base_url', os.getenv('LM_STUDIO_BASE_URL', 'http://localhost:1234/v1'))
    api_key = options.get('api_key', os.getenv('LM_STUDIO_API_KEY', 'lm-studio'))
    model = options.get('model', options.get('model_id', 'local-model'))
    max_tokens = options.get('max_tokens', 1000)
    temperature = options.get('temperature', 0.7)
    timeout = options.get('timeout', 60)
    
    # Ensure base_url doesn't have trailing slash
    base_url = base_url.rstrip('/')
    
    # Construct the chat completions endpoint
    url = f"{base_url}/chat/completions"
    
    # Prepare the request payload
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    # Add optional parameters if provided
    if 'top_p' in options:
        payload['top_p'] = options['top_p']
    if 'frequency_penalty' in options:
        payload['frequency_penalty'] = options['frequency_penalty']
    if 'presence_penalty' in options:
        payload['presence_penalty'] = options['presence_penalty']
    if 'stop' in options:
        payload['stop'] = options['stop']
    
    # Prepare headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        # Make the API request
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=timeout
        )
        
        # Raise an exception for bad status codes
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        # Extract the response text from the OpenAI-compatible format
        if 'choices' in data and len(data['choices']) > 0:
            output = data['choices'][0]['message']['content']
            
            # Return the response in the format Promptfoo expects
            result = {
                "output": output
            }
            
            # Include additional metadata if available
            if 'usage' in data:
                result['tokenUsage'] = {
                    "prompt": data['usage'].get('prompt_tokens', 0),
                    "completion": data['usage'].get('completion_tokens', 0),
                    "total": data['usage'].get('total_tokens', 0)
                }
            
            return result
        else:
            raise ValueError("No choices in API response")
            
    except requests.exceptions.RequestException as e:
        # Handle network errors
        error_msg = f"LM Studio API error: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg += f" - {json.dumps(error_detail)}"
            except:
                error_msg += f" - Status: {e.response.status_code}"
        
        return {
            "error": error_msg,
            "output": ""
        }
    
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        # Handle parsing errors
        return {
            "error": f"Response parsing error: {str(e)}",
            "output": ""
        }
    
    except Exception as e:
        # Handle any other unexpected errors
        return {
            "error": f"Unexpected error: {str(e)}",
            "output": ""
        }

