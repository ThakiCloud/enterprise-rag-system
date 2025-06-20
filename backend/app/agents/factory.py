from agno.agent import Agent
from agno.models.base import Model
from agno.models.openai import OpenAIChat
from agno.embedder.openai import OpenAIEmbedder
# Only import models that are actually working
try:
    from agno.models.anthropic import AnthropicChat
except ImportError:
    AnthropicChat = None

try:
    from agno.models.google import GoogleChat
except ImportError:
    GoogleChat = None

try:
    from agno.models.ollama import OllamaChat
except ImportError:
    OllamaChat = None

from agno.tools.knowledge import KnowledgeTools
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.storage.sqlite import SqliteStorage
from agno.team import Team
try:
    from agno.tools.reasoning import ReasoningTools
except ImportError:
    ReasoningTools = None

try:
    from agno.tools.thinking import ThinkingTools
except ImportError:
    ThinkingTools = None

from agno.knowledge.text import AgentKnowledge

from ..core import config

def get_model() -> Model:
    """Creates and returns a chat model instance based on the provider specified in config."""
    provider = config.MODEL_PROVIDER
    
    if provider == "openai":
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set for provider 'openai'")
        return OpenAIChat(id=config.OPENAI_MODEL_NAME, api_key=config.OPENAI_API_KEY)
    
    if provider == "anthropic":
        if not AnthropicChat:
            raise ValueError("Anthropic model not available. Please install compatible anthropic library.")
        if not config.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set for provider 'anthropic'")
        return AnthropicChat(id=config.ANTHROPIC_MODEL_NAME, api_key=config.ANTHROPIC_API_KEY)
        
    if provider == "google":
        if not GoogleChat:
            raise ValueError("Google model not available. Please install compatible google library.")
        if not config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable not set for provider 'google'")
        return GoogleChat(id=config.GOOGLE_MODEL_NAME, api_key=config.GOOGLE_API_KEY)

    if provider == "ollama":
        if not OllamaChat:
            raise ValueError("Ollama model not available. Please install compatible ollama library.")
        return OllamaChat(id=config.OLLAMA_MODEL_NAME, base_url=config.OLLAMA_BASE_URL)

    if provider == "lm-studio":
        return OpenAIChat(
            id=config.CUSTOM_MODEL_NAME,
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

def get_embedder():
    """Creates and returns an embedder instance based on the provider specified in config."""
    provider = config.MODEL_PROVIDER
    
    if provider == "lm-studio":
        # Use LM Studio's embedding model
        return OpenAIEmbedder(
            id="text-embedding-nomic-embed-text-v1.5",
            api_key="not-needed",
            base_url=config.LM_STUDIO_BASE_URL,
        )
    elif provider == "openai":
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set for provider 'openai'")
        return OpenAIEmbedder(
            id="text-embedding-ada-002",
            api_key=config.OPENAI_API_KEY,
        )
    else:
        # For other providers, try to use LM Studio if available, otherwise OpenAI
        try:
            return OpenAIEmbedder(
                id="text-embedding-nomic-embed-text-v1.5",
                api_key="not-needed",
                base_url=config.LM_STUDIO_BASE_URL,
            )
        except:
            # Fallback to OpenAI if LM Studio not available
            if config.OPENAI_API_KEY:
                return OpenAIEmbedder(
                    id="text-embedding-ada-002",
                    api_key=config.OPENAI_API_KEY,
                )
            else:
                raise ValueError("No embedder available. Please set up LM Studio or OpenAI API key.")

def create_knowledge_base():
    """Initialize the vector database and knowledge base"""
    return AgentKnowledge(
        sources=[],
        vector_db=LanceDb(
            uri=str(config.VECTOR_DB_PATH),
            table_name="enterprise_documents",
            search_type=SearchType.hybrid,
            embedder=get_embedder(),
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
        num_history_responses=5,
        add_datetime_to_instructions=False,
        markdown=True,
        show_tool_calls=False,
    )

def create_reasoning_agent(knowledge_base: AgentKnowledge):
    """Create the advanced reasoning agent"""
    knowledge_tools = KnowledgeTools(knowledge=knowledge_base)
    
    tools = [knowledge_tools]
    if ReasoningTools:
        tools.append(ReasoningTools(add_instructions=True))
    if ThinkingTools:
        tools.append(ThinkingTools(add_instructions=True))
    
    return Agent(
        name="Reasoning Specialist",
        role="Advanced reasoning and analysis expert",
        agent_id=config.REASONING_AGENT_ID,
        model=get_model(),
        tools=tools,
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
        num_history_responses=3,
        add_datetime_to_instructions=False,
        markdown=True,
        show_tool_calls=False,
        reasoning=False,
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
        add_datetime_to_instructions=False,
        markdown=True,
        show_tool_calls=False,
        show_members_responses=False,
    ) 