from agno.agent import Agent
from agno.models.base import Model
from agno.models.openai import OpenAIChat
from agno.embedder.openai import OpenAIEmbedder

# Try to import agno memory modules, but handle if not available
try:
    from agno.memory.v2.memory import Memory
    from agno.memory.v2.db.sqlite import SqliteMemoryDb
    AGNO_MEMORY_AVAILABLE = True
except ImportError:
    AGNO_MEMORY_AVAILABLE = False
    # Create dummy classes
    class Memory:
        def __init__(self, *args, **kwargs):
            pass
    
    class SqliteMemoryDb:
        def __init__(self, *args, **kwargs):
            pass

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
from pathlib import Path

from ..core import config
from ..core.memory_manager import session_memory_manager

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

def create_memory_db():
    """Create memory database for agents"""
    if not AGNO_MEMORY_AVAILABLE:
        return None
    
    try:
        memory_db_path = Path(config.DB_FILE).parent / "agent_memories.db"
        return SqliteMemoryDb(
            table_name="agent_memories",
            db_file=str(memory_db_path)
        )
    except Exception as e:
        print(f"Failed to create memory database: {e}")
        return None

def create_rag_agent(knowledge_base: AgentKnowledge, enable_memory: bool = True):
    """Create the main RAG agent with memory support"""
    knowledge_tools = KnowledgeTools(
        knowledge=knowledge_base,
        think=True,
        search=True,
        analyze=True,
        add_few_shot=True,
    )
    
    # Setup memory if enabled
    memory = None
    if enable_memory and AGNO_MEMORY_AVAILABLE:
        try:
            memory_db = create_memory_db()
            if memory_db:
                memory = Memory(
                    model=get_model(),
                    db=memory_db
                )
        except Exception as e:
            print(f"Memory initialization failed: {e}")
            memory = None
    
    return Agent(
        name="Enterprise RAG Assistant",
        role="Advanced document analysis and knowledge retrieval specialist",
        agent_id=config.RAG_AGENT_ID,
        model=get_model(),
        tools=[knowledge_tools],
        memory=memory,
        enable_user_memories=enable_memory,
        instructions=[
            "당신은 문서 분석 전문 기업용 RAG 어시스턴트입니다.",
            "반드시 한국어로만 답변해주세요. 영어나 다른 언어로 답변하지 마세요.",
            "사용 가능한 문서를 바탕으로 항상 포괄적인 답변을 제공하세요.",
            "답변에 관련 소스와 인용을 포함하세요.",
            "친근하고 전문적인 톤으로 답변하세요.",
            "이전 대화 내용을 기억하고 연관성 있는 답변을 제공하세요.",
            "사용자의 선호도와 관심사를 기억하여 개인화된 답변을 제공하세요.",
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

def create_reasoning_agent(knowledge_base: AgentKnowledge, enable_memory: bool = True):
    """Create the advanced reasoning agent with memory support"""
    knowledge_tools = KnowledgeTools(knowledge=knowledge_base)
    
    tools = [knowledge_tools]
    if ReasoningTools:
        tools.append(ReasoningTools(add_instructions=True))
    if ThinkingTools:
        tools.append(ThinkingTools(add_instructions=True))
    
    # Setup memory if enabled
    memory = None
    if enable_memory and AGNO_MEMORY_AVAILABLE:
        try:
            memory_db = create_memory_db()
            if memory_db:
                memory = Memory(
                    model=get_model(),
                    db=memory_db
                )
        except Exception as e:
            print(f"Memory initialization failed for reasoning agent: {e}")
            memory = None
    
    return Agent(
        name="Reasoning Specialist",
        role="Advanced reasoning and analysis expert",
        agent_id=config.REASONING_AGENT_ID,
        model=get_model(),
        tools=tools,
        memory=memory,
        enable_user_memories=enable_memory,
        instructions=[
            "당신은 추론 전문가입니다. 복잡한 문제를 단계별로 분석하세요.",
            "반드시 한국어로만 답변해주세요. 영어나 다른 언어로 답변하지 마세요.",
            "복잡한 질문에는 연쇄 사고(chain-of-thought) 방식을 사용하세요.",
            "논리적이고 체계적인 분석을 제공하세요.",
            "이전 대화 맥락을 고려하여 일관성 있는 추론을 제공하세요.",
            "사용자의 관심 분야와 지식 수준을 기억하여 적절한 설명을 제공하세요.",
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

def create_research_team(rag_agent: Agent, reasoning_agent: Agent, enable_memory: bool = True):
    """Create the research team that combines RAG and reasoning agents with memory support"""
    # Setup memory if enabled
    memory = None
    if enable_memory and AGNO_MEMORY_AVAILABLE:
        try:
            memory_db = create_memory_db()
            if memory_db:
                memory = Memory(
                    model=get_model(),
                    db=memory_db
                )
        except Exception as e:
            print(f"Memory initialization failed for research team: {e}")
            memory = None
    
    return Team(
        name="Enterprise Research Team",
        members=[rag_agent, reasoning_agent],
        mode="coordinate",
        model=get_model(),
        memory=memory,
        enable_user_memories=enable_memory,
        instructions=[
            "RAG와 추론 에이전트 간의 협력을 통해 최적의 결과를 도출하세요.",
            "반드시 한국어로만 답변해주세요. 영어나 다른 언어로 답변하지 마세요.",
            "먼저 정보를 수집한 다음 추론과 분석을 적용하세요.",
            "팀워크를 통해 포괄적이고 정확한 답변을 제공하세요.",
            "팀원들이 이전 대화 내용과 사용자 선호도를 공유하여 일관성 있는 답변을 제공하세요.",
            "사용자의 질문 패턴과 관심사를 기억하여 더 적절한 협업을 수행하세요.",
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