from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Body
from datetime import datetime
from typing import List, Dict, Any
import logging
import requests
from bs4 import BeautifulSoup
import re

from ..schemas.query import QueryRequest, QueryResponse
from ..schemas.document import DocumentUploadResponse
from ..schemas.session import SessionInfo
from ..core.dependencies import get_rag_agent, get_research_team, get_knowledge_base, SimpleAgent, SimpleKnowledgeBase

router = APIRouter()

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def extract_web_content(url: str) -> Dict[str, Any]:
    """Extract content from a web URL"""
    try:
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No title"
        
        # Extract main content
        # Try to find main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|article', re.I))
        
        if main_content:
            content_text = main_content.get_text()
        else:
            # Fallback to body content
            content_text = soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in content_text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content_text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        # Extract headings for structure
        headings = []
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append(f"{heading.name}: {heading.get_text().strip()}")
        
        return {
            'url': url,
            'title': title_text,
            'description': description,
            'content': content_text[:5000],  # Limit content length
            'headings': headings[:10],  # Limit number of headings
            'word_count': len(content_text.split()),
            'status': 'success'
        }
        
    except requests.RequestException as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return {
            'url': url,
            'error': f"Failed to fetch URL: {str(e)}",
            'status': 'error'
        }
    except Exception as e:
        logger.error(f"Error processing URL {url}: {e}")
        return {
            'url': url,
            'error': f"Failed to process content: {str(e)}",
            'status': 'error'
        }

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
        logger.info(f"Processing URL: {url}")
        
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="URL must start with http:// or https://")
        
        # Extract web content
        content_data = extract_web_content(url)
        
        if content_data['status'] == 'error':
            raise HTTPException(status_code=400, detail=content_data['error'])
        
        # Prepare content for knowledge base
        formatted_content = f"""
URL: {content_data['url']}
Title: {content_data['title']}
Description: {content_data['description']}

Headings:
{chr(10).join(content_data['headings'])}

Content:
{content_data['content']}
        """.strip()
        
        # Add to knowledge base
        knowledge_base = get_knowledge_base()
        metadata = {
            "url": url,
            "title": content_data['title'],
            "type": "web_content",
            "word_count": content_data['word_count'],
            "extracted_at": datetime.now().isoformat()
        }
        
        knowledge_base.add_document(formatted_content, metadata)
        
        logger.info(f"Successfully added URL content to knowledge base: {url}")
        
        return {
            "url": url,
            "title": content_data['title'],
            "word_count": content_data['word_count'],
            "status": "success",
            "message": f"Successfully extracted and added content from '{content_data['title']}'"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing URL: {str(e)}")


@router.post("/analyze-url/")
async def analyze_url_endpoint(
    url: str = Body(..., embed=True),
    question: str = Body(default="Analyze this web content and provide a comprehensive summary.", embed=True)
):
    """Extract content from URL and immediately analyze it."""
    try:
        logger.info(f"Analyzing URL: {url}")
        
        # First, add the URL to knowledge base
        url_result = await add_url_endpoint(url)
        
        if url_result['status'] != 'success':
            raise HTTPException(status_code=400, detail="Failed to extract URL content")
        
        # Now analyze the content
        rag_agent = get_rag_agent()
        
        # Create analysis question that references the URL
        analysis_question = f"Based on the content from {url} (titled '{url_result['title']}'), {question}"
        
        logger.info(f"Analyzing with question: {analysis_question}")
        response = await rag_agent.arun(analysis_question)
        
        return {
            "url": url,
            "title": url_result['title'],
            "word_count": url_result['word_count'],
            "question": question,
            "analysis": response,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing URL {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing URL: {str(e)}")


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
        
        # Count different types of documents
        total_docs = len(knowledge_base.documents)
        web_docs = sum(1 for doc in knowledge_base.documents if doc.get('metadata', {}).get('type') == 'web_content')
        file_docs = total_docs - web_docs
        
        stats = {
            "total_documents": total_docs,
            "web_documents": web_docs,
            "file_documents": file_docs,
            "status": "active"
        }
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting knowledge base stats: {str(e)}") 