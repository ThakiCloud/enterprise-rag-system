import os
import logging
from pathlib import Path
from fastapi import UploadFile, HTTPException
from datetime import datetime
from typing import Dict, Any, Optional

from agno.knowledge.text import AgentKnowledge
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.knowledge.docx import DocxKnowledgeBase  
from agno.knowledge.url import UrlKnowledge
from agno.vectordb.lancedb import LanceDb, SearchType

from ..core import config
from ..schemas.document import DocumentUploadResponse

# Set up logging
logger = logging.getLogger(__name__)

async def process_uploaded_file(file: UploadFile, knowledge_base: AgentKnowledge) -> DocumentUploadResponse:
    """Save, process, and load a document into the knowledge base."""
    file_path = None
    try:
        logger.info(f"Processing uploaded file: {file.filename}")
        
        # Ensure upload directory exists
        config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file
        file_path = config.UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"File saved to: {file_path}")
        
        # Get file extension and validate
        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        
        # Create vector DB configuration
        doc_knowledge_params = {
            "vector_db": LanceDb(
                uri=str(config.VECTOR_DB_PATH),
                table_name="enterprise_documents",
                search_type=SearchType.hybrid,
            )
        }

        # Process based on file type
        doc_knowledge = None
        if file_extension == 'pdf':
            logger.info("Processing PDF document")
            doc_knowledge = PDFKnowledgeBase(path=str(file_path), **doc_knowledge_params)
        elif file_extension == 'docx':
            logger.info("Processing DOCX document")
            doc_knowledge = DocxKnowledgeBase(path=str(file_path), **doc_knowledge_params)
        elif file_extension in ['txt', 'md']:
            logger.info("Processing text document")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            doc_knowledge = AgentKnowledge(sources=[content], **doc_knowledge_params)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")

        # Load document into vector database
        logger.info("Loading document into vector database")
        await doc_knowledge.aload(recreate=False)
        
        # Update knowledge base sources if available
        if hasattr(doc_knowledge, 'sources') and doc_knowledge.sources:
            if not hasattr(knowledge_base, 'sources'):
                knowledge_base.sources = []
            knowledge_base.sources.extend(doc_knowledge.sources)
            logger.info(f"Added {len(doc_knowledge.sources)} sources to knowledge base")
        
        # Generate document ID
        document_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename.replace(' ', '_')}"
        
        logger.info(f"Successfully processed document: {file.filename}")
        
        return DocumentUploadResponse(
            message=f"Document {file.filename} processed successfully",
            document_id=document_id,
            filename=file.filename,
            status="success"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing document {file.filename}: {str(e)}")
        
        # Clean up file if it was created
        if file_path and file_path.exists():
            try:
                file_path.unlink()
                logger.info(f"Cleaned up file: {file_path}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup file {file_path}: {cleanup_error}")
        
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


async def process_url(url: str, knowledge_base: AgentKnowledge) -> Dict[str, Any]:
    """Process and load a URL's content into the knowledge base."""
    try:
        logger.info(f"Processing URL: {url}")
        
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

        # Create URL knowledge object
        url_knowledge = UrlKnowledge(
            urls=[url],
            vector_db=LanceDb(
                uri=str(config.VECTOR_DB_PATH),
                table_name="enterprise_documents",
                search_type=SearchType.hybrid,
            ),
        )
        
        # Load URL content into vector database
        logger.info("Loading URL content into vector database")
        await url_knowledge.aload(recreate=False)
        
        # Update knowledge base sources if available
        if hasattr(url_knowledge, 'sources') and url_knowledge.sources:
            if not hasattr(knowledge_base, 'sources'):
                knowledge_base.sources = []
            knowledge_base.sources.extend(url_knowledge.sources)
            logger.info(f"Added {len(url_knowledge.sources)} sources from URL to knowledge base")
        
        logger.info(f"Successfully processed URL: {url}")
        
        return {
            "message": "URL content added successfully",
            "url": url,
            "status": "success",
            "sources_added": len(url_knowledge.sources) if hasattr(url_knowledge, 'sources') else 0
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing URL: {str(e)}")


def get_knowledge_base_info(knowledge_base: AgentKnowledge) -> Dict[str, Any]:
    """Get information about the current knowledge base."""
    try:
        info = {
            "total_sources": len(knowledge_base.sources) if hasattr(knowledge_base, 'sources') else 0,
            "vector_db_path": str(config.VECTOR_DB_PATH),
            "vector_db_table": "enterprise_documents",
            "search_type": "hybrid",
            "status": "active"
        }
        
        # Add vector DB specific info if available
        if hasattr(knowledge_base, 'vector_db') and knowledge_base.vector_db:
            info["vector_db_uri"] = knowledge_base.vector_db.uri if hasattr(knowledge_base.vector_db, 'uri') else None
            info["vector_db_table_name"] = knowledge_base.vector_db.table_name if hasattr(knowledge_base.vector_db, 'table_name') else None
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting knowledge base info: {str(e)}")
        return {
            "error": str(e),
            "status": "error"
        }


def cleanup_old_files(max_age_days: int = 7) -> Dict[str, Any]:
    """Clean up old uploaded files."""
    try:
        if not config.UPLOAD_DIR.exists():
            return {"message": "Upload directory does not exist", "files_removed": 0}
        
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        files_removed = 0
        
        for file_path in config.UPLOAD_DIR.iterdir():
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    files_removed += 1
                    logger.info(f"Removed old file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to remove file {file_path}: {e}")
        
        return {
            "message": f"Cleanup completed. Removed {files_removed} files older than {max_age_days} days.",
            "files_removed": files_removed,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        return {
            "error": str(e),
            "status": "error"
        } 