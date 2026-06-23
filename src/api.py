# src/api.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.agent.core import CloudOpsAgent
from src.agent.llm_client_openai import OpenAIClient

app = FastAPI(title="CloudOps Buddy API", version="0.1.0")

# Initialize the agent once (reuses the same logic)
llm = OpenAIClient(
    model_name=os.getenv("OPENAI_MODEL", "qwen3:0.6b"),
    base_url=os.getenv("OPENAI_BASE_URL", "http://ollama:11434/v1")
)
agent = CloudOpsAgent(llm_client=llm, execute_mode=False)

class QueryRequest(BaseModel):
    query: str
    provider: str = "openai"   # or "groq", "gemini"
    execute: bool = False

@app.post("/chat")
def chat(request: QueryRequest):
    try:
        # We could support provider switching here if needed
        response = agent.chat(request.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}