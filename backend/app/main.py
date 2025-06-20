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
                overflow-y: auto;
                max-height: 500px;
                position: relative;
            }
            .response-area.streaming {
                border-color: #4CAF50;
                background: linear-gradient(135deg, #f8f9fa 0%, #e8f5e8 100%);
            }
            .response-area.streaming::after {
                content: '▋';
                color: #4CAF50;
                animation: blink 1s infinite;
                font-weight: bold;
            }
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0; }
            }
            
            /* Structured response display */
            .response-container {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                white-space: normal;
            }
            
            .response-section {
                margin-bottom: 20px;
                border: 1px solid #e1e5e9;
                border-radius: 8px;
                overflow: hidden;
            }
            
            .response-section-header {
                background: #f8f9fa;
                padding: 12px 16px;
                border-bottom: 1px solid #e1e5e9;
                font-weight: 600;
                color: #495057;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .response-section-content {
                padding: 16px;
                background: white;
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 13px;
                line-height: 1.5;
                white-space: pre-wrap;
            }
            
            .query-section .response-section-header {
                background: #e3f2fd;
                color: #1976d2;
            }
            
            .think-section .response-section-header {
                background: #fff3e0;
                color: #f57c00;
                cursor: pointer;
                user-select: none;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .think-section .response-section-header:hover {
                background: #ffe0b2;
            }
            
            .think-toggle {
                font-size: 12px;
                transition: transform 0.2s ease;
            }
            
            .think-toggle.collapsed {
                transform: rotate(-90deg);
            }
            
            .response-section .response-section-header {
                background: #e8f5e8;
                color: #2e7d32;
            }
            
            .metadata-section .response-section-header {
                background: #f3e5f5;
                color: #7b1fa2;
            }
            
            .think-content {
                max-height: 300px;
                overflow-y: auto;
                transition: max-height 0.3s ease;
            }
            
            .think-content.collapsed {
                max-height: 0;
                padding: 0 16px;
                overflow: hidden;
            }
            
            .metadata-content {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 12px;
                color: #6c757d;
            }
            
            .metadata-item {
                margin-bottom: 8px;
            }
            
            .metadata-label {
                font-weight: 600;
                color: #495057;
            }
            
            .streaming-cursor {
                color: #4CAF50;
                animation: blink 1s infinite;
                font-weight: bold;
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
            
            /* Upload area styles */
            .upload-container {
                margin: 20px 0;
            }
            
            .upload-area {
                border: 3px dashed #007bff;
                border-radius: 10px;
                padding: 40px 20px;
                text-align: center;
                background: #f8f9fa;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-bottom: 20px;
            }
            
            .upload-area:hover {
                border-color: #0056b3;
                background: #e3f2fd;
            }
            
            .upload-area.drag-over {
                border-color: #28a745;
                background: #d4edda;
                transform: scale(1.02);
            }
            
            .upload-icon {
                font-size: 48px;
                margin-bottom: 15px;
            }
            
            .upload-text p {
                margin: 5px 0;
                color: #333;
            }
            
            .upload-text p:first-child {
                font-size: 18px;
                color: #007bff;
            }
            
            .upload-text p:last-child {
                font-size: 14px;
                color: #666;
            }
            
            /* File list styles */
            .file-list {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
            }
            
            .file-list h4 {
                margin: 0 0 10px 0;
                color: #333;
                font-size: 16px;
            }
            
            .file-list ul {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            
            .file-item {
                padding: 8px 12px;
                margin: 5px 0;
                border-radius: 5px;
                font-size: 14px;
            }
            
            .file-valid {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            
            .file-invalid {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            
            .file-warning {
                background: #fff3cd;
                color: #856404;
                border: 1px solid #ffeaa7;
            }
            
            /* Upload action buttons */
            .upload-actions {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                justify-content: center;
            }
            
            .action-btn {
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                min-width: 140px;
            }
            
            .upload-btn {
                background: #007bff;
                color: white;
            }
            
            .upload-btn:hover {
                background: #0056b3;
                transform: translateY(-2px);
            }
            
            .analyze-btn {
                background: #28a745;
                color: white;
            }
            
            .analyze-btn:hover {
                background: #1e7e34;
                transform: translateY(-2px);
            }
            
            .clear-btn {
                background: #6c757d;
                color: white;
            }
            
            .clear-btn:hover {
                background: #545b62;
                transform: translateY(-2px);
            }
            
            @media (max-width: 768px) {
                .upload-actions {
                    flex-direction: column;
                    align-items: stretch;
                }
                
                .action-btn {
                    width: 100%;
                    margin-bottom: 10px;
                }
                
                .upload-area {
                    padding: 30px 15px;
                }
                
                .upload-icon {
                    font-size: 36px;
                }
            }
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
                        <div class="section">
                            <h2>📄 문서 업로드</h2>
                            <div class="upload-container">
                                <div class="upload-area" id="uploadArea">
                                    <div class="upload-icon">📁</div>
                                    <div class="upload-text">
                                        <p><strong>파일을 드래그하여 놓거나 클릭하여 선택하세요</strong></p>
                                        <p>지원 형식: PDF, DOCX, TXT, MD (최대 10MB)</p>
                                    </div>
                                    <input type="file" id="fileInput" multiple accept=".pdf,.docx,.txt,.md" style="display: none;">
                                </div>
                                
                                <div class="file-list" id="fileList" style="display: none;">
                                    <h4>선택된 파일:</h4>
                                    <ul id="selectedFiles"></ul>
                                </div>
                                
                                <div class="upload-actions">
                                    <button onclick="uploadFiles()" class="action-btn upload-btn">
                                        📤 업로드하기
                                    </button>
                                    <button onclick="analyzeDocument()" class="action-btn analyze-btn">
                                        🔍 바로 분석하기
                                    </button>
                                    <button onclick="clearFiles()" class="action-btn clear-btn">
                                        🗑️ 선택 해제
                                    </button>
                                </div>
                            </div>
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
                    <form id="queryForm">
                        <div class="form-group">
                            <label for="queryInput">질문을 입력하세요:</label>
                            <textarea id="queryInput" class="form-control" rows="3" 
                                    placeholder="업로드된 문서에 대해 질문하거나 일반적인 질문을 하세요..."></textarea>
                            <div class="checkbox-group">
                                <button type="submit" id="submitBtn" class="btn" style="margin-top: 15px;">Submit Query</button>
                                <button type="button" id="clearBtn" class="btn btn-secondary" style="margin-top: 15px; margin-left: 10px;">New Session</button>
                            </div>
                        </div>
                    </form>
                    
                    <div id="responseArea" class="response-area">
                        Enterprise RAG System에 오신 것을 환영합니다! 🚀
                        
                        주요 기능:
                        • 문서 업로드 및 분석 (PDF, DOCX, TXT, MD)
                        • 웹 콘텐츠 URL 추가 및 분석
                        • 고급 추론 및 사고 과정 분석
                        • 세션 메모리로 지속적인 대화
                        • 전문적인 문서 분석
                        • 다중 언어 모델 지원
                        
                        문서를 업로드하거나 질문을 시작해보세요!
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
                    showStatus('업로드할 파일을 선택해주세요', 'error');
                    return;
                }
                
                // Validate file types
                const allowedTypes = ['.pdf', '.docx', '.txt', '.md'];
                const invalidFiles = [];
                
                for (let file of files) {
                    const extension = '.' + file.name.split('.').pop().toLowerCase();
                    if (!allowedTypes.includes(extension)) {
                        invalidFiles.push(file.name);
                    }
                }
                
                if (invalidFiles.length > 0) {
                    showStatus('지원하지 않는 파일 형식: ' + invalidFiles.join(', '), 'error');
                    return;
                }
                
                // Check file sizes
                const maxSize = 10 * 1024 * 1024; // 10MB
                const oversizedFiles = [];
                
                for (let file of files) {
                    if (file.size > maxSize) {
                        oversizedFiles.push(file.name);
                    }
                }
                
                if (oversizedFiles.length > 0) {
                    showStatus('파일 크기가 10MB를 초과: ' + oversizedFiles.join(', '), 'error');
                    return;
                }
                
                showStatus('파일 업로드 중...', 'loading');
                debugLog('Uploading ' + files.length + ' file(s)');
                
                if (files.length === 1) {
                    uploadSingleFile(files[0]);
                } else {
                    uploadMultipleFiles(files);
                }
            }
            
            function uploadSingleFile(file) {
                const formData = new FormData();
                formData.append('file', file);
                
                fetch('/api/v1/upload-document/', {
                    method: 'POST',
                    body: formData
                })
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                    }
                    return response.json();
                })
                .then(function(result) {
                    debugLog('Single file upload result:', result);
                    
                    if (result.status === 'success') {
                        showStatus('파일 업로드 성공!', 'success');
                        
                        // Display upload result
                        const uploadQuery = '문서 업로드: ' + result.filename;
                        const uploadResponse = '문서가 성공적으로 업로드되고 분석되었습니다!\\n\\n' +
                                             '파일명: ' + result.filename + '\\n' +
                                             '문서 ID: ' + result.document_id + '\\n' +
                                             '단어 수: ' + result.metadata.word_count + '개\\n' +
                                             '문자 수: ' + result.metadata.char_count + '개\\n' +
                                             '줄 수: ' + result.metadata.line_count + '개\\n' +
                                             '파일 형식: ' + result.metadata.file_type + '\\n\\n' +
                                             result.message + '\\n\\n' +
                                             '이제 이 문서에 대해 질문할 수 있습니다!';
                        
                        parseAndDisplayResponse(
                            uploadQuery,
                            uploadResponse,
                            'upload_' + Date.now(),
                            new Date().toISOString(),
                            false
                        );
                        
                        // Clear file input
                        document.getElementById('fileInput').value = '';
                    } else {
                        showStatus('업로드 실패: ' + (result.message || 'Unknown error'), 'error');
                    }
                })
                .catch(function(error) {
                    debugLog('File upload error:', error);
                    showStatus('업로드 오류: ' + error.message, 'error');
                });
            }
            
            function uploadMultipleFiles(files) {
                const formData = new FormData();
                for (let file of files) {
                    formData.append('files', file);
                }
                
                fetch('/api/v1/upload-multiple-documents/', {
                    method: 'POST',
                    body: formData
                })
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                    }
                    return response.json();
                })
                .then(function(result) {
                    debugLog('Multiple files upload result:', result);
                    
                    showStatus('다중 파일 업로드 완료!', 'success');
                    
                    // Display detailed results
                    let uploadResponse = '다중 문서 업로드 결과:\\n\\n' +
                                       result.message + '\\n\\n';
                    
                    // Show successful uploads
                    const successFiles = result.results.filter(r => r.status === 'success');
                    if (successFiles.length > 0) {
                        uploadResponse += '✅ 성공한 파일들:\\n';
                        successFiles.forEach(function(file) {
                            uploadResponse += '• ' + file.filename + 
                                           ' (단어: ' + file.metadata.word_count + '개)\\n';
                        });
                        uploadResponse += '\\n';
                    }
                    
                    // Show failed uploads
                    const errorFiles = result.results.filter(r => r.status === 'error');
                    if (errorFiles.length > 0) {
                        uploadResponse += '❌ 실패한 파일들:\\n';
                        errorFiles.forEach(function(file) {
                            uploadResponse += '• ' + file.filename + ': ' + file.error + '\\n';
                        });
                        uploadResponse += '\\n';
                    }
                    
                    uploadResponse += '이제 업로드된 문서들에 대해 질문할 수 있습니다!';
                    
                    parseAndDisplayResponse(
                        '다중 문서 업로드 (' + files.length + '개 파일)',
                        uploadResponse,
                        'multi_upload_' + Date.now(),
                        result.timestamp,
                        false
                    );
                    
                    // Clear file input
                    document.getElementById('fileInput').value = '';
                })
                .catch(function(error) {
                    debugLog('Multiple files upload error:', error);
                    showStatus('다중 업로드 오류: ' + error.message, 'error');
                });
            }
            
            function analyzeDocument() {
                debugLog('Analyze document button clicked');
                const fileInput = document.getElementById('fileInput');
                const files = fileInput.files;
                
                if (files.length === 0) {
                    showStatus('분석할 파일을 선택해주세요', 'error');
                    return;
                }
                
                if (files.length > 1) {
                    showStatus('문서 분석은 한 번에 하나의 파일만 가능합니다', 'error');
                    return;
                }
                
                const file = files[0];
                
                // Validate file type
                const allowedTypes = ['.pdf', '.docx', '.txt', '.md'];
                const extension = '.' + file.name.split('.').pop().toLowerCase();
                
                if (!allowedTypes.includes(extension)) {
                    showStatus('지원하지 않는 파일 형식: ' + extension, 'error');
                    return;
                }
                
                // Check file size
                const maxSize = 10 * 1024 * 1024; // 10MB
                if (file.size > maxSize) {
                    showStatus('파일 크기가 10MB를 초과합니다', 'error');
                    return;
                }
                
                showStatus('문서 분석 중...', 'loading');
                debugLog('Analyzing document: ' + file.name);
                
                const formData = new FormData();
                formData.append('file', file);
                formData.append('question', '이 문서의 내용을 분석하고 주요 내용, 핵심 포인트, 그리고 중요한 인사이트를 요약해주세요.');
                
                fetch('/api/v1/analyze-document/', {
                    method: 'POST',
                    body: formData
                })
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                    }
                    return response.json();
                })
                .then(function(result) {
                    debugLog('Document analysis result:', result);
                    
                    if (result.status === 'success') {
                        showStatus('문서 분석 완료!', 'success');
                        
                        // Display analysis result
                        const analysisQuery = '문서 분석: ' + result.filename;
                        
                        parseAndDisplayResponse(
                            analysisQuery,
                            result.analysis,
                            result.document_id,
                            result.timestamp,
                            false
                        );
                        
                        // Clear file input
                        document.getElementById('fileInput').value = '';
                    } else {
                        showStatus('분석 실패: ' + (result.message || 'Unknown error'), 'error');
                    }
                })
                .catch(function(error) {
                    debugLog('Document analysis error:', error);
                    showStatus('분석 오류: ' + error.message, 'error');
                });
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
                        
                        // Create structured display for URL addition
                        const urlQuery = 'Add URL to knowledge base: ' + result.url;
                        const urlResponse = 'Successfully added web content to knowledge base!\\n\\n' +
                                          'Title: ' + result.title + '\\n' +
                                          'Word Count: ' + result.word_count + ' words\\n\\n' +
                                          result.message + '\\n\\n' +
                                          'You can now ask questions about this content!';
                        
                        parseAndDisplayResponse(
                            urlQuery,
                            urlResponse,
                            'url_add_' + Date.now(),
                            new Date().toISOString(),
                            false
                        );
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
                        
                        // Create a structured query for URL analysis
                        const urlQuery = 'Analyze the content from: ' + result.url + ' (Title: ' + result.title + ')';
                        
                        parseAndDisplayResponse(
                            urlQuery,
                            result.analysis,
                            'url_analysis_' + Date.now(),
                            result.timestamp,
                            false
                        );
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
                const question = document.getElementById('queryInput').value.trim();
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
                    
                    if (result.answer) {
                        parseAndDisplayResponse(
                            question,
                            result.answer,
                            result.session_id,
                            new Date().toISOString(),
                            false
                        );
                        showStatus('Query completed successfully!', 'success');
                    } else {
                        showStatus('Error: ' + (result.message || 'No answer received'), 'error');
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
                document.getElementById('queryInput').value = '';
                document.getElementById('responseArea').textContent = 'New session started. You can now ask questions!';
                showStatus('Session cleared', 'success');
            }
            
            // Initialize when page loads
            function initRagDashboard() {
                debugLog('Initializing RAG Dashboard...');
                
                // Setup file upload functionality
                setupFileUpload();
                
                // Set up form submission
                const form = document.getElementById('queryForm');
                if (form) {
                    form.onsubmit = function(e) {
                        e.preventDefault();
                        submitQuery();
                    };
                }
                
                // Set up enter key submission
                const queryInput = document.getElementById('queryInput');
                if (queryInput) {
                    queryInput.onkeypress = function(e) {
                        if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            submitQuery();
                        }
                    };
                }
                
                // Set up web analysis buttons
                const addUrlBtn = document.getElementById('addUrlBtn');
                if (addUrlBtn) {
                    addUrlBtn.onclick = function(e) {
                        e.preventDefault();
                        addUrl();
                    };
                }
                
                const analyzeUrlBtn = document.getElementById('analyzeUrlBtn');
                if (analyzeUrlBtn) {
                    analyzeUrlBtn.onclick = function(e) {
                        e.preventDefault();
                        analyzeUrl();
                    };
                }
                
                // Set up clear session button
                const clearBtn = document.getElementById('clearBtn');
                if (clearBtn) {
                    clearBtn.onclick = function(e) {
                        e.preventDefault();
                        clearSession();
                    };
                }
                
                debugLog('RAG Dashboard initialized successfully');
            }
            
            // Run initialization
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initRagDashboard);
            } else {
                initRagDashboard();
            }
            
            console.log('Script finished loading');

            function parseAndDisplayResponse(query, response, sessionId, timestamp, isStreaming = false) {
                const responseArea = document.getElementById('responseArea');
                
                // Parse the response to extract think section
                const thinkMatch = response.match(/<think>([\s\S]*?)<\/think>/);
                const thinkContent = thinkMatch ? thinkMatch[1].trim() : '';
                const actualResponse = response.replace(/<think>[\s\S]*?<\/think>/, '').trim();
                
                // Create structured HTML
                const structuredHtml = `
                    <div class="response-container">
                        <div class="response-section query-section">
                            <div class="response-section-header">📝 Query</div>
                            <div class="response-section-content">${query}</div>
                        </div>
                        
                        ${thinkContent ? `
                        <div class="response-section think-section">
                            <div class="response-section-header" onclick="toggleThinkSection()">
                                🤔 Thinking Process
                                <span class="think-toggle">▼</span>
                            </div>
                            <div class="response-section-content think-content" id="thinkContent">
                                ${thinkContent}
                            </div>
                        </div>
                        ` : ''}
                        
                        <div class="response-section response-section">
                            <div class="response-section-header">💡 Response</div>
                            <div class="response-section-content" id="actualResponseContent">
                                ${actualResponse}${isStreaming ? '<span class="streaming-cursor">▋</span>' : ''}
                            </div>
                        </div>
                        
                        <div class="response-section metadata-section">
                            <div class="response-section-header">ℹ️ Metadata</div>
                            <div class="response-section-content metadata-content">
                                <div class="metadata-item">
                                    <span class="metadata-label">Session ID:</span> ${sessionId}
                                </div>
                                <div class="metadata-item">
                                    <span class="metadata-label">Timestamp:</span> ${timestamp}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                responseArea.innerHTML = structuredHtml;
                
                // Add streaming cursor animation if needed
                if (isStreaming) {
                    responseArea.classList.add('streaming');
                } else {
                    responseArea.classList.remove('streaming');
                }
            }
            
            function toggleThinkSection() {
                const thinkContent = document.getElementById('thinkContent');
                const thinkToggle = document.querySelector('.think-toggle');
                
                if (thinkContent && thinkToggle) {
                    thinkContent.classList.toggle('collapsed');
                    thinkToggle.classList.toggle('collapsed');
                }
            }
            
            function updateStreamingResponse(content) {
                const actualResponseContent = document.getElementById('actualResponseContent');
                if (actualResponseContent) {
                    // Remove existing streaming cursor
                    const existingCursor = actualResponseContent.querySelector('.streaming-cursor');
                    if (existingCursor) {
                        existingCursor.remove();
                    }
                    
                    // Add new content and cursor
                    actualResponseContent.innerHTML = content + '<span class="streaming-cursor">▋</span>';
                    
                    // Scroll to bottom
                    actualResponseContent.scrollTop = actualResponseContent.scrollHeight;
                }
            }

            // File upload drag and drop functionality
            function setupFileUpload() {
                const uploadArea = document.getElementById('uploadArea');
                const fileInput = document.getElementById('fileInput');
                const fileList = document.getElementById('fileList');
                const selectedFiles = document.getElementById('selectedFiles');
                
                // Click to select files
                uploadArea.onclick = function() {
                    fileInput.click();
                };
                
                // File input change event
                fileInput.onchange = function() {
                    updateFileList();
                };
                
                // Drag and drop events
                uploadArea.ondragover = function(e) {
                    e.preventDefault();
                    uploadArea.classList.add('drag-over');
                };
                
                uploadArea.ondragleave = function(e) {
                    e.preventDefault();
                    uploadArea.classList.remove('drag-over');
                };
                
                uploadArea.ondrop = function(e) {
                    e.preventDefault();
                    uploadArea.classList.remove('drag-over');
                    
                    const files = e.dataTransfer.files;
                    fileInput.files = files;
                    updateFileList();
                };
            }
            
            function updateFileList() {
                const fileInput = document.getElementById('fileInput');
                const fileList = document.getElementById('fileList');
                const selectedFiles = document.getElementById('selectedFiles');
                
                if (fileInput.files.length === 0) {
                    fileList.style.display = 'none';
                    return;
                }
                
                fileList.style.display = 'block';
                selectedFiles.innerHTML = '';
                
                for (let i = 0; i < fileInput.files.length; i++) {
                    const file = fileInput.files[i];
                    const li = document.createElement('li');
                    li.className = 'file-item';
                    
                    const fileSize = formatFileSize(file.size);
                    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
                    
                    // Check if file type is supported
                    const allowedTypes = ['.pdf', '.docx', '.txt', '.md'];
                    const isSupported = allowedTypes.includes(fileExtension);
                    const isOversized = file.size > 10 * 1024 * 1024; // 10MB
                    
                    let statusIcon = '✅';
                    let statusClass = 'file-valid';
                    
                    if (!isSupported) {
                        statusIcon = '❌';
                        statusClass = 'file-invalid';
                    } else if (isOversized) {
                        statusIcon = '⚠️';
                        statusClass = 'file-warning';
                    }
                    
                    li.innerHTML = statusIcon + ' <strong>' + file.name + '</strong> (' + fileSize + ')';
                    li.className += ' ' + statusClass;
                    
                    selectedFiles.appendChild(li);
                }
            }
            
            function formatFileSize(bytes) {
                if (bytes === 0) return '0 Bytes';
                const k = 1024;
                const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
            }
            
            function clearFiles() {
                const fileInput = document.getElementById('fileInput');
                const fileList = document.getElementById('fileList');
                
                fileInput.value = '';
                fileList.style.display = 'none';
                
                showStatus('파일 선택이 해제되었습니다', 'info');
            }
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
