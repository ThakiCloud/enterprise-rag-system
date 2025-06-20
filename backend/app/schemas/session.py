from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserMemory(BaseModel):
    """User memory model"""
    memory_id: Optional[str] = Field(None, description="Memory ID")
    memory: str = Field(..., description="Memory content")
    topics: List[str] = Field(default_factory=list, description="Related topics")
    created_at: str = Field(..., description="Memory creation timestamp")
    last_updated: str = Field(..., description="Last update timestamp")
    user_id: str = Field(..., description="User ID associated with memory")

class SessionInfo(BaseModel):
    """Session information model"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: Optional[str] = Field(None, description="User ID for memory association")
    created_at: str = Field(..., description="Session creation timestamp")
    last_activity: str = Field(..., description="Last activity timestamp")
    query_count: int = Field(default=0, description="Number of queries in this session")
    has_memory: bool = Field(default=False, description="Whether session has persistent memory")
    memory_count: int = Field(default=0, description="Number of memories stored")
    
class SessionCreate(BaseModel):
    """Session creation model"""
    session_id: Optional[str] = Field(None, description="Optional custom session ID")
    user_id: Optional[str] = Field(None, description="User ID for memory persistence")
    enable_memory: bool = Field(True, description="Enable persistent memory for this session")
    
class SessionResponse(BaseModel):
    """Session response model"""
    session_id: str = Field(..., description="Session ID")
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Response message")
    memories: Optional[List[UserMemory]] = Field(None, description="Associated memories")

class SessionMemoryRequest(BaseModel):
    """Request to manage session memories"""
    session_id: str = Field(..., description="Session ID")
    user_id: Optional[str] = Field(None, description="User ID")
    action: str = Field(..., description="Action: 'get', 'clear', 'add', 'delete'")
    memory_content: Optional[str] = Field(None, description="Memory content for add action")
    memory_id: Optional[str] = Field(None, description="Memory ID for delete action")
    topics: Optional[List[str]] = Field(None, description="Topics for new memory") 