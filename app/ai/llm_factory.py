import os
import json
import httpx
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.config import settings
from app.tools import tool_registry

class BaseLLMClient(ABC):
    @abstractmethod
    def generate(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate response from LLM, returning dict with text and optional tool_calls."""
        pass

class MockLLMClient(BaseLLMClient):
    """Deterministic Mock LLM driver for offline demos and evals without external API keys."""

    def generate(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        # Inspect user query / incident ID from prompt
        last_msg = messages[-1]["content"] if messages else ""
        
        # Scenario 1: INC-101 (Plan & GAID Integrity)
        if "INC-101" in last_msg or "pipe_claims_integrity" in last_msg or "Plan" in last_msg or "GAID" in last_msg:
            return {
                "role": "assistant",
                "content": "I am initiating an automated root-cause investigation into incident INC-101 (pipe_claims_integrity failure).",
                "tool_calls": [
                    {"name": "inspect_pipeline", "args": {"pipeline_id": "PIPE-001"}},
                    {"name": "search_logs", "args": {"run_id": "RUN-001-A", "keyword": "IntegrityValidationError"}},
                    {"name": "inspect_schema", "args": {"table_name": "claims"}},
                    {"name": "profile_dataset", "args": {"table_name": "claims"}},
                    {"name": "detect_anomalies", "args": {"table_name": "claims"}},
                    {"name": "find_dependencies", "args": {"table_name": "claims"}},
                    {"name": "simulate_impact", "args": {"target_table": "claims", "filter_condition": "plan_id = 'PLAN-104'"}},
                    {"name": "generate_sql_fix", "args": {"table_name": "claims", "fix_type": "DELETE_STALE_REFS", "condition": "plan_id = 'PLAN-104'"}},
                    {"name": "generate_remediation_plan", "args": {
                        "incident_id": "INC-101",
                        "sql_fix": "DELETE FROM claims WHERE plan_id = 'PLAN-104'; DELETE FROM benefits WHERE plan_id = 'PLAN-104';",
                        "impact_summary": "Removes 45 stale claim records and 28 benefit records referencing TERMINATED Plan PLAN-104."
                    }}
                ]
            }
        
        # Scenario 2: INC-102 (Schema Drift)
        elif "INC-102" in last_msg or "pipe_schema_sync" in last_msg or "Schema" in last_msg:
            return {
                "role": "assistant",
                "content": "Investigating INC-102 schema drift error...",
                "tool_calls": [
                    {"name": "compare_schemas", "args": {"table_name": "customers"}},
                    {"name": "search_logs", "args": {"run_id": "RUN-002-A", "keyword": "SchemaMismatchError"}},
                    {"name": "generate_remediation_plan", "args": {
                        "incident_id": "INC-102",
                        "sql_fix": "ALTER TABLE customers ALTER COLUMN country TYPE VARCHAR;",
                        "impact_summary": "Re-aligns physical country column type with metadata specification VARCHAR."
                    }}
                ]
            }
        
        # Scenario 3: INC-103 (Null Spike)
        elif "INC-103" in last_msg or "pipe_txn_aggregate" in last_msg or "Null" in last_msg:
            return {
                "role": "assistant",
                "content": "Investigating INC-103 null rate spike...",
                "tool_calls": [
                    {"name": "run_data_quality_check", "args": {"table_name": "transactions"}},
                    {"name": "profile_dataset", "args": {"table_name": "transactions"}},
                    {"name": "generate_remediation_plan", "args": {
                        "incident_id": "INC-103",
                        "sql_fix": "UPDATE transactions SET amount = 0.0, currency = 'USD' WHERE amount IS NULL;",
                        "impact_summary": "Fills 400 null transaction records with default baseline fallback values."
                    }}
                ]
            }

        # Fallback generic plan
        return {
            "role": "assistant",
            "content": "Completed basic diagnostics for pipeline investigation.",
            "tool_calls": [
                {"name": "inspect_pipeline", "args": {"pipeline_id": "PIPE-001"}},
                {"name": "search_logs", "args": {"keyword": "ERROR"}}
            ]
        }

class OpenAILLMClient(BaseLLMClient):
    """OpenAI API integration for tool calling."""
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL.rstrip('/')
        self.model = settings.OPENAI_MODEL

    def generate(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        if not self.api_key:
            # Fallback to Mock LLM if no API key provided
            return MockLLMClient().generate(messages, tools)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_request()
            data = resp.json()
            message = data["choices"][0]["message"]
            
            tool_calls = []
            if "tool_calls" in message:
                for tc in message["tool_calls"]:
                    tool_calls.append({
                        "name": tc["function"]["name"],
                        "args": json.loads(tc["function"]["arguments"])
                    })
            
            return {
                "role": "assistant",
                "content": message.get("content", ""),
                "tool_calls": tool_calls
            }

class OllamaLLMClient(BaseLLMClient):
    """Local Ollama LLM integration."""
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip('/')
        self.model = settings.OLLAMA_MODEL

    def generate(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_request()
                data = resp.json()
                content = data["message"]["content"]
                return {"role": "assistant", "content": content, "tool_calls": []}
        except Exception:
            # Fallback to Mock if local Ollama server is unreachable
            return MockLLMClient().generate(messages, tools)

def get_llm_client() -> BaseLLMClient:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "openai":
        return OpenAILLMClient()
    elif provider == "ollama":
        return OllamaLLMClient()
    else:
        return MockLLMClient()
