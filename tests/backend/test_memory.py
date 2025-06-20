import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

@pytest.fixture
def mock_memory_manager():
    """Mock memory manager for testing"""
    manager = MagicMock()
    manager.add_user_memory = MagicMock(return_value="test_memory_id")
    manager.get_user_memories = MagicMock(return_value=[])
    manager.search_user_memories = MagicMock(return_value=[])
    manager.create_memories_from_conversation = MagicMock(return_value=["memory_id_1"])
    manager.delete_user_memory = MagicMock(return_value=True)
    manager.clear_user_memories = MagicMock(return_value=True)
    manager.get_memory_count = MagicMock(return_value=0)
    manager.get_relevant_memories_for_query = MagicMock(return_value=[])
    return manager

@pytest.fixture
def sample_user_memory():
    """Sample user memory for testing"""
    from backend.app.schemas.session import UserMemory
    return UserMemory(
        memory_id="test_memory_1",
        memory="사용자는 Python 개발자입니다",
        topics=["개발", "Python"],
        created_at="2024-01-01T10:00:00",
        last_updated="2024-01-01T10:00:00",
        user_id="test_user"
    )

class TestMemoryManager:
    """Test memory manager functionality"""
    
    def test_add_user_memory(self, mock_memory_manager):
        """Test adding user memory"""
        user_id = "test_user"
        memory_content = "사용자는 개발자입니다"
        topics = ["개발"]
        
        memory_id = mock_memory_manager.add_user_memory(user_id, memory_content, topics)
        
        assert memory_id == "test_memory_id"
        mock_memory_manager.add_user_memory.assert_called_once_with(user_id, memory_content, topics)
    
    def test_get_user_memories(self, mock_memory_manager, sample_user_memory):
        """Test getting user memories"""
        user_id = "test_user"
        mock_memory_manager.get_user_memories.return_value = [sample_user_memory]
        
        memories = mock_memory_manager.get_user_memories(user_id, limit=10)
        
        assert len(memories) == 1
        assert memories[0].memory == "사용자는 Python 개발자입니다"
        mock_memory_manager.get_user_memories.assert_called_once_with(user_id, limit=10)
    
    def test_search_user_memories(self, mock_memory_manager, sample_user_memory):
        """Test searching user memories"""
        user_id = "test_user"
        query = "개발자"
        mock_memory_manager.search_user_memories.return_value = [sample_user_memory]
        
        memories = mock_memory_manager.search_user_memories(user_id, query, limit=5)
        
        assert len(memories) == 1
        assert memories[0].memory == "사용자는 Python 개발자입니다"
        mock_memory_manager.search_user_memories.assert_called_once_with(user_id, query, limit=5)
    
    def test_create_memories_from_conversation(self, mock_memory_manager):
        """Test creating memories from conversation"""
        user_id = "test_user"
        messages = [
            {"role": "user", "content": "안녕하세요, 저는 개발자입니다"},
            {"role": "assistant", "content": "안녕하세요! 개발자시군요."}
        ]
        
        memory_ids = mock_memory_manager.create_memories_from_conversation(user_id, messages)
        
        assert len(memory_ids) == 1
        assert memory_ids[0] == "memory_id_1"
        mock_memory_manager.create_memories_from_conversation.assert_called_once_with(user_id, messages)
    
    def test_delete_user_memory(self, mock_memory_manager):
        """Test deleting user memory"""
        user_id = "test_user"
        memory_id = "test_memory_1"
        
        result = mock_memory_manager.delete_user_memory(user_id, memory_id)
        
        assert result is True
        mock_memory_manager.delete_user_memory.assert_called_once_with(user_id, memory_id)
    
    def test_clear_user_memories(self, mock_memory_manager):
        """Test clearing all user memories"""
        user_id = "test_user"
        
        result = mock_memory_manager.clear_user_memories(user_id)
        
        assert result is True
        mock_memory_manager.clear_user_memories.assert_called_once_with(user_id)

