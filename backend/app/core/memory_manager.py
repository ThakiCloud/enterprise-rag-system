try:
    from agno.memory.v2.memory import Memory
    from agno.memory.v2.db.sqlite import SqliteMemoryDb
    from agno.memory.v2.schema import UserMemory as AgnoUserMemory
    from agno.models.openai import OpenAIChat
    from agno.models.anthropic import AnthropicChat
    from agno.models.google import GoogleChat
    AGNO_AVAILABLE = True
except ImportError:
    AGNO_AVAILABLE = False
    # Create dummy classes for when agno is not available
    class Memory:
        def __init__(self, *args, **kwargs):
            pass
    
    class SqliteMemoryDb:
        def __init__(self, *args, **kwargs):
            pass
    
    class AgnoUserMemory:
        def __init__(self, *args, **kwargs):
            pass

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from pathlib import Path

from .config import (
    MODEL_PROVIDER, OPENAI_API_KEY, OPENAI_MODEL_NAME,
    ANTHROPIC_API_KEY, ANTHROPIC_MODEL_NAME,
    GOOGLE_API_KEY, GOOGLE_MODEL_NAME,
    DB_FILE, ENABLE_MEMORY_SYSTEM
)
from ..schemas.session import UserMemory

logger = logging.getLogger(__name__)

