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
                            <button id="uploadBtn" class="btn" style="margin-top: 10px; width: 100%;">Upload Documents</button>
                        </div>
                    </div>
                    
                    <div class="feature-box">
                        <h3>🌐 Web Content Analysis</h3>
                        <p>Add or analyze web content from URLs.</p>
                        <div class="form-group">
                            <input type="url" id="urlInput" class="form-control" placeholder="https://example.com">
                            <div style="display: flex; gap: 10px; margin-top: 10px;">
                                <button id="addUrlBtn" class="btn btn-secondary" style="flex: 1;">Add URL</button>
                                <button id="analyzeUrlBtn" class="btn" style="flex: 1;">Analyze URL</button>
                            </div>
                            <small style="color: #666; margin-top: 5px; display: block;">
                                Add: Save to knowledge base | Analyze: Extract & analyze immediately
                            </small>
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
                            <button id="submitBtn" class="btn" style="margin-top: 15px;">Submit Query</button>
                            <button id="clearBtn" class="btn btn-secondary" style="margin-top: 15px; margin-left: 10px;">New Session</button>
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
            console.log('Script started loading...');
            
            let currentSessionId = null;
            
            function debugLog(message, data) {
                console.log('[Enterprise RAG] ' + message, data || '');
            }
            
            function generateSessionId() {
                return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            }
            
            function showStatus(message, type) {
                type = type || 'loading';
                debugLog('Status: ' + type, message);
                const statusArea = document.getElementById('statusArea');
                if (statusArea) {
                    statusArea.innerHTML = '<div class="status ' + type + '">' + message + '</div>';
                    if (type !== 'loading') {
                        setTimeout(function() {
                            statusArea.innerHTML = '';
                        }, 5000);
                    }
                }
            }
            
            function uploadFiles() {
                debugLog('Upload button clicked');
                const fileInput = document.getElementById('fileInput');
                const files = fileInput.files;
                
                if (files.length === 0) {
                    showStatus('Please select files to upload', 'error');
                    return;
                }
                
                showStatus('Uploading ' + files.length + ' file(s)...', 'loading');
                // Simplified upload logic for now
                setTimeout(function() {
                    showStatus('Upload feature coming soon!', 'success');
                }, 1000);
            }
            
            function addUrl() {
                debugLog('Add URL button clicked');
                const urlInput = document.getElementById('urlInput');
                const url = urlInput.value.trim();
                
                if (!url) {
                    showStatus('Please enter a URL', 'error');
                    return;
                }
                
                // Basic URL validation
                try {
                    new URL(url);
                } catch (e) {
                    showStatus('Please enter a valid URL', 'error');
                    return;
                }
                
                showStatus('Processing URL content...', 'loading');
                debugLog('Processing URL: ' + url);
                
                fetch('/api/v1/add-url/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                })
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                    }
                    return response.json();
                })
                .then(function(result) {
                    debugLog('URL processing result:', result);
                    
                    if (result.status === 'success') {
                        showStatus('URL content added successfully!', 'success');
                        urlInput.value = '';
                        
                        // Update response area with URL info
                        const responseArea = document.getElementById('responseArea');
                        const urlInfo = 'URL Added to Knowledge Base:\\n\\n' +
                                       'Title: ' + result.title + '\\n' +
                                       'URL: ' + result.url + '\\n' +
                                       'Word Count: ' + result.word_count + '\\n\\n' +
                                       result.message + '\\n\\n' +
                                       'You can now ask questions about this content!';
                        responseArea.textContent = urlInfo;
                    } else {
                        showStatus('Error: ' + (result.message || 'Unknown error'), 'error');
                    }
                })
                .catch(function(error) {
                    debugLog('URL processing error:', error);
                    showStatus('Error: ' + error.message, 'error');
                });
            }
            
            function analyzeUrl() {
                debugLog('Analyze URL button clicked');
                const urlInput = document.getElementById('urlInput');
                const url = urlInput.value.trim();
                
                if (!url) {
                    showStatus('Please enter a URL to analyze', 'error');
                    return;
                }
                
                // Basic URL validation
                try {
                    new URL(url);
                } catch (e) {
                    showStatus('Please enter a valid URL', 'error');
                    return;
                }
                
                showStatus('Analyzing URL content...', 'loading');
                debugLog('Analyzing URL: ' + url);
                
                fetch('/api/v1/analyze-url/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        url: url,
                        question: 'Analyze this web content and provide a comprehensive summary including key points, main topics, and any important insights.'
                    })
                })
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                    }
                    return response.json();
                })
                .then(function(result) {
                    debugLog('URL analysis result:', result);
                    
                    if (result.status === 'success') {
                        showStatus('URL analysis completed!', 'success');
                        urlInput.value = '';
                        
                        // Update response area with analysis
                        const responseArea = document.getElementById('responseArea');
                        const analysisText = 'Web Content Analysis:\\n\\n' +
                                           'Title: ' + result.title + '\\n' +
                                           'URL: ' + result.url + '\\n' +
                                           'Word Count: ' + result.word_count + '\\n\\n' +
                                           'Analysis:\\n' + result.analysis + '\\n\\n' +
                                           'Timestamp: ' + result.timestamp;
                        responseArea.textContent = analysisText;
                    } else {
                        showStatus('Error: ' + (result.message || 'Unknown error'), 'error');
                    }
                })
                .catch(function(error) {
                    debugLog('URL analysis error:', error);
                    showStatus('Error: ' + error.message, 'error');
                });
            }
            
            function submitQuery() {
                debugLog('Submit button clicked!');
                const question = document.getElementById('questionInput').value.trim();
                if (!question) {
                    showStatus('Please enter a question', 'error');
                    return;
                }
                
                if (!currentSessionId) {
                    currentSessionId = generateSessionId();
                    debugLog('Generated new session ID: ' + currentSessionId);
                }
                
                const advancedReasoning = document.getElementById('advancedReasoning').checked;
                debugLog('Query: "' + question + '", Advanced Reasoning: ' + advancedReasoning);
                
                showStatus('Processing your query...', 'loading');
                
                const requestBody = {
                    question: question,
                    session_id: currentSessionId,
                    use_advanced_reasoning: advancedReasoning
                };
                
                debugLog('Sending request to /api/v1/query/', requestBody);
                
                fetch('/api/v1/query/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestBody)
                })
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                    }
                    return response.json();
                })
                .then(function(result) {
                    debugLog('Query result:', result);
                    
                    if (result.status === 'success') {
                        const responseArea = document.getElementById('responseArea');
                        let responseText = 'Query: ' + result.query + '\\n\\nResponse:\\n' + result.response + '\\n\\nSession ID: ' + result.session_id + '\\nTimestamp: ' + result.timestamp;
                        
                        if (result.sources && result.sources.length > 0) {
                            responseText += '\\n\\nSources: ' + result.sources.length + ' documents referenced';
                        }
                        
                        if (result.reasoning_steps && result.reasoning_steps.length > 0) {
                            responseText += '\\n\\nReasoning Steps:\\n';
                            for (let i = 0; i < result.reasoning_steps.length; i++) {
                                responseText += (i + 1) + '. ' + result.reasoning_steps[i] + '\\n';
                            }
                        }
                        
                        responseArea.textContent = responseText;
                        showStatus('Query completed successfully!', 'success');
                    } else {
                        showStatus('Error: ' + (result.message || 'Unknown error'), 'error');
                    }
                })
                .catch(function(error) {
                    debugLog('Query submission error:', error);
                    showStatus('Error: ' + error.message, 'error');
                    console.error('Query error:', error);
                });
            }
            
            function clearSession() {
                debugLog('Clear session button clicked');
                currentSessionId = null;
                document.getElementById('questionInput').value = '';
                document.getElementById('responseArea').textContent = 'New session started. You can now ask questions!';
                showStatus('Session cleared', 'success');
            }
            
            // Initialize when page loads
            function initializePage() {
                debugLog('Initializing page...');
                
                // Attach event listeners
                const uploadBtn = document.getElementById('uploadBtn');
                if (uploadBtn) {
                    uploadBtn.onclick = uploadFiles;
                    debugLog('Upload button listener attached');
                }
                
                const urlBtn = document.getElementById('addUrlBtn');
                if (urlBtn) {
                    urlBtn.onclick = addUrl;
                    debugLog('Add URL button listener attached');
                }
                
                const analyzeUrlBtn = document.getElementById('analyzeUrlBtn');
                if (analyzeUrlBtn) {
                    analyzeUrlBtn.onclick = analyzeUrl;
                    debugLog('Analyze URL button listener attached');
                }
                
                const submitBtn = document.getElementById('submitBtn');
                if (submitBtn) {
                    submitBtn.onclick = function(e) {
                        e.preventDefault();
                        submitQuery();
                    };
                    debugLog('Submit button listener attached');
                }
                
                const clearBtn = document.getElementById('clearBtn');
                if (clearBtn) {
                    clearBtn.onclick = function(e) {
                        e.preventDefault();
                        clearSession();
                    };
                    debugLog('Clear button listener attached');
                }
                
                // Enter key submission
                const questionInput = document.getElementById('questionInput');
                if (questionInput) {
                    questionInput.onkeypress = function(e) {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            submitQuery();
                        }
                    };
                }
                
                // Test backend connectivity
                fetch('/api/v1/knowledge-base/stats')
                    .then(function(response) {
                        return response.json();
                    })
                    .then(function(data) {
                        debugLog('Backend connectivity test passed', data);
                        showStatus('Backend connected - ' + data.total_documents + ' documents in knowledge base', 'success');
                    })
                    .catch(function(error) {
                        debugLog('Backend connectivity test failed', error);
                        showStatus('Warning: Backend connection failed', 'error');
                    });
                
                debugLog('Page initialization complete!');
            }
            
            // Run initialization
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initializePage);
            } else {
                initializePage();
            }
            
            console.log('Script finished loading');
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
