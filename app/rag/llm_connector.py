import os
from typing import List, Dict, Any
import openai
import anthropic
from transformers import pipeline

class LLMConnector:
    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if self.provider == "huggingface_local":
            print("Initializing local Hugging Face model (LaMini-Flan-T5-248M)...")
            # Using a small, fast model for CPU inference
            self.hf_pipeline = pipeline(
                "text2text-generation", 
                model="MBZUAI/LaMini-Flan-T5-248M", 
                max_length=512
            )

    def generate_answer(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """Generates an answer using the selected LLM provider."""
        context_text = "\n\n".join([f"Source: {doc['metadata']['source']}\nContent: {doc['content']}" for doc in context_docs])
        
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
        else:
            return "Error: Invalid LLM provider."

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        if not self.openai_api_key:
            return "Error: OpenAI API key not found."
        
        client = openai.OpenAI(api_key=self.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content

    def _call_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        if not self.anthropic_api_key:
            return "Error: Anthropic API key not found."
        
        client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text

    def _call_huggingface_local(self, system_prompt: str, user_prompt: str) -> str:
        # Combine system and user prompt for T5 models as they don't support system roles natively in the same way
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        response = self.hf_pipeline(full_prompt)
        return response[0]['generated_text']
