import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add ui directory to path
ui_dir = Path(__file__).parent.parent.parent / "ui"
sys.path.insert(0, str(ui_dir))

def test_ui_imports():
    """Test that UI modules can be imported correctly."""
    try:
        import config
        import main
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import UI modules: {e}")

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
    from agno.models.openai import OpenAIChat
    
    agent = BackendRAGAgent(
        backend_url="http://test:8000",
        name="Test Agent",
        model=OpenAIChat(id="gpt-4o", api_key="test-key")
    )
    
    response = agent.run("Test query")
    
    assert "Test response" in response.content
    assert "📚 Sources:" in response.content
    assert "🧠 Reasoning Steps:" in response.content

def test_agui_app_creation():
    """Test that AGUIApp can be created successfully."""
    try:
        from main import agui_app
        assert agui_app is not None
        assert agui_app.name == "Enterprise RAG System"
        assert agui_app.app_id == "enterprise_rag_system"
    except Exception as e:
        pytest.fail(f"Failed to create AGUIApp: {e}") 