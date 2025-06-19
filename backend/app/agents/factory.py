from agno.agent import Agent
from agno.models.base import ChatModel
from agno.models.openai import OpenAIChat
from agno.models.anthropic import AnthropicChat
from agno.models.google import GoogleChat
from agno.models.ollama import OllamaChat
from agno.tools.knowledge import KnowledgeTools
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.storage.sqlite import SqliteStorage
from agno.team import Team
from agno.tools.reasoning import ReasoningTools
from agno.tools.thinking import ThinkingTools
from agno.knowledge.text import AgentKnowledge

from ..core import config

def get_model() -> ChatModel:
    """Creates and returns a chat model instance based on the provider specified in config."""
    provider = config.MODEL_PROVIDER
    
    if provider == "openai":
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set for provider 'openai'")
        return OpenAIChat(id=config.OPENAI_MODEL_NAME, api_key=config.OPENAI_API_KEY)
    
    if provider == "anthropic":
        if not config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set for provider 'anthropic'")
        return AnthropicChat(id=config.ANTHROPIC_MODEL_NAME, api_key=config.ANTHROPIC_API_KEY)
        
    if provider == "google":
        if not config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable not set for provider 'google'")
        return GoogleChat(id=config.GOOGLE_MODEL_NAME, api_key=config.GOOGLE_API_KEY)

    if provider == "ollama":
        return OllamaChat(id=config.OLLAMA_MODEL_NAME, base_url=config.OLLAMA_BASE_URL)

    if provider == "lm-studio":
        return OpenAIChat(
            id=config.CUSTOM_MODEL_NAME, # LM Studio doesn't use model id from here
            api_key="not-needed",
            base_url=config.LM_STUDIO_BASE_URL,
        )

    if provider in ["vllm", "custom"]:
        if not config.CUSTOM_API_BASE_URL:
            raise ValueError(f"CUSTOM_API_BASE_URL environment variable not set for provider '{provider}'")
        return OpenAIChat(
            id=config.CUSTOM_MODEL_NAME,
            api_key=config.CUSTOM_API_KEY,
            base_url=config.CUSTOM_API_BASE_URL,
        )
        
    raise ValueError(f"Unsupported model provider specified: {provider}")

def create_knowledge_base():
    """Initialize the vector database and knowledge base"""
    return AgentKnowledge(
        sources=[],
        vector_db=LanceDb(
            uri=str(config.VECTOR_DB_PATH),
            table_name="enterprise_documents",
            search_type=SearchType.hybrid,
        ),
    )

def create_rag_agent(knowledge_base: AgentKnowledge):
    """Create the main RAG agent"""
    knowledge_tools = KnowledgeTools(
        knowledge=knowledge_base,
        think=True,
        search=True,
        analyze=True,
        add_few_shot=True,
        num_documents=10,
        chunk_size=1000,
    )
    
    return Agent(
        name="Enterprise RAG Assistant",
        role="Advanced document analysis and knowledge retrieval specialist",
        agent_id=config.RAG_AGENT_ID,
        model=get_model(),
        tools=[knowledge_tools],
        instructions=[
            "You are an enterprise RAG assistant specialized in document analysis.",
            "Always provide comprehensive answers based on available documents.",
            "Include relevant sources and citations in your responses.",
        ],
        storage=SqliteStorage(
            table_name="rag_agent_sessions",
            db_file=str(config.DB_FILE),
            auto_upgrade_schema=True
        ),
        add_history_to_messages=True,
        num_history_responses=10,
        add_datetime_to_instructions=True,
        markdown=True,
        show_tool_calls=True,
    )

def create_reasoning_agent(knowledge_base: AgentKnowledge):
    """Create the advanced reasoning agent"""
    knowledge_tools = KnowledgeTools(knowledge=knowledge_base, num_documents=5)
    
    return Agent(
        name="Reasoning Specialist",
        role="Advanced reasoning and analysis expert",
        agent_id=config.REASONING_AGENT_ID,
        model=get_model(),
        tools=[
            knowledge_tools,
            ReasoningTools(add_instructions=True),
            ThinkingTools(add_instructions=True),
        ],
        instructions=[
            "You are a reasoning specialist. Break down complex problems.",
            "Use chain-of-thought for complex queries.",
        ],
        storage=SqliteStorage(
            table_name="reasoning_agent_sessions",
            db_file=str(config.DB_FILE),
            auto_upgrade_schema=True
        ),
        add_history_to_messages=True,
        num_history_responses=5,
        add_datetime_to_instructions=True,
        markdown=True,
        show_tool_calls=True,
        reasoning=True,
    )

def create_research_team(rag_agent: Agent, reasoning_agent: Agent):
    """Create the research team that combines RAG and reasoning agents"""
    return Team(
        name="Enterprise Research Team",
        members=[rag_agent, reasoning_agent],
        mode="coordinate",
        model=get_model(),
        instructions=[
            "Coordinate between RAG and reasoning for optimal results.",
            "First gather information, then apply reasoning and analysis.",
        ],
        team_id=config.RESEARCH_TEAM_ID,
        storage=SqliteStorage(
            table_name="research_team_sessions",
            db_file=str(config.DB_FILE),
            auto_upgrade_schema=True
        ),
        add_datetime_to_instructions=True,
        markdown=True,
        show_tool_calls=True,
        show_members_responses=True,
    ) 