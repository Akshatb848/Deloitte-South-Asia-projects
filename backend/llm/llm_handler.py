"""
LLM Handler - Ollama Integration
Manages communication with local LLM (Mistral/Llama)
"""

import os
import httpx
from typing import Dict, Any, Optional, List

class LLMHandler:
    """Handler for LLM operations using Ollama"""

    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("LLM_MODEL", "mistral:7b-instruct")
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load the official system prompt for the Education Intelligence Assistant"""
        return """You are an official Education Intelligence Assistant for the Ministry of Education, Government of India.

Your role and responsibilities:
1. Answer strictly based on the Vidya Samiksha Kendra newsletter data provided in the context
2. Maintain a formal, policy-aligned tone suitable for government officials
3. Provide accurate, data-driven insights without speculation
4. Cite specific statistics and time periods when relevant
5. If information is not found in the provided context, respond: "The requested information is not available in the current reporting period."

Guidelines:
- Use precise numbers and percentages
- Compare data across time periods when relevant
- Highlight trends and patterns
- Maintain professional language
- Avoid casual expressions or emojis
- Focus on factual reporting

Format your responses clearly with:
- Direct answers to the question
- Supporting statistics
- Relevant time periods
- Data sources (month/section)"""

    async def check_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_host}/api/tags")
                return response.status_code == 200
        except Exception as e:
            print(f"LLM connection error: {e}")
            return False

    async def generate_response(
        self,
        query: str,
        context: str,
        temperature: float = 0.3,
        max_tokens: int = 500
    ) -> str:
        """
        Generate response using Ollama LLM

        Args:
            query: User query
            context: Retrieved context from RAG
            temperature: Sampling temperature (lower = more focused)
            max_tokens: Maximum response length

        Returns:
            Generated response text
        """
        try:
            prompt = self._build_prompt(query, context)

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "system": self.system_prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                            "top_p": 0.9,
                            "top_k": 40
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    return "I apologize, but I am currently unable to process your request. Please try again later."

        except httpx.TimeoutException:
            return "Request timed out. Please try again with a simpler query."
        except Exception as e:
            print(f"Error generating response: {e}")
            return "An error occurred while processing your request."

    def _build_prompt(self, query: str, context: str) -> str:
        """Build the complete prompt with context and query"""
        return f"""Based on the following education data from the Ministry of Education newsletter:

CONTEXT:
{context}

USER QUESTION:
{query}

Please provide a comprehensive, data-driven answer based strictly on the context provided. Include specific statistics and time periods where relevant."""

    async def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze user query to determine intent

        Returns:
            Dictionary with intent classification:
            - type: 'comparison', 'visualization', 'factual', 'trend'
            - entities: relevant entities (states, metrics, etc.)
            - time_scope: 'single', 'range', 'all'
        """
        try:
            prompt = f"""Analyze this query and extract structured information:

Query: "{query}"

Classify the query intent:
1. Type: Is this a comparison, visualization request, factual question, or trend analysis?
2. Entities: What states, metrics, or data points are mentioned?
3. Time scope: Is this about a single month, a range, or all available data?

Respond in this format:
Type: [comparison/visualization/factual/trend]
Entities: [comma-separated list]
Time scope: [single/range/all]
Metric: [specific metric if mentioned]"""

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "num_predict": 200
                        }
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    analysis = self._parse_intent_response(result.get("response", ""))
                    return analysis
                else:
                    return self._default_intent()

        except Exception as e:
            print(f"Error analyzing intent: {e}")
            return self._default_intent()

    def _parse_intent_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM's intent analysis response"""
        intent = {
            "type": "factual",
            "entities": [],
            "time_scope": "single",
            "metric": None
        }

        lines = response.lower().split('\n')
        for line in lines:
            if 'type:' in line:
                for intent_type in ['comparison', 'visualization', 'trend', 'factual']:
                    if intent_type in line:
                        intent['type'] = intent_type
                        break

            elif 'entities:' in line:
                entities_str = line.split('entities:')[1].strip()
                intent['entities'] = [e.strip() for e in entities_str.split(',') if e.strip()]

            elif 'time scope:' in line or 'time_scope:' in line:
                for scope in ['range', 'all', 'single']:
                    if scope in line:
                        intent['time_scope'] = scope
                        break

            elif 'metric:' in line:
                metric_str = line.split('metric:')[1].strip()
                if metric_str and metric_str not in ['none', 'n/a', '-']:
                    intent['metric'] = metric_str

        return intent

    def _default_intent(self) -> Dict[str, Any]:
        """Return default intent when analysis fails"""
        return {
            "type": "factual",
            "entities": [],
            "time_scope": "single",
            "metric": None
        }

    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current LLM model"""
        return {
            "model": self.model,
            "host": self.ollama_host,
            "type": "local"
        }
