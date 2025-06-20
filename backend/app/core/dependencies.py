from fastapi import Depends
import os
from typing import Optional, TYPE_CHECKING
import logging
import asyncio
from openai import AsyncOpenAI
from unittest.mock import MagicMock

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Mock knowledge base for testing
class MockKnowledgeBase(MagicMock):
    def __init__(self):
        super().__init__()
        self.documents = []
        
    def add_document(self, content: str, metadata: Optional[dict] = None):
        return "mock_doc_id"
    
    def search(self, query: str, limit: int = 5):
        return []

# Simple knowledge base implementation
class SimpleKnowledgeBase:
    def __init__(self):
        self.documents = []
        
    def add_document(self, content: str, metadata: Optional[dict] = None):
        self.documents.append({
            "content": content,
            "metadata": metadata or {}
        })
    
    def search(self, query: str, limit: int = 5):
        # Simple text-based search
        results = []
        for i, doc in enumerate(self.documents):
            if query.lower() in doc["content"].lower():
                results.append({
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "score": 0.8  # dummy score
                })
        return results[:limit]

# Mock agent for testing
class MockAgent(MagicMock):
    def __init__(self, name: str, knowledge_base=None):
        super().__init__()
        self.name = name
        self.knowledge_base = knowledge_base
        self.content = "Mock response"
        self.sources = []
        
    async def arun(self, query: str, user_id: str = None, session_id: str = None):
        return "Mock response from agent"
    
    def run(self, query: str):
        mock_response = MagicMock()
        mock_response.content = "Mock response from agent"
        mock_response.sources = []
        return mock_response

# Simple agent implementation
class SimpleAgent:
    def __init__(self, name: str, knowledge_base: SimpleKnowledgeBase):
        self.name = name
        self.knowledge_base = knowledge_base
        
    async def arun(self, query: str, user_id: str = None, session_id: str = None):
        # Simple implementation that searches knowledge base
        results = self.knowledge_base.search(query)
        if results:
            context = "\n".join([r["content"] for r in results])
            return f"사용 가능한 문서를 바탕으로 답변드립니다:\n\n{context}\n\n질문: {query}\n\n위 문서 내용을 참고하여 답변드립니다. ({self.name}에서 제공)"
        else:
            return f"죄송합니다. 질문 '{query}'에 대한 관련 정보를 찾을 수 없습니다. 더 구체적인 질문을 해주시거나 관련 문서를 업로드해 주세요."

# LM Studio compatible agent
class LMStudioAgent:
    def __init__(self, name: str, knowledge_base: SimpleKnowledgeBase):
        self.name = name
        self.knowledge_base = knowledge_base
        from ..core import config
        self.client = AsyncOpenAI(
            api_key="not-needed",
            base_url=config.LM_STUDIO_BASE_URL
        )
        self.model_id = config.CUSTOM_MODEL_NAME
        
    async def arun(self, query: str, user_id: str = None, session_id: str = None):
        try:
            # Search knowledge base first
            results = self.knowledge_base.search(query)
            
            # Prepare context with Korean language instruction
            base_system_prompt = """당신은 한국어로 답변하는 기업용 RAG(검색 증강 생성) 어시스턴트입니다. 
반드시 한국어로만 답변해주세요. 영어나 다른 언어로 답변하지 마세요.

사용자의 질문에 대해 정확하고 도움이 되는 답변을 제공하세요. 
답변은 친근하고 전문적인 톤으로 작성해주세요."""

            if results:
                context = "\n".join([f"문서 {i+1}: {r['content'][:500]}..." for i, r in enumerate(results)])
                system_message = f"""{base_system_prompt}

다음 문서들을 참고하여 사용자의 질문에 답변해주세요:

{context}

위 문서 내용을 바탕으로 사용자의 질문에 한국어로 답변해주세요."""
            else:
                system_message = f"""{base_system_prompt}

사용자의 질문에 대해 당신의 지식을 바탕으로 한국어로 답변해주세요."""
            
            # Call LM Studio with simple message format
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LM Studio agent error: {e}")
            # Fallback to simple response in Korean
            results = self.knowledge_base.search(query)
            if results:
                context = "\n".join([r["content"] for r in results])
                return f"사용 가능한 문서를 바탕으로 답변드립니다:\n{context}\n\n질문에 대한 답변: {query}\n\n(참고: LM Studio 연결 실패로 기본 응답을 사용했습니다)"
            else:
                return f"죄송합니다. 질문 '{query}'에 대한 관련 정보를 찾을 수 없습니다.\n\n(참고: LM Studio 연결 실패)"

# Try to import advanced agent factory; fall back to SimpleAgent if unavailable.
try:
    from ..agents.factory import (
        create_knowledge_base,
        create_rag_agent,
        create_reasoning_agent,
        create_research_team,
    )
    _ADVANCED_FACTORY_AVAILABLE = True
