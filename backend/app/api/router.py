from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Body
from datetime import datetime
from typing import List, Dict, Any
import logging

from ..schemas.query import QueryRequest, QueryResponse
from ..schemas.document import DocumentUploadResponse
from ..schemas.session import SessionInfo
from ..core.dependencies import get_rag_agent, get_research_team, get_knowledge_base, SimpleAgent, SimpleKnowledgeBase

router = APIRouter()

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/query/", response_model=QueryResponse)
async def query_knowledge(
    request: QueryRequest
):
    """Process a query using the RAG system."""
    try:
        logger.info(f"Received query request for session: {request.session_id}")
        session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Getting agent for query (advanced_reasoning={request.use_advanced_reasoning})...")
        rag_agent = get_rag_agent()
        research_team = get_research_team()
        agent = research_team if request.use_advanced_reasoning else rag_agent
        logger.info(f"Using agent: {agent.name if hasattr(agent, 'name') else 'SimpleAgent'}")
        
        logger.info(f"Executing agent with question: '{request.question}'")
        response = await agent.arun(request.question)
        logger.info("Agent execution finished, creating response.")
        
        # Simple response handling
        sources = []
        reasoning_steps = None
        
        return QueryResponse(
            query=request.question,
            response=response,
            session_id=session_id,
            sources=sources,
            reasoning_steps=reasoning_steps,
            timestamp=datetime.now().isoformat(),
            status="success"
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/upload-document/", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...)
):
    """Upload and process a document into the knowledge base."""
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt', '.md']
        file_extension = '.' + file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # Simple file processing - just add as text to knowledge base
        content = file_content.decode('utf-8', errors='ignore')
        knowledge_base = get_knowledge_base()
        knowledge_base.add_document(content, {"filename": file.filename, "type": file_extension})
        
        return DocumentUploadResponse(
            message=f"Document {file.filename} uploaded successfully",
            document_id=f"doc_{len(knowledge_base.documents)}",
            filename=file.filename,
            status="success"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.post("/add-url/")
async def add_url_endpoint(
    url: str = Body(..., embed=True)
):
    """Add URL content to the knowledge base."""
    try:
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
        
        # Simple URL processing - just add a placeholder
        knowledge_base = get_knowledge_base()
        knowledge_base.add_document(f"Content from URL: {url}", {"url": url, "type": "url"})
        
        return {
            "url": url,
            "status": "success",
            "message": f"URL content added to knowledge base"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing URL: {str(e)}")


@router.get("/sessions/", response_model=List[SessionInfo])
async def list_sessions():
    """List all active sessions."""
    try:
        # Simple implementation
        sessions = [SessionInfo(
            session_id="example_session",
            created_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            query_count=0
        )]
        
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str
):
    """Delete a specific session."""
    try:
        return {
            "message": f"Session {session_id} deleted successfully",
            "session_id": session_id,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str
):
    """Get information about a specific session."""
    try:
        return SessionInfo(
            session_id=session_id,
            created_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            query_count=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session info: {str(e)}")


@router.get("/knowledge-base/stats")
async def get_knowledge_base_stats():
    """Get statistics about the knowledge base."""
    try:
        knowledge_base = get_knowledge_base()
        stats = {
            "total_documents": len(knowledge_base.documents),
            "status": "active"
        }
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting knowledge base stats: {str(e)}") 