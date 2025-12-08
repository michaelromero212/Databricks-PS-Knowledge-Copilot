"""
LLM Connector Module

Supports multiple LLM providers:
- OpenAI (GPT-4)
- Anthropic (Claude)
- Hugging Face Local (LaMini-Flan-T5)
- Databricks Foundation Models (DBRX, Mixtral, Llama)
"""

import os
from typing import List, Dict, Any, Optional
import openai
import anthropic


class LLMConfig:
    """Centralized LLM configuration."""
    OPENAI_MODEL = "gpt-4o-mini"  # Cost-effective default
    ANTHROPIC_MODEL = "claude-3-haiku-20240307"
    DATABRICKS_MODEL = "databricks-dbrx-instruct"  # Free tier available
    
    # Fallback models for Databricks
    DATABRICKS_FALLBACK_MODELS = [
        "databricks-mixtral-8x7b-instruct",
        "databricks-llama-2-70b-chat",
    ]


class LLMConnector:
    """
    Multi-provider LLM connector for RAG answer generation.
    
    Supports OpenAI, Anthropic, Hugging Face local models, and 
    Databricks Foundation Models (free tier compatible).
    """
    
    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.databricks_host = os.getenv("DATABRICKS_HOST")
        self.databricks_token = os.getenv("DATABRICKS_TOKEN")
        
        # Lazy-load Hugging Face model
        self._hf_pipeline = None
        
        if self.provider == "huggingface_local":
            self._init_huggingface()
    
    def _init_huggingface(self):
        """Initialize local Hugging Face model."""
        if self._hf_pipeline is None:
            print("Initializing local Hugging Face model (LaMini-Flan-T5-248M)...")
            from transformers import pipeline
            self._hf_pipeline = pipeline(
                "text2text-generation", 
                model="MBZUAI/LaMini-Flan-T5-248M", 
                max_length=512
            )

    def generate_answer(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Generates an answer using the selected LLM provider.
        
        Args:
            query: The user's question
            context_docs: Retrieved documents with 'content' and 'metadata' keys
            
        Returns:
            Generated answer string
        """
        context_text = "\n\n".join([
            f"Source: {doc['metadata'].get('source', 'Unknown')}\nContent: {doc['content']}" 
            for doc in context_docs
        ])
        
        system_prompt = """You are a Databricks Professional Services expert.
Return the best possible answer using only the context provided.
If context is insufficient, say so.
Always cite at least one source in the answer.

Format:

ANSWER:
<detailed helpful answer>

SOURCES:
- <document reference>"""

        user_prompt = f"Context:\n{context_text}\n\nQuestion: {query}"

        if self.provider == "openai":
            return self._call_openai(system_prompt, user_prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic(system_prompt, user_prompt)
        elif self.provider == "huggingface_local":
            return self._call_huggingface_local(system_prompt, user_prompt)
        elif self.provider == "databricks":
            return self._call_databricks(system_prompt, user_prompt)
        else:
            return f"Error: Invalid LLM provider '{self.provider}'."

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API."""
        if not self.openai_api_key:
            return "Error: OpenAI API key not found. Set OPENAI_API_KEY environment variable."
        
        try:
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model=LLMConfig.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling OpenAI: {str(e)}"

    def _call_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        """Call Anthropic API."""
        if not self.anthropic_api_key:
            return "Error: Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable."
        
        try:
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            response = client.messages.create(
                model=LLMConfig.ANTHROPIC_MODEL,
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return f"Error calling Anthropic: {str(e)}"

    def _call_huggingface_local(self, system_prompt: str, user_prompt: str) -> str:
        """Call local Hugging Face model."""
        if self._hf_pipeline is None:
            self._init_huggingface()
        
        try:
            # Combine prompts for T5 models
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            response = self._hf_pipeline(full_prompt)
            return response[0]['generated_text']
        except Exception as e:
            return f"Error with local model: {str(e)}"

    def _call_databricks(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call Databricks Foundation Model Serving API.
        
        Compatible with Databricks Free Edition when using
        foundation model endpoints.
        """
        if not self.databricks_host or not self.databricks_token:
            return "Error: Databricks credentials not found. Set DATABRICKS_HOST and DATABRICKS_TOKEN environment variables."
        
        try:
            import requests
            
            # Clean host URL
            host = self.databricks_host.rstrip('/')
            if not host.startswith('https://'):
                host = f"https://{host}"
            
            # Try foundation model endpoint
            endpoint_url = f"{host}/serving-endpoints/{LLMConfig.DATABRICKS_MODEL}/invocations"
            
            headers = {
                "Authorization": f"Bearer {self.databricks_token}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.7,
            }
            
            response = requests.post(
                endpoint_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                # Handle different response formats
                if "choices" in result:
                    return result["choices"][0]["message"]["content"]
                elif "predictions" in result:
                    return result["predictions"][0]
                else:
                    return str(result)
            else:
                return f"Error from Databricks API ({response.status_code}): {response.text}"
                
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Databricks: {str(e)}"
        except Exception as e:
            return f"Error calling Databricks: {str(e)}"

    @staticmethod
    def get_available_providers() -> List[str]:
        """Return list of available LLM providers."""
        return ["openai", "anthropic", "huggingface_local", "databricks"]