except Exception:
    # The advanced factory relies on optional dependencies (e.g., agno).
    _ADVANCED_FACTORY_AVAILABLE = False


# Helper to decide whether we should use the advanced stack
def _use_advanced_stack() -> bool:
    """Return True if the advanced agent stack should be used."""
    # Check if we're in test mode
    if os.getenv("PYTEST_CURRENT_TEST") or "pytest" in os.getenv("PYTHONPATH", ""):
        logger.info("Test mode detected. Using mock objects.")
        return False
    
    if not _ADVANCED_FACTORY_AVAILABLE:
        logger.info("Advanced agent factory not available. Falling back to SimpleAgent.")
        return False

    # For LM Studio, use our custom LMStudioAgent instead of agno
    from ..core import config
    if config.MODEL_PROVIDER == "lm-studio":
        logger.info("MODEL_PROVIDER='lm-studio'. Using LMStudioAgent instead of agno.")
        return False  # Use our custom LM Studio agent
    
    use_advanced = config.MODEL_PROVIDER not in {"simple", "mock", "test"}
    logger.info(f"MODEL_PROVIDER='{config.MODEL_PROVIDER}'. Using advanced stack: {use_advanced}")
    return use_advanced

# In-memory cache for singleton instances
_knowledge_base: SimpleKnowledgeBase = None
_rag_agent: SimpleAgent = None
_reasoning_agent: SimpleAgent = None
_research_team: SimpleAgent = None


def get_knowledge_base() -> SimpleKnowledgeBase:
    global _knowledge_base
    if _knowledge_base is None:
        # Check if we're in test mode first
        if os.getenv("PYTEST_CURRENT_TEST") or "pytest" in os.getenv("PYTHONPATH", ""):
            _knowledge_base = MockKnowledgeBase()
        elif _use_advanced_stack():
            # Use vector-store backed knowledge base
            _knowledge_base = create_knowledge_base()
        else:
            _knowledge_base = SimpleKnowledgeBase()
    return _knowledge_base


def get_rag_agent(enable_memory: bool = True) -> SimpleAgent:
    global _rag_agent
    if _rag_agent is None:
        kb = get_knowledge_base()
        # Check if we're in test mode first
        if os.getenv("PYTEST_CURRENT_TEST") or "pytest" in os.getenv("PYTHONPATH", ""):
            _rag_agent = MockAgent("Enterprise RAG Assistant", kb)
        elif _use_advanced_stack():
            _rag_agent = create_rag_agent(kb, enable_memory=enable_memory)
        else:
            # Check if we should use LM Studio agent
            from ..core import config
            if config.MODEL_PROVIDER == "lm-studio":
                _rag_agent = LMStudioAgent("Enterprise RAG Assistant", kb)
            else:
                _rag_agent = SimpleAgent("Enterprise RAG Assistant", kb)
    return _rag_agent


def get_reasoning_agent(enable_memory: bool = True) -> SimpleAgent:
    global _reasoning_agent
    if _reasoning_agent is None:
        kb = get_knowledge_base()
        # Check if we're in test mode first
        if os.getenv("PYTEST_CURRENT_TEST") or "pytest" in os.getenv("PYTHONPATH", ""):
            _reasoning_agent = MockAgent("Reasoning Specialist", kb)
        elif _use_advanced_stack():
            _reasoning_agent = create_reasoning_agent(kb, enable_memory=enable_memory)
        else:
            # Check if we should use LM Studio agent
            from ..core import config
            if config.MODEL_PROVIDER == "lm-studio":
                _reasoning_agent = LMStudioAgent("Reasoning Specialist", kb)
            else:
                _reasoning_agent = SimpleAgent("Reasoning Specialist", kb)
    return _reasoning_agent


def get_research_team(enable_memory: bool = True) -> SimpleAgent:
    global _research_team
    if _research_team is None:
        # Check if we're in test mode first
        if os.getenv("PYTEST_CURRENT_TEST") or "pytest" in os.getenv("PYTHONPATH", ""):
            _research_team = MockAgent("Research Team", get_knowledge_base())
        elif _use_advanced_stack():
            _research_team = create_research_team(
                get_rag_agent(enable_memory=enable_memory), 
                get_reasoning_agent(enable_memory=enable_memory),
                enable_memory=enable_memory
            )
        else:
            # Check if we should use LM Studio agent
            from ..core import config
            if config.MODEL_PROVIDER == "lm-studio":
                kb = get_knowledge_base()
                _research_team = LMStudioAgent("Enterprise Research Team", kb)
            else:
                kb = get_knowledge_base()
                _research_team = SimpleAgent("Enterprise Research Team", kb)
    return _research_team 