class SessionMemoryManager:
    """Session-based memory manager using Agno's memory system"""
    
    def __init__(self):
        self.agno_available = AGNO_AVAILABLE and ENABLE_MEMORY_SYSTEM
        
        if not self.agno_available:
            logger.warning("Agno library not available or memory system disabled. Memory features will be limited.")
            self.memory = None
            self.memory_db = None
            return
            
        try:
            self.memory_db_path = Path(DB_FILE).parent / "session_memories.db"
            self.memory_db = SqliteMemoryDb(
                table_name="session_memories",
                db_file=str(self.memory_db_path)
            )
            
            self.memory = Memory(
                model=self._get_memory_model(),
                db=self.memory_db
            )
        except Exception as e:
            logger.error(f"Failed to initialize memory system: {e}")
            self.agno_available = False
            self.memory = None
            self.memory_db = None
        
    def _get_memory_model(self):
        """Get the model for memory processing"""
        if not self.agno_available:
            return None
            
        try:
            if MODEL_PROVIDER == "openai" and OPENAI_API_KEY:
                return OpenAIChat(id=OPENAI_MODEL_NAME, api_key=OPENAI_API_KEY)
            elif MODEL_PROVIDER == "anthropic" and ANTHROPIC_API_KEY:
                return AnthropicChat(id=ANTHROPIC_MODEL_NAME, api_key=ANTHROPIC_API_KEY)
            elif MODEL_PROVIDER == "google" and GOOGLE_API_KEY:
                return GoogleChat(id=GOOGLE_MODEL_NAME, api_key=GOOGLE_API_KEY)
            else:
                # Fallback to a simple OpenAI model
                if OPENAI_API_KEY:
                    return OpenAIChat(id="gpt-3.5-turbo", api_key=OPENAI_API_KEY)
                return None
        except Exception as e:
            logger.warning(f"Failed to initialize memory model: {e}")
            return None
    
    def add_user_memory(self, user_id: str, memory_content: str, topics: List[str] = None) -> str:
        """Add a new memory for a user"""
        if not self.agno_available or not self.memory:
            logger.warning("Memory system not available")
            return f"fallback_memory_{datetime.now().timestamp()}"
            
        try:
            if topics is None:
                topics = []
                
            user_memory = AgnoUserMemory(
                memory=memory_content,
                topics=topics
            )
            
            memory_id = self.memory.add_user_memory(
                memory=user_memory,
                user_id=user_id
            )
            
            logger.info(f"Added memory {memory_id} for user {user_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to add memory for user {user_id}: {e}")
            return f"fallback_memory_{datetime.now().timestamp()}"
    
    def get_user_memories(self, user_id: str, limit: int = 10) -> List[UserMemory]:
        """Get memories for a user"""
        if not self.agno_available or not self.memory:
            logger.warning("Memory system not available")
            return []
            
        try:
            agno_memories = self.memory.get_user_memories(user_id=user_id)
            
            # Convert Agno memories to our schema
            memories = []
            for agno_mem in agno_memories[-limit:]:  # Get latest memories
                memory = UserMemory(
                    memory_id=agno_mem.id,
                    memory=agno_mem.memory,
                    topics=agno_mem.topics or [],
                    created_at=agno_mem.created_at.isoformat() if hasattr(agno_mem, 'created_at') else datetime.now().isoformat(),
                    last_updated=agno_mem.last_updated.isoformat() if hasattr(agno_mem, 'last_updated') else datetime.now().isoformat(),
                    user_id=user_id
                )
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get memories for user {user_id}: {e}")
            return []
    
    def search_user_memories(self, user_id: str, query: str, limit: int = 5) -> List[UserMemory]:
        """Search user memories based on query"""
        if not self.agno_available or not self.memory:
            logger.warning("Memory system not available")
            return []
            
        try:
            if not self.memory.model:
                # Fallback to simple get if no model available
                return self.get_user_memories(user_id, limit)
                
            agno_memories = self.memory.search_user_memories(
                user_id=user_id,
                query=query,
                limit=limit,
                retrieval_method="agentic"
            )
            
            # Convert to our schema
            memories = []
            for agno_mem in agno_memories:
                memory = UserMemory(
                    memory_id=agno_mem.id,
                    memory=agno_mem.memory,
                    topics=agno_mem.topics or [],
                    created_at=agno_mem.created_at.isoformat() if hasattr(agno_mem, 'created_at') else datetime.now().isoformat(),
                    last_updated=agno_mem.last_updated.isoformat() if hasattr(agno_mem, 'last_updated') else datetime.now().isoformat(),
                    user_id=user_id
                )
                memories.append(memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to search memories for user {user_id}: {e}")
            return []
    
    def create_memories_from_conversation(self, user_id: str, messages: List[Dict[str, str]]) -> List[str]:
        """Create memories from conversation messages"""
        if not self.agno_available or not self.memory:
            logger.warning("Memory system not available")
            return []
            
        try:
            if not self.memory.model:
                logger.warning("Memory model not available, skipping memory creation")
                return []
                
            from agno.models.message import Message
            
            # Convert messages to Agno format
            agno_messages = []
            for msg in messages:
                agno_messages.append(
                    Message(role=msg.get("role", "user"), content=msg.get("content", ""))
                )
            
            # Create memories from messages
            self.memory.create_user_memories(
                messages=agno_messages,
                user_id=user_id
            )
            
            # Get the newly created memories
            memories = self.get_user_memories(user_id, limit=5)
            return [mem.memory_id for mem in memories if mem.memory_id]
            
        except Exception as e:
            logger.error(f"Failed to create memories from conversation for user {user_id}: {e}")
            return []
    
    def delete_user_memory(self, user_id: str, memory_id: str) -> bool:
        """Delete a specific memory"""
        if not self.agno_available or not self.memory:
            logger.warning("Memory system not available")
            return False
            
        try:
            self.memory.delete_user_memory(user_id=user_id, memory_id=memory_id)
            logger.info(f"Deleted memory {memory_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id} for user {user_id}: {e}")
            return False
    
    def clear_user_memories(self, user_id: str) -> bool:
        """Clear all memories for a user"""
        if not self.agno_available or not self.memory:
            logger.warning("Memory system not available")
            return False
            
        try:
            memories = self.get_user_memories(user_id)
            for memory in memories:
                if memory.memory_id:
                    self.delete_user_memory(user_id, memory.memory_id)
            
            logger.info(f"Cleared all memories for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear memories for user {user_id}: {e}")
            return False
    
    def get_memory_count(self, user_id: str) -> int:
        """Get the count of memories for a user"""
        try:
            memories = self.get_user_memories(user_id)
            return len(memories)
        except Exception as e:
            logger.error(f"Failed to get memory count for user {user_id}: {e}")
            return 0
    
    def get_relevant_memories_for_query(self, user_id: str, query: str, limit: int = 3) -> List[UserMemory]:
        """Get memories relevant to a specific query"""
        try:
            return self.search_user_memories(user_id, query, limit)
        except Exception as e:
            logger.error(f"Failed to get relevant memories for user {user_id}: {e}")
            return []

# Global instance
session_memory_manager = SessionMemoryManager() 