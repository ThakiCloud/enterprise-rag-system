"""Core configuration and dependencies module."""

from . import config
from .dependencies import (
    get_knowledge_base,
    get_rag_agent,
    get_reasoning_agent,
    get_research_team,
)

__all__ = [
    "config",
    "get_knowledge_base",
    "get_rag_agent",
    "get_reasoning_agent", 
    "get_research_team",
] 