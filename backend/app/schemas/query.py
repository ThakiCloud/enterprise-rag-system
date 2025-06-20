from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    question: str = Field(..., description="User's question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    user_id: Optional[str] = Field(None, description="User ID for memory persistence")
    use_advanced_reasoning: Optional[bool] = Field(False, description="Enable advanced reasoning")
    use_memory: Optional[bool] = Field(True, description="Enable session memory for context")
    max_history_messages: Optional[int] = Field(5, description="Maximum number of history messages to include")

class QueryResponse(BaseModel):
    """Response from the query endpoint"""
    answer: str = Field(..., description="Generated answer")
    session_id: str = Field(..., description="Session ID used")
    user_id: Optional[str] = Field(None, description="User ID used")
    sources: Optional[List[str]] = Field(None, description="Source documents used")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    memory_updated: bool = Field(False, description="Whether memory was updated")
    memory_count: int = Field(0, description="Number of memories stored for this user")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    model_used: Optional[str] = Field(None, description="Model used for generation")
    
class MemoryInfo(BaseModel):
    """Memory information for responses"""
    memory_id: str = Field(..., description="Memory ID")
    content: str = Field(..., description="Memory content")
    topics: List[str] = Field(default_factory=list, description="Related topics")
    relevance_score: Optional[float] = Field(None, description="Relevance to current query")
    created_at: str = Field(..., description="Creation timestamp") 