import requests
import asyncio
from typing import Dict, Any, Optional

from agno.agent import Agent
from agno.app.agui.app import AGUIApp
from agno.models.openai import OpenAIChat

import config

class BackendRAGAgent(Agent):
    """Custom Agent that forwards queries to the backend RAG system."""
    
    def __init__(self, backend_url: str, **kwargs):
        self.backend_url = backend_url
        super().__init__(**kwargs)
    
    def run(self, query: str, **kwargs) -> Any:
        """Override run method to query the backend instead of using the LLM directly."""
        session_id = kwargs.get("session_id", "default")
        
        # Check for advanced reasoning keywords
        use_advanced_reasoning = (
            "reasoning" in query.lower() or 
            "analyze" in query.lower() or
            "think" in query.lower()
        )
        
        try:
            # Query the backend
            api_url = f"{self.backend_url}/api/v1/query/"
            payload = {
                "question": query,
                "session_id": session_id,
                "use_advanced_reasoning": use_advanced_reasoning,
            }
            
            response = requests.post(api_url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            
            # Format the response
            formatted_response = data["response"]
            
            if data.get("sources"):
                formatted_response += "\n\n**📚 Sources:**\n"
                for i, source in enumerate(data["sources"], 1):
                    source_info = source.get("uri", source.get("content", "Unknown source"))
                    formatted_response += f"{i}. {source_info}\n"
            
            if data.get("reasoning_steps"):
                formatted_response += "\n\n**🧠 Reasoning Steps:**\n"
                for i, step in enumerate(data["reasoning_steps"], 1):
                    formatted_response += f"{i}. {step}\n"
            
            # Create a response object that AGUIApp expects
            class MockResponse:
                def __init__(self, content):
                    self.content = content
                    self.sources = data.get("sources", [])
                    self.reasoning = data.get("reasoning_steps")
            
            return MockResponse(formatted_response)
            
        except requests.RequestException as e:
            class ErrorResponse:
                def __init__(self, error_msg, backend_url):
                    self.content = f"❌ **Backend Error:** {error_msg}\n\nPlease ensure the backend server is running at {backend_url}"
            
            return ErrorResponse(str(e), self.backend_url)

# Create the backend-connected agent
chat_agent = BackendRAGAgent(
    backend_url=config.BACKEND_URL,
    name="Enterprise RAG Assistant",
    model=OpenAIChat(id=config.AGENT_MODEL, api_key=config.OPENAI_API_KEY),
    instructions=[
        "You are an Enterprise RAG Assistant that processes queries through a backend system.",
        "You help users query and analyze documents using advanced retrieval and reasoning.",
        "You can process various document types and provide comprehensive answers.",
        "Use 'reasoning' or 'analyze' keywords to trigger advanced reasoning mode.",
    ],
    add_datetime_to_instructions=True,
    markdown=True,
)

# Create the AGUIApp instance
agui_app = AGUIApp(
    agent=chat_agent,
    name="Enterprise RAG System",
    app_id="enterprise_rag_system",
    description="Advanced RAG system with multi-LLM support and document processing capabilities.",
)

# Get the FastAPI app
app = agui_app.get_app()

# Add root route for web interface
@app.get("/")
async def root():
    """Root endpoint that provides a simple web interface."""
    return {
        "message": "Enterprise RAG System UI",
        "status": "running",
        "endpoints": {
            "chat": "/agui",
            "status": "/status",
            "upload": "/upload-document/",
            "docs": "/docs"
        },
        "description": "AGUIApp-based Enterprise RAG System interface"
    }

# Add custom route for document upload
@app.post("/upload-document/")
async def upload_document_endpoint(file: bytes, filename: str, content_type: str):
    """Custom endpoint for document uploads."""
    try:
        api_url = f"{config.BACKEND_URL}/api/v1/upload-document/"
        files = {'file': (filename, file, content_type)}
        
        # Use asyncio for non-blocking request
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: requests.post(api_url, files=files, timeout=300)
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"status": "error", "message": f"Upload failed: {str(e)}"}

if __name__ == "__main__":
    agui_app.serve(app="main:app", port=8501, reload=True)
