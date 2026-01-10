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
    HUGGINGFACE_API_MODEL = "google/flan-t5-base"  # Publicly available, fast
    
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
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
        
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
        elif self.provider == "huggingface_api":
            return self._call_huggingface_api(system_prompt, user_prompt)
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

    def _call_huggingface_api(self, system_prompt: str, user_prompt: str) -> str:
        """Call Hugging Face Inference API."""
        if not self.huggingface_api_key:
            return "Error: Hugging Face API key not found. Set HUGGINGFACE_API_KEY environment variable."
        
        try:
            import requests
            import json
            
            api_url = f"https://router.huggingface.co/models/{LLMConfig.HUGGINGFACE_API_MODEL}"
            headers = {
                "Authorization": f"Bearer {self.huggingface_api_key}",
                "Content-Type": "application/json"
            }
            
            # Format as messages for chat models
            payload = {
                "inputs": f"{system_prompt}\n\n{user_prompt}",
                "parameters": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "return_full_text": False
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", str(result))
                elif isinstance(result, dict):
                    return result.get("generated_text", str(result))
                return str(result)
            else:
                return f"Error from Hugging Face API ({response.status_code}): {response.text}"
                
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Hugging Face: {str(e)}"
        except Exception as e:
            return f"Error calling Hugging Face API: {str(e)}"

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

    def generate_follow_up_questions(self, query: str, answer: str) -> List[str]:
        """Generate follow-up questions based on the query and answer."""
        prompt = f"""Given this question and answer, generate 3 relevant follow-up questions.

Question: {query}
Answer: {answer}

Generate exactly 3 follow-up questions, one per line. Each question should:
1. Be relevant to the topic
2. Explore related aspects not covered in the answer
3. Be concise and clear

Follow-up questions:"""
        
        try:
            response = self._call_simple(prompt)
            # Parse response into list of questions
            questions = [q.strip() for q in response.split('\n') if q.strip() and '?' in q]
            return questions[:3]  # Return max 3 questions
        except Exception as e:
            print(f"Error generating follow-up questions: {str(e)}")
            return []
    
    def analyze_document(self, text: str) -> dict:
        """Analyze a document and extract summary, tags, and complexity."""
        # Truncate text if too long
        max_length = 2000
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        prompt = f"""Analyze this text and provide:
1. A concise summary (2-3 sentences)
2. 3-5 relevant topic tags
3. Complexity level (beginner/intermediate/advanced)

Text:
{text}

Provide your response in this exact format:

SUMMARY:
<your summary here>

TAGS:
<tag1>, <tag2>, <tag3>

COMPLEXITY:
<beginner/intermediate/advanced>"""
        
        try:
            response = self._call_simple(prompt)
            
            # Parse response
            summary = ""
            tags = []
            complexity = "intermediate"
            
            if "SUMMARY:" in response:
                summary_section = response.split("SUMMARY:")[1].split("TAGS:")[0].strip()
                summary = summary_section
            
            if "TAGS:" in response:
                tags_section = response.split("TAGS:")[1].split("COMPLEXITY:")[0].strip()
                tags = [tag.strip() for tag in tags_section.split(',')]
            
            if "COMPLEXITY:" in response:
                complexity_section = response.split("COMPLEXITY:")[1].strip().lower()
                if any(level in complexity_section for level in ["beginner", "intermediate", "advanced"]):
                    for level in ["beginner", "intermediate", "advanced"]:
                        if level in complexity_section:
                            complexity = level
                            break
            
            return {
                "summary": summary or "Analysis unavailable",
                "tags": tags or ["general"],
                "complexity": complexity
            }
        except Exception as e:
            print(f"Error analyzing document: {str(e)}")
            return {
                "summary": "Error analyzing document",
                "tags": [],
                "complexity": "intermediate"
            }
    
    def _call_simple(self, prompt: str) -> str:
        """Simple prompt call without system/user separation."""
        if self.provider == "openai":
            return self._call_openai("", prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic("", prompt)
        elif self.provider == "huggingface_api":
            return self._call_huggingface_api("", prompt)
        elif self.provider == "huggingface_local":
            return self._call_huggingface_local("", prompt)
        elif self.provider == "databricks":
            return self._call_databricks("", prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def check_connection(self) -> dict:
        """Check if the LLM provider is accessible."""
        try:
            # Simple test prompt
            test_response = self._call_simple("Say 'OK' if you can read this.")
            
            # Determine model name based on provider
            model_name = None
            if self.provider == "openai":
                model_name = LLMConfig.OPENAI_MODEL
            elif self.provider == "anthropic":
                model_name = LLMConfig.ANTHROPIC_MODEL
            elif self.provider == "huggingface_api":
                model_name = LLMConfig.HUGGINGFACE_API_MODEL
            elif self.provider == "huggingface_local":
                model_name = "LaMini-Flan-T5-248M"
            elif self.provider == "databricks":
                model_name = LLMConfig.DATABRICKS_MODEL
            
            if "Error" in test_response:
                return {
                    "status": "disconnected",
                    "model": model_name,
                    "details": test_response
                }
            else:
                return {
                    "status": "connected",
                    "model": model_name,
                    "details": "Connection successful"
                }
        except Exception as e:
            return {
                "status": "disconnected",
                "model": None,
                "details": str(e)
            }
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Return list of available LLM providers."""
        return ["openai", "anthropic", "huggingface_local", "huggingface_api", "databricks"]

