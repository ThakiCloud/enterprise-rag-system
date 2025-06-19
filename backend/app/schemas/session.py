from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SessionInfo(BaseModel):
    """Session information model"""
    session_id: str = Field(..., description="Unique session identifier")
    created_at: str = Field(..., description="Session creation timestamp")
    last_activity: str = Field(..., description="Last activity timestamp")
    query_count: int = Field(default=0, description="Number of queries in this session")
    
class SessionCreate(BaseModel):
    """Session creation model"""
    session_id: Optional[str] = Field(None, description="Optional custom session ID")
    
class SessionResponse(BaseModel):
    """Session response model"""
    session_id: str = Field(..., description="Session ID")
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Response message") 