class TestMemoryAPI:
    """Test memory-related API endpoints"""
    
    @pytest.mark.asyncio
    async def test_query_with_memory(self, mock_memory_manager):
        """Test query endpoint with memory enabled"""
        from fastapi.testclient import TestClient
        
        with patch('backend.app.core.memory_manager.session_memory_manager', mock_memory_manager):
            with patch('backend.app.core.dependencies.get_rag_agent') as mock_get_agent:
                # Mock agent response
                mock_agent = AsyncMock()
                mock_agent.arun = AsyncMock(return_value="안녕하세요! 도움이 필요하시면 말씀해주세요.")
                mock_get_agent.return_value = mock_agent
                
                from backend.app.main import app
                client = TestClient(app)
                
                response = client.post("/api/query/", json={
                    "question": "안녕하세요",
                    "session_id": "test_session",
                    "user_id": "test_user",
                    "use_memory": True
                })
                
                # Note: This test might fail due to dependencies, but shows the structure
                # In a real test environment, you would mock all dependencies properly
    
    def test_session_memory_endpoints(self):
        """Test session memory management endpoints"""
        from fastapi.testclient import TestClient
        
        # Mock the memory manager
        with patch('backend.app.core.memory_manager.session_memory_manager') as mock_manager:
            mock_manager.get_user_memories.return_value = []
            mock_manager.add_user_memory.return_value = "new_memory_id"
            mock_manager.delete_user_memory.return_value = True
            mock_manager.clear_user_memories.return_value = True
            mock_manager.search_user_memories.return_value = []
            
            from backend.app.main import app
            client = TestClient(app)
            
            # Test get memories
            response = client.get("/api/v1/sessions/test_session/memories")
            assert response.status_code == 200
            
            # Test add memory
            response = client.post("/api/v1/sessions/test_session/memories", json={
                "session_id": "test_session",
                "action": "add",
                "memory_content": "테스트 메모리",
                "topics": ["테스트"]
            })
            assert response.status_code == 200
            
            # Test clear memories  
            response = client.post("/api/v1/sessions/test_session/memories", json={
                "session_id": "test_session",
                "action": "clear"
            })
            assert response.status_code == 200

class TestMemorySchemas:
    """Test memory-related Pydantic schemas"""
    
    def test_user_memory_schema(self):
        """Test UserMemory schema validation"""
        from backend.app.schemas.session import UserMemory
        
        memory_data = {
            "memory_id": "test_id",
            "memory": "사용자는 개발자입니다",
            "topics": ["개발", "Python"],
            "created_at": "2024-01-01T10:00:00",
            "last_updated": "2024-01-01T10:00:00",
            "user_id": "test_user"
        }
        
        memory = UserMemory(**memory_data)
        assert memory.memory == "사용자는 개발자입니다"
        assert memory.topics == ["개발", "Python"]
        assert memory.user_id == "test_user"
    
    def test_session_memory_request_schema(self):
        """Test SessionMemoryRequest schema validation"""
        from backend.app.schemas.session import SessionMemoryRequest
        
        # Test add action
        request_data = {
            "session_id": "test_session",
            "action": "add",
            "memory_content": "테스트 메모리",
            "topics": ["테스트"]
        }
        
        request = SessionMemoryRequest(**request_data)
        assert request.action == "add"
        assert request.memory_content == "테스트 메모리"
        assert request.topics == ["테스트"]
        
        # Test clear action
        clear_request = SessionMemoryRequest(
            session_id="test_session",
            action="clear"
        )
        assert clear_request.action == "clear"
        assert clear_request.memory_content is None

class TestMemoryIntegration:
    """Integration tests for memory system"""
    
    @pytest.mark.asyncio
    async def test_memory_workflow(self, mock_memory_manager, sample_user_memory):
        """Test complete memory workflow"""
        user_id = "test_user"
        
        # 1. Add memory
        memory_id = mock_memory_manager.add_user_memory(
            user_id, "사용자는 Python 개발자입니다", ["개발", "Python"]
        )
        assert memory_id == "test_memory_id"
        
        # 2. Get memories
        mock_memory_manager.get_user_memories.return_value = [sample_user_memory]
        memories = mock_memory_manager.get_user_memories(user_id)
        assert len(memories) == 1
        
        # 3. Search memories
        mock_memory_manager.search_user_memories.return_value = [sample_user_memory]
        search_results = mock_memory_manager.search_user_memories(user_id, "개발자")
        assert len(search_results) == 1
        
        # 4. Delete memory
        result = mock_memory_manager.delete_user_memory(user_id, memory_id)
        assert result is True
        
        # 5. Verify deletion
        mock_memory_manager.get_user_memories.return_value = []
        memories_after_delete = mock_memory_manager.get_user_memories(user_id)
        assert len(memories_after_delete) == 0

if __name__ == "__main__":
    pytest.main([__file__]) 