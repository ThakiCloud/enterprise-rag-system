from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime

from .api.router import router as api_router
from .core.dependencies import get_knowledge_base, get_rag_agent

app = FastAPI(
    title="Enterprise RAG System",
    description="Advanced RAG system with memory, document processing, and reasoning capabilities",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize agents and knowledge base on startup"""
    print("🚀 Initializing Enterprise RAG System...")
    get_knowledge_base()
    get_rag_agent()
    print("✅ Services initialized successfully!")

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard UI"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Enterprise RAG System</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white; 
                border-radius: 20px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header { 
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white; 
                padding: 30px; 
                text-align: center;
            }
            .header h1 { font-size: 2.5em; margin-bottom: 10px; }
            .header p { font-size: 1.2em; opacity: 0.9; }
            .main-content { display: flex; min-height: 600px; }
            .sidebar { 
                width: 300px; 
                background: #f8f9fa; 
                padding: 30px; 
                border-right: 1px solid #e9ecef;
            }
            .content { flex: 1; padding: 30px; }
            .form-group { margin-bottom: 20px; }
            .form-group label { 
                display: block; 
                margin-bottom: 8px; 
                font-weight: 600; 
                color: #333;
            }
            .form-control { 
                width: 100%; 
                padding: 12px; 
                border: 2px solid #e9ecef; 
                border-radius: 8px; 
                font-size: 14px;
                transition: border-color 0.3s;
            }
            .form-control:focus { 
                outline: none; 
                border-color: #4CAF50; 
                box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
            }
            .btn { 
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white; 
                border: none; 
                padding: 12px 24px; 
                border-radius: 8px; 
                cursor: pointer; 
                font-size: 14px; 
                font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .btn:hover { 
                transform: translateY(-2px); 
                box-shadow: 0 8px 20px rgba(76, 175, 80, 0.3);
            }
            .btn-secondary { 
                background: linear-gradient(135deg, #6c757d, #5a6268);
            }
            .btn-secondary:hover { 
                box-shadow: 0 8px 20px rgba(108, 117, 125, 0.3);
            }
            .response-area { 
                background: #f8f9fa; 
                border: 2px solid #e9ecef; 
                border-radius: 12px; 
                padding: 20px; 
                min-height: 300px; 
                margin-top: 20px;
                white-space: pre-wrap;
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 14px;
                line-height: 1.6;
            }
            .feature-box { 
                background: white; 
                border: 2px solid #e9ecef; 
                border-radius: 12px; 
                padding: 20px; 
                margin-bottom: 20px;
                transition: border-color 0.3s;
            }
            .feature-box:hover { border-color: #4CAF50; }
            .feature-box h3 { color: #4CAF50; margin-bottom: 10px; }
            .status { 
                padding: 8px 16px; 
                border-radius: 20px; 
                font-size: 12px; 
                font-weight: 600; 
                text-transform: uppercase;
                display: inline-block;
                margin-top: 10px;
            }
            .status.success { background: #d4edda; color: #155724; }
            .status.error { background: #f8d7da; color: #721c24; }
            .status.loading { background: #d1ecf1; color: #0c5460; }
            .checkbox-group { display: flex; align-items: center; gap: 8px; margin-top: 10px; }
            .checkbox-group input[type="checkbox"] { transform: scale(1.2); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Enterprise RAG System</h1>
                <p>Advanced document analysis with memory and reasoning capabilities</p>
            </div>
            
            <div class="main-content">
                <div class="sidebar">
                    <div class="feature-box">
                        <h3>📄 Document Upload</h3>
                        <p>Upload PDF, DOCX, or text files to expand the knowledge base.</p>
                        <div class="form-group">
                            <input type="file" id="fileInput" class="form-control" multiple accept=".pdf,.docx,.txt">
                            <button onclick="uploadFiles()" class="btn" style="margin-top: 10px; width: 100%;">Upload Documents</button>
                        </div>
                    </div>
                    
                    <div class="feature-box">
                        <h3>🔗 URL Knowledge</h3>
                        <p>Add web content to the knowledge base.</p>
                        <div class="form-group">
                            <input type="url" id="urlInput" class="form-control" placeholder="https://example.com">
                            <button onclick="addUrl()" class="btn btn-secondary" style="margin-top: 10px; width: 100%;">Add URL</button>
                        </div>
                    </div>
                    
                    <div class="feature-box">
                        <h3>⚙️ Settings</h3>
                        <div class="checkbox-group">
                            <input type="checkbox" id="advancedReasoning">
                            <label for="advancedReasoning">Advanced Reasoning</label>
                        </div>
                        <div class="checkbox-group">
                            <input type="checkbox" id="streamResponse" checked>
                            <label for="streamResponse">Stream Response</label>
                        </div>
                    </div>
                </div>
                
                <div class="content">
                    <div class="form-group">
                        <label for="questionInput">Ask your question:</label>
                        <textarea id="questionInput" class="form-control" rows="3" 
                                placeholder="Enter your question about the uploaded documents..."></textarea>
                        <div class="checkbox-group">
                            <button onclick="submitQuery()" class="btn" style="margin-top: 15px;">Submit Query</button>
                            <button onclick="clearSession()" class="btn btn-secondary" style="margin-top: 15px; margin-left: 10px;">New Session</button>
                        </div>
                    </div>
                    
                    <div id="responseArea" class="response-area">
                        Welcome to the Enterprise RAG System! 🚀
                        
                        Features:
                        • Upload and analyze documents (PDF, DOCX, TXT)
                        • Add web content via URLs
                        • Advanced reasoning and chain-of-thought analysis
                        • Session memory for continuous conversations
                        • Professional document analysis
                        • Multi-LLM provider support
                        
                        Start by uploading documents or asking a question!
                    </div>
                    
                    <div id="statusArea"></div>
                </div>
            </div>
        </div>

        <script>
            let currentSessionId = null;
            
            function generateSessionId() {
                return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            }
            
            function showStatus(message, type = 'loading') {
                const statusArea = document.getElementById('statusArea');
                statusArea.innerHTML = `<div class="status ${type}">${message}</div>`;
                if (type !== 'loading') {
                    setTimeout(() => statusArea.innerHTML = '', 3000);
                }
            }
            
            async function uploadFiles() {
                const fileInput = document.getElementById('fileInput');
                const files = fileInput.files;
                
                if (files.length === 0) {
                    showStatus('Please select files to upload', 'error');
                    return;
                }
                
                showStatus('Uploading and processing documents...', 'loading');
                
                for (let file of files) {
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    try {
                        const response = await fetch('/api/v1/upload-document/', {
                            method: 'POST',
                            body: formData
                        });
                        
                        const result = await response.json();
                        if (result.status === 'success') {
                            showStatus(`Successfully uploaded: ${file.name}`, 'success');
                        } else {
                            showStatus(`Error uploading ${file.name}: ${result.message}`, 'error');
                        }
                    } catch (error) {
                        showStatus(`Error uploading ${file.name}: ${error.message}`, 'error');
                    }
                }
                
                fileInput.value = '';
            }
            
            async function addUrl() {
                const urlInput = document.getElementById('urlInput');
                const url = urlInput.value.trim();
                
                if (!url) {
                    showStatus('Please enter a URL', 'error');
                    return;
                }
                
                showStatus('Processing URL content...', 'loading');
                
                try {
                    const response = await fetch('/api/v1/add-url/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ url: url })
                    });
                    
                    const result = await response.json();
                    if (result.status === 'success') {
                        showStatus('URL content added successfully!', 'success');
                        urlInput.value = '';
                    } else {
                        showStatus(`Error: ${result.message}`, 'error');
                    }
                } catch (error) {
                    showStatus(`Error: ${error.message}`, 'error');
                }
            }
            
            async function submitQuery() {
                const question = document.getElementById('questionInput').value.trim();
                if (!question) {
                    showStatus('Please enter a question', 'error');
                    return;
                }
                
                if (!currentSessionId) {
                    currentSessionId = generateSessionId();
                }
                
                const advancedReasoning = document.getElementById('advancedReasoning').checked;
                
                showStatus('Processing your query...', 'loading');
                
                try {
                    const response = await fetch('/api/v1/query/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            question: question,
                            session_id: currentSessionId,
                            use_advanced_reasoning: advancedReasoning
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        const responseArea = document.getElementById('responseArea');
                        let responseText = `Query: ${result.query}\n\nResponse:\n${result.response}\n\nSession ID: ${result.session_id}\nTimestamp: ${result.timestamp}`;
                        
                        if (result.sources && result.sources.length > 0) {
                            responseText += `\n\nSources: ${result.sources.length} documents referenced`;
                        }
                        
                        if (result.reasoning_steps && result.reasoning_steps.length > 0) {
                            responseText += `\n\nReasoning Steps:\n${result.reasoning_steps.map((step, i) => `${i+1}. ${step}`).join('\n')}`;
                        }
                        
                        responseArea.innerHTML = responseText;
                        showStatus('Query completed successfully!', 'success');
                    } else {
                        showStatus(`Error: ${result.message || 'Unknown error'}`, 'error');
                    }
                } catch (error) {
                    showStatus(`Error: ${error.message}`, 'error');
                }
            }
            
            function clearSession() {
                currentSessionId = null;
                document.getElementById('questionInput').value = '';
                document.getElementById('responseArea').innerHTML = 'New session started. You can now ask questions!';
                showStatus('Session cleared', 'success');
            }
            
            // Enable Enter key submission
            document.getElementById('questionInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    submitQuery();
                }
            });
        </script>
    </body>
    </html>
    """

@app.get("/health/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "knowledge_base_initialized": get_knowledge_base() is not None,
        "rag_agent_initialized": get_rag_agent() is not None
    }
