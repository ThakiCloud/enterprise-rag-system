from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    question: str = Field(..., description="User's question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    use_advanced_reasoning: Optional[bool] = Field(False, description="Enable advanced reasoning")

class QueryResponse(BaseModel):
    query: str
    response: str
    session_id: str
    sources: List[Dict[str, Any]]
    reasoning_steps: Optional[List[str]] = None
    timestamp: str
    status: str 