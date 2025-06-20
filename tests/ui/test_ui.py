import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add ui directory to path
ui_dir = Path(__file__).parent.parent.parent / "ui"
sys.path.insert(0, str(ui_dir))

# Mock agno modules before importing
class MockAgent:
    def __init__(self, **kwargs):
        self.backend_url = kwargs.get('backend_url')
        self.name = kwargs.get('name')
        self.model = kwargs.get('model')
        
    def run(self, query, **kwargs):
        # This will be overridden by BackendRAGAgent
        pass

class MockAGUIApp:
    def __init__(self, **kwargs):
        self.agent = kwargs.get('agent')
        self.name = kwargs.get('name', 'Enterprise RAG System')
        self.app_id = kwargs.get('app_id', 'enterprise_rag_system')
        
    def get_app(self):
        return MagicMock()
        
    def serve(self, **kwargs):
        pass

class MockOpenAIChat:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.api_key = kwargs.get('api_key')

sys.modules['agno'] = MagicMock()
sys.modules['agno.agent'] = MagicMock()
sys.modules['agno.agent'].Agent = MockAgent
sys.modules['agno.app'] = MagicMock()
sys.modules['agno.app.agui'] = MagicMock()
sys.modules['agno.app.agui.app'] = MagicMock()
sys.modules['agno.app.agui.app'].AGUIApp = MockAGUIApp
sys.modules['agno.models'] = MagicMock()
sys.modules['agno.models.openai'] = MagicMock()
sys.modules['agno.models.openai'].OpenAIChat = MockOpenAIChat

def test_ui_imports():
    """Test that UI modules can be imported correctly."""
    try:
        import config
        import main
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import UI modules: {e}")

def test_config_values():
    """Test UI configuration values."""
    import config
    assert hasattr(config, 'BACKEND_URL')
    assert hasattr(config, 'AGENT_MODEL')
    assert hasattr(config, 'OPENAI_API_KEY')

@patch('main.requests.post')
def test_backend_agent_query(mock_post):
    """Test the BackendRAGAgent query functionality."""
    # Mock successful backend response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "status": "success",
        "response": "Test response",
        "session_id": "test_session",
        "sources": [{"uri": "test_source.pdf"}],
        "reasoning_steps": ["Step 1", "Step 2"]
    }
    mock_post.return_value = mock_response
    
    # Import and test the agent
    from main import BackendRAGAgent
    
    agent = BackendRAGAgent(
        backend_url="http://test:8000",
        name="Test Agent",
        model=MockOpenAIChat(id="gpt-4o", api_key="test-key")
    )
    
    response = agent.run("Test query")
    
    assert "Test response" in response.content
    assert "📚 Sources:" in response.content
    assert "🧠 Reasoning Steps:" in response.content

@patch('main.requests.post')
def test_backend_agent_error_handling(mock_post):
    """Test error handling in BackendRAGAgent."""
    # Mock failed backend response with RequestException
    import requests
    mock_post.side_effect = requests.RequestException("Connection failed")
    
    from main import BackendRAGAgent
    
    agent = BackendRAGAgent(
        backend_url="http://test:8000",
        name="Test Agent",
        model=MockOpenAIChat(id="gpt-4o", api_key="test-key")
    )
    
    response = agent.run("Test query")
    
    assert "❌ **Backend Error:**" in response.content
    assert "Connection failed" in response.content

def test_backend_agent_advanced_reasoning():
    """Test advanced reasoning trigger in BackendRAGAgent."""
    with patch('main.requests.post') as mock_post:
        # Mock successful backend response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "status": "success",
            "response": "Advanced reasoning response",
            "session_id": "test_session",
            "sources": [],
            "reasoning_steps": []
        }
        mock_post.return_value = mock_response
        
        from main import BackendRAGAgent
        
        agent = BackendRAGAgent(
            backend_url="http://test:8000",
            name="Test Agent",
            model=MockOpenAIChat(id="gpt-4o", api_key="test-key")
        )
        
        # Test query with reasoning keyword
        agent.run("analyze this document")
        
        # Verify the API call was made with use_advanced_reasoning=True
        args, kwargs = mock_post.call_args
        payload = kwargs['json']
        assert payload['use_advanced_reasoning'] is True

def test_agui_app_creation():
    """Test that AGUIApp can be created successfully."""
    try:
        from main import agui_app
        assert agui_app is not None
        assert agui_app.name == "Enterprise RAG System"
        assert agui_app.app_id == "enterprise_rag_system"
    except Exception as e:
        pytest.fail(f"Failed to create AGUIApp: {e}")

def test_fastapi_app_creation():
    """Test that FastAPI app can be created."""
    try:
        from main import app
        assert app is not None
    except Exception as e:
        pytest.fail(f"Failed to create FastAPI app: {e}")

def test_upload_document_endpoint():
    """Test that the upload document endpoint function exists and is properly defined."""
    # Test if the function is defined in the module by checking the source
    import main
    import inspect
    
    # Get the source code to verify the function is defined
    source = inspect.getsource(main)
    
    # Verify the function is defined in the source
    assert "async def upload_document_endpoint" in source
    assert "file: bytes" in source  
    assert "filename: str" in source
    assert "content_type: str" in source
    
    # Verify it has the expected decorator
    assert "@app.post(\"/upload-document/\")" in source 