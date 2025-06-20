from fastapi import Depends
import os
from typing import Optional, TYPE_CHECKING
import logging
import asyncio
from openai import AsyncOpenAI

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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

# Simple agent implementation
class SimpleAgent:
    def __init__(self, name: str, knowledge_base: SimpleKnowledgeBase):
        self.name = name
        self.knowledge_base = knowledge_base
        
    async def arun(self, query: str):
        # Simple implementation that searches knowledge base
        results = self.knowledge_base.search(query)
        if results:
            context = "\n".join([r["content"] for r in results])
            return f"Based on the available documents:\n{context}\n\nRegarding your query: {query}\nThis is a simple response from {self.name}."
        else:
            return f"I couldn't find relevant information for your query: {query}"

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
        
    async def arun(self, query: str):
        try:
            # Search knowledge base first
            results = self.knowledge_base.search(query)
            
            # Prepare context
            if results:
                context = "\n".join([f"Document {i+1}: {r['content'][:500]}..." for i, r in enumerate(results)])
                system_message = f"You are an enterprise RAG assistant. Use the following documents to answer the user's question:\n\n{context}"
            else:
                system_message = "You are an enterprise RAG assistant. Answer the user's question based on your knowledge."
            
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
            # Fallback to simple response
            results = self.knowledge_base.search(query)
            if results:
                context = "\n".join([r["content"] for r in results])
                return f"Based on the available documents:\n{context}\n\nRegarding your query: {query}\n\n(Note: LM Studio connection failed, using fallback response)"
            else:
                return f"I couldn't find relevant information for your query: {query}\n\n(Note: LM Studio connection failed)"

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
        if _use_advanced_stack():
            # Use vector-store backed knowledge base
            _knowledge_base = create_knowledge_base()
        else:
            _knowledge_base = SimpleKnowledgeBase()
    return _knowledge_base


def get_rag_agent() -> SimpleAgent:
    global _rag_agent
    if _rag_agent is None:
        kb = get_knowledge_base()
        if _use_advanced_stack():
            _rag_agent = create_rag_agent(kb)
        else:
            # Check if we should use LM Studio agent
            from ..core import config
            if config.MODEL_PROVIDER == "lm-studio":
                _rag_agent = LMStudioAgent("Enterprise RAG Assistant", kb)
            else:
                _rag_agent = SimpleAgent("Enterprise RAG Assistant", kb)
    return _rag_agent


def get_reasoning_agent() -> SimpleAgent:
    global _reasoning_agent
    if _reasoning_agent is None:
        kb = get_knowledge_base()
        if _use_advanced_stack():
            _reasoning_agent = create_reasoning_agent(kb)
        else:
            # Check if we should use LM Studio agent
            from ..core import config
            if config.MODEL_PROVIDER == "lm-studio":
                _reasoning_agent = LMStudioAgent("Reasoning Specialist", kb)
            else:
                _reasoning_agent = SimpleAgent("Reasoning Specialist", kb)
    return _reasoning_agent


def get_research_team() -> SimpleAgent:
    global _research_team
    if _research_team is None:
        if _use_advanced_stack():
            _research_team = create_research_team(get_rag_agent(), get_reasoning_agent())